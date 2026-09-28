# Architecture

## End-to-end flow

```text
Azure Blob / ADLS Gen2 (staecommpipeline)
  container: ecommerce-data/incremental_load/
    ├── orders_data/source|archive
    ├── customers_data/source|archive
    ├── products_data/source|archive
    ├── inventory_data/source|archive
    ├── shipping_data/source|archive
    └── trigger/                    ← file-arrival trigger watches here
              │
              ▼
Azure Databricks (adb-ecomm-pipeline)
  Access Connector (ac-ecomm-pipeline)
    → Storage credential (cred-ecomm-storage)
    → External location (ext-ecomm-incremental)
    → External Volume (/Volumes/demo-external-catalog/default/incremental_load)
              │
              ▼
Workflow: ecomm_event_driven_pipeline
  [parallel] 01–05 stage loads (CSV → Delta staging tables)
       → 06 data validation
       → 07 enrichment
       → 08 SCD2 merge + analytics tables
```

## Why this design

| Choice | Reason |
|---|---|
| Files in **your** Azure Storage | Realistic lakehouse pattern; source of truth outside the compute workspace |
| **Access Connector + External Location** | Secure Entra ID auth (no account keys in notebooks) |
| **External Volume** | Notebooks keep `/Volumes/...` paths while data stays in ADLS |
| **File-arrival trigger** | Event-driven batch: job starts when a trigger JSON lands |
| **Delta staging + SCD2 targets** | ACID writes, history tracking, SQL-friendly analytics |

## Medallion-style layers in this repo

| Layer | Objects | Format |
|---|---|---|
| Landing | Volume folders (`source/`) | CSV / JSON |
| Staging | `*_stage` tables | Delta |
| Curated | `*_target` (SCD2) | Delta |
| Serving | `enriched_orders`, `*_analytics`, `analytics_summary` | Delta |

## Job DAG

```text
customers_stage_load ──┐
inventory_stage_load ──┤
orders_stage_load ─────┼──► data_validation ──► data_enrichment ──► final_merge_operation
products_stage_load ───┤
shipping_stage_load ───┘
```

Proven in a live run: launched by **file arrival**, status **Succeeded** (~11 minutes on a single-node `Standard_D4ds_v4` cluster, DBR 17.3).
