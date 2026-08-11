import streamlit as st
import duckdb

st.set_page_config(page_title="Financial Market Lakehouse", layout="wide")
st.title("📈 Financial Market Lakehouse Dashboard")

@st.cache_data
def load_data():
    conn = duckdb.connect()
    # Updated to point to your exact gold_exports folder path
    return conn.execute("SELECT * FROM 'data/gold_exports/*.parquet'").df()

try:
    df = load_data()
    st.success("Gold layer data loaded successfully!")
    st.dataframe(df)
except Exception as e:
    st.error(f"Error loading Parquet files: {e}")