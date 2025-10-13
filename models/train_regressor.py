import yfinance as yf
from pyspark.sql import SparkSession
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import GBTRegressor
from pyspark.sql import functions as F
from pyspark.sql.window import Window
import os

# --- Configuration ---
STOCKS_TO_TRAIN = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]
MODEL_SAVE_PATH = "../models/price_regressor_model"

def clean_col_names(df):
    df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
    return df

# --- Main Training Logic ---
def train_model(spark, symbol):
    print(f"--- Training Regression Model for {symbol} ---")
    
    data = yf.download(symbol, period="6d", interval="5m", auto_adjust=True)
    if data.empty:
        print(f"No data for {symbol}, skipping.")
        return
        
    data = clean_col_names(data)
    df = spark.createDataFrame(data.reset_index())
    
    time_window_spec = Window.orderBy("Datetime")
    df = df.withColumn("label", F.lead("Close", 1).over(time_window_spec))

    ma5_spec = time_window_spec.rowsBetween(-4, 0)
    ma20_spec = time_window_spec.rowsBetween(-19, 0)
    
    df = df.withColumn("ma5", F.avg("Close").over(ma5_spec))
    # THE FIX IS HERE: Corrected "withC-olumn" to "withColumn"
    df = df.withColumn("ma20", F.avg("Close").over(ma20_spec))
    
    df = df.dropna()
    
    assembler = VectorAssembler(inputCols=["Close", "ma5", "ma20", "Volume"], outputCol="features")
    df_assembled = assembler.transform(df)
    
    gbt = GBTRegressor(featuresCol="features", labelCol="label", seed=42)
    model = gbt.fit(df_assembled)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_save_dir = os.path.join(script_dir, MODEL_SAVE_PATH)
    os.makedirs(model_save_dir, exist_ok=True)
    
    model_path_full = os.path.join(model_save_dir, symbol)
    model.write().overwrite().save(model_path_full)
    print(f"✅ Model for {symbol} saved to {model_path_full}")

if __name__ == "__main__":
    spark = SparkSession.builder.appName("StockRegressorTraining").getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")

    for stock_symbol in STOCKS_TO_TRAIN:
        train_model(spark, stock_symbol)
        
    spark.stop()