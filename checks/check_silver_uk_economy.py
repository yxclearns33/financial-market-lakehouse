import duckdb

conn = duckdb.connect("data/financial_market.duckdb")

df = conn.execute("""
SELECT *
FROM silver_uk_economy
LIMIT 20;
""").fetchdf()

print(df)

print("\nColumns:")
print(df.columns)

conn.close()