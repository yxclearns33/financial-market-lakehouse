import duckdb

DB_PATH = 'data/financial_market.duckdb'

def validate():
    conn = duckdb.connect(DB_PATH)
    
    print("\n--- 1. TABLE ROW COUNTS ---")
    counts_sql = """
    SELECT 'gold_dim_company' AS table_name, COUNT(*) AS row_count FROM gold_dim_company
    UNION ALL
    SELECT 'gold_dim_date', COUNT(*) FROM gold_dim_date
    UNION ALL
    SELECT 'gold_dim_uk_economy', COUNT(*) FROM gold_dim_uk_economy
    UNION ALL
    SELECT 'gold_fact_stock_performance', COUNT(*) FROM gold_fact_stock_performance;
    """
    print(conn.execute(counts_sql).fetchdf())

    print("\n--- 2. STAR SCHEMA JOIN SAMPLE ---")
    join_sql = """
    SELECT 
        f.date_key,
        d.full_date,
        c.ticker,
        c.company_name,
        f.close_price,
        f.daily_return
    FROM gold_fact_stock_performance f
    JOIN gold_dim_company c ON f.company_key = c.company_key
    JOIN gold_dim_date d ON f.date_key = d.date_key
    LIMIT 5;
    """
    print(conn.execute(join_sql).fetchdf())
    
    conn.close()

if __name__ == '__main__':
    validate()