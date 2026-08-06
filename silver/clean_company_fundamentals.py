import duckdb
import pandas as pd


database_path = "data/financial_market.duckdb"


conn = duckdb.connect(database_path)


df = conn.execute("""
SELECT *
FROM bronze_company_fundamentals
""").fetchdf()


# Remove duplicate records
df = df.drop_duplicates()


# Standardise column names
df.columns = (
    df.columns
    .str.lower()
    .str.replace(" ", "_")
)


# Remove rows with no ticker
if "ticker" in df.columns:
    df = df.dropna(subset=["ticker"])


# Create clean silver table
conn.execute("""
CREATE OR REPLACE TABLE silver_company_metrics AS
SELECT *
FROM df
""")


conn.close()


print("Silver company fundamentals complete!")