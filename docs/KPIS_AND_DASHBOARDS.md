# IntelliBI Sales Lakehouse — KPIs, Reports & Dashboards Guide

> **Locale:** India. All revenue / profit / discount values are in **INR** (`₹`).
> Counter widgets in the bundled Databricks dashboard are configured with
> `currencyCode = INR`. Sales tax assumption = 18% GST (blended).
> Regional dimensions correspond to India zones (North / South / East /
> West / Central / NE / Exports).

This guide describes every report, KPI and visualization recommendation that
can be produced from the Gold-layer star schema. Use it together with the
SQL views in `Notebooks/reports/sql_gold_business_views.sql` and the
Databricks SQL dashboard `IntelliBI_Sales_Executive.lvdash.json`.

---

## 1. Recommended Dashboards

| # | Dashboard | Audience | Refresh |
|---|-----------|----------|---------|
| 1 | **Executive Sales Summary** | C-suite, VP Sales | Daily |
| 2 | **Product & Category Analytics** | Merchandising, Category mgrs | Daily |
| 3 | **Regional & Store Performance** | Regional managers, Store ops | Daily / weekly |
| 4 | **Customer Insights (360 / RFM)** | Marketing, CRM | Weekly |
| 5 | **Discount & Promotion Effectiveness** | Pricing, Marketing | Weekly |
| 6 | **Invoice / Accounts Receivable** | Finance, Collections | Daily |
| 7 | **Channel & Payment Mix** | Digital, Finance | Weekly |
| 8 | **Cohort & Retention** | Growth, CRM | Monthly |

---

## 2. KPIs by Subject Area

### 2.1 Executive

| KPI | Formula | View |
|-----|---------|------|
| Total Orders | `COUNT(DISTINCT sale_id)` | `vw_exec_kpi_summary` |
| Gross Revenue | `SUM(gross_amount)` | `vw_exec_kpi_summary` |
| Net Revenue | `SUM(net_amount)` | `vw_exec_kpi_summary` |
| Total Discount | `SUM(discount_amount)` | `vw_exec_kpi_summary` |
| Gross Profit | `SUM(net_amount) − SUM(cost_amount)` | `vw_exec_kpi_summary` |
| Gross Margin % | `profit / net_revenue × 100` | `vw_exec_kpi_summary` |
| Avg Order Value (AOV) | `net_revenue / orders` | `vw_exec_kpi_summary` |
| Unique Customers | `COUNT(DISTINCT customer_sk)` | `vw_exec_kpi_summary` |
| Revenue YoY Growth % | `(this_year − last_year) / last_year` | `vw_sales_yoy` |

### 2.2 Product

| KPI | Description | View |
|-----|-------------|------|
| Top-N Products by Revenue / Profit | Ranking | `vw_top10_products` |
| Category Margin Mix | Margin % per category | `vw_category_performance` |
| Brand Share of Revenue | Brand-level grouping | `vw_product_performance` |
| Slow-Movers | `units_sold < threshold` | `vw_product_performance` |
| Inventory Turn (proxy) | `units_sold / period` | `vw_product_performance` |

### 2.3 Store / Region

| KPI | Description | View |
|-----|-------------|------|
| Revenue / Profit per Store | Store ranking | `vw_store_performance` |
| Revenue per Sq Ft | Productivity | `vw_store_performance` |
| Region Contribution % | Share of total | `vw_regional_performance` |
| Store Type Mix | Flagship vs outlet vs popup | `vw_store_performance` |
| Regional Margin % | Profitability by region | `vw_regional_performance` |

### 2.4 Customer

| KPI | Description | View |
|-----|-------------|------|
| Customer Lifetime Value | Sum of net revenue | `vw_customer_360` |
| Avg Order Value per segment | Segment AOV | `vw_customer_segment_perf` |
| Recency / Frequency / Monetary | RFM 1–5 scores | `vw_customer_rfm` |
| New vs Returning | Cohort split | `vw_monthly_new_vs_returning` |
| Days Since Last Purchase | Churn signal | `vw_customer_360` |
| Customer Count per Segment | Distribution | `vw_customer_segment_perf` |

### 2.5 Discount

| KPI | Description | View |
|-----|-------------|------|
| Discount Redemption Rate | `orders_with_discount / total_orders` | `vw_discount_effectiveness` |
| Discount % of Gross | Promotional cost intensity | `vw_discount_effectiveness` |
| Margin: With vs Without Discount | Incremental impact | `vw_discount_vs_nondiscount` |
| Top Performing Promo Codes | Revenue ranking | `vw_discount_effectiveness` |

### 2.6 Invoice / Finance

| KPI | Description | View |
|-----|-------------|------|
| Total Billed | Sum of invoices | `vw_invoice_status_summary` |
| Avg Days to Pay | Collections efficiency | `vw_invoice_status_summary` |
| % Overdue / Pending | Risk metric | `vw_invoice_overdue` |
| Invoice Aging Buckets | 0-30 / 31-60 / 60+ | extension of `vw_invoice_overdue` |
| Payment Method Mix | Customer behaviour | `vw_payment_method_perf` |

### 2.7 Channel

| KPI | View |
|-----|------|
| Online vs In-Store revenue | `vw_channel_perf` |
| Channel margin % | `vw_channel_perf` |
| Channel growth trend | join `vw_channel_perf` with `dim_date` |

---

## 3. Visualization Recommendations

| KPI / Report | Best Visualization |
|--------------|-------------------|
| Single KPI (revenue, margin, orders) | **Counter** / big-number card |
| Monthly trend (revenue, profit) | **Line chart** with two series |
| YoY / Period comparison | **Line + markers** or **Combo bar+line** |
| Category / Region / Brand share | **Pie / Donut chart** (≤ 6 slices) or **stacked bar** |
| Top-N rankings | **Horizontal bar chart** |
| Store ranking table | **Sortable data table** with conditional formatting |
| RFM segmentation | **Heatmap** (R × F × M) |
| Geographic spread | **Map / choropleth** if PostGIS / lat-long enriched |
| Funnel: Visit → Cart → Order | **Funnel chart** (extend with web data) |
| Cohort retention | **Cohort heatmap** |
| Invoice aging | **Stacked bar** by aging bucket |
| Discount vs no-discount | **Side-by-side bar** |
| Channel mix | **Pie** + **bar trend** |

---

## 4. Sales Analytics Use Cases

* **Revenue forecasting** — feed `vw_sales_monthly` into Databricks ML / Prophet.
* **Promo ROI** — measure margin uplift attributed to each discount code.
* **Stock-out detection** — surface products with declining unit velocity.
* **Customer churn** — flag customers with `days_since_last_purchase > 90`.
* **Cross-sell opportunities** — market-basket analysis on `fact_sales` joined by `sale_id`.
* **Price elasticity** — correlate `unit_price` changes against `quantity` over time.

## 5. Customer Insights Use Cases

* **RFM-based campaigns** — target `r_score+f_score+m_score ≥ 12` for VIP campaigns.
* **Segment migration** — track customers moving REGULAR → PREMIUM → VIP across SCD2 history.
* **Geographic expansion** — find under-served cities with high AOV but low order volume.
* **Loyalty programme design** — set thresholds using `vw_customer_360` lifetime value distribution.

## 6. Regional & Product Performance Use Cases

* **Region scorecards** — monthly PDF emailed to each Regional Manager.
* **Product profitability matrix** — `category × region` margin grid.
* **Store rationalisation** — identify bottom-decile stores by `revenue_per_sqft`.
* **Assortment optimisation** — combine product turn with margin to recommend SKUs.

## 7. Discount & Revenue Analysis Use Cases

* **Discount cannibalisation** — see whether discounted orders shift volume vs add it.
* **Code lifecycle reports** — measure usage curves across `valid_from..valid_to`.
* **Segment-targeted promos** — measure REGULAR vs PREMIUM uplift per promo type.
* **Margin protection** — alert when `discount_pct_of_gross > 20%` for a category.

---

## 8. How to Import the Dashboard

1. Open Databricks workspace → **Dashboards** → **Create dashboard** → **Import**.
2. Upload `Notebooks/reports/IntelliBI_Sales_Executive.lvdash.json`.
3. Select the SQL warehouse to bind to.
4. (If using `qa` / `prd`) edit each dataset's query — replace `saleslake_dev`
   with `saleslake_qa` or `saleslake_prd`.
5. Click **Publish** and share with the appropriate Unity Catalog group.

## 9. Performance Tips

* Ensure all `vw_*` views run against partitioned `fact_*` tables (already partitioned on date columns).
* Run `OPTIMIZE saleslake_dev.gold_dev.fact_sales ZORDER BY (customer_sk, product_sk)` weekly.
* Enable `liquid clustering` on `fact_sales` if cluster supports DBR 13.3+.
* Schedule `VACUUM` (default 7-day retention) to manage storage.
