from __future__ import annotations

import random
from datetime import datetime, timedelta

from db.connection import get_connection


PAYMENT_TYPES = ["credit_card", "boleto", "voucher", "debit_card"]
PRODUCT_CATEGORIES = [
    "electronics",
    "fashion",
    "books",
    "home",
    "sports",
    "health_beauty",
    "toys",
    "auto",
]
ORDER_STATUSES = ["delivered", "shipped", "processing", "invoiced"]
STATES = ["SP", "RJ", "MG", "RS", "PR", "BA", "SC", "GO"]
CITIES = ["sao_paulo", "rio_de_janeiro", "belo_horizonte", "curitiba", "salvador"]


def get_table_count(table_name: str) -> int:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            return int(cur.fetchone()[0])
    finally:
        conn.close()


def seed_olist_demo_data() -> None:
    if get_table_count("olist_orders") > 0:
        return

    rng = random.Random(42)
    now = datetime.now()
    products = []

    for index in range(1, 31):
        products.append(
            (
                f"demo_product_{index:03d}",
                rng.choice(PRODUCT_CATEGORIES),
                rng.randint(18, 70),
                rng.randint(80, 900),
                rng.randint(1, 6),
                rng.randint(100, 5000),
                rng.randint(10, 60),
                rng.randint(5, 40),
                rng.randint(10, 50),
            )
        )

    customers = []
    orders = []
    order_items = []
    payments = []

    for index in range(1, 121):
        customer_id = f"demo_customer_{index:03d}"
        order_id = f"demo_order_{index:03d}"
        purchase_time = now - timedelta(days=rng.randint(1, 180), hours=rng.randint(0, 23))
        delivered_time = purchase_time + timedelta(days=rng.randint(2, 14))
        estimated_time = purchase_time + timedelta(days=rng.randint(7, 20))
        item_count = rng.randint(1, 3)

        customers.append(
            (
                customer_id,
                f"demo_unique_{index:03d}",
                rng.randint(10000, 99999),
                rng.choice(CITIES),
                rng.choice(STATES),
            )
        )

        orders.append(
            (
                order_id,
                customer_id,
                rng.choice(ORDER_STATUSES),
                purchase_time,
                purchase_time + timedelta(hours=rng.randint(1, 12)),
                purchase_time + timedelta(days=rng.randint(1, 4)),
                delivered_time,
                estimated_time,
            )
        )

        total_payment = 0.0
        for item_index in range(1, item_count + 1):
            product_id = rng.choice(products)[0]
            price = round(rng.uniform(25, 850), 2)
            freight = round(rng.uniform(5, 90), 2)
            total_payment += price + freight
            order_items.append(
                (
                    order_id,
                    item_index,
                    product_id,
                    f"demo_seller_{rng.randint(1, 15):03d}",
                    purchase_time + timedelta(days=rng.randint(3, 8)),
                    price,
                    freight,
                )
            )

        payments.append(
            (
                order_id,
                1,
                rng.choice(PAYMENT_TYPES),
                rng.randint(1, 10),
                round(total_payment, 2),
            )
        )

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO olist_products (
                    product_id, product_category_name, product_name_lenght,
                    product_description_lenght, product_photos_qty,
                    product_weight_g, product_length_cm, product_height_cm,
                    product_width_cm
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO NOTHING
                """,
                products,
            )
            cur.executemany(
                """
                INSERT INTO olist_customers (
                    customer_id, customer_unique_id, customer_zip_code_prefix,
                    customer_city, customer_state
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (customer_id) DO NOTHING
                """,
                customers,
            )
            cur.executemany(
                """
                INSERT INTO olist_orders (
                    order_id, customer_id, order_status, order_purchase_timestamp,
                    order_approved_at, order_delivered_carrier_date,
                    order_delivered_customer_date, order_estimated_delivery_date
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id) DO NOTHING
                """,
                orders,
            )
            cur.executemany(
                """
                INSERT INTO olist_order_items (
                    order_id, order_item_id, product_id, seller_id,
                    shipping_limit_date, price, freight_value
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (order_id, order_item_id) DO NOTHING
                """,
                order_items,
            )
            cur.executemany(
                """
                INSERT INTO olist_order_payments (
                    order_id, payment_sequential, payment_type,
                    payment_installments, payment_value
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (order_id, payment_sequential) DO NOTHING
                """,
                payments,
            )
        conn.commit()
    finally:
        conn.close()

    print(
        "Olist demo data seeded | "
        f"customers={len(customers)} orders={len(orders)} "
        f"items={len(order_items)} payments={len(payments)} products={len(products)}"
    )
