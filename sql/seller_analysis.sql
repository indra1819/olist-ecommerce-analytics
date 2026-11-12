
-- 1. Top 10 Sellers by Revenue

SELECT
    oi.seller_id,
    s.seller_city,
    s.seller_state,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_product_price

FROM olist_order_items_dataset_cleaned oi

JOIN olist_orders_dataset_cleaned o
    ON oi.order_id = o.order_id

JOIN olist_sellers_dataset_cleaned s
    ON oi.seller_id = s.seller_id

WHERE o.order_status = 'delivered'

GROUP BY
    oi.seller_id,
    s.seller_city,
    s.seller_state

ORDER BY total_revenue DESC

LIMIT 10;


-- 2. Seller Performance Summary

SELECT
    oi.seller_id,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(
        SUM(oi.price)::numeric /
        NULLIF(COUNT(DISTINCT o.order_id), 0), 2
    ) AS avg_order_value

FROM olist_order_items_dataset_cleaned oi

JOIN olist_orders_dataset_cleaned o
    ON oi.order_id = o.order_id

WHERE o.order_status = 'delivered'

GROUP BY oi.seller_id

ORDER BY total_revenue DESC

LIMIT 20;


-- 3. State-wise Seller Performance

SELECT
    s.seller_state,
    COUNT(DISTINCT s.seller_id) AS total_sellers,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue

FROM olist_order_items_dataset_cleaned oi

JOIN olist_orders_dataset_cleaned o
    ON oi.order_id = o.order_id

JOIN olist_sellers_dataset_cleaned s
    ON oi.seller_id = s.seller_id

WHERE o.order_status = 'delivered'

GROUP BY s.seller_state

ORDER BY total_revenue DESC;
