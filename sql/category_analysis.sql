
-- 1. Category Performance

SELECT
    COALESCE(
        t.product_category_name_english,
        p.product_category_name
    ) AS category,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    COUNT(*) AS total_items,
    ROUND(SUM(oi.price)::numeric, 2) AS total_revenue,
    ROUND(AVG(oi.price)::numeric, 2) AS avg_price
FROM olist_order_items_dataset_cleaned oi
JOIN olist_orders_dataset_cleaned o
    ON oi.order_id = o.order_id
JOIN olist_products_dataset_cleaned p
    ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation_cleaned t
    ON p.product_category_name = t.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY total_revenue DESC;


-- 2. Top 10 Categories by Orders

SELECT
    COALESCE(
        t.product_category_name_english,
        p.product_category_name
    ) AS category,
    COUNT(DISTINCT oi.order_id) AS total_orders
FROM olist_order_items_dataset_cleaned oi
JOIN olist_orders_dataset_cleaned o
    ON oi.order_id = o.order_id
JOIN olist_products_dataset_cleaned p
    ON oi.product_id = p.product_id
LEFT JOIN product_category_name_translation_cleaned t
    ON p.product_category_name = t.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY 1
ORDER BY total_orders DESC
LIMIT 10;
