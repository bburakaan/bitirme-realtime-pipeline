from __future__ import annotations

import zipfile
from pathlib import Path
from io import TextIOWrapper

from db.connection import get_connection
from db.demo_seed import get_table_count, seed_olist_demo_data


DATA_DIR = Path("data/olist")
FULL_DATA_THRESHOLD = 50_000

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
