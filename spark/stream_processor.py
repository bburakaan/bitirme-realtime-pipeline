import os


KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user-events")
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
CHECKPOINT_DIR = os.getenv("SPARK_CHECKPOINT_DIR", "results/spark/checkpoints/event_counts")


def main() -> None:
    try:
        from pyspark.sql import SparkSession
        from pyspark.sql.functions import col, count, from_json, to_timestamp, window
        from pyspark.sql.types import DoubleType, IntegerType, StringType, StructField, StructType
    except ImportError as exc:
        raise SystemExit(
            "PySpark is required for this optional script. Run it with spark-submit "
            "or install pyspark in the active environment."
        ) from exc

    spark = SparkSession.builder.appName("RealtimeEcommerceKafkaStream").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    schema = StructType(
        [
            StructField("event_id", StringType()),
            StructField("user_id", IntegerType()),
            StructField("session_id", StringType()),
            StructField("event_type", StringType()),
            StructField("product_id", IntegerType()),
            StructField("category", StringType()),
            StructField("price", DoubleType()),
            StructField("timestamp", StringType()),
            StructField("device_type", StringType()),
            StructField("source", StringType()),
            StructField("profile", StringType()),
        ]
    )

    kafka_df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_SERVER)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "latest")
        .load()
    )

    events_df = (
        kafka_df.selectExpr("CAST(value AS STRING) AS json_value")
        .select(from_json(col("json_value"), schema).alias("event"))
        .select("event.*")
        .withColumn("event_timestamp", to_timestamp("timestamp"))
    )

    summary_df = (
        events_df.withWatermark("event_timestamp", "5 minutes")
        .groupBy(
            window(col("event_timestamp"), "1 minute"),
            col("event_type"),
            col("profile"),
        )
        .agg(count("*").alias("event_count"))
        .orderBy(col("window").desc(), col("event_count").desc())
    )

    query = (
        summary_df.writeStream.outputMode("complete")
        .format("console")
        .option("truncate", "false")
        .option("checkpointLocation", CHECKPOINT_DIR)
        .start()
    )

    query.awaitTermination()


if __name__ == "__main__":
    main()
