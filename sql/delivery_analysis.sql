
-- DELIVERY PERFORMANCE ANALYSIS

SELECT
    c.customer_state,

    COUNT(o.order_id) AS total_delivered_orders,

    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (
                o.order_delivered_customer_date -
                o.order_purchase_timestamp
            )) / 86400
        )::numeric, 2
    ) AS avg_delivery_days,

    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (
                o.order_estimated_delivery_date -
                o.order_delivered_customer_date
            )) / 86400
        )::numeric, 2
    ) AS avg_days_before_estimated_date,

    COUNT(*) FILTER (
        WHERE o.order_delivered_customer_date >
              o.order_estimated_delivery_date
    ) AS late_deliveries

FROM olist_orders_dataset_cleaned o

JOIN olist_customers_dataset_cleaned c
    ON o.customer_id = c.customer_id

WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
  AND o.order_estimated_delivery_date IS NOT NULL

GROUP BY c.customer_state

ORDER BY avg_delivery_days DESC;
