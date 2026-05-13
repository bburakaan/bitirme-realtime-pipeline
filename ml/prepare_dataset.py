import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "realtime_ecommerce")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

OUTPUT_PATH = "data/session_features_from_db.csv"


def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def main():
    query = """
        SELECT
            session_id,
            user_id,
            profile,
            total_event_count,
            click_count,
            page_view_count,
            search_count,
            add_to_cart_count,
            purchase_count,
            session_duration_sec,
            avg_price,
            click_rate,
            cart_rate,
            actual_label,
            finalize_reason,
            processed_at
        FROM session_features
        ORDER BY id
    """

    conn = get_connection()
    try:
        df = pd.read_sql(query, conn)
    finally:
        conn.close()

    os.makedirs("data", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Exported {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()