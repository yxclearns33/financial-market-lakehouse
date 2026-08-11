import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Quant & Macro Financial Lakehouse", layout="wide")

st.title("🏛️ Financial Market Lakehouse: Quantitative & Macro Analytics")
st.caption("Gold Layer Business Intelligence | Multi-Asset & Macro Correlation Engine")
st.markdown("---")

@st.cache_data
def load_gold_lakehouse():
    conn = duckdb.connect()
    
    # Advanced Star Schema SQL Join across Fact and ALL Dimension tables
    query = """
        SELECT 
            f.date_key,
            CAST(f.date_key AS VARCHAR) as date_str,
            COALESCE(c.ticker, 'UNKNOWN') as ticker,
            COALESCE(c.company_name, 'Unknown Company') as company_name,
            COALESCE(c.sector, 'General') as sector,
            f.open_price,
            f.high_price,
            f.low_price,
            f.close_price,
            f.volume,
            f.daily_return,
            e.gdp_growth,
            e.inflation_rate,
            e.interest_rate
        FROM 'data/gold_exports/gold_fact_stock_performance.parquet' f
        LEFT JOIN 'data/gold_exports/gold_dim_company.parquet' c
            ON f.company_key = c.company_key
        LEFT JOIN 'data/gold_exports/gold_dim_uk_economy.parquet' e
            ON f.date_key = e.date_key
    """
    df = conn.execute(query).df()
    df['date'] = pd.to_datetime(df['date_str'], format='%Y%m%d', errors='coerce')
    return df.sort_values('date')

try:
    df = load_gold_lakehouse()

    # --- SIDEBAR CONTROLS ---
    st.sidebar.header("🕹️ Quant Controls")
    available_tickers = sorted(df['ticker'].unique())
    selected_ticker = st.sidebar.selectbox("Select Asset to Analyze", available_tickers)

    # Filter for selected asset
    asset_df = df[df['ticker'] == selected_ticker].copy()

    # --- ADVANCED GOLD METRIC CALCULATIONS ---
    # 1. Moving Averages
    asset_df['SMA_20'] = asset_df['close_price'].rolling(window=20).mean()
    asset_df['SMA_50'] = asset_df['close_price'].rolling(window=50).mean()

    # 2. 30-Day Rolling Annualized Volatility (Std Dev of Daily Returns * sqrt(252 trading days))
    asset_df['rolling_volatility_30d'] = asset_df['daily_return'].rolling(window=30).std() * np.sqrt(252) * 100

    # 3. Cumulative Growth (Growth of $1 invested)
    asset_df['cum_return'] = (1 + asset_df['daily_return'].fillna(0)).cumprod() - 1

    # --- TOP EXECUTIVE SUMMARY KPIs ---
    latest = asset_df.iloc[-1] if not asset_df.empty else None
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Selected Ticker", selected_ticker)
    col2.metric("Latest Close", f"${latest['close_price']:.2f}" if latest is not None else "N/A")
    col3.metric("Total Return", f"{latest['cum_return']*100:.2f}%" if latest is not None else "N/A")
    
    vol_val = latest['rolling_volatility_30d'] if latest is not None and not np.isnan(latest['rolling_volatility_30d']) else 0
    col4.metric("30-Day Ann. Volatility", f"{vol_val:.2f}%")

    st.markdown("---")

    # --- TAB NAVIGATION FOR INSIGHTS ---
    tab1, tab2, tab3 = st.tabs(["📈 Technical & Momentum Signals", "⚡ Volatility & Risk Analysis", "🇬🇧 Macro Economy Correlation"])

    # TAB 1: Moving Average Crossovers (Golden/Death Cross)
    with tab1:
        st.subheader("Technical Alpha: 20-Day vs 50-Day SMA Trend Detection")
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=asset_df['date'], y=asset_df['close_price'], name='Close Price', line=dict(color='gray', width=1)))
        fig1.add_trace(go.Scatter(x=asset_df['date'], y=asset_df['SMA_20'], name='20-Day SMA (Short Term)', line=dict(color='cyan', width=2)))
        fig1.add_trace(go.Scatter(x=asset_df['date'], y=asset_df['SMA_50'], name='50-Day SMA (Long Term)', line=dict(color='orange', width=2)))
        fig1.update_layout(template="plotly_dark", height=450, xaxis_title="Date", yaxis_title="Price ($)")
        st.plotly_chart(fig1, use_container_width=True)

    # TAB 2: Rolling Volatility & Risk Profiles
    with tab2:
        st.subheader("Risk Analytics: 30-Day Rolling Volatility (%)")
        fig2 = px.area(
            asset_df, 
            x='date', 
            y='rolling_volatility_30d', 
            title=f"{selected_ticker} Risk Regime over Time",
            labels={'rolling_volatility_30d': 'Annualized Volatility (%)'},
            template="plotly_dark",
            color_discrete_sequence=['#FF4B4B']
        )
        st.plotly_chart(fig2, use_container_width=True)

    # TAB 3: Stock Returns vs UK Macro Economy
    with tab3:
        st.subheader("Cross-Asset Insights: Stock Returns vs Macro Indicators")
        if 'inflation_rate' in asset_df.columns and asset_df['inflation_rate'].notna().sum() > 0:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x=asset_df['date'], y=asset_df['cum_return']*100, name=f'{selected_ticker} Cum. Return (%)', yaxis='y1', line=dict(color='green')))
            fig3.add_trace(go.Scatter(x=asset_df['date'], y=asset_df['inflation_rate'], name='UK Inflation Rate (%)', yaxis='y2', line=dict(color='red', dash='dot')))
            
            fig3.update_layout(
                template="plotly_dark",
                height=450,
                yaxis=dict(title=f"{selected_ticker} Return (%)"),
                yaxis2=dict(title="UK Inflation Rate (%)", overlaying='y', side='right')
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Macroeconomic features (UK Inflation/Interest Rates) are integrated in the query. Populate `gold_dim_uk_economy.parquet` to display cross-asset correlation trends.")

    # Schema Audit
    with st.expander("🔍 SQL Star Schema Query Execution Output"):
        st.dataframe(asset_df.tail(50), use_container_width=True)

except Exception as e:
    st.error(f"Error building Gold quant metrics: {e}")