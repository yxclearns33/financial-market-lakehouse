import duckdb

conn = duckdb.connect("data/financial_market.duckdb")

df = conn.execute("""
SELECT DISTINCT metric
FROM bronze_financial_statements
ORDER BY metric;
""").fetchdf()

print(df)

conn.close()