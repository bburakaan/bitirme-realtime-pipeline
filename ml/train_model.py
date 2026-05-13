import os
from pathlib import Path

import joblib
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.model_selection import train_test_split

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "realtime_ecommerce")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

MODEL_PATH = Path("ml/saved_model/buyer_model.pkl")

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

LABEL_COLUMN = "actual_label"


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def load_training_data() -> pd.DataFrame:
    query = """
        SELECT
            total_event_count,
            click_count,
            page_view_count,
            search_count,
            add_to_cart_count,
            session_duration_sec,
            avg_price,
            click_rate,
            cart_rate,
            actual_label
        FROM session_features
        WHERE actual_label IS NOT NULL
    """
    conn = get_connection()
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()
    return df


def main():
    print("Loading training data from PostgreSQL...")
    df = load_training_data()

    if df.empty:
        print("No training data found in session_features table.")
        return

    if len(df) < 10:
        print(f"Not enough rows to train a useful model. Current row count: {len(df)}")
        return

    print(f"Training rows found: {len(df)}")

    X = df[FEATURE_COLUMNS].copy()
    y = df[LABEL_COLUMN].astype(int).copy()

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y if y.nunique() > 1 else None,
    )

    model = LogisticRegression(max_iter=2000)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print("\nModel evaluation results:")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-Score : {f1:.4f}")
    print(f"\nModel saved to {MODEL_PATH}")


if __name__ == "__main__":
    main()