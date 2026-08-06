import duckdb

conn = duckdb.connect("data/financial_market.duckdb")

df = conn.execute("""
SELECT *
FROM bronze_company_fundamentals
""").fetchdf()

print(df)

conn.close()