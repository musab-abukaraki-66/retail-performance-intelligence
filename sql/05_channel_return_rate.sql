-- Return rate by sales channel and category.
-- Business question: is Marketplace's discount-driven growth quietly eroding
-- margin through higher return rates?
SELECT
    channel,
    category,
    COUNT(*)                                              AS total_orders,
    SUM(is_returned)                                       AS returned_orders,
    ROUND(SUM(is_returned) * 100.0 / COUNT(*), 2)          AS return_rate_pct,
    ROUND(AVG(discount_pct) * 100, 2)                      AS avg_discount_pct
FROM orders
GROUP BY channel, category
HAVING total_orders >= 30
ORDER BY return_rate_pct DESC
LIMIT 15;
