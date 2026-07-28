"""Single Kafka consumer that records fresh quotes and turns active alerts into notifications."""
from __future__ import annotations

import json
import os
import signal

from confluent_kafka import Consumer, KafkaError

from db import get_database, init_database, utcnow

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
PRICE_TOPIC = "stocks"
PREDICTION_TOPIC = "stock_predictions"
running = True


def stop(*_):
    global running
    running = False


def create_notification(db, alert, title, body, details):
    now = utcnow()
    # The status predicate makes triggering atomic when more than one monitor is running.
    result = db.alerts.update_one(
        {"_id": alert["_id"], "status": "active"},
        {"$set": {"status": "triggered", "triggered_at": now, "updated_at": now}},
    )
    if result.modified_count:
        db.notifications.insert_one(
            {"user_id": alert["user_id"], "alert_id": str(alert["_id"]), "title": title, "body": body, "details": details, "created_at": now}
        )


def process_price(db, payload):
    symbol = str(payload.get("symbol", "")).upper()
    if not symbol or payload.get("price") is None:
        return
    price_paise = int(round(float(payload["price"]) * 100))
    now = utcnow()
    old = db.market_quotes.find_one({"symbol": symbol})
    previous = old.get("price_paise") if old else None
    db.market_quotes.update_one(
        {"symbol": symbol},
        {"$set": {"symbol": symbol, "price_paise": price_paise, "change_pct": payload.get("change_pct"), "source_timestamp": payload.get("timestamp"), "updated_at": now}},
        upsert=True,
    )
    print(f"Quote received: {symbol} ₹{price_paise / 100:.2f}", flush=True)
    if previous is None:
        return
    alerts = db.alerts.find({"symbol": symbol, "kind": "price", "status": "active"})
    for alert in alerts:
        threshold = alert["threshold_paise"]
        crossed = (alert["direction"] == "above" and previous < threshold <= price_paise) or (alert["direction"] == "below" and previous > threshold >= price_paise)
        if crossed:
            rupees = threshold / 100
            create_notification(db, alert, f"Price alert: {symbol}", f"{symbol} crossed {'above' if alert['direction'] == 'above' else 'below'} ₹{rupees:,.2f}.", {"price_paise": price_paise, "threshold_paise": threshold})


def process_prediction(db, payload):
    symbol = str(payload.get("symbol", "")).upper()
    if not symbol or payload.get("prediction") is None:
        return
    quote = db.market_quotes.find_one({"symbol": symbol})
    if not quote or not quote.get("price_paise"):
        return
    prediction_paise = int(round(float(payload["prediction"]) * 100))
    print(f"Prediction received: {symbol} ₹{prediction_paise / 100:.2f}", flush=True)
    movement = ((prediction_paise - quote["price_paise"]) / quote["price_paise"]) * 100
    if abs(movement) < 1.5:
        return
    direction = "up" if movement > 0 else "down"
    for alert in db.alerts.find({"symbol": symbol, "kind": "ai_movement", "status": "active"}):
        create_notification(
            db,
            alert,
            f"AI movement alert: {symbol}",
            f"TradeX forecasts {direction} {abs(movement):.2f}% in the next 5 minutes.",
            {"price_paise": quote["price_paise"], "prediction_paise": prediction_paise, "movement_percent": round(movement, 4)},
        )


def main():
    print("Connecting to MongoDB Atlas…", flush=True)
    db = init_database()
    print("MongoDB Atlas connected.", flush=True)
    consumer = Consumer({"bootstrap.servers": KAFKA_BOOTSTRAP, "group.id": "tradex-market-monitor", "auto.offset.reset": "latest", "enable.auto.commit": True})
    consumer.subscribe([PRICE_TOPIC, PREDICTION_TOPIC])
    print(f"Listening for Kafka topics: {PRICE_TOPIC}, {PREDICTION_TOPIC}", flush=True)
    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        while running:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                if message.error().code() != KafkaError._PARTITION_EOF:
                    print(f"Kafka error: {message.error()}")
                continue
            try:
                payload = json.loads(message.value().decode("utf-8"))
                if message.topic() == PRICE_TOPIC:
                    process_price(db, payload)
                else:
                    process_prediction(db, payload)
            except Exception as exc:
                print(f"Could not process market event: {exc}")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
