
-- State-wise Revenue and Customer Analysis

SELECT
    c.customer_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT c.customer_unique_id) AS total_customers,
    ROUND(SUM(oi.price + oi.freight_value)::numeric, 2)
        AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_product_price
FROM olist_orders_dataset_cleaned o
JOIN olist_customers_dataset_cleaned c
    ON o.customer_id = c.customer_id
JOIN olist_order_items_dataset_cleaned oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC;


-- Top 10 States by Revenue

SELECT
    c.customer_state,
    ROUND(SUM(oi.price + oi.freight_value)::numeric, 2)
        AS total_revenue
FROM olist_orders_dataset_cleaned o
JOIN olist_customers_dataset_cleaned c
    ON o.customer_id = c.customer_id
JOIN olist_order_items_dataset_cleaned oi
    ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY total_revenue DESC
LIMIT 10;
