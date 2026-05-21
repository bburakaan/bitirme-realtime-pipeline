import os

import pandas as pd
from dotenv import load_dotenv

from db.connection import get_connection

load_dotenv()

OUTPUT_PATH = "data/session_features_from_db.csv"


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
