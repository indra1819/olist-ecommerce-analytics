
-- Recency, Frequency and Monetary Analysis

WITH customer_rfm AS (
    SELECT
        c.customer_unique_id,
        MAX(o.order_purchase_timestamp) AS last_purchase,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(oi.price + oi.freight_value) AS monetary
    FROM olist_orders_dataset_cleaned o
    JOIN olist_customers_dataset_cleaned c
        ON o.customer_id = c.customer_id
    JOIN olist_order_items_dataset_cleaned oi
        ON o.order_id = oi.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),
rfm AS (
    SELECT
        customer_unique_id,
        CURRENT_DATE - last_purchase::date AS recency_days,
        frequency,
        ROUND(monetary::numeric, 2) AS monetary
    FROM customer_rfm
)
SELECT
    customer_unique_id,
    recency_days,
    frequency,
    monetary,
    CASE
        WHEN recency_days <= 90 AND frequency >= 3
            THEN 'Champions'
        WHEN recency_days <= 180 AND frequency >= 2
            THEN 'Loyal Customers'
        WHEN recency_days > 180 AND frequency >= 2
            THEN 'At Risk'
        WHEN frequency = 1
            THEN 'New / One-Time Customers'
        ELSE 'Potential Customers'
    END AS customer_segment
FROM rfm
ORDER BY monetary DESC;

