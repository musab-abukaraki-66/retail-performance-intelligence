-- Category-level profitability and discount exposure.
-- Business question: which categories look strong on revenue but weak on margin
-- because of heavy discounting?
SELECT
    category,
    ROUND(SUM(net_revenue), 2)                        AS net_revenue,
    ROUND(SUM(profit), 2)                              AS profit,
    ROUND(SUM(profit) * 100.0 / SUM(net_revenue), 2)   AS profit_margin_pct,
    ROUND(AVG(discount_pct) * 100, 2)                  AS avg_discount_pct
FROM orders
WHERE is_returned = 0
GROUP BY category
ORDER BY net_revenue DESC;
