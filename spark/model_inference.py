import os
from pathlib import Path

import joblib


INPUT_PATH = Path(os.getenv("SESSION_FEATURE_INPUT", "data/session_features_from_db.csv"))
MODEL_PATH = Path(os.getenv("SESSION_MODEL_PATH", "ml/saved_model/buyer_model.pkl"))
OUTPUT_PATH = Path(os.getenv("SPARK_PREDICTION_OUTPUT", "results/metrics/spark_session_predictions.csv"))

FEATURE_COLUMNS = [
    "total_event_count",
    "click_count",
    "page_view_count",
    "search_count",
    "add_to_cart_count",
    "session_duration_sec",
    "avg_price",
    "click_rate",
    "cart_rate",
]


def main() -> None:
    try:
        from pyspark.sql import SparkSession
    except ImportError as exc:
        raise SystemExit(
            "PySpark is required for this optional script. Run it with spark-submit "
            "or install pyspark in the active environment."
        ) from exc

    if not INPUT_PATH.exists():
        raise SystemExit(f"Input file not found: {INPUT_PATH}")

    if not MODEL_PATH.exists():
        raise SystemExit(f"Model file not found: {MODEL_PATH}")

    spark = SparkSession.builder.appName("RealtimeEcommerceBatchInference").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")

    spark_df = spark.read.csv(str(INPUT_PATH), header=True, inferSchema=True)
    missing_columns = [column for column in FEATURE_COLUMNS if column not in spark_df.columns]
    if missing_columns:
        raise SystemExit(f"Missing feature columns: {', '.join(missing_columns)}")

    pdf = spark_df.toPandas()
    model = joblib.load(MODEL_PATH)

    features = pdf[FEATURE_COLUMNS]
    pdf["predicted_label"] = model.predict(features).astype(int)

    if hasattr(model, "predict_proba"):
        pdf["probability"] = model.predict_proba(features)[:, 1]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pdf.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved {len(pdf)} predictions to {OUTPUT_PATH}")

    spark.stop()


if __name__ == "__main__":
    main()
