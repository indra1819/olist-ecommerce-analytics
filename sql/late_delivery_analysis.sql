
-- 1. Overall Delivery Performance

SELECT
    COUNT(*) AS delivered_orders,
    COUNT(*) FILTER (
        WHERE order_delivered_customer_date >
              order_estimated_delivery_date
    ) AS late_orders,
    ROUND(
        COUNT(*) FILTER (
            WHERE order_delivered_customer_date >
                  order_estimated_delivery_date
        ) * 100.0 / NULLIF(COUNT(*), 0), 2
    ) AS late_delivery_percentage
FROM olist_orders_dataset_cleaned
WHERE order_status = 'delivered'
AND order_delivered_customer_date IS NOT NULL
AND order_estimated_delivery_date IS NOT NULL;


-- 2. Average Delivery Time

SELECT
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (
                order_delivered_customer_date -
                order_purchase_timestamp
            )) / 86400
        )::numeric, 2
    ) AS avg_delivery_days
FROM olist_orders_dataset_cleaned
WHERE order_status = 'delivered'
AND order_delivered_customer_date IS NOT NULL;


-- 3. Top 20 Orders with Highest Delivery Delay

SELECT
    order_id,
    order_purchase_timestamp,
    order_delivered_customer_date,
    order_estimated_delivery_date,
    ROUND(
        (
            EXTRACT(EPOCH FROM (
                order_delivered_customer_date -
                order_estimated_delivery_date
            )) / 86400
        )::numeric, 2
    ) AS delay_days
FROM olist_orders_dataset_cleaned
WHERE order_status = 'delivered'
AND order_delivered_customer_date >
    order_estimated_delivery_date
ORDER BY delay_days DESC
LIMIT 20;
