CREATE SCHEMA SOURCE_DATA;
CREATE SCHEMA DATA_WAREHOUSE;
CREATE SCHEMA DATA_LAKE;


CREATE TABLE SOURCE_DATA.product_category_name_translation (
    product_category_name VARCHAR(64) PRIMARY KEY,
    product_category_name_english VARCHAR(64)
);
CREATE TABLE SOURCE_DATA.olist_customers_dataset (
    customer_id VARCHAR(32) PRIMARY KEY,
    customer_unique_id VARCHAR(32),
    customer_zip_code_prefix VARCHAR(8),
    customer_city VARCHAR(64),
    customer_state CHAR(2)
);

CREATE TABLE SOURCE_DATA.olist_geolocation_dataset (
    geolocation_zip_code_prefix VARCHAR(8),
    geolocation_lat DOUBLE PRECISION,
    geolocation_lng DOUBLE PRECISION,
    geolocation_city VARCHAR(64),
    geolocation_state CHAR(2)
);

CREATE TABLE SOURCE_DATA.olist_orders_dataset (
    order_id VARCHAR(32) PRIMARY KEY,
    customer_id VARCHAR(32) REFERENCES SOURCE_DATA.olist_customers_dataset(customer_id),
    order_status VARCHAR(20),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE SOURCE_DATA.olist_order_payments_dataset (
    order_id VARCHAR(32) REFERENCES SOURCE_DATA.olist_orders_dataset(order_id),
    payment_sequential INTEGER,
    payment_type VARCHAR(20),
    payment_installments INTEGER,
    payment_value NUMERIC(10,2)
);

CREATE TABLE SOURCE_DATA.olist_sellers_dataset (
    seller_id VARCHAR(32) PRIMARY KEY,
    seller_zip_code_prefix VARCHAR(8),
    seller_city VARCHAR(64),
    seller_state CHAR(2)
);

CREATE TABLE SOURCE_DATA.olist_products_dataset (
    product_id VARCHAR(32) PRIMARY KEY,
    product_category_name VARCHAR(64),
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g INTEGER,
    product_length_cm INTEGER,
    product_height_cm INTEGER,
    product_width_cm INTEGER
);

CREATE TABLE SOURCE_DATA.olist_order_reviews_dataset (
    review_id VARCHAR(32),
    order_id VARCHAR(32) REFERENCES SOURCE_DATA.olist_orders_dataset(order_id),
    review_score INTEGER,
    review_comment_title VARCHAR(255),
    review_comment_message TEXT,
    review_creation_date DATE,
    review_answer_timestamp TIMESTAMP
);

CREATE TABLE SOURCE_DATA.olist_order_items_dataset (
    order_id VARCHAR(32) REFERENCES SOURCE_DATA.olist_orders_dataset(order_id),
    order_item_id INT,
    product_id VARCHAR(32) REFERENCES SOURCE_DATA.olist_products_dataset(product_id),
    seller_id VARCHAR(32)  REFERENCES SOURCE_DATA.olist_sellers_dataset(seller_id),
    shipping_limit_date TIMESTAMP,
    price NUMERIC(10,2),
    freight_value NUMERIC(10,2)
);

-- Loading data into table
COPY SOURCE_DATA.product_category_name_translation
FROM '/docker-entrypoint-initdb.d/product_category_name_translation.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);

COPY SOURCE_DATA.olist_customers_dataset
FROM '/docker-entrypoint-initdb.d/olist_customers_dataset.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);

COPY SOURCE_DATA.olist_geolocation_dataset
FROM '/docker-entrypoint-initdb.d/olist_geolocation_dataset.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);

COPY SOURCE_DATA.olist_orders_dataset
FROM '/docker-entrypoint-initdb.d/olist_orders_dataset.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);

COPY SOURCE_DATA.olist_sellers_dataset
FROM '/docker-entrypoint-initdb.d/olist_sellers_dataset.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);

COPY SOURCE_DATA.olist_products_dataset
FROM '/docker-entrypoint-initdb.d/olist_products_dataset.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);

COPY SOURCE_DATA.olist_order_items_dataset
FROM '/docker-entrypoint-initdb.d/olist_order_items_dataset.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);

COPY SOURCE_DATA.olist_order_payments_dataset
FROM '/docker-entrypoint-initdb.d/olist_order_payments_dataset.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);

COPY SOURCE_DATA.olist_order_reviews_dataset
FROM '/docker-entrypoint-initdb.d/olist_order_reviews_dataset.csv'
WITH (FORMAT csv, ON_ERROR 'ignore', HEADER);



