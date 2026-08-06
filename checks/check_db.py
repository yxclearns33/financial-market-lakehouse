import duckdb

# Connect to DuckDB database
conn = duckdb.connect(
    "data/financial_market.duckdb"
)

# Check Bronze table
df = conn.execute("""
SELECT *
FROM bronze_stock_prices
LIMIT 10
""").fetchdf()

print(df)

conn.close()