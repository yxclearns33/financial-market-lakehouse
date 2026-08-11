import streamlit as st
import duckdb
import plotly.express as px

st.set_page_config(page_title="Financial Market Lakehouse", layout="wide")
st.title("📈 Financial Market Lakehouse Dashboard")

@st.cache_data
def load_data():
    conn = duckdb.connect()
    
    # Query your Gold Fact table (and optionally join dimensions)
    query = """
        SELECT * 
        FROM 'data/gold_exports/gold_fact_stock_performance.parquet'
    """
    return conn.execute(query).df()

try:
    df = load_data()
    
    st.success("Gold Layer Fact Table Loaded Successfully!")
    
    # Display KPI Cards
    col1, col2 = st.columns(2)
    col1.metric("Total Fact Records", f"{len(df):,}")
    col2.metric("Pipeline Health", "Active 🟢")
    
    # Interactive Data Table / Visuals
    st.subheader("📊 Stock Performance Data (Gold Layer)")
    st.dataframe(df.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Error loading Parquet files: {e}")
    st.info("Check if `data/gold_exports/` files are committed and pushed to GitHub!")