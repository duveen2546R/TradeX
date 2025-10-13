import yfinance as yf
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os
import sys

# This script is meant to be called from the command line, e.g.:
# python train_on_demand.py RELIANCE.NS

MODEL_SAVE_PATH = "../models/price_regressor_model"

def clean_col_names(df):
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

def train_single_model(symbol):
    """Trains a model for one symbol, but only if it doesn't already exist."""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_save_dir = os.path.join(script_dir, MODEL_SAVE_PATH)
    model_path_full = os.path.join(model_save_dir, symbol)

    # --- CRITICAL CHECK: Skip if model already exists ---
    if os.path.exists(model_path_full):
        print(f"✅ Model for {symbol} already exists. Skipping training.")
        return

    print(f"⏳ Model for {symbol} not found. Starting on-demand training...")

    # Initialize a local Spark Session just for this job
    spark = SparkSession.builder.appName(f"OnDemandTrainer_{symbol}").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    try:
        data = yf.download(symbol, period="15d", interval="5m", auto_adjust=True, progress=False)
        if data.empty or len(data) < 50:
            print(f"Skipping {symbol}: Not enough data.")
            spark.stop()
            return

        data = clean_col_names(data)
        df = spark.createDataFrame(data.reset_index())

        # (Feature Engineering is identical to the previous training script)
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

        os.makedirs(model_save_dir, exist_ok=True)
        model.write().overwrite().save(model_path_full)
        
        print(f"✅ On-demand model for {symbol} saved successfully.")

    except Exception as e:
        print(f"❌ Error during on-demand training for {symbol}: {e}")
    finally:
        # Always stop the Spark session to release resources
        spark.stop()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python train_on_demand.py <STOCK_SYMBOL>")
        sys.exit(1)
        
    stock_to_train = sys.argv[1]
    train_single_model(stock_to_train)