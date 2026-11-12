CREATE TABLE monthly_revenue AS

SELECT
    DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month,

    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(DISTINCT o.customer_id) AS total_customers,

    ROUND(SUM(p.payment_value)::NUMERIC, 2) AS total_revenue,

    ROUND(AVG(p.payment_value)::NUMERIC, 2) AS avg_payment

FROM olist_orders_dataset_cleaned o

JOIN olist_order_payments_dataset_cleaned p
    ON o.order_id = p.order_id

WHERE o.order_status = 'delivered'

GROUP BY DATE_TRUNC('month', o.order_purchase_timestamp)

ORDER BY order_month;