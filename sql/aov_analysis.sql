
-- 1. Overall Average Order Value
-- Aggregate payments first to avoid duplicate order joins.

WITH order_payments AS (
    SELECT
        order_id,
        SUM(payment_value) AS order_value
    FROM olist_order_payments_dataset_cleaned
    GROUP BY order_id
)
SELECT
    COUNT(*) AS total_orders,
    ROUND(SUM(order_value)::numeric, 2) AS total_revenue,
    ROUND(AVG(order_value)::numeric, 2) AS average_order_value
FROM order_payments p
JOIN olist_orders_dataset_cleaned o
    ON p.order_id = o.order_id
WHERE o.order_status = 'delivered';


-- 2. Monthly Average Order Value

WITH order_payments AS (
    SELECT
        order_id,
        SUM(payment_value) AS order_value
    FROM olist_order_payments_dataset_cleaned
    GROUP BY order_id
)
SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp)
        AS order_month,
    COUNT(*) AS total_orders,
    ROUND(SUM(p.order_value)::numeric, 2) AS total_revenue,
    ROUND(AVG(p.order_value)::numeric, 2) AS avg_order_value
FROM order_payments p
JOIN olist_orders_dataset_cleaned o
    ON p.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY 1;
