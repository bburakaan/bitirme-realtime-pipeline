import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from db.connection import get_connection
from db.demo_seed import get_table_count, seed_olist_demo_data
from db.init_db import init_database
from producer.event_generator import generate_session_events


MODEL_PATH = Path("ml/saved_model/buyer_model.pkl")
SLEEP_SEC = int(os.getenv("ONLINE_DEMO_SLEEP_SEC", "5"))
MIN_SESSIONS = int(os.getenv("ONLINE_DEMO_MIN_SESSIONS", "100"))

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


def parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now()

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return datetime.now()


def load_model():
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return None


def build_session_row(events: list[dict[str, Any]]) -> dict[str, Any]:
    first_event = events[0]
    timestamps = [parse_timestamp(event.get("timestamp")) for event in events]
    total = len(events)
    price_sum = sum(float(event.get("price", 0) or 0) for event in events)

    def count_event(event_type: str) -> int:
        return sum(1 for event in events if event.get("event_type") == event_type)

    click_count = count_event("click")
    page_view_count = count_event("page_view")
    search_count = count_event("search")
    add_to_cart_count = count_event("add_to_cart")
    purchase_count = count_event("purchase")
    duration = (max(timestamps) - min(timestamps)).total_seconds()

    return {
        "session_id": first_event.get("session_id"),
        "user_id": first_event.get("user_id"),
        "profile": first_event.get("profile"),
        "total_event_count": total,
        "click_count": click_count,
        "page_view_count": page_view_count,
        "search_count": search_count,
        "add_to_cart_count": add_to_cart_count,
        "purchase_count": purchase_count,
        "session_duration_sec": max(duration, 0.0),
        "avg_price": price_sum / total if total else 0.0,
        "click_rate": click_count / total if total else 0.0,
        "cart_rate": add_to_cart_count / total if total else 0.0,
        "label": int(purchase_count > 0),
        "finalize_reason": "online_demo",
        "processed_at": datetime.now().isoformat(),
    }


def predict_row(row: dict[str, Any], model) -> tuple[int | None, float | None]:
    if model is None:
        return row["label"], None

    feature_df = pd.DataFrame([{column: row[column] for column in FEATURE_COLUMNS}])
    predicted_label = int(model.predict(feature_df)[0])
    probability = None

    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(feature_df)[0][1])

    return predicted_label, probability


def save_raw_event(cur, event: dict[str, Any]) -> None:
    cur.execute(
        """
        INSERT INTO raw_events (
            event_id, user_id, session_id, event_type, product_id,
            category, price, event_timestamp, device_type, source,
            profile, raw_json
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb)
        """,
        (
            event.get("event_id"),
            str(event.get("user_id")) if event.get("user_id") is not None else None,
            event.get("session_id"),
            event.get("event_type"),
            str(event.get("product_id")) if event.get("product_id") is not None else None,
            event.get("category"),
            float(event.get("price", 0) or 0),
            event.get("timestamp"),
            event.get("device_type"),
            event.get("source"),
            event.get("profile"),
            json.dumps(event, ensure_ascii=False),
        ),
    )


def save_session_row(cur, row: dict[str, Any]) -> None:
    cur.execute(
        """
        INSERT INTO session_features (
            session_id, user_id, profile, total_event_count, click_count,
            page_view_count, search_count, add_to_cart_count, purchase_count,
            session_duration_sec, avg_price, click_rate, cart_rate,
            actual_label, finalize_reason, processed_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            row.get("session_id"),
            str(row.get("user_id")) if row.get("user_id") is not None else None,
            row.get("profile"),
            row.get("total_event_count"),
            row.get("click_count"),
            row.get("page_view_count"),
            row.get("search_count"),
            row.get("add_to_cart_count"),
            row.get("purchase_count"),
            row.get("session_duration_sec"),
            row.get("avg_price"),
            row.get("click_rate"),
            row.get("cart_rate"),
            row.get("label"),
            row.get("finalize_reason"),
            row.get("processed_at"),
        ),
    )


def save_prediction_row(cur, row: dict[str, Any]) -> None:
    cur.execute(
        """
        INSERT INTO predictions (
            session_id, user_id, actual_label, predicted_label,
            probability, processed_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            row.get("session_id"),
            str(row.get("user_id")) if row.get("user_id") is not None else None,
            row.get("label"),
            row.get("predicted_label"),
            row.get("probability"),
            row.get("processed_at"),
        ),
    )


def generate_once(model=None) -> dict[str, Any]:
    events = generate_session_events()
    row = build_session_row(events)
    predicted_label, probability = predict_row(row, model)
    row["predicted_label"] = predicted_label
    row["probability"] = probability

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            for event in events:
                save_raw_event(cur, event)
            save_session_row(cur, row)
            save_prediction_row(cur, row)
        conn.commit()
    finally:
        conn.close()

    return row


def run_forever() -> None:
    init_database()
    seed_olist_demo_data()
    model = load_model()
    current_sessions = get_table_count("session_features")

    while current_sessions < MIN_SESSIONS:
        row = generate_once(model)
        current_sessions += 1
        print(
            "Initial online demo session seeded | "
            f"session_id={row['session_id']} | "
            f"count={current_sessions}/{MIN_SESSIONS}"
        )

    while True:
        try:
            row = generate_once(model)
            print(
                "Online demo session generated | "
                f"session_id={row['session_id']} | "
                f"events={row['total_event_count']} | "
                f"label={row['label']}"
            )
        except Exception as exc:
            print(f"Online demo worker error: {exc}")

        time.sleep(SLEEP_SEC)


def main() -> None:
    run_forever()


if __name__ == "__main__":
    main()
