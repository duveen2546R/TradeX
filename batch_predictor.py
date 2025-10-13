import yfinance as yf
from pyspark.sql import SparkSession
from pyspark.ml.classification import GBTClassificationModel
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler
import os
import json

# --- Configuration ---
STOCKS_TO_PREDICT = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
MODEL_PATH = "models/direction_classifier_model"
OUTPUT_FILE = "daily_predictions.json"

# ✨ CORRECTED column cleaning function
def clean_col_names(df):
    """Simplifies column names from yfinance, handles tuples."""
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

# --- Main Prediction Logic ---
def run_predictions(spark):
    print("--- Running Batch Predictions for Next Trading Day ---")
    all_predictions = {}
    
    for symbol in STOCKS_TO_PREDICT:
        try:
            # 1. Load the pre-trained model
            model_path_full = os.path.join(MODEL_PATH, symbol)
            # Verify that the model path actually exists before trying to load it
            if not os.path.exists(model_path_full):
                print(f"⚠️ Model for {symbol} not found at {model_path_full}, skipping.")
                continue
                
            model = GBTClassificationModel.load(model_path_full)
            
            # 2. Fetch the latest available data
            data = yf.download(symbol, period="20d", interval="1d", auto_adjust=True, progress=False)
            if data.empty:
                print(f"No yfinance data for {symbol}, skipping.")
                continue

            data = clean_col_names(data)
            df = spark.createDataFrame(data.reset_index())

            # 3. Feature Engineering (must be IDENTICAL to training)
            window_spec = Window.orderBy("Date")
            df = df.withColumn("return_1d", (F.col("Close") / F.lag("Close", 1).over(window_spec)) - 1)
            df = df.withColumn("return_5d", (F.col("Close") / F.lag("Close", 5).over(window_spec)) - 1)
            
            # Get the most recent row that is not null to make a prediction on
            latest_data = df.dropna(subset=["Open", "High", "Low", "Close", "Volume", "return_1d", "return_5d"]).orderBy(F.desc("Date")).limit(1)
            
            # 4. Make Prediction
            assembler = VectorAssembler(inputCols=["Open", "High", "Low", "Close", "Volume", "return_1d", "return_5d"], outputCol="features")
            latest_assembled = assembler.transform(latest_data)
            
            prediction_result = model.transform(latest_assembled)
            
            # The 'prediction' column will contain 0.0 or 1.0
            outlook = prediction_result.select("prediction").first()['prediction']
            
            outlook_text = "Increase 📈" if outlook == 1.0 else "Decrease 📉"
            all_predictions[symbol] = outlook_text
            
            print(f"✅ Prediction for {symbol}: {outlook_text}")

        except Exception as e:
            print(f"⚠️ Could not generate prediction for {symbol}: {e}")

    # 5. Save all predictions to a single file
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_predictions, f, indent=4)
    print(f"\n--- All daily predictions saved to {OUTPUT_FILE} ---")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("BatchPredictor").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    run_predictions(spark)
    spark.stop()