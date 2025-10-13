import yfinance as yf
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import GBTClassifier
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os

# --- Configuration ---
STOCKS_TO_TRAIN = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
MODEL_SAVE_PATH = "../models/direction_classifier_model"

# ✨ CORRECTED column cleaning function
def clean_col_names(df):
    """Simplifies column names from yfinance, handles tuples."""
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

# --- Main Training Logic ---
def train_model(spark, symbol):
    print(f"--- Training Classification Model for {symbol} ---")
    
    # 1. Fetch Daily Data
    data = yf.download(symbol, period="5y", interval="1d", auto_adjust=True)
    if data.empty:
        print(f"No data for {symbol}, skipping.")
        return
        
    data = clean_col_names(data)
    df = spark.createDataFrame(data.reset_index())
    
    # 2. Feature Engineering
    window_spec = Window.orderBy("Date")
    
    # Create features like returns from previous days
    df = df.withColumn("return_1d", (F.col("Close") / F.lag("Close", 1).over(window_spec)) - 1)
    df = df.withColumn("return_5d", (F.col("Close") / F.lag("Close", 5).over(window_spec)) - 1)
    
    # 3. Create the Label
    df = df.withColumn("price_change_next_day", F.lead("Close", 1).over(window_spec) - F.col("Close"))
    df = df.withColumn("label", F.when(F.col("price_change_next_day") > 0, 1.0).otherwise(0.0))
    
    df = df.dropna()
    
    # 4. Assemble Features
    assembler = VectorAssembler(inputCols=["Open", "High", "Low", "Close", "Volume", "return_1d", "return_5d"], outputCol="features")
    df_assembled = assembler.transform(df)
    
    # 5. Train the Model
    gbt = GBTClassifier(featuresCol="features", labelCol="label", seed=42)
    model = gbt.fit(df_assembled)
    
    # 6. Save the Model
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_save_dir = os.path.join(script_dir, MODEL_SAVE_PATH)
    os.makedirs(model_save_dir, exist_ok=True)
    
    model_path_full = os.path.join(model_save_dir, symbol)
    model.write().overwrite().save(model_path_full)
    print(f"✅ Classification model for {symbol} saved to {model_path_full}")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("StockClassifierTraining").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    for stock_symbol in STOCKS_TO_TRAIN:
        train_model(spark, stock_symbol)
        
    spark.stop()