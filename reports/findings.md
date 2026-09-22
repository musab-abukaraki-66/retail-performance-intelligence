# Findings — Retail Performance Intelligence

All numbers below are copy-pasted, unedited, from `python src/run_sql.py` against
`data/retail.db` (18,000 orders, 1,200 customers, 25 SKUs, Jan 2023–Dec 2024,
synthetic data — see [README](../README.md#dataset)).

## 1. Revenue is seasonal and margin compresses in Nov/Dec

Monthly profit margin holds a tight 39–41% band for ten months of the year, then
drops to **36.5–37.2%** every November and December despite revenue peaking in
the same months (`sql/01_monthly_revenue_trend.sql`). The cause is discount
depth, not cost: `generate_data` (and the real-world pattern it mimics) applies
heavier holiday discounting, and `sql/05_channel_return_rate.sql` shows that
discount-heavy periods carry more returns. **Recommendation:** cap holiday
discount depth per category rather than applying a blanket seasonal discount,
and monitor margin — not just revenue — as the primary holiday KPI.

## 2. North region leads revenue, but not because customers there spend more

North is the top region by net revenue ($1.24M) and South is second ($1.11M),
but average order value is nearly identical across all five regions ($300–$309,
`sql/02_regional_performance.sql`). The revenue gap is driven by *order volume*
(4,133 vs. 2,880 orders for North vs. West), i.e. customer base size and
purchase frequency, not basket size. **Recommendation:** growth initiatives in
West/Central should target acquisition and purchase frequency, not AOV-focused
tactics like bundling — the data doesn't show an AOV problem there.

## 3. Office has the smallest revenue share but the best margin

Office products generate the least category revenue ($1.15M, 4th of 5) but the
highest margin (42.9%) at a discount rate in line with every other category
(9.88% avg. vs. 9.77–10.09% elsewhere, `sql/03_category_profitability.sql`).
Outdoor is the mirror case: highest revenue ($1.27M) but lowest margin (36.8%).
**Recommendation:** the margin gap isn't discount-driven — it's cost structure.
Any assortment or supplier renegotiation exercise should start with Outdoor.

## 4. Marketplace returns run ~26% higher than the other channels

Aggregating `sql/05_channel_return_rate.sql` by channel: Marketplace returns
8.7% of orders vs. 7.1% (In-Store) and 6.9% (Online), and Marketplace also
carries the deepest average discounting (12.2–12.7% vs. ~9.2–9.6% elsewhere).
Apparel is the highest-risk combination specifically: Marketplace+Apparel
returns 12.58% of orders, the single worst cell in the table.
**Recommendation:** treat Marketplace discount depth as a lever with a
downstream cost (returns processing, restocking), not a free growth channel —
model return-adjusted margin before setting Marketplace promo budgets.

## 5. A small, identifiable customer segment drives disproportionate frequency

The RFM segmentation (`sql/04_customer_segmentation_rfm.sql`) isolates a
"Champions" segment — customers scoring in the top quartile on all three of
recency, frequency, and monetary value — with 17–24 orders each over the two
years and $5,200–$8,700 in lifetime net revenue, roughly 15–29x the dataset's
per-customer average. **Recommendation:** this is the segment to protect first
in any retention program; a churn model or win-back trigger is highest-value
when scoped to Champions who go quiet (rising `recency_days`), not the full
customer base.

## Limitations

- **Data is synthetic.** It was generated with seeded randomness
  (`src/generate_data.py`, `SEED=42`) to resemble realistic retail patterns —
  seasonality, regional mix, channel-based discount behavior — but it does not
  describe any real company, and the specific numbers above are not real
  business outcomes. The methodology (SQL structure, segmentation logic, chart
  design, the kind of question each query answers) is what should transfer to
  a real dataset, not the figures themselves.
- **No causal inference.** The discount → return-rate association in Finding 4
  is a correlation across ~15 channel × category cells; there is no experiment
  or control group here, so "discount depth causes returns" should be tested,
  not assumed, before it drives a pricing decision on real data.
- **Single-period seasonality.** Two years of data captures one holiday cycle
  clearly, one only partially — an inference like "Nov/Dec margin always drops"
  would need a third year to confirm it's a pattern rather than one event.

## Next steps in a production setting

- Replace `src/generate_data.py` with a real ingestion job (warehouse extract
  or POS/ERP export) feeding the same `orders` / `customers` / `products`
  schema — the SQL and chart layer need no changes.
- Move the RFM segmentation from a one-off query to a scheduled table refresh,
  and expose it to the retention/CRM team rather than data/analytics only.
- Add a discount-elasticity model (does a 1pt discount increase actually pay
  for the incremental return rate it causes?) before Finding 4 becomes a
  pricing recommendation.
