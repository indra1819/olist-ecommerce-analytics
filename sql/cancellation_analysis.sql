
-- 1. Cancellation Overview

SELECT
    order_status,
    COUNT(*) AS total_orders,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2
    ) AS percentage
FROM olist_orders_dataset_cleaned
GROUP BY order_status
ORDER BY total_orders DESC;


-- 2. Monthly Cancellations

SELECT
    DATE_TRUNC('month', order_purchase_timestamp)
        AS order_month,
    COUNT(*) AS cancelled_orders
FROM olist_orders_dataset_cleaned
WHERE order_status = 'canceled'
GROUP BY 1
ORDER BY 1;


-- 3. Cancellation by Customer State

SELECT
    c.customer_state,
    COUNT(*) AS cancelled_orders
FROM olist_orders_dataset_cleaned o
JOIN olist_customers_dataset_cleaned c
    ON o.customer_id = c.customer_id
WHERE o.order_status = 'canceled'
GROUP BY c.customer_state
ORDER BY cancelled_orders DESC;
