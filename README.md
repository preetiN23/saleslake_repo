# IntelliBI Sales Lakehouse — Databricks Data Engineering Project

End-to-end enterprise Sales & Analytics Lakehouse on **Databricks Unity
Catalog** using **Medallion Architecture** with a classic **Star Schema** in
the Gold layer and a ready-to-import **Databricks SQL Dashboard**.

> Reference: [Medallion Architecture on Databricks](https://docs.databricks.com/aws/en/lakehouse/medallion)

---

## 1. What's Inside

```
IntelliBI_Data_Engineering-main/
├── Notebooks/
│   ├── bronze/                # Raw COPY INTO loaders
│   │   ├── nb_customer_files_bronze.ipynb
│   │   ├── nb_sales_files_bronze.ipynb
│   │   ├── nb_discount_files_bronze.ipynb
│   │   ├── nb_invoice_srcfiles_aws_bronze.ipynb
│   │   ├── nb_region_files_bronze.ipynb         (NEW)
│   │   ├── nb_product_files_bronze.ipynb        (NEW)
│   │   └── nb_store_files_bronze.ipynb          (NEW)
│   ├── silver/                # Cleansed / typed
│   │   ├── nb_customer_bronze_silver.ipynb
│   │   ├── nb_sales_bronze_silver.ipynb
│   │   ├── nb_invoice_aws_bronze_silver.ipynb
│   │   ├── nb_region_bronze_silver.ipynb        (NEW)
│   │   ├── nb_product_bronze_silver.ipynb       (NEW)
│   │   ├── nb_store_bronze_silver.ipynb         (NEW)
│   │   └── nb_discount_bronze_silver.ipynb      (NEW)
│   ├── gold/                  # Dimensions, facts, business logic
│   │   ├── nb_cust_silver_gold.ipynb            (existing SCD2 SQL)
│   │   ├── nb_sales_silver_gold.ipynb           (existing)
│   │   ├── nb_invoice_aws_silver_gold.ipynb     (existing)
│   │   ├── nb_dim_date_load.ipynb               (NEW)
│   │   ├── nb_dim_region_scd1_pyspark.ipynb     (NEW - PySpark SCD1)
│   │   ├── nb_dim_product_scd2_pyspark.ipynb    (NEW - PySpark SCD2)
│   │   ├── nb_dim_store_scd2_pyspark.ipynb      (NEW - PySpark SCD2)
│   │   ├── nb_dim_discount_scd2_pyspark.ipynb   (NEW - PySpark SCD2)
│   │   ├── nb_fact_sales_load.ipynb             (NEW - Star schema fact)
│   │   └── nb_fact_invoice_load.ipynb           (NEW)
│   ├── orchestration/
│   │   ├── sql_cat_schm_tables_ddl.dbquery.ipynb (CONSOLIDATED - all DDLs, new entities on AWS S3)
│   │   ├── nb_master_pipeline_run_all.ipynb     (NEW - E2E orchestrator)
│   │   └── (existing orchestration notebooks)
│   ├── reports/                                  (NEW)
│   │   ├── sql_gold_business_views.sql          # 20+ reporting views
│   │   └── IntelliBI_Sales_Executive.lvdash.json # Importable dashboard
│   └── data_generators/                          (NEW)
│       └── generate_all_sample_data.py          # Pure-stdlib generator
├── sample_data/                                  (NEW)
│   ├── region/   product/   store/   discount/
│   ├── customer/ sales/     invoice/
├── docs/                                         (NEW)
│   ├── DATA_MODEL.md          # Star schema & SCD design
│   └── KPIS_AND_DASHBOARDS.md # 8 dashboards, 40+ KPIs, viz guide
└── README.md
```

## 2. Environments

Three Unity Catalogs are provisioned by `sql_cat_schm_tables_ddl.dbquery.ipynb`:

| Env | Catalog | Use |
|-----|---------|-----|
| dev | `saleslake_dev` | Development |
| qa  | `saleslake_qa`  | Testing |
| prd | `saleslake_prd` | Production |

All notebooks accept a widget `environment` (dev/qa/prd) so a single notebook
runs against any layer.

## 3. Entities & SCD Strategy

| Entity   | Type          | SCD type | Loader |
|----------|---------------|----------|--------|
| Region   | Reference     | **SCD1** | PySpark — `nb_dim_region_scd1_pyspark` |
| Product  | Master        | **SCD2** | PySpark — `nb_dim_product_scd2_pyspark` |
| Store    | Master        | **SCD2** | PySpark — `nb_dim_store_scd2_pyspark` |
| Discount | Master        | **SCD2** | PySpark — `nb_dim_discount_scd2_pyspark` |
| Customer | Master        | **SCD2** | SQL MERGE — `nb_cust_silver_gold` (existing) |
| Sales    | Transactional | n/a → Fact | `nb_fact_sales_load` |
| Invoice  | Transactional | n/a → Fact | `nb_fact_invoice_load` |
| Date     | Static        | static    | `nb_dim_date_load` |

**All new SCD logic uses PySpark + Delta `DeltaTable` Python API — no SQL MERGE.**
SCD1 uses `DeltaTable.merge()` in 3 steps; SCD2 uses the classic 4-step expire-and-insert
pattern with a SHA-256 hash to detect business-column changes.

## 4. How to Run (End-to-End)

```text
1. Run  Notebooks/orchestration/sql_cat_schm_tables_ddl.dbquery.ipynb   (once per env — provisions catalogs, schemas, volumes & all tables incl. AWS S3 externals)
2. Upload sample_data/<entity>/*.csv to /Volumes/saleslake_<env>/bronze_<env>/vol_saleslake_src_files_<env>/<folder>/
3. Run  Notebooks/orchestration/nb_master_pipeline_run_all.ipynb        (env widget=dev)
4. Run  Notebooks/reports/sql_gold_business_views.sql                   (creates 19 vw_*)
5. Import Notebooks/reports/IntelliBI_Sales_Executive.lvdash.json into Databricks SQL
```

### Storage backend per entity

| Layer / Entity | Backend |
|---|---|
| Existing customer/sales/discount bronze + silver + gold | Managed (Unity Catalog default storage) |
| Existing invoice (bronze/silver/gold) | **External Delta on AWS S3** |
| **All new entities** (region, product, store, discount-silver, dim_*, fact_*, dim_date) | **External Delta on AWS S3** — `s3://saleslake-748005667258-eu-north-1-an/saleslake/<env>/delta_tables/<layer>/<entity>/` |

## 5. Sample Data — India-Centric

Generated by `Notebooks/data_generators/generate_all_sample_data.py`
(pure standard library — no extra deps). All entities use Indian
geographies, names, +91 phone numbers, INR pricing and 18% GST.

| File | Rows |
|------|------|
| region_master.csv | 7 — India zones (North, South, East, West, Central, NE, Exports) |
| product_catalog.csv | 500 — INR-priced, Indian + global brands |
| store_master.csv | 200 — Major Indian cities (Delhi / Mumbai / Bengaluru / Chennai / Kolkata / etc.) |
| discount_master.csv | 40 — Festival-themed (DIWALI, HOLI, REPUBLIC, EOSS, etc.) |
| customer_initial.csv | 2,000 — Indian names, +91 phones, 6-digit PIN codes |
| customer_updates.csv | 100 (SCD2 delta demo) |
| daily_sales_enhanced.csv | 50,000 — INR pricing, UPI/COD/etc. payment methods |
| invoice_aws_export.csv | 12,000 — currency = INR, 18% GST applied |

### Region / zone layout

| region_id | code  | region_name        | sub-zone   |
|-----------|-------|--------------------|------------|
| 1 | IN-N  | INDIA NORTH        | NORTH      |
| 2 | IN-S  | INDIA SOUTH        | SOUTH      |
| 3 | IN-E  | INDIA EAST         | EAST       |
| 4 | IN-W  | INDIA WEST         | WEST       |
| 5 | IN-C  | INDIA CENTRAL      | CENTRAL    |
| 6 | IN-NE | INDIA NORTH EAST   | NORTH EAST |
| 7 | IN-EX | INDIA EXPORTS      | EXPORTS    |

All FK relationships are guaranteed (`sales.product_id → product.product_id`,
etc.) so dimension joins on the Gold layer will not orphan rows.

> **Note:** if `store_master.csv` or `daily_sales_enhanced.csv` were open in
> Excel/Preview on Windows during generation, the original files may be
> locked and the new India-centric versions are saved as
> `store_master_india.csv` / `daily_sales_enhanced_india.csv`. Close the
> viewer and rename them in place (or rerun the generator) when convenient.

## 6. Reporting & Dashboards

* See **`docs/KPIS_AND_DASHBOARDS.md`** for the full list of 8 dashboards,
  40+ KPIs, visualization recommendations, and analytics use cases.
* The dashboard JSON (`IntelliBI_Sales_Executive.lvdash.json`) contains
  6 pages: Executive, Products, Regional/Store, Customers, Discount/Channel, Invoice/AR.

## 7. Conventions

* Notebook naming: `nb_<entity>_<src>_<tgt>.ipynb` or `nb_dim_<entity>_<scdtype>_pyspark.ipynb`.
* Table naming: `raw<Entity>` (bronze), `cleaned<Entity>` (silver), `dim_<entity>` / `refined<Entity>` / `fact_<grain>` (gold).
* Watermarking: every silver/gold load filters on
  `ingest_ts > max(target.ingest_ts)` for idempotent incremental runs.
* All Gold tables have `GENERATED ALWAYS AS IDENTITY` surrogate keys.

---

Reference: [Databricks Medallion Architecture](https://docs.databricks.com/aws/en/lakehouse/medallion)
