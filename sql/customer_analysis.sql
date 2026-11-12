-- CUSTOMER ORDER SUMMARY

CREATE TABLE customer_order_summary AS

SELECT
    c.customer_id,
    c.customer_city,
    c.customer_state,

    COUNT(DISTINCT o.order_id) AS total_orders,

    ROUND(
        COALESCE(SUM(p.payment_value), 0)::NUMERIC,
        2
    ) AS total_spent,

    ROUND(
        COALESCE(AVG(p.payment_value), 0)::NUMERIC,
        2
    ) AS avg_payment

FROM olist_customers_dataset_cleaned c

LEFT JOIN olist_orders_dataset_cleaned o
    ON c.customer_id = o.customer_id

LEFT JOIN olist_order_payments_dataset_cleaned p
    ON o.order_id = p.order_id

GROUP BY
    c.customer_id,
    c.customer_city,
    c.customer_state;