
-- ==========================================
-- REVIEW & CUSTOMER SATISFACTION ANALYSIS
-- ==========================================

-- 1. Overall review performance

SELECT
    COUNT(*) AS total_reviews,
    ROUND(AVG(review_score), 2) AS average_rating,
    COUNT(*) FILTER (WHERE review_score = 5) AS five_star_reviews,
    COUNT(*) FILTER (WHERE review_score <= 2) AS negative_reviews
FROM olist_order_reviews_dataset_cleaned;


-- 2. Review score distribution

SELECT
    review_score,
    COUNT(*) AS total_reviews,
    ROUND(
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2
    ) AS review_percentage
FROM olist_order_reviews_dataset_cleaned
GROUP BY review_score
ORDER BY review_score DESC;


-- 3. Monthly customer satisfaction trend

SELECT
    DATE_TRUNC('month', review_creation_date) AS review_month,
    COUNT(*) AS total_reviews,
    ROUND(AVG(review_score), 2) AS average_rating
FROM olist_order_reviews_dataset_cleaned
GROUP BY DATE_TRUNC('month', review_creation_date)
ORDER BY review_month;


-- 4. Positive vs Negative reviews

SELECT
    CASE
        WHEN review_score >= 4 THEN 'Positive'
        WHEN review_score = 3 THEN 'Neutral'
        ELSE 'Negative'
    END AS review_category,
    COUNT(*) AS total_reviews
FROM olist_order_reviews_dataset_cleaned
GROUP BY review_category
ORDER BY total_reviews DESC;


-- 5. Reviews with and without comments

SELECT
    CASE
        WHEN review_comment_message IS NULL
             OR TRIM(review_comment_message) = ''
        THEN 'No Comment'
        ELSE 'Has Comment'
    END AS comment_status,
    COUNT(*) AS total_reviews
FROM olist_order_reviews_dataset_cleaned
GROUP BY comment_status;


-- 6. Lowest-rated orders

SELECT
    review_id,
    order_id,
    review_score,
    review_comment_message
FROM olist_order_reviews_dataset_cleaned
WHERE review_score <= 2
ORDER BY review_score ASC
LIMIT 20;


-- 7. Customer review response time (hours)

SELECT
    ROUND(
        AVG(
            EXTRACT(EPOCH FROM (
                review_answer_timestamp - review_creation_date
            )) / 3600
        )::NUMERIC, 2
    ) AS avg_response_hours
FROM olist_order_reviews_dataset_cleaned
WHERE review_answer_timestamp IS NOT NULL
  AND review_creation_date IS NOT NULL;


-- ==========================================
-- ANALYSIS COMPLETED
-- ==========================================
