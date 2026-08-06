import duckdb

conn = duckdb.connect("data/financial_market.duckdb")

df = conn.execute("""
SELECT *
FROM bronze_uk_economic_indicators
LIMIT 20;
""").fetchdf()

print(df)

conn.close()
