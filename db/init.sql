CREATE TABLE IF NOT EXISTS raw_events (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT,
    user_id TEXT,
    session_id TEXT,
    event_type TEXT,
    product_id TEXT,
    category TEXT,
    price NUMERIC(12, 2),
    event_timestamp TIMESTAMP,
    device_type TEXT,
    source TEXT,
    profile TEXT,
    raw_json JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_raw_events_session_id ON raw_events (session_id);
CREATE INDEX IF NOT EXISTS idx_raw_events_created_at ON raw_events (created_at DESC);

CREATE TABLE IF NOT EXISTS session_features (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT,
    user_id TEXT,
    profile TEXT,
    total_event_count INTEGER,
    click_count INTEGER,
    page_view_count INTEGER,
    search_count INTEGER,
    add_to_cart_count INTEGER,
    purchase_count INTEGER,
    session_duration_sec NUMERIC(12, 2),
    avg_price NUMERIC(12, 2),
    click_rate NUMERIC(8, 4),
    cart_rate NUMERIC(8, 4),
    actual_label INTEGER,
    finalize_reason TEXT,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_session_features_session_id ON session_features (session_id);
CREATE INDEX IF NOT EXISTS idx_session_features_created_at ON session_features (created_at DESC);

CREATE TABLE IF NOT EXISTS predictions (
    id BIGSERIAL PRIMARY KEY,
    session_id TEXT,
    user_id TEXT,
    actual_label INTEGER,
    predicted_label INTEGER,
    probability NUMERIC(10, 6),
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_predictions_session_id ON predictions (session_id);
CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions (created_at DESC);

CREATE TABLE IF NOT EXISTS olist_customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT,
    customer_zip_code_prefix INTEGER,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE IF NOT EXISTS olist_orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_olist_orders_purchase_ts
    ON olist_orders (order_purchase_timestamp DESC);

CREATE TABLE IF NOT EXISTS olist_order_items (
    order_id TEXT,
    order_item_id INTEGER,
    product_id TEXT,
    seller_id TEXT,
    shipping_limit_date TIMESTAMP,
    price NUMERIC(12, 2),
    freight_value NUMERIC(12, 2),
    PRIMARY KEY (order_id, order_item_id)
);

CREATE INDEX IF NOT EXISTS idx_olist_order_items_product_id
    ON olist_order_items (product_id);

CREATE TABLE IF NOT EXISTS olist_order_payments (
    order_id TEXT,
    payment_sequential INTEGER,
    payment_type TEXT,
    payment_installments INTEGER,
    payment_value NUMERIC(12, 2),
    PRIMARY KEY (order_id, payment_sequential)
);

CREATE INDEX IF NOT EXISTS idx_olist_order_payments_type
    ON olist_order_payments (payment_type);

CREATE TABLE IF NOT EXISTS olist_products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);
