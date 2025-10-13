import time
import json
import threading
from confluent_kafka import Producer, Consumer, KafkaError
import yfinance as yf
from datetime import datetime, timezone
import os

# Import PySpark components
from pyspark.sql import SparkSession
from pyspark.ml.regression import GBTRegressionModel
from pyspark.ml.feature import VectorAssembler

# --- 1. Configuration ---
KAFKA_BOOTSTRAP = "localhost:9092"
PRICE_TOPIC = "stocks"
PREDICTION_TOPIC = "stock_predictions"
COMMAND_TOPIC = "prediction_requests"
MODEL_BASE_PATH = "models/price_regressor_model"
POLL_INTERVAL = 5  # seconds

# --- 2. In-Memory State Management ---
stocks_to_predict = set()
loaded_models = {}
state_lock = threading.Lock() # To safely modify the set from multiple threads

# --- 3. Initialize Spark and Kafka ---
print("Initializing Spark Session...")
spark = SparkSession.builder.appName("LiveEnginePredictor").getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
print("✅ Spark Session Initialized.")

producer_config = {'bootstrap.servers': KAFKA_BOOTSTRAP}
producer = Producer(producer_config)
print("✅ Confluent Kafka Producer connected.")


# --- 4. Core Functions ---

def fetch_tick(symbol):
    """Fetches the latest available stock price."""
    try:
        # Fetching a very short period is efficient for the latest price
        data = yf.Ticker(symbol).history(period="1d", interval="1m")
        if data.empty: return None
        
        last_price = data["Close"].iloc[-1]
        previous_price = data["Close"].iloc[-2] if len(data) > 1 else last_price
        change_pct = ((last_price - previous_price) / previous_price) * 100 if previous_price != 0 else 0.0
        
        return {
            "symbol": symbol,
            "price": round(float(last_price), 2),
            "change_pct": round(float(change_pct), 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        print(f"❌ Fetch error for {symbol}: {e}")
        return None

def generate_prediction(symbol, tick_data):
    """Uses a pre-trained MLlib model to predict the next price."""
    with state_lock:
        # Step A: Load the model if it's not already cached in memory
        if symbol not in loaded_models:
            model_path = os.path.join(MODEL_BASE_PATH, symbol)
            if os.path.exists(model_path):
                print(f"🧠 Loading ML model for {symbol}...")
                loaded_models[symbol] = GBTRegressionModel.load(model_path)
            else:
                print(f"⚠️ Model for {symbol} not found. Cannot generate prediction.")
                loaded_models[symbol] = None # Cache "None" to prevent re-trying
                return None
        
        model = loaded_models.get(symbol)
        if model is None:
            return None

    # Step B: Create a Spark DataFrame for the single new data point
    tick_df = spark.createDataFrame([
        # These features MUST match the features used in your training script
        (tick_data['price'], tick_data['price'], tick_data['price'], tick_data['change_pct'] * 1000)
    ], ["Close", "ma5", "ma20", "Volume"])
    
    # Step C: Assemble the features into a vector
    assembler = VectorAssembler(inputCols=["Close", "ma5", "ma20", "Volume"], outputCol="features")
    tick_assembled = assembler.transform(tick_df)

    # Step D: Apply the model to predict the price
    prediction_result = model.transform(tick_assembled).first()
    return round(prediction_result.prediction, 2)


def command_listener():
    """This function runs in a background thread, listening for commands from the web app."""
    consumer_config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': 'live_engine_command_group_1', # Must have a group.id
        'auto.offset.reset': 'latest'
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe([COMMAND_TOPIC])
    print("🚀 Command listener started, waiting for requests...")

    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error():
            if msg.error().code() != KafkaError._PARTITION_EOF:
                print(f"Consumer error: {msg.error()}")
            continue
        
        try:
            command = json.loads(msg.value().decode('utf-8'))
            symbol = command.get("symbol")
            action = command.get("action")
            
            with state_lock:
                if action == "ADD" and symbol:
                    stocks_to_predict.add(symbol)
                    print(f"📬 Received ADD command for {symbol}. Current prediction set: {list(stocks_to_predict)}")
                elif action == "REMOVE" and symbol:
                    stocks_to_predict.discard(symbol)
                    print(f"📪 Received REMOVE command for {symbol}. Current prediction set: {list(stocks_to_predict)}")
        except json.JSONDecodeError:
            print("Received malformed command.")


if __name__ == "__main__":
    # --- 5. Start the System ---
    
    # Start the command listener in a separate, non-blocking thread
    listener_thread = threading.Thread(target=command_listener, daemon=True)
    listener_thread.start()

    print("🚀 Starting main producer loop...")
    
    # This is a base list of stocks to always get price data for.
    # It can be empty if you only want to fetch data on demand.
    base_symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
    
    try:
        while True:
            with state_lock:
                # Make a copy to avoid changing the set while iterating
                current_prediction_list = list(stocks_to_predict)

            # Combine the base list and the on-demand list for efficient fetching
            symbols_to_fetch = set(base_symbols + current_prediction_list)

            for s in symbols_to_fetch:
                tick = fetch_tick(s)
                if not tick:
                    continue

                # 5a. Always publish the live price to the 'stocks' topic
                producer.produce(PRICE_TOPIC, key=s.encode('utf-8'), value=json.dumps(tick).encode('utf-8'))
                print(f"Published PRICE for {s}: {tick['price']}")

                # 5b. ONLY if this stock has been requested, generate and publish a prediction
                if s in current_prediction_list:
                    prediction = generate_prediction(s, tick)
                    if prediction is not None:
                        prediction_payload = {"symbol": s, "prediction": prediction}
                        producer.produce(PREDICTION_TOPIC, key=s.encode('utf-8'), value=json.dumps(prediction_payload).encode('utf-8'))
                        print(f"🤖 Published PREDICTION for {s}: {prediction}")
            
            producer.flush()
            time.sleep(POLL_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping engine...")
    finally:
        producer.flush()
        spark.stop()
        print("Engine and Spark session stopped.")