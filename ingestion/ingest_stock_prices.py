import yfinance as yf
import duckdb
import pandas as pd
import os
from datetime import datetime


# -------------------------
# Configuration
# -------------------------

tickers = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "GOOGL"
]

database_path = "data/financial_market.duckdb"


# -------------------------
# Extract Stock Prices
# -------------------------

print("Starting stock price ingestion...")

all_prices = []

for ticker in tickers:

    print(f"Downloading {ticker}")

    df = yf.download(
        ticker,
        start="2024-01-01",
        interval="1d",
        auto_adjust=False
    )

    df.reset_index(inplace=True)

    # Flatten yfinance columns
    df.columns = [
        col[0] if isinstance(col, tuple) else col
        for col in df.columns
    ]

    df["ticker"] = ticker

    # Add ingestion timestamp
    df["ingestion_time"] = datetime.now()

    all_prices.append(df)


# Combine all stocks
prices = pd.concat(all_prices)


# -------------------------
# Load Bronze Layer
# -------------------------

print("Writing to DuckDB...")

os.makedirs("data", exist_ok=True)

conn = duckdb.connect(database_path)


conn.execute("""
CREATE TABLE IF NOT EXISTS bronze_stock_prices AS
SELECT *
FROM prices
WHERE 1=0
""")


conn.execute("""
INSERT INTO bronze_stock_prices
SELECT *
FROM prices
""")


conn.close()


print("Bronze stock ingestion complete!")
print(datetime.now())