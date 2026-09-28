# Databricks notebook source
# MAGIC %md
# MAGIC # One-time Setup
# MAGIC Creates the catalog, schema, volume and folder layout that notebooks 01-08 expect.
# MAGIC Run this once before uploading any data files.

# COMMAND ----------

catalog = "demo-external-catalog"
schema = "default"
volume = "incremental_load"
datasets = ["orders", "customers", "products", "inventory", "shipping"]

spark.sql(f"CREATE CATALOG IF NOT EXISTS `{catalog}`")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS `{catalog}`.{schema}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS `{catalog}`.{schema}.{volume}")

print(f"Catalog, schema and volume ready: {catalog}.{schema}.{volume}")

# COMMAND ----------

# Create source/archive folders for every dataset, plus a trigger folder for the file-arrival trigger
base_path = f"/Volumes/{catalog}/{schema}/{volume}"

for name in datasets:
    for sub in ["source", "archive"]:
        path = f"{base_path}/{name}_data/{sub}/"
        dbutils.fs.mkdirs(path)
        print(f"Created: {path}")

dbutils.fs.mkdirs(f"{base_path}/trigger/")
print(f"Created: {base_path}/trigger/")

# COMMAND ----------

# Pre-create the shared processing_log table so the parallel stage-load tasks don't race to create it
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS `{catalog}`.{schema}.processing_log (
        archived_files BIGINT,
        invalid_records BIGINT,
        status STRING,
        task STRING,
        timestamp STRING,
        total_records BIGINT,
        valid_records BIGINT
    ) USING DELTA
""")
print("processing_log table ready")

# COMMAND ----------

# Verify the layout
display(dbutils.fs.ls(base_path))
