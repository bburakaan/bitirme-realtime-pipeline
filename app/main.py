import os
import json
import threading
import joblib
import pandas as pd

from typing import Any
from pathlib import Path
from pydantic import BaseModel

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from db.connection import get_connection
from db.init_db import init_database

load_dotenv()

INTENT_MODEL_PATH = Path("ml/saved_model/intent_model.pkl")
INTENT_METRICS_PATH = Path("ml/saved_model/intent_model_metrics.json")
ENABLE_DEMO_PRODUCER = (
    os.getenv("ENABLE_DEMO_PRODUCER", os.getenv("RENDER", "false")).lower() == "true"
)

app = FastAPI(title="Realtime E-Commerce Backend API")

intent_model = None
if INTENT_MODEL_PATH.exists():
    intent_model = joblib.load(INTENT_MODEL_PATH)

default_origins = [
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5175",
    "http://localhost:5173",
    "http://localhost:5175",
    "https://bitirme-frontend.onrender.com",
]
configured_origins = [
    origin.strip()
    for origin in os.getenv("FRONTEND_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=sorted(set(default_origins + configured_origins)),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def rows_to_dicts(cur) -> list[dict[str, Any]]:
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    return [dict(zip(columns, row)) for row in rows]


@app.on_event("startup")
def startup_tasks():
    init_database()

    if ENABLE_DEMO_PRODUCER:
        from producer.db_demo_worker import run_forever

        thread = threading.Thread(target=run_forever, daemon=True)
        thread.start()


class IntentPredictionInput(BaseModel):
    Administrative: int
    Administrative_Duration: float
    Informational: int
    Informational_Duration: float
    ProductRelated: int
    ProductRelated_Duration: float
    BounceRates: float
    ExitRates: float
    PageValues: float
    SpecialDay: float
    Month: str
    OperatingSystems: int
    Browser: int
    Region: int
    TrafficType: int
    VisitorType: str
    Weekend: bool


@app.get("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return {
            "status": "ok",
            "database": "connected",
            "service": "realtime-ecommerce-api"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "not_connected",
            "detail": str(e)
        }


@app.get("/deployment-info")
def deployment_info():
    is_render = os.getenv("RENDER", "false").lower() == "true"

    return {
        "render": os.getenv("RENDER", "false"),
        "service_name": os.getenv("RENDER_SERVICE_NAME"),
        "service_type": os.getenv("RENDER_SERVICE_TYPE"),
        "git_branch": os.getenv("RENDER_GIT_BRANCH"),
        "git_commit": os.getenv("RENDER_GIT_COMMIT"),
        "demo_producer_enabled": ENABLE_DEMO_PRODUCER,
        "olist_import_mode": os.getenv(
            "OLIST_IMPORT_MODE",
            "incremental" if is_render else "full",
        ),
        "olist_reset_on_start": os.getenv(
            "OLIST_RESET_ON_START",
            "true" if is_render else "false",
        ),
    }


@app.get("/events/recent")
def get_recent_events(limit: int = 20):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, event_id, user_id, session_id, event_type, product_id,
                       category, price, event_timestamp, device_type, source,
                       profile, created_at
                FROM raw_events
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )
            data = rows_to_dicts(cur)
        return {
            "count": len(data),
            "items": data
        }
    finally:
        conn.close()


@app.get("/sessions/recent")
def get_recent_sessions(limit: int = 20):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, session_id, user_id, profile, total_event_count,
                       click_count, page_view_count, search_count,
                       add_to_cart_count, purchase_count, session_duration_sec,
                       avg_price, click_rate, cart_rate, actual_label,
                       finalize_reason, processed_at, created_at
                FROM session_features
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )
            data = rows_to_dicts(cur)
        return {
            "count": len(data),
            "items": data
        }
    finally:
        conn.close()


@app.get("/predictions/recent")
def get_recent_predictions(limit: int = 20):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, session_id, user_id, actual_label,
                       predicted_label, probability, processed_at, created_at
                FROM predictions
                ORDER BY id DESC
                LIMIT %s
                """,
                (limit,)
            )
            data = rows_to_dicts(cur)
        return {
            "count": len(data),
            "items": data
        }
    finally:
        conn.close()


@app.get("/stats/summary")
def get_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM raw_events")
            raw_events_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM session_features")
            session_features_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM predictions")
            predictions_count = cur.fetchone()[0]

            cur.execute(
                """
                SELECT profile, COUNT(*) AS count
                FROM session_features
                GROUP BY profile
                ORDER BY count DESC
                """
            )
            profile_distribution = rows_to_dicts(cur)

            cur.execute(
                """
                SELECT finalize_reason, COUNT(*) AS count
                FROM session_features
                GROUP BY finalize_reason
                ORDER BY count DESC
                """
            )
            finalize_reason_distribution = rows_to_dicts(cur)

        return {
            "raw_events_count": raw_events_count,
            "session_features_count": session_features_count,
            "predictions_count": predictions_count,
            "profile_distribution": profile_distribution,
            "finalize_reason_distribution": finalize_reason_distribution
        }
    finally:
        conn.close()


@app.get("/olist/summary")
def get_olist_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM olist_customers")
            customers_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM olist_orders")
            orders_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM olist_order_items")
            order_items_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM olist_order_payments")
            payments_count = cur.fetchone()[0]

            cur.execute("SELECT COUNT(*) FROM olist_products")
            products_count = cur.fetchone()[0]

        return {
            "customers_count": customers_count,
            "orders_count": orders_count,
            "order_items_count": order_items_count,
            "payments_count": payments_count,
            "products_count": products_count,
        }
    finally:
        conn.close()


@app.get("/olist/orders/recent")
def get_recent_olist_orders(limit: int = 20):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT order_id, customer_id, order_status,
                       order_purchase_timestamp,
                       order_delivered_customer_date,
                       order_estimated_delivery_date
                FROM olist_orders
                ORDER BY order_purchase_timestamp DESC NULLS LAST
                LIMIT %s
                """,
                (limit,)
            )
            data = rows_to_dicts(cur)
        return {"count": len(data), "items": data}
    finally:
        conn.close()


@app.get("/olist/products/recent")
def get_recent_olist_products(limit: int = 20):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT product_id, product_category_name,
                       product_name_lenght, product_description_lenght,
                       product_photos_qty, product_weight_g
                FROM olist_products
                LIMIT %s
                """,
                (limit,)
            )
            data = rows_to_dicts(cur)
        return {"count": len(data), "items": data}
    finally:
        conn.close()


@app.get("/olist/payments/summary")
def get_olist_payment_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT payment_type, COUNT(*) AS count, SUM(payment_value) AS total_value
                FROM olist_order_payments
                GROUP BY payment_type
                ORDER BY count DESC
                """
            )
            data = rows_to_dicts(cur)
        return {"count": len(data), "items": data}
    finally:
        conn.close()


@app.get("/intent/model-info")
def get_intent_model_info():
    if not INTENT_MODEL_PATH.exists():
        return {
            "status": "error",
            "message": "intent_model.pkl not found"
        }

    metrics = {}
    if INTENT_METRICS_PATH.exists():
        with open(INTENT_METRICS_PATH, "r", encoding="utf-8") as f:
            metrics = json.load(f)

    return {
        "status": "ok",
        "model_loaded": intent_model is not None,
        "model_path": str(INTENT_MODEL_PATH),
        "metrics": metrics
    }


@app.get("/intent/sample-input")
def get_intent_sample_input():
    return {
        "Administrative": 1,
        "Administrative_Duration": 6.0,
        "Informational": 0,
        "Informational_Duration": 0.0,
        "ProductRelated": 15,
        "ProductRelated_Duration": 579.0,
        "BounceRates": 0.0,
        "ExitRates": 0.0125,
        "PageValues": 63.93506419,
        "SpecialDay": 0.0,
        "Month": "Dec",
        "OperatingSystems": 1,
        "Browser": 1,
        "Region": 4,
        "TrafficType": 2,
        "VisitorType": "New_Visitor",
        "Weekend": False
    }


@app.post("/intent/predict")
def predict_intent(payload: IntentPredictionInput):
    if intent_model is None:
        return {
            "status": "error",
            "message": "Intent model is not loaded"
        }

    row = payload.model_dump()
    row["Weekend"] = str(row["Weekend"])

    df = pd.DataFrame([row])

    predicted_label = int(intent_model.predict(df)[0])

    probability = None
    if hasattr(intent_model, "predict_proba"):
        probability = float(intent_model.predict_proba(df)[0][1])

    return {
        "status": "ok",
        "predicted_label": predicted_label,
        "predicted_revenue": bool(predicted_label),
        "probability": probability,
        "input": payload.model_dump()
    }
