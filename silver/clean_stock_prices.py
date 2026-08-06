import duckdb
import pandas as pd


database_path = "data/financial_market.duckdb"


conn = duckdb.connect(database_path)


df = conn.execute("""
SELECT *
FROM bronze_stock_prices
""").fetchdf()


df = df.rename(columns={
    "Date": "date",
    "Open": "open_price",
    "High": "high_price",
    "Low": "low_price",
    "Close": "close_price",
    "Volume": "volume"
})


df = df.drop(columns=["Adj Close"], errors="ignore")


df = df.sort_values(
    ["ticker", "date"]
)


df["daily_return"] = (
    df.groupby("ticker")["close_price"]
    .pct_change()
)


conn.execute("""
CREATE OR REPLACE TABLE silver_stock_prices AS
SELECT *
FROM df
""")


conn.close()


print("Silver stock prices complete!")