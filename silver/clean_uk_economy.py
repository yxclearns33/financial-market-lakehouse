import duckdb
import pandas as pd


database_path = "data/financial_market.duckdb"


conn = duckdb.connect(database_path)


df = conn.execute("""
SELECT *
FROM bronze_uk_economic_indicators
""").fetchdf()


# Remove duplicate rows
df = df.drop_duplicates()


# Standardise column names
df.columns = (
    df.columns
    .str.lower()
    .str.replace(" ", "_")
)


# Sort economic data
df = df.sort_values(
    ["indicator", "year"]
)


# Create Silver table
conn.execute("""
CREATE OR REPLACE TABLE silver_uk_economy AS
SELECT *
FROM df
""")


conn.close()


print("Silver UK economy complete!")