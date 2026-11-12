
-- ORDER STATUS ANALYSIS

SELECT
    order_status,
    COUNT(DISTINCT order_id) AS total_orders,

    ROUND(
        COUNT(DISTINCT order_id) * 100.0 /
        SUM(COUNT(DISTINCT order_id)) OVER (),
        2
    ) AS order_percentage

FROM olist_orders_dataset_cleaned

GROUP BY order_status

ORDER BY total_orders DESC;
