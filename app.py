from __future__ import annotations

import json
import os
import random
import time
from datetime import timedelta
from functools import wraps

import requests
import yfinance as yf
import db as mongo
from bson import ObjectId
from confluent_kafka import Consumer, KafkaError, Producer
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from db import get_database, init_database, utcnow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOCKS_CACHE_FILE = os.path.join(BASE_DIR, "stocks_master.json")
DAILY_PREDICTIONS_FILE = os.path.join(BASE_DIR, "daily_predictions.json")
CACHE_EXPIRY = 24 * 3600
STARTING_CASH_PAISE = 100_000_000  # INR 10,00,000
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
KAFKA_PRICE_TOPIC = "stocks"
KAFKA_PREDICTION_TOPIC = "stock_predictions"
PREDICTION_COMMAND_TOPIC = "prediction_requests"
TRAINING_COMMAND_TOPIC = "training_requests"


class User(UserMixin):
    def __init__(self, document):
        self.document = document
        self.id = str(document["_id"])

    @property
    def email(self):
        return self.document["email"]


login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv("FLASK_SECRET_KEY", ""),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
    )
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("FLASK_SECRET_KEY is required. Configure it in your environment.")
    CORS(app, origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")], supports_credentials=True)
    init_database()
    login_manager.init_app(app)
    return app


@login_manager.user_loader
def load_user(user_id):
    try:
        document = get_database().users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None
    return User(document) if document else None


def api_error(message, status=400):
    return jsonify({"error": message}), status


def api_login_required(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            return api_error("Authentication required.", 401)
        return fn(*args, **kwargs)
    return decorated


def user_id():
    return current_user.id


def serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize(item) for key, item in value.items()}
    return value


def get_active_portfolio(db, account_id, session=None):
    return db.portfolios.find_one({"user_id": account_id, "status": "active"}, session=session)


def ensure_active_portfolio(db, account_id, session=None):
    portfolio = get_active_portfolio(db, account_id, session)
    if portfolio:
        return portfolio
    now = utcnow()
    document = {
        "user_id": account_id,
        "status": "active",
        "starting_cash_paise": STARTING_CASH_PAISE,
        "cash_paise": STARTING_CASH_PAISE,
        "realized_pnl_paise": 0,
        "closed_lots": 0,
        "winning_lots": 0,
        "positions": [],
        "created_at": now,
        "updated_at": now,
    }
    inserted = db.portfolios.insert_one(document, session=session)
    document["_id"] = inserted.inserted_id
    return document


def price_to_paise(value):
    return int(round(float(value) * 100))


def get_fresh_quote(db, symbol):
    quote = db.market_quotes.find_one({"symbol": symbol.upper()})
    if not quote:
        return None
    max_age = int(os.getenv("QUOTE_MAX_AGE_SECONDS", "90"))
    if utcnow() - quote["updated_at"] > timedelta(seconds=max_age):
        return None
    return quote


def portfolio_view(db, portfolio):
    market_value = 0
    unrealized = 0
    positions = []
    for position in portfolio.get("positions", []):
        quote = db.market_quotes.find_one({"symbol": position["symbol"]})
        quote_paise = quote.get("price_paise") if quote else None
        cost_paise = sum(lot["quantity"] * lot["entry_price_paise"] for lot in position["lots"])
        item = {
            "symbol": position["symbol"],
            "quantity": position["quantity"],
            "cost_paise": cost_paise,
            "average_cost_paise": cost_paise // position["quantity"],
            "last_price_paise": quote_paise,
            "market_value_paise": None,
            "unrealized_pnl_paise": None,
        }
        if quote_paise is not None:
            item["market_value_paise"] = position["quantity"] * quote_paise
            item["unrealized_pnl_paise"] = item["market_value_paise"] - cost_paise
            market_value += item["market_value_paise"]
            unrealized += item["unrealized_pnl_paise"]
        positions.append(item)
    equity = portfolio["cash_paise"] + market_value
    closed = portfolio["closed_lots"]
    return {
        "id": str(portfolio["_id"]),
        "starting_cash_paise": portfolio["starting_cash_paise"],
        "cash_paise": portfolio["cash_paise"],
        "market_value_paise": market_value,
        "equity_paise": equity,
        "realized_pnl_paise": portfolio["realized_pnl_paise"],
        "unrealized_pnl_paise": unrealized,
        "total_pnl_paise": equity - portfolio["starting_cash_paise"],
        "win_rate": round((portfolio["winning_lots"] / closed) * 100, 2) if closed else 0,
        "closed_lots": closed,
        "positions": positions,
    }


def kafka_consumer_generator(topics, group_id_prefix):
    consumer = Consumer({"bootstrap.servers": KAFKA_BOOTSTRAP, "group.id": f"{group_id_prefix}-{random.randint(0, 99999)}", "auto.offset.reset": "latest"})
    consumer.subscribe(topics)
    try:
        while True:
            message = consumer.poll(1.0)
            if message is None:
                continue
            if message.error():
                if message.error().code() != KafkaError._PARTITION_EOF:
                    print(f"Kafka consumer error: {message.error()}")
                continue
            yield {"key": message.key().decode("utf-8") if message.key() else None, "value": message.value().decode("utf-8")}
    finally:
        consumer.close()


def send_command(topic, command):
    try:
        producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP})
        producer.produce(topic, value=json.dumps(command).encode("utf-8"))
        producer.flush(1)
    except Exception as exc:
        print(f"Kafka command failed: {exc}")


app = create_app()


@app.get("/health")
def health():
    try:
        get_database().command("ping")
        return jsonify({"status": "ok", "database": "connected"})
    except Exception as exc:
        return api_error(f"Database unavailable: {exc}", 503)


@app.post("/api/auth/register")
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if "@" not in email or len(password) < 8:
        return api_error("Enter a valid email and a password of at least 8 characters.")
    db = get_database()
    now = utcnow()
    try:
        result = db.users.insert_one({"email": email, "password_hash": generate_password_hash(password), "created_at": now})
    except Exception:
        return api_error("An account already exists for that email.", 409)
    account = db.users.find_one({"_id": result.inserted_id})
    ensure_active_portfolio(db, str(result.inserted_id))
    login_user(User(account), remember=True)
    return jsonify({"user": {"id": str(result.inserted_id), "email": email}}), 201


@app.post("/api/auth/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    account = get_database().users.find_one({"email": email})
    if not account or not check_password_hash(account["password_hash"], str(data.get("password", ""))):
        return api_error("Invalid email or password.", 401)
    login_user(User(account), remember=True)
    return jsonify({"user": {"id": str(account["_id"]), "email": account["email"]}})


@app.post("/api/auth/logout")
@api_login_required
def logout():
    logout_user()
    return jsonify({"status": "ok"})


@app.get("/api/auth/me")
@api_login_required
def me():
    return jsonify({"user": {"id": user_id(), "email": current_user.email}})


@app.get("/api/portfolio")
@api_login_required
def read_portfolio():
    db = get_database()
    return jsonify(portfolio_view(db, ensure_active_portfolio(db, user_id())))


@app.get("/api/orders")
@api_login_required
def order_history():
    orders = get_database().orders.find({"user_id": user_id()}).sort("created_at", -1).limit(100)
    return jsonify([serialize(order) for order in orders])


@app.post("/api/orders")
@api_login_required
def place_order():
    data = request.get_json(silent=True) or {}
    symbol = str(data.get("symbol", "")).upper().strip()
    side = str(data.get("side", "")).upper()
    try:
        quantity = int(data.get("quantity", 0))
    except (ValueError, TypeError):
        quantity = 0
    if not symbol or side not in {"BUY", "SELL"} or quantity < 1:
        return api_error("symbol, BUY or SELL side, and a whole-share quantity are required.")
    db = get_database()
    quote = get_fresh_quote(db, symbol)
    if not quote:
        return api_error("Trading is unavailable until a fresh live market price arrives.", 409)
    price_paise = quote["price_paise"]
    now = utcnow()
    account_id = user_id()

    def commit_order(session):
        portfolio = ensure_active_portfolio(db, account_id, session)
        positions = portfolio.get("positions", [])
        position_index = next((i for i, item in enumerate(positions) if item["symbol"] == symbol), None)
        gross_paise = quantity * price_paise
        realized = 0
        closed_lots = 0
        winning_lots = 0
        if side == "BUY":
            if portfolio["cash_paise"] < gross_paise:
                raise ValueError("Insufficient virtual cash for this order.")
            lot = {"quantity": quantity, "entry_price_paise": price_paise, "opened_at": now}
            if position_index is None:
                positions.append({"symbol": symbol, "quantity": quantity, "lots": [lot]})
            else:
                positions[position_index]["quantity"] += quantity
                positions[position_index]["lots"].append(lot)
            cash = portfolio["cash_paise"] - gross_paise
        else:
            if position_index is None or positions[position_index]["quantity"] < quantity:
                raise ValueError("You can only sell shares currently held in the portfolio.")
            position = positions[position_index]
            remaining = quantity
            remaining_lots = []
            for lot in position["lots"]:
                sold = min(lot["quantity"], remaining)
                if sold:
                    lot_pnl = sold * (price_paise - lot["entry_price_paise"])
                    realized += lot_pnl
                    closed_lots += 1
                    winning_lots += int(lot_pnl > 0)
                    remaining -= sold
                if sold < lot["quantity"]:
                    remaining_lots.append({**lot, "quantity": lot["quantity"] - sold})
            position["quantity"] -= quantity
            if position["quantity"] == 0:
                positions.pop(position_index)
            else:
                position["lots"] = remaining_lots
            cash = portfolio["cash_paise"] + gross_paise
        order = {"user_id": account_id, "portfolio_id": str(portfolio["_id"]), "symbol": symbol, "side": side, "quantity": quantity, "price_paise": price_paise, "gross_paise": gross_paise, "realized_pnl_paise": realized, "created_at": now}
        db.portfolios.update_one({"_id": portfolio["_id"]}, {"$set": {"cash_paise": cash, "positions": positions, "updated_at": now}, "$inc": {"realized_pnl_paise": realized, "closed_lots": closed_lots, "winning_lots": winning_lots}}, session=session)
        db.orders.insert_one(order, session=session)
        return order

    try:
        if mongo.client is None:
            raise RuntimeError("MongoDB client is unavailable")
        with mongo.client.start_session() as session:
            order = session.with_transaction(commit_order)
    except ValueError as exc:
        return api_error(str(exc), 409)
    except Exception as exc:
        return api_error(f"Could not place order: {exc}", 503)
    return jsonify(serialize(order)), 201


@app.post("/api/portfolio/reset")
@api_login_required
def reset_portfolio():
    db = get_database()
    now = utcnow()
    existing = ensure_active_portfolio(db, user_id())
    db.portfolios.update_one({"_id": existing["_id"]}, {"$set": {"status": "archived", "archived_at": now}})
    portfolio = ensure_active_portfolio(db, user_id())
    return jsonify(portfolio_view(db, portfolio)), 201


@app.get("/api/watchlist")
@api_login_required
def get_watchlist():
    record = get_database().watchlists.find_one({"user_id": user_id()}) or {"symbols": []}
    return jsonify(record["symbols"])


@app.post("/api/watchlist")
@api_login_required
def add_watchlist_symbol():
    symbol = str((request.get_json(silent=True) or {}).get("symbol", "")).upper().strip()
    if not symbol:
        return api_error("A symbol is required.")
    get_database().watchlists.update_one({"user_id": user_id()}, {"$addToSet": {"symbols": symbol}, "$set": {"updated_at": utcnow()}}, upsert=True)
    send_command(PREDICTION_COMMAND_TOPIC, {"action": "ADD", "symbol": symbol})
    return jsonify({"status": "ok"}), 201


@app.delete("/api/watchlist/<symbol>")
@api_login_required
def remove_watchlist_symbol(symbol):
    get_database().watchlists.update_one({"user_id": user_id()}, {"$pull": {"symbols": symbol.upper()}, "$set": {"updated_at": utcnow()}})
    return jsonify({"status": "ok"})


@app.get("/api/alerts")
@api_login_required
def list_alerts():
    alerts = get_database().alerts.find({"user_id": user_id()}).sort("created_at", -1)
    return jsonify([serialize(alert) for alert in alerts])


@app.post("/api/alerts")
@api_login_required
def create_alert():
    data = request.get_json(silent=True) or {}
    kind = str(data.get("kind", "")).lower()
    symbol = str(data.get("symbol", "")).upper().strip()
    if kind not in {"price", "ai_movement"} or not symbol:
        return api_error("A symbol and price or ai_movement alert type are required.")
    alert = {"user_id": user_id(), "symbol": symbol, "kind": kind, "status": "active", "created_at": utcnow(), "updated_at": utcnow()}
    if kind == "price":
        direction = str(data.get("direction", "")).lower()
        try:
            threshold_paise = price_to_paise(data.get("threshold"))
        except (ValueError, TypeError):
            threshold_paise = 0
        if direction not in {"above", "below"} or threshold_paise < 1:
            return api_error("Price alerts require an above/below direction and a positive rupee threshold.")
        alert.update({"direction": direction, "threshold_paise": threshold_paise})
    else:
        alert["threshold_percent"] = 1.5
    inserted = get_database().alerts.insert_one(alert)
    send_command(PREDICTION_COMMAND_TOPIC, {"action": "ADD", "symbol": symbol})
    alert["_id"] = inserted.inserted_id
    return jsonify(serialize(alert)), 201


@app.post("/api/alerts/<alert_id>/disable")
@api_login_required
def disable_alert(alert_id):
    get_database().alerts.update_one({"_id": ObjectId(alert_id), "user_id": user_id(), "status": "active"}, {"$set": {"status": "disabled", "updated_at": utcnow()}})
    return jsonify({"status": "ok"})


@app.delete("/api/alerts/<alert_id>")
@api_login_required
def delete_alert(alert_id):
    get_database().alerts.delete_one({"_id": ObjectId(alert_id), "user_id": user_id()})
    return jsonify({"status": "ok"})


@app.get("/api/notifications")
@api_login_required
def notifications():
    items = get_database().notifications.find({"user_id": user_id()}).sort("created_at", -1).limit(50)
    return jsonify([serialize(item) for item in items])


@app.get("/api/stream/notifications")
@api_login_required
def notification_stream():
    account_id = user_id()
    def stream():
        latest = utcnow()
        while True:
            records = get_database().notifications.find({"user_id": account_id, "created_at": {"$gt": latest}}).sort("created_at", 1)
            for record in records:
                latest = record["created_at"]
                yield f"data: {json.dumps(serialize(record))}\n\n"
            yield ": keepalive\n\n"
            time.sleep(1)
    return Response(stream(), content_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def load_all_indian_stocks():
    if os.path.exists(STOCKS_CACHE_FILE) and time.time() - os.path.getmtime(STOCKS_CACHE_FILE) < CACHE_EXPIRY:
        with open(STOCKS_CACHE_FILE, "r", encoding="utf-8") as source:
            return json.load(source)
    stocks = {}
    try:
        rows = requests.get("https://archives.nseindia.com/content/equities/EQUITY_L.csv", headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text.splitlines()
        for row in rows[1:]:
            parts = row.split(",")
            if len(parts) >= 2 and parts[0].strip() and parts[1].strip():
                stocks[f"{parts[0].strip()}.NS"] = f"{parts[1].strip().title()} (NSE)"
    except Exception as exc:
        print(f"NSE search failed: {exc}")
    with open(STOCKS_CACHE_FILE, "w", encoding="utf-8") as target:
        json.dump(stocks, target, indent=2)
    return stocks


@app.get("/search")
def search_stocks():
    query = request.args.get("query", "").strip().lower()
    if not query:
        return jsonify({"symbols": []})
    matches = [{"symbol": symbol, "name": name} for symbol, name in load_all_indian_stocks().items() if query in symbol.lower() or query in name.lower()]
    return jsonify({"symbols": matches[:50]})


def stock_response(symbol):
    stock = yf.Ticker(symbol)
    history = stock.history(period="1d", interval="5m")
    if history.empty:
        return None
    info = stock.info
    trend = [
        {
            "time": index.strftime("%H:%M"),
            "timestamp": index.isoformat(),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "price": round(float(row["Close"]), 2),  # Backwards compatible line-chart field.
            "volume": int(row.get("Volume", 0) or 0),
        }
        for index, row in history.iterrows()
    ]
    current = trend[-1]["price"]
    previous_close = float(info.get("previousClose", 0) or 0)
    return {"symbol": symbol, "name": info.get("longName", symbol), "current": current, "change": round(((current - previous_close) / previous_close) * 100, 2) if previous_close else 0, "summary": info.get("longBusinessSummary", "No company summary available."), "previousClose": previous_close, "dayHigh": float(info.get("dayHigh", 0) or 0), "dayLow": float(info.get("dayLow", 0) or 0), "marketCap": info.get("marketCap"), "sector": info.get("sector"), "updated": utcnow().strftime("%H:%M:%S"), "intraday_trend": trend}


@app.get("/stock/<symbol>")
@app.get("/stock_history/<symbol>")
def stock_detail(symbol):
    try:
        data = stock_response(symbol)
        return jsonify(data) if data else api_error("No recent intraday data available.", 404)
    except Exception as exc:
        return api_error(str(exc), 500)


@app.get("/prediction/daily/<symbol>")
def daily_prediction(symbol):
    if not os.path.exists(DAILY_PREDICTIONS_FILE):
        return jsonify({"outlook": "Not yet calculated."})
    with open(DAILY_PREDICTIONS_FILE, "r", encoding="utf-8") as source:
        return jsonify({"outlook": json.load(source).get(symbol, "Not available.")})


@app.post("/predict/start/<symbol>")
def start_prediction(symbol):
    send_command(PREDICTION_COMMAND_TOPIC, {"action": "ADD", "symbol": symbol})
    return jsonify({"status": "ok"})


@app.post("/train/on_demand/<symbol>")
def train_on_demand(symbol):
    send_command(TRAINING_COMMAND_TOPIC, {"symbol": symbol})
    return jsonify({"status": "ok"}), 202


@app.get("/stream/<symbol>")
def stream_price(symbol):
    def filtered():
        for message in kafka_consumer_generator([KAFKA_PRICE_TOPIC], "price-stream"):
            if message["key"] == symbol:
                yield f"data: {message['value']}\n\n"
    return Response(filtered(), content_type="text/event-stream")


@app.get("/stream/prediction/<symbol>")
def stream_prediction(symbol):
    def filtered():
        for message in kafka_consumer_generator([KAFKA_PREDICTION_TOPIC], "prediction-stream"):
            if message["key"] == symbol:
                yield f"data: {message['value']}\n\n"
    return Response(filtered(), content_type="text/event-stream")


@app.get("/stream/all_prices")
def stream_all_prices():
    def broadcast():
        for message in kafka_consumer_generator([KAFKA_PRICE_TOPIC], "all-prices-stream"):
            yield f"data: {message['value']}\n\n"
    return Response(broadcast(), content_type="text/event-stream")


if __name__ == "__main__":
    app.run(debug=True, threaded=True, port=5000)
