-- Regional performance ranking with revenue, margin, and average order value.
-- Business question: which regions drive revenue, and which are most profitable per order?
SELECT
    region,
    COUNT(DISTINCT order_id)                          AS orders,
    ROUND(SUM(net_revenue), 2)                         AS net_revenue,
    ROUND(SUM(net_revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
    ROUND(SUM(profit) * 100.0 / SUM(net_revenue), 2)   AS profit_margin_pct,
    RANK() OVER (ORDER BY SUM(net_revenue) DESC)       AS revenue_rank
FROM orders
WHERE is_returned = 0
GROUP BY region
ORDER BY net_revenue DESC;
