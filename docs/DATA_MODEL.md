# IntelliBI Sales Lakehouse — Data Model

> **Locale:** India. Currency = INR (`₹`). Geographic zones = North / South /
> East / West / Central / North East / Exports. Phones = `+91-XXXXX-XXXXX`.
> Tax = 18% GST (blended) applied to invoice subtotals.

## 1. Overview

The project implements a full **Medallion (Bronze → Silver → Gold) Lakehouse**
on Databricks Unity Catalog, with a classic **Star Schema** in the Gold layer
optimised for BI / SQL dashboards.

```
                        ┌───────────────────┐
                        │  Source Volumes    │  CSV files (daily drops)
                        └─────────┬──────────┘
                                  ▼
        BRONZE  (raw_*)   COPY INTO, all STRING, ingest_ts audit
                                  ▼
        SILVER  (cleaned_*) Dedupe, trim, typecast, watermark INSERT
                                  ▼
        GOLD (dim_* / refined_* / fact_* / vw_*)
                  │
                  ├─  SCD1 dimensions  (region)
                  ├─  SCD2 dimensions  (customer, product, store, discount)
                  ├─  Fact tables      (fact_sales, fact_invoice)
                  └─  Reporting views  (vw_*  →  Databricks SQL dashboard)
```

## 2. Catalog & Schema Layout (Unity Catalog)

| Env | Catalog | Bronze schema | Silver schema | Gold schema |
|-----|---------|---------------|---------------|-------------|
| dev | `saleslake_dev` | `bronze_dev` | `silver_dev` | `gold_dev` |
| qa  | `saleslake_qa`  | `bronze_qa`  | `silver_qa`  | `gold_qa`  |
| prd | `saleslake_prd` | `bronze_prd` | `silver_prd` | `gold_prd` |

## 3. Entities

| Entity | Type | SCD | Source location (volume) |
|--------|------|-----|--------------------------|
| Sales      | Transactional | n/a | `daily_sales/` |
| Invoice    | Transactional | n/a | `daily_invoice/` (also AWS S3) |
| Customer   | Master | **SCD2** | `daily_customer/` |
| Product    | Master | **SCD2** | `daily_product/` |
| Store      | Master | **SCD2** | `daily_store/` |
| Discount   | Master | **SCD2** | `manual_discount/` |
| Region     | Reference | **SCD1** | `daily_region/` |
| Date       | Static  | static | generated |

## 4. Star Schema — Fact_Sales

```
                                  ┌──────────────┐
                                  │   dim_date    │
                                  └─────┬─────────┘
   ┌──────────────┐      ┌──────────────┐      ┌──────────────┐
   │  dim_region   │◀────│              │────▶│ dim_customer  │
   └──────────────┘      │              │      └──────────────┘
                          │              │
   ┌──────────────┐      │  fact_sales  │      ┌──────────────┐
   │  dim_store    │◀────│              │────▶│  dim_product  │
   └──────────────┘      │              │      └──────────────┘
                          │              │
                          └──────┬───────┘
                                 ▼
                           ┌──────────────┐
                           │ dim_discount  │
                           └──────────────┘
```

### Fact_Sales — Grain & Measures

* **Grain**: one row per sale transaction line.
* **Surrogate FKs**: `date_sk`, `customer_sk`, `product_sk`, `store_sk`, `region_sk`, `discount_sk`.
* **Measures**: `quantity`, `unit_price`, `gross_amount`, `discount_amount`, `net_amount`, `cost_amount`, `profit_amount`, `profit_margin_pct`.
* **Degenerate**: `sale_id` (business key), `payment_method`, `channel`.
* **Partitioning**: `sale_date` (Delta partition pruning).

### Fact_Invoice — Grain & Measures

* **Grain**: one row per invoice (header level).
* **Surrogate FKs**: `customer_sk`, `store_sk`, `region_sk`, `discount_sk`,
  `invoice_date_sk`, `due_date_sk`, `payment_date_sk`.
* **Measures**: `subtotal_amount`, `discount_amount`, `tax_amount`, `total_amount`, `days_to_pay`.
* **Flags**: `is_overdue`, `payment_status`.

## 5. Keys & Relationships

| FK in fact | References | Cardinality |
|-----------|-----------|------------|
| fact_sales.customer_sk | refinedCustomer.customer_sk (active row) | many → 1 |
| fact_sales.product_sk  | dim_product.product_sk (active row)      | many → 1 |
| fact_sales.store_sk    | dim_store.store_sk (active row)          | many → 1 |
| fact_sales.region_sk   | dim_region.region_sk                     | many → 1 |
| fact_sales.discount_sk | dim_discount.discount_sk (nullable)      | many → 0..1 |
| fact_sales.date_sk     | dim_date.date_sk                         | many → 1 |

> The natural keys (`product_id`, `store_id`, `region_id`, `customer_id`,
> `discount_code`) flow through Silver and are used **at join time** to look up
> surrogate keys in the active dimension row.

## 6. Slowly Changing Dimensions — Implementation Notes

* All SCD logic is implemented in **PySpark using Delta Python API**
  (`DeltaTable.update()` / `append`) — **no SQL MERGE statements** for the new
  dimensions, per project requirement.
* SCD2 columns: `is_active` (`Y` / `N`), `rec_version` (int), `start_effective_ts`, `end_effective_ts`.
* SCD2 algorithm:
  1. Snapshot silver → dedupe latest by natural key.
  2. Hash business attributes (`sha2` over concatenated cols).
  3. Left join active dim slice → flag rows as `NEW` / `CHANGE` / `NO_CHANGE`.
  4. For `CHANGE`: expire old active row (`is_active='N'`, `end_effective_ts=now`).
  5. For `NEW` + `CHANGE`: insert new active row with `rec_version+1`.

## 7. Loading Order

```
catalog/schema/table DDL
        │
        ├─ Bronze (parallel ok)
        ├─ Silver (parallel ok within layer)
        ├─ Gold dimensions  ──┐
        │                      │  must complete BEFORE
        └─ Gold facts ◀────────┘
                  │
                  └─ Business views (vw_*) — created once
```
