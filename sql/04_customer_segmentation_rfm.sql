-- RFM-style customer segmentation (Recency, Frequency, Monetary).
-- Business question: who are the highest-value, at-risk customers to prioritize
-- for retention?
WITH customer_orders AS (
    SELECT
        customer_id,
        MAX(order_date)                AS last_order_date,
        COUNT(DISTINCT order_id)       AS frequency,
        ROUND(SUM(net_revenue), 2)     AS monetary
    FROM orders
    WHERE is_returned = 0
    GROUP BY customer_id
),
scored AS (
    SELECT
        customer_id,
        frequency,
        monetary,
        CAST(julianday('2024-12-31') - julianday(last_order_date) AS INTEGER) AS recency_days,
        NTILE(4) OVER (ORDER BY julianday(last_order_date) DESC) AS recency_score,
        NTILE(4) OVER (ORDER BY frequency ASC)                   AS frequency_score,
        NTILE(4) OVER (ORDER BY monetary ASC)                    AS monetary_score
    FROM customer_orders
)
SELECT
    customer_id,
    recency_days,
    frequency,
    monetary,
    (recency_score + frequency_score + monetary_score) AS rfm_score,
    CASE
        WHEN (recency_score + frequency_score + monetary_score) >= 10 THEN 'Champions'
        WHEN (recency_score + frequency_score + monetary_score) >= 7  THEN 'Loyal'
        WHEN (recency_score + frequency_score + monetary_score) >= 5  THEN 'At Risk'
        ELSE 'Dormant'
    END AS segment
FROM scored
ORDER BY rfm_score DESC
LIMIT 20;
