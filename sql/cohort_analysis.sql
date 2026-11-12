
-- Customer Cohort Retention Analysis

WITH customer_first_purchase AS (
    SELECT
        c.customer_unique_id,
        DATE_TRUNC(
            'month',
            MIN(o.order_purchase_timestamp)
        ) AS cohort_month
    FROM olist_orders_dataset_cleaned o
    JOIN olist_customers_dataset_cleaned c
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),

customer_activity AS (
    SELECT DISTINCT
        c.customer_unique_id,
        DATE_TRUNC(
            'month',
            o.order_purchase_timestamp
        ) AS activity_month
    FROM olist_orders_dataset_cleaned o
    JOIN olist_customers_dataset_cleaned c
        ON o.customer_id = c.customer_id
    WHERE o.order_status = 'delivered'
),

cohort_data AS (
    SELECT
        f.cohort_month,
        a.activity_month,
        f.customer_unique_id,
        (
            EXTRACT(YEAR FROM a.activity_month) -
            EXTRACT(YEAR FROM f.cohort_month)
        ) * 12 +
        (
            EXTRACT(MONTH FROM a.activity_month) -
            EXTRACT(MONTH FROM f.cohort_month)
        ) AS cohort_age
    FROM customer_first_purchase f
    JOIN customer_activity a
        ON f.customer_unique_id = a.customer_unique_id
    WHERE a.activity_month >= f.cohort_month
),

cohort_size AS (
    SELECT
        cohort_month,
        COUNT(*) AS total_customers
    FROM customer_first_purchase
    GROUP BY cohort_month
)

SELECT
    d.cohort_month,
    d.cohort_age,
    s.total_customers,
    COUNT(DISTINCT d.customer_unique_id)
        AS active_customers,
    ROUND(
        COUNT(DISTINCT d.customer_unique_id) * 100.0 /
        NULLIF(s.total_customers, 0), 2
    ) AS retention_percentage
FROM cohort_data d
JOIN cohort_size s
    ON d.cohort_month = s.cohort_month
GROUP BY
    d.cohort_month,
    d.cohort_age,
    s.total_customers
ORDER BY
    d.cohort_month,
    d.cohort_age;
