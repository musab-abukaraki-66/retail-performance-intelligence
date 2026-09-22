-- Monthly net revenue, profit, and order volume trend.
-- Business question: is revenue growing, and is profit growing with it?
SELECT
    strftime('%Y-%m', order_date)              AS month,
    COUNT(DISTINCT order_id)                    AS orders,
    ROUND(SUM(net_revenue), 2)                  AS net_revenue,
    ROUND(SUM(profit), 2)                       AS profit,
    ROUND(SUM(profit) * 100.0 / SUM(net_revenue), 2) AS profit_margin_pct
FROM orders
WHERE is_returned = 0
GROUP BY month
ORDER BY month;
