-- PAYMENT METHOD ANALYSIS

SELECT
    payment_type,
    COUNT(*) AS total_payments,
    COUNT(DISTINCT order_id) AS unique_orders,
    ROUND(SUM(payment_value)::numeric, 2) AS total_payment,
    ROUND(AVG(payment_value)::numeric, 2) AS avg_payment

FROM olist_order_payments_dataset_cleaned

GROUP BY payment_type

ORDER BY total_payment DESC;