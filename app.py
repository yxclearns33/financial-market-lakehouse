import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Executive Financial Command Center", layout="wide", initial_sidebar_state="expanded")

st.title("📊 Executive Financial Command Center")
st.caption("Gold Layer Business Intelligence | Medallion Lakehouse Architecture")
st.markdown("---")

@st.cache_data
def load_gold_star_schema():
    conn = duckdb.connect()
    query = """
        SELECT 
            f.date_key,
            CAST(f.date_key AS VARCHAR) as date_str,
            COALESCE(c.ticker, 'TICKER') as ticker,
            COALESCE(c.company_name, 'Unknown Asset') as company_name,
            COALESCE(c.sector, 'Technology') as sector,
            f.open_price,
            f.high_price,
            f.low_price,
            f.close_price,
            f.volume,
            f.daily_return
        FROM 'data/gold_exports/gold_fact_stock_performance.parquet' f
        LEFT JOIN 'data/gold_exports/gold_dim_company.parquet' c
            ON f.company_key = c.company_key
    """
    df = conn.execute(query).df()
    df['date'] = pd.to_datetime(df['date_str'], format='%Y%m%d', errors='coerce')
    df['rolling_volatility'] = df.groupby('ticker')['daily_return'].transform(lambda x: x.rolling(30).std() * np.sqrt(252) * 100)
    df['dollar_volume'] = df['close_price'] * df['volume']
    return df

try:
    df = load_gold_star_schema()

    # Sidebar Slicers
    st.sidebar.header("🎛️ Report Slicers")
    sectors = ["All"] + sorted(list(df['sector'].dropna().unique()))
    selected_sector = st.sidebar.selectbox("Sector Filter", sectors)
    filtered_df = df[df['sector'] == selected_sector] if selected_sector != "All" else df.copy()

    tickers = ["All"] + sorted(list(filtered_df['ticker'].dropna().unique()))
    selected_ticker = st.sidebar.selectbox("Asset / Ticker Slicer", tickers)
    if selected_ticker != "All":
        filtered_df = filtered_df[filtered_df['ticker'] == selected_ticker]

    # KPI Header
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Avg Close Price", f"${filtered_df['close_price'].mean():.2f}")
    kpi2.metric("Total Volume", f"{filtered_df['volume'].sum()/1e6:.1f}M")
    kpi3.metric("Avg 30D Volatility", f"{filtered_df['rolling_volatility'].mean():.2f}%")
    kpi4.metric("Max Daily Gain", f"+{filtered_df['daily_return'].max()*100:.2f}%")
    kpi5.metric("Max Daily Loss", f"{filtered_df['daily_return'].min()*100:.2f}%")

    st.markdown("---")
    
    # Clickable Bar Chart & Trend
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("1️⃣ Select Asset (Click Bar)")
        ticker_summary = filtered_df.groupby('ticker', as_index=False).agg({'dollar_volume': 'sum', 'daily_return': 'mean'}).sort_values('dollar_volume', ascending=False)
        bar_fig = px.bar(ticker_summary, x='dollar_volume', y='ticker', orientation='h', title="Total Dollar Liquidity ($)", color='daily_return', color_continuous_scale="RdYlGn", template="plotly_dark")
        bar_fig.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10))
        
        selected_bar = st.plotly_chart(bar_fig, use_container_width=True, on_select="rerun")
        clicked_ticker = selected_bar["selection"]["points"][0]["y"] if selected_bar and "selection" in selected_bar and selected_bar["selection"]["points"] else None
        if clicked_ticker:
            st.success(f"Filtered for: **{clicked_ticker}**")

    active_df = filtered_df[filtered_df['ticker'] == clicked_ticker] if clicked_ticker else filtered_df

    with col2:
        st.subheader("2️⃣ Price Performance & Volatility Trend")
        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(x=active_df['date'], y=active_df['close_price'], name="Close Price ($)", line=dict(color='#2962FF', width=2)))
        line_fig.add_trace(go.Scatter(x=active_df['date'], y=active_df['rolling_volatility'], name="Volatility (%)", yaxis="y2", line=dict(color='#FF6D00', dash='dot')))
        line_fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=40, b=10), yaxis=dict(title="Close Price ($)"), yaxis2=dict(title="Volatility (%)", overlaying="y", side="right"))
        st.plotly_chart(line_fig, use_container_width=True)

    # Data Table Matrix
    st.markdown("---")
    st.subheader("📋 Star Schema Data Matrix")
    st.dataframe(active_df[['date_str', 'ticker', 'company_name', 'close_price', 'volume', 'daily_return', 'rolling_volatility']].sort_values('date_str', ascending=False), use_container_width=True, height=250)

except Exception as e:
    st.error(f"Error: {e}")