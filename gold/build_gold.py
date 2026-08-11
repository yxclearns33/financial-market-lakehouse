import duckdb

DB_PATH = 'data/financial_market.duckdb'

def build_gold_layer():
    conn = duckdb.connect(DB_PATH)
    print("Building Gold Layer tables...")

    # 1. Build gold_dim_company
    conn.execute("""
        CREATE OR REPLACE TABLE gold_dim_company AS
        SELECT 
            ROW_NUMBER() OVER (ORDER BY ticker) AS company_key,
            ticker,
            company_name,
            sector,
            industry,
            market_cap,
            pe_ratio,
            dividend_yield,
            country,
            currency
        FROM silver_company_metrics;
    """)
    print("  Created: gold_dim_company")

    # 2. Build gold_dim_date
    conn.execute("""
        CREATE OR REPLACE TABLE gold_dim_date AS
        SELECT DISTINCT
            CAST(strftime(date, '%Y%m%d') AS INT) AS date_key,
            CAST(date AS DATE) AS full_date,
            YEAR(date) AS year,
            MONTH(date) AS month,
            MONTHNAME(date) AS month_name,
            QUARTER(date) AS quarter,
            DAYNAME(date) AS day_name
        FROM silver_stock_prices
        ORDER BY full_date;
    """)
    print("  Created: gold_dim_date")

    # 3. Build gold_dim_uk_economy
    conn.execute("""
        CREATE OR REPLACE TABLE gold_dim_uk_economy AS
        SELECT 
            ROW_NUMBER() OVER (ORDER BY year, indicator) AS economy_key,
            country,
            country_code,
            indicator,
            year,
            value
        FROM silver_uk_economy;
    """)
    print("  Created: gold_dim_uk_economy")

    # 4. Build gold_fact_stock_performance
    conn.execute("""
        CREATE OR REPLACE TABLE gold_fact_stock_performance AS
        SELECT 
            CAST(strftime(s.date, '%Y%m%d') AS INT) AS date_key,
            c.company_key,
            s.open_price,
            s.high_price,
            s.low_price,
            s.close_price,
            s.volume,
            s.daily_return
        FROM silver_stock_prices s
        JOIN gold_dim_company c ON s.ticker = c.ticker;
    """)
    print("  Created: gold_fact_stock_performance")

    conn.close()
    print("Gold Layer built successfully!")

if __name__ == '__main__':
    build_gold_layer()