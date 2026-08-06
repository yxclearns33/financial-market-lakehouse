import duckdb

conn = duckdb.connect("data/financial_market.duckdb")

df = conn.execute("""
SELECT *
FROM silver_stock_prices
LIMIT 20;
""").fetchdf()

print(df)

print("\nColumns:")
print(df.columns)

conn.close()