import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, FloatType, TimestampType
from pyspark.ml.regression import GBTRegressionModel
from pyspark.ml.feature import VectorAssembler

# --- Configuration ---
KAFKA_BOOTSTRAP = "localhost:9092"
KAFKA_SOURCE_TOPIC = "stocks"
KAFKA_SINK_TOPIC = "stock_predictions"
MODEL_BASE_PATH = "models/price_regressor_model"

# --- Spark Streaming Application ---
spark = SparkSession.builder.appName("StockStreamPredictor").getOrCreate()
spark.sparkContext.setLogLevel("WARN")

# Define schema for incoming Kafka messages
schema = StructType([
    StructField("symbol", StringType(), True),
    StructField("price", FloatType(), True),
    StructField("change_pct", FloatType(), True),
    StructField("timestamp", TimestampType(), True),
])

# Read from the raw stocks Kafka topic
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", KAFKA_SOURCE_TOPIC) \
    .load()

# Deserialize the JSON message
df = df.selectExpr("CAST(value AS STRING) as json") \
    .withColumn("data", from_json(col("json"), schema)) \
    .select("data.*") # <-- THE FIX IS HERE! We only select the columns from the JSON payload.

# Simplified feature engineering
df = df.withColumnRenamed("price", "Close") \
       .withColumn("ma5", col("Close")) \
       .withColumn("ma20", col("Close")) \
       .withColumn("Volume", col("change_pct") * 1000)

# Assemble features
assembler = VectorAssembler(inputCols=["Close", "ma5", "ma20", "Volume"], outputCol="features")
df_assembled = assembler.transform(df)

# Load a single model for demonstration
print(f"Loading model for RELIANCE.NS...")
model = GBTRegressionModel.load(os.path.join(MODEL_BASE_PATH, "RELIANCE.NS"))

# Make predictions
predictions = model.transform(df_assembled)

# Select prediction and format for Kafka sink
output = predictions.select(
    col("symbol").alias("key"), # The `symbol` column is now unambiguous
    F.to_json(F.struct(col("symbol"), col("prediction"))).alias("value")
)

# Write predictions to the new Kafka topic
query = output.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("topic", KAFKA_SINK_TOPIC) \
    .option("checkpointLocation", "/tmp/spark_checkpoint") \
    .start()

print("🚀 Spark Streaming Predictor is running. Waiting for Kafka messages...")
query.awaitTermination()