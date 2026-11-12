
-- PRODUCT CATEGORY ANALYSIS

SELECT
    t.product_category_name_english AS category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.price) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_price

FROM olist_order_items_dataset_cleaned oi

JOIN olist_products_dataset_cleaned p
    ON oi.product_id = p.product_id

JOIN product_category_name_translation_cleaned t
    ON p.product_category_name = t.product_category_name

GROUP BY
    t.product_category_name_english

ORDER BY total_revenue DESC

LIMIT 10;
