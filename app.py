from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from confluent_kafka import Producer, Consumer, KafkaError
import yfinance as yf
import requests
import json
import os
import time
import random
from datetime import datetime

# ==========================================================
# ⚙️ Flask App Setup
# ==========================================================
app = Flask(__name__)
CORS(app)

# --- Files & Config using absolute paths for reliability ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOCKS_CACHE_FILE = os.path.join(BASE_DIR, "stocks_master.json")
FAVORITES_FILE = os.path.join(BASE_DIR, "favorites.json")
DAILY_PREDICTIONS_FILE = os.path.join(BASE_DIR, "daily_predictions.json")
CACHE_EXPIRY = 24 * 3600
user_favorites = {}

# --- Kafka Config ---
KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_PRICE_TOPIC = "stocks"
KAFKA_PREDICTION_TOPIC = "stock_predictions"
PREDICTION_COMMAND_TOPIC = "prediction_requests"
TRAINING_COMMAND_TOPIC = "training_requests"

# ==========================================================
# 💖 FAVORITES PERSISTENCE
# ==========================================================
def load_favorites_from_file():
    global user_favorites
    try:
        with open(FAVORITES_FILE, "r") as f:
            user_favorites = json.load(f)
        print("✅ Favorites loaded from file.")
    except (FileNotFoundError, json.JSONDecodeError):
        print("📝 Favorites file not found or is corrupt. Creating a new one.")
        user_favorites = {}
        save_favorites_to_file()

def save_favorites_to_file():
    try:
        with open(FAVORITES_FILE, "w") as f:
            json.dump(user_favorites, f, indent=4)
    except Exception as e:
        print(f"⚠️ Error saving favorites to file: {e}")

# ==========================================================
# ⚡️ COMMAND PRODUCER (Sends commands to backend services)
# ==========================================================
producer_config = {'bootstrap.servers': KAFKA_BOOTSTRAP}
try:
    command_producer = Producer(producer_config)
    print("✅ Confluent Kafka Command Producer connected.")
except Exception as e:
    command_producer = None
    print(f"⚠️ Could not connect Confluent Kafka Command Producer: {e}")

def send_prediction_command(action, symbol):
    if not command_producer: return
    command = {"action": action, "symbol": symbol}
    try:
        command_producer.produce(PREDICTION_COMMAND_TOPIC, value=json.dumps(command).encode('utf-8'))
        command_producer.flush(1)
        print(f"Sent prediction command to '{PREDICTION_COMMAND_TOPIC}': {command}")
    except Exception as e:
        print(f"⚠️ Error sending prediction command: {e}")
        
def send_training_command(symbol):
    if not command_producer: return
    command = {"symbol": symbol}
    try:
        command_producer.produce(TRAINING_COMMAND_TOPIC, value=json.dumps(command).encode('utf-8'))
        command_producer.flush(1)
        print(f"Sent training command to '{TRAINING_COMMAND_TOPIC}': {command}")
    except Exception as e:
        print(f"⚠️ Error sending training command: {e}")

# ==========================================================
# 🧠 STOCK DATA & API ROUTES
# ==========================================================
def load_all_indian_stocks():
    if os.path.exists(STOCKS_CACHE_FILE) and time.time() - os.path.getmtime(STOCKS_CACHE_FILE) < CACHE_EXPIRY:
        with open(STOCKS_CACHE_FILE, "r") as f:
            return json.load(f)
    print("🔄 Fetching full Indian stock list...")
    stocks = {}
    try:
        nse_url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
        headers = {"User-Agent": "Mozilla/5.0"}
        nse_data = requests.get(nse_url, headers=headers, timeout=10).text.splitlines()
        for row in nse_data[1:]:
            parts = row.split(",")
            if len(parts) >= 2:
                symbol, name = parts[0].strip(), parts[1].strip().title()
                if symbol and name: stocks[symbol + ".NS"] = name + " (NSE)"
    except Exception as e: print(f"⚠️ NSE fetch failed: {e}")

    with open(STOCKS_CACHE_FILE, "w") as f: json.dump(stocks, f, indent=2)
    print(f"✅ Loaded {len(stocks)} total Indian stocks.")
    return stocks

@app.route("/search")
def search_stocks():
    query = request.args.get("query", "").strip().lower()
    if not query: return jsonify({"symbols": []})
    all_stocks = load_all_indian_stocks()
    matches = [{"symbol": sym, "name": name} for sym, name in all_stocks.items() if query in sym.lower() or query in name.lower()]
    return jsonify({"symbols": matches[:50]})

@app.route("/stock/<symbol>")
def get_stock(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d", interval="5m")
        if hist.empty: return jsonify({"error": "No recent intraday data available."}), 404
        info = stock.info
        intraday_data = [{"time": index.strftime("%H:%M"), "price": round(row["Close"], 2)} for index, row in hist.iterrows()]
        latest_price = intraday_data[-1]['price']
        previous_close = info.get("previousClose", 0)
        change = round(((latest_price - previous_close) / previous_close) * 100, 2) if previous_close != 0 else 0
        return jsonify({
            "symbol": symbol, "name": info.get("longName", symbol), "current": latest_price, "change": change,
            "summary": info.get("longBusinessSummary", "No company summary available."),
            "previousClose": previous_close, "dayHigh": info.get("dayHigh", 0), "dayLow": info.get("dayLow", 0),
            "marketCap": info.get("marketCap"), "sector": info.get("sector"),
            "updated": datetime.now().strftime("%H:%M:%S"), "intraday_trend": intraday_data
        })
    except Exception as e: return jsonify({"error": str(e)}), 500

@app.route("/stock_history/<symbol>")
def get_stock_history(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d", interval="5m")
        if hist.empty: return jsonify({"error": "No recent intraday data available."}), 404
        info = stock.info
        intraday_data = [{"time": index.strftime("%H:%M"), "price": round(row["Close"], 2)} for index, row in hist.iterrows()]
        latest_price = intraday_data[-1]['price']
        previous_close = info.get("previousClose", 0)
        change = round(((latest_price - previous_close) / previous_close) * 100, 2) if previous_close != 0 else 0
        return jsonify({
            "symbol": symbol, "name": info.get("longName", symbol), "current": latest_price, "change": change,
            "summary": info.get("longBusinessSummary", "No company summary available."),
            "previousClose": previous_close, "dayHigh": info.get("dayHigh", 0), "dayLow": info.get("dayLow", 0),
            "marketCap": info.get("marketCap"), "sector": info.get("sector"),
            "updated": hist.index[-1].strftime('%b %d, %Y') + ' (Closing)', "intraday_trend": intraday_data
        })
    except Exception as e: return jsonify({"error": str(e)}), 500

# ==========================================================
# 🔮 FAVORITES & COMMAND TRIGGERS
# ==========================================================
@app.route("/update_favorites", methods=["POST"])
def update_favorites():
    data = request.get_json()
    user_id, symbol, action = str(data.get("user_id", "1")), data.get("symbol"), data.get("action")
    if user_id not in user_favorites: user_favorites[user_id] = []
    
    if action == "add" and symbol not in user_favorites[user_id]:
        user_favorites[user_id].append(symbol)
        send_prediction_command("ADD", symbol)
        send_training_command(symbol)
    elif action == "remove" and symbol in user_favorites[user_id]:
        user_favorites[user_id].remove(symbol)
        send_prediction_command("REMOVE", symbol)
    
    save_favorites_to_file()
    return jsonify({"favorites": user_favorites.get(user_id, [])})

@app.route("/favorites/<user_id>")
def get_favorites(user_id):
    symbols = user_favorites.get(str(user_id), [])
    for sym in symbols:
        send_prediction_command("ADD", sym)
    
    results = []
    for sym in symbols:
        try:
            stock = yf.Ticker(sym)
            info = stock.info
            hist = stock.history(period="5d", interval="1d")
            if not hist.empty:
                latest, previous = hist.iloc[-1], hist.iloc[-2] if len(hist) > 1 else hist.iloc[-1]
                current = float(latest["Close"])
                change = round(((latest["Close"] - previous["Close"]) / previous["Close"]) * 100, 2) if previous["Close"] != 0 else 0
                results.append({"symbol": sym, "current": current, "change": change, "name": info.get("shortName", sym), "predictions": [round(p, 2) for p in hist["Close"].tolist()]})
        except Exception as e: print(f"⚠️ Error fetching favorite {sym}: {e}")
    return jsonify(results)

@app.route("/predict/start/<symbol>", methods=["POST"])
def start_prediction(symbol):
    send_prediction_command("ADD", symbol)
    return jsonify({"status": "ok"})

@app.route("/predict/stop/<symbol>", methods=["POST"])
def stop_prediction(symbol):
    user_id = '1'
    if symbol not in user_favorites.get(user_id, []):
        send_prediction_command("REMOVE", symbol)
    return jsonify({"status": "ok"})

@app.route("/prediction/daily/<symbol>")
def get_daily_prediction(symbol):
    if not os.path.exists(DAILY_PREDICTIONS_FILE): return jsonify({"outlook": "Not yet calculated."})
    try:
        with open(DAILY_PREDICTIONS_FILE, 'r') as f:
            predictions = json.load(f)
            return jsonify({"outlook": predictions.get(symbol, "Not available.")})
    except Exception as e: return jsonify({"error": str(e)}), 500
        
@app.route("/train/on_demand/<symbol>", methods=["POST"])
def trigger_on_demand_training(symbol):
    print(f"Relaying on-demand training request for {symbol} to training service...")
    send_training_command(symbol)
    return jsonify({"status": "ok", "message": "Training request accepted."}), 202

# ==========================================================
# 🔄 KAFKA STREAMING CONSUMERS
# ==========================================================
def kafka_consumer_generator(topics, group_id_prefix):
    consumer_config = { 'bootstrap.servers': KAFKA_BOOTSTRAP, 'group.id': f'{group_id_prefix}-{random.randint(0, 99999)}', 'auto.offset.reset': 'latest' }
    consumer = Consumer(consumer_config)
    consumer.subscribe(topics)
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF: print(f"Flask Consumer error: {msg.error()}")
                continue
            yield { "key": msg.key().decode('utf-8') if msg.key() else None, "value": msg.value().decode('utf-8') }
    finally:
        consumer.close()
        print(f"Flask consumer for {topics} closed.")

@app.route("/stream/<symbol>")
def stream_price(symbol):
    def price_filter():
        for msg in kafka_consumer_generator([KAFKA_PRICE_TOPIC], "price-stream"):
            if msg['key'] == symbol:
                yield f"data: {msg['value']}\n\n"
    return Response(price_filter(), content_type="text/event-stream")

@app.route("/stream/prediction/<symbol>")
def stream_prediction(symbol):
    def prediction_filter():
        for msg in kafka_consumer_generator([KAFKA_PREDICTION_TOPIC], "prediction-stream"):
            if msg['key'] == symbol:
                yield f"data: {msg['value']}\n\n"
    return Response(prediction_filter(), content_type="text/event-stream")

@app.route("/stream/all_prices")
def stream_all_prices():
    """
    This stream sends ALL price updates from the 'stocks' topic without filtering.
    It's designed to be used by the main dashboard.
    """
    def broadcast_all():
        for msg in kafka_consumer_generator([KAFKA_PRICE_TOPIC], "all-prices-stream"):
            yield f"data: {msg['value']}\n\n"
    return Response(broadcast_all(), content_type="text/event-stream")

# ==========================================================
# 🚀 RUN SERVER
# ==========================================================
if __name__ == "__main__":
    load_favorites_from_file()
    app.run(debug=True, threaded=True, port=5000)