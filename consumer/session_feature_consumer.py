import psycopg2
import json
import os
import time
from datetime import datetime
from typing import Any

import joblib
import pandas as pd
from dotenv import load_dotenv
from kafka import KafkaConsumer

load_dotenv()


KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user-events")
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "user-events-feature-consumer")
SESSION_IDLE_TIMEOUT_SEC = int(os.getenv("SESSION_IDLE_TIMEOUT_SEC", "3"))

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "realtime_ecommerce")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

MODEL_PATH = "ml/saved_model/buyer_model.pkl"
RAW_LOG_PATH = "results/logs/kafka_consumed_events.jsonl"
PREDICTION_CSV = "results/metrics/kafka_session_predictions.csv"

FEATURE_COLUMNS = [
    "total_event_count",
    "click_count",
    "page_view_count",
    "search_count",
    "add_to_cart_count",
    "session_duration_sec",
    "avg_price",
    "click_rate",
    "cart_rate"
]

active_sessions: dict[str, dict[str, Any]] = {}
model = None
db_conn = None

def ensure_dirs() -> None:
    os.makedirs("results/logs", exist_ok=True)
    os.makedirs("results/metrics", exist_ok=True)

def connect_db():
    global db_conn
    db_conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    db_conn.autocommit = True
    print(f"Connected to PostgreSQL: {DB_NAME}@{DB_HOST}:{DB_PORT}")

def load_model() -> None:
    global model
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"Model loaded from: {MODEL_PATH}")
    else:
        model = None
        print("Model file not found. Features will still be produced, but prediction will be skipped.")


def parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now()

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return datetime.now()


def append_raw_event(event: dict[str, Any]) -> None:
    with open(RAW_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

def save_raw_event_to_db(event: dict[str, Any]) -> None:
    if db_conn is None:
        return

    with db_conn.cursor() as cur:
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
                json.dumps(event, ensure_ascii=False)
            )
        )

def create_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_SERVER,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )


def initialize_session(event: dict[str, Any]) -> dict[str, Any]:
    ts = parse_timestamp(event.get("timestamp"))
    price = float(event.get("price", 0) or 0)

    return {
        "session_id": event.get("session_id"),
        "user_id": event.get("user_id"),
        "profile": event.get("profile"),
        "total_event_count": 0,
        "click_count": 0,
        "page_view_count": 0,
        "search_count": 0,
        "add_to_cart_count": 0,
        "purchase_count": 0,
        "price_sum": 0.0,
        "first_event_ts": ts,
        "last_event_ts": ts,
        "wall_last_seen": time.time(),
        "last_price": price
    }


def update_session(state: dict[str, Any], event: dict[str, Any]) -> None:
    event_type = event.get("event_type", "")
    ts = parse_timestamp(event.get("timestamp"))
    price = float(event.get("price", 0) or 0)

    state["total_event_count"] += 1
    state["price_sum"] += price
    state["last_price"] = price

    if event_type == "click":
        state["click_count"] += 1
    elif event_type == "page_view":
        state["page_view_count"] += 1
    elif event_type == "search":
        state["search_count"] += 1
    elif event_type == "add_to_cart":
        state["add_to_cart_count"] += 1
    elif event_type == "purchase":
        state["purchase_count"] += 1

    if ts < state["first_event_ts"]:
        state["first_event_ts"] = ts
    if ts > state["last_event_ts"]:
        state["last_event_ts"] = ts

    state["wall_last_seen"] = time.time()


def build_feature_row(state: dict[str, Any]) -> dict[str, Any]:
    total = state["total_event_count"]
    duration = (state["last_event_ts"] - state["first_event_ts"]).total_seconds()
    if duration < 0:
        duration = 0.0

    avg_price = state["price_sum"] / total if total > 0 else 0.0
    click_rate = state["click_count"] / total if total > 0 else 0.0
    cart_rate = state["add_to_cart_count"] / total if total > 0 else 0.0

    row = {
        "session_id": state["session_id"],
        "user_id": state["user_id"],
        "profile": state["profile"],
        "total_event_count": total,
        "click_count": state["click_count"],
        "page_view_count": state["page_view_count"],
        "search_count": state["search_count"],
        "add_to_cart_count": state["add_to_cart_count"],
        "purchase_count": state["purchase_count"],
        "session_duration_sec": duration,
        "avg_price": avg_price,
        "click_rate": click_rate,
        "cart_rate": cart_rate,
        "label": int(state["purchase_count"] > 0),
        "processed_at": datetime.now().isoformat()
    }
    return row


def predict_feature_row(row: dict[str, Any]) -> tuple[Any, Any]:
    if model is None:
        return None, None

    feature_df = pd.DataFrame([{col: row[col] for col in FEATURE_COLUMNS}])

    predicted_label = int(model.predict(feature_df)[0])

    probability = None
    if hasattr(model, "predict_proba"):
        probability = float(model.predict_proba(feature_df)[0][1])

    return predicted_label, probability


def save_prediction_row(row: dict[str, Any]) -> None:
    df = pd.DataFrame([row])
    file_exists = os.path.exists(PREDICTION_CSV)
    df.to_csv(PREDICTION_CSV, mode="a", header=not file_exists, index=False)

def save_session_feature_to_db(row: dict[str, Any]) -> None:
    if db_conn is None:
        return

    with db_conn.cursor() as cur:
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
            )
        )


def save_prediction_to_db(row: dict[str, Any]) -> None:
    if db_conn is None:
        return

    with db_conn.cursor() as cur:
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
            )
        )

def finalize_session(session_id: str, reason: str) -> None:
    state = active_sessions.pop(session_id, None)
    if state is None:
        return

    row = build_feature_row(state)
    predicted_label, probability = predict_feature_row(row)

    row["predicted_label"] = predicted_label
    row["probability"] = probability
    row["finalize_reason"] = reason

    save_prediction_row(row)
    save_session_feature_to_db(row)
    save_prediction_to_db(row)

    print(f"\nSession finalized: {session_id}")
    print(f"reason          : {reason}")
    print(f"user_id         : {row['user_id']}")
    print(f"profile         : {row['profile']}")
    print(f"total_events    : {row['total_event_count']}")
    print(f"click_count     : {row['click_count']}")
    print(f"add_to_cart     : {row['add_to_cart_count']}")
    print(f"purchase_count  : {row['purchase_count']}")
    print(f"duration_sec    : {row['session_duration_sec']:.2f}")
    print(f"actual_label    : {row['label']}")
    print(f"predicted_label : {row['predicted_label']}")
    print(f"probability     : {row['probability']}")
    print("-" * 60)


def expire_idle_sessions() -> None:
    now = time.time()
    expired = []

    for session_id, state in active_sessions.items():
        if now - state["wall_last_seen"] >= SESSION_IDLE_TIMEOUT_SEC:
            expired.append(session_id)

    for session_id in expired:
        finalize_session(session_id, reason="idle_timeout")


def main() -> None:
    ensure_dirs()
    connect_db()
    load_model()

    consumer = create_consumer()

    print(f"Listening Kafka topic: {KAFKA_TOPIC}")
    print(f"Consumer group       : {KAFKA_GROUP_ID}")
    print(f"Idle timeout         : {SESSION_IDLE_TIMEOUT_SEC} sec")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            records = consumer.poll(timeout_ms=1000)

            if not records:
                expire_idle_sessions()
                continue

            for _, messages in records.items():
                for message in messages:
                    event = message.value
                    append_raw_event(event)
                    save_raw_event_to_db(event)

                    session_id = event.get("session_id")
                    if not session_id:
                        continue

                    if session_id not in active_sessions:
                        active_sessions[session_id] = initialize_session(event)

                    update_session(active_sessions[session_id], event)

                    print(
                        f"Received | session_id={session_id} | "
                        f"event_type={event.get('event_type')} | "
                        f"user_id={event.get('user_id')} | "
                        f"profile={event.get('profile')}"
                    )

                    if event.get("event_type") == "purchase":
                        finalize_session(session_id, reason="purchase_event")

            expire_idle_sessions()

    except KeyboardInterrupt:
        print("\nStopping consumer...")
        for session_id in list(active_sessions.keys()):
            finalize_session(session_id, reason="shutdown")
    finally:
        consumer.close()
        if db_conn is not None:
            db_conn.close()
        print("Consumer stopped.")


if __name__ == "__main__":
    main()

