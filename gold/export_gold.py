import os
import duckdb

DB_PATH = 'data/financial_market.duckdb'
EXPORT_DIR = 'data/gold_exports'

def export_gold_tables():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = duckdb.connect(DB_PATH)
    
    tables = [
        'gold_dim_company',
        'gold_dim_date',
        'gold_dim_uk_economy',
        'gold_fact_stock_performance'
    ]
    
    print("Exporting Gold tables to Parquet...")
    for table in tables:
        output_path = os.path.join(EXPORT_DIR, f"{table}.parquet")
        conn.execute(f"COPY {table} TO '{output_path}' (FORMAT PARQUET);")
        print(f"  Exported: {output_path}")
        
    conn.close()
    print("All Gold tables successfully exported!")

if __name__ == '__main__':
    export_gold_tables()