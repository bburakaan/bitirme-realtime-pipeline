from __future__ import annotations

import zipfile
from pathlib import Path
from io import TextIOWrapper
import os
import time

import pandas as pd
from psycopg2.extras import execute_values

from db.connection import get_connection
from db.demo_seed import get_table_count, seed_olist_demo_data


DATA_DIR = Path("data/olist")
FULL_DATA_THRESHOLD = 50_000
IS_RENDER = os.getenv("RENDER", "false").lower() == "true"
INCREMENTAL_BATCH_SIZE = int(os.getenv("OLIST_IMPORT_BATCH_SIZE", "1000"))
INCREMENTAL_SLEEP_SEC = float(os.getenv("OLIST_IMPORT_SLEEP_SEC", "2"))
RESET_ON_START = (
    os.getenv("OLIST_RESET_ON_START", "true" if IS_RENDER else "false").lower() == "true"
)

DATASETS = [
    {
        "table": "olist_customers",
        "file": "olist_customers_dataset.csv.zip",
        "columns": [
            "customer_id",
            "customer_unique_id",
            "customer_zip_code_prefix",
            "customer_city",
            "customer_state",
        ],
    },
    {
        "table": "olist_products",
        "file": "olist_products_dataset.csv.zip",
        "columns": [
            "product_id",
            "product_category_name",
            "product_name_lenght",
            "product_description_lenght",
            "product_photos_qty",
            "product_weight_g",
            "product_length_cm",
            "product_height_cm",
            "product_width_cm",
        ],
    },
    {
        "table": "olist_orders",
        "file": "olist_orders_dataset.csv.zip",
        "columns": [
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    },
    {
        "table": "olist_order_items",
        "file": "olist_order_items_dataset.csv.zip",
        "columns": [
            "order_id",
            "order_item_id",
            "product_id",
            "seller_id",
            "shipping_limit_date",
            "price",
            "freight_value",
        ],
    },
    {
        "table": "olist_order_payments",
        "file": "olist_order_payments_dataset.csv.zip",
        "columns": [
            "order_id",
            "payment_sequential",
            "payment_type",
            "payment_installments",
            "payment_value",
        ],
    },
]


def full_olist_files_available() -> bool:
    return all((DATA_DIR / dataset["file"]).exists() for dataset in DATASETS)


def clear_olist_tables() -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            truncate_olist_tables(cur)


def truncate_olist_tables(cur) -> None:
    cur.execute(
        """
        TRUNCATE TABLE
            olist_order_payments,
            olist_order_items,
            olist_orders,
            olist_customers,
            olist_products
        RESTART IDENTITY
        """
    )


def copy_dataset(cur, table: str, file_name: str, columns: list[str]) -> None:
    path = DATA_DIR / file_name
    columns_sql = ", ".join(columns)
    copy_sql = (
        f"COPY {table} ({columns_sql}) "
        "FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    )

    with zipfile.ZipFile(path) as archive:
        inner_name = archive.namelist()[0]
        with archive.open(inner_name) as raw_file:
            text_file = TextIOWrapper(raw_file, encoding="utf-8")
            cur.copy_expert(copy_sql, text_file)

    print(f"Loaded {file_name} into {table}")


def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        return value.item()

    return value


def clean_chunk(df: pd.DataFrame, columns: list[str]) -> list[tuple]:
    rows = []

    for raw_row in df[columns].itertuples(index=False, name=None):
        rows.append(tuple(clean_value(value) for value in raw_row))

    return rows


def insert_rows(table: str, columns: list[str], rows: list[tuple]) -> int:
    if not rows:
        return 0

    columns_sql = ", ".join(columns)
    sql = f"INSERT INTO {table} ({columns_sql}) VALUES %s ON CONFLICT DO NOTHING"

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            execute_values(cur, sql, rows, page_size=len(rows))
        conn.commit()
    finally:
        conn.close()

    return len(rows)


def stream_full_olist_data(
    *,
    reset: bool = RESET_ON_START,
    batch_size: int = INCREMENTAL_BATCH_SIZE,
    sleep_sec: float = INCREMENTAL_SLEEP_SEC,
) -> None:
    if not full_olist_files_available():
        seed_olist_demo_data()
        return

    if reset:
        clear_olist_tables()
    elif get_table_count("olist_orders") >= FULL_DATA_THRESHOLD:
        return

    iterators = [
        (
            dataset,
            pd.read_csv(DATA_DIR / dataset["file"], chunksize=batch_size),
        )
        for dataset in DATASETS
    ]

    active_iterators = iterators
    cycle = 0

    while active_iterators:
        cycle += 1
        next_iterators = []

        for dataset, iterator in active_iterators:
            try:
                df = next(iterator)
            except StopIteration:
                continue

            rows = clean_chunk(df, dataset["columns"])
            inserted = insert_rows(dataset["table"], dataset["columns"], rows)
            print(
                "Olist incremental import | "
                f"cycle={cycle} table={dataset['table']} rows={inserted}"
            )
            next_iterators.append((dataset, iterator))

        active_iterators = next_iterators

        if active_iterators and sleep_sec > 0:
            time.sleep(sleep_sec)

    print("Olist incremental import completed.")


def load_full_olist_data() -> bool:
    if get_table_count("olist_orders") >= FULL_DATA_THRESHOLD:
        return True

    if not full_olist_files_available():
        return False

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            truncate_olist_tables(cur)

            for dataset in DATASETS:
                copy_dataset(
                    cur,
                    table=dataset["table"],
                    file_name=dataset["file"],
                    columns=dataset["columns"],
                )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return True


def load_or_seed_olist_data() -> None:
    if load_full_olist_data():
        return

    seed_olist_demo_data()


def load_olist_for_online_demo() -> None:
    mode = os.getenv("OLIST_IMPORT_MODE", "incremental" if IS_RENDER else "full").lower()

    if mode == "incremental":
        stream_full_olist_data()
        return

    load_or_seed_olist_data()
