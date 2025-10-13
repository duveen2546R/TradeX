from confluent_kafka import Consumer, KafkaError
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import yfinance as yf
import json
import os
import sys

# --- Configuration ---
KAFKA_BOOTSTRAP = "localhost:9092"
COMMAND_TOPIC = "training_requests"
MODEL_SAVE_PATH = "models/price_regressor_model"

def clean_col_names(df):
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

def train_single_model(symbol):
    """The core training logic for one symbol."""
    
    model_path_full = os.path.join(MODEL_SAVE_PATH, symbol)

    if os.path.exists(model_path_full):
        print(f"✅ Model for {symbol} already exists. Skipping.")
        return

    print(f"⏳ Training request received for new stock: {symbol}. Starting job...")
    
    # Each job gets its own Spark Session for isolation
    spark = SparkSession.builder.appName(f"TrainingJob_{symbol}").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    
    try:
        data = yf.download(symbol, period="15d", interval="5m", auto_adjust=True, progress=False)
        if data.empty or len(data) < 50:
            print(f"Skipping {symbol}: Not enough data.")
            spark.stop()
            return
            
        data = clean_col_names(data)
        df = spark.createDataFrame(data.reset_index())
        
        # (Feature Engineering...)
        time_window_spec = Window.orderBy("Datetime")
        df = df.withColumn("label", F.lead("Close", 1).over(time_window_spec))
        ma5_spec = time_window_spec.rowsBetween(-4, 0)
        ma20_spec = time_window_spec.rowsBetween(-19, 0)
        df = df.withColumn("ma5", F.avg("Close").over(ma5_spec))
        df = df.withColumn("ma20", F.avg("Close").over(ma20_spec))
        df = df.dropna()

        assembler = VectorAssembler(inputCols=["Close", "ma5", "ma20", "Volume"], outputCol="features")
        df_assembled = assembler.transform(df)

        gbt = GBTRegressor(featuresCol="features", labelCol="label", seed=42)
        model = gbt.fit(df_assembled)

        os.makedirs(os.path.dirname(model_path_full), exist_ok=True)
        model.write().overwrite().save(model_path_full)
        
        print(f"✅🧠 Model for {symbol} trained and saved successfully.")
    except Exception as e:
        print(f"❌ Error during training for {symbol}: {e}")
    finally:
        spark.stop() # CRITICAL: Stop the Spark session to release memory and CPU


def start_training_listener():
    """Continuously listens to the training_requests topic."""
    consumer_config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP,
        'group.id': 'training-service-group', # A stable group.id
        'auto.offset.reset': 'earliest'
    }
    consumer = Consumer(consumer_config)
    consumer.subscribe([COMMAND_TOPIC])
    print("🚀 Training Service is running, listening for new stock requests...")

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None: continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"Consumer error: {msg.error()}")
                continue
            
            try:
                command = json.loads(msg.value().decode('utf-8'))
                symbol_to_train = command.get("symbol")
                if symbol_to_train:
                    # Execute the training logic for the received symbol
                    train_single_model(symbol_to_train)
            except json.JSONDecodeError:
                print("Received a malformed message.")
            except Exception as e:
                print(f"An unexpected error occurred during job processing: {e}")
                
    except KeyboardInterrupt:
        print("\nStopping Training Service...")
    finally:
        consumer.close()

if __name__ == "__main__":
    start_training_listener()