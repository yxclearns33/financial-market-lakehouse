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
# Extract Company Fundamentals
# -------------------------

print("Starting company fundamentals ingestion...")


all_companies = []


for ticker in tickers:

    print(f"Downloading fundamentals for {ticker}")

    company = yf.Ticker(ticker)

    info = company.info

    row = {

        "ticker": ticker,

        "company_name": info.get("longName"),

        "sector": info.get("sector"),

        "industry": info.get("industry"),

        "market_cap": info.get("marketCap"),

        "enterprise_value": info.get("enterpriseValue"),

        "pe_ratio": info.get("trailingPE"),

        "forward_pe": info.get("forwardPE"),

        "dividend_yield": info.get("dividendYield"),

        "profit_margin": info.get("profitMargins"),

        "revenue_growth": info.get("revenueGrowth"),

        "country": info.get("country"),

        "currency": info.get("currency"),

        "ingestion_time": datetime.now()

    }


    all_companies.append(row)



fundamentals = pd.DataFrame(all_companies)


# -------------------------
# Load Bronze Layer
# -------------------------

print("Writing fundamentals to DuckDB...")


os.makedirs("data", exist_ok=True)


conn = duckdb.connect(database_path)


conn.execute("""
CREATE OR REPLACE TABLE bronze_company_fundamentals AS
SELECT *
FROM fundamentals
""")


conn.close()


print("Bronze fundamentals ingestion complete!")
print(datetime.now())