import streamlit as st
import duckdb
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION (Power BI Style Layout) ---
st.set_page_config(
    page_title="Executive Financial Command Center",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR POWER BI CARDS & INSIGHTS ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #1E222D;
        border-radius: 8px;
        padding: 15px;
        border-left: 5px solid #2962FF;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .insight-box {
        background-color: #131722;
        border: 1px solid #2A2E39;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Dashboard Title Banner
st.title("📊 Executive Financial Command Center")
st.caption("Gold Layer Business Intelligence | Medallion Lakehouse Architecture")
st.markdown("---")

# --- DATA LOADING FUNCTION (STABLE STAR SCHEMA JOIN) ---
@st.cache_data
def load_gold_star_schema():
    conn = duckdb.connect()
    
    # SQL Join between Fact Stock Performance and Company Dimension
    query = """
        SELECT 
            f.date_key,
            CAST(f.date_key AS VARCHAR) as date_str,
            COALESCE(c.ticker, 'TICKER') as ticker,
            COALESCE(c.company_name, 'Unknown Asset') as company_name,
            COALESCE(c.sector, 'Financials') as sector,
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
    
    # Format dates
    df['date'] = pd.to_datetime(df['date_str'], format='%Y%m%d', errors='coerce')
    
    # Calculate Gold Quantitative Metrics
    df['rolling_volatility'] = df.groupby('ticker')['daily_return'].transform(
        lambda x: x.rolling(30).std() * np.sqrt(252) * 100
    )
    df['dollar_volume'] = df['close_price'] * df['volume']
    
    return df

try:
    df = load_gold_star_schema()

    # --- SIDEBAR POWER BI SLICERS ---
    st.sidebar.header("🎛️ Report Slicers")
    
    # 1. Sector Slicer
    sectors = ["All"] + sorted(list(df['sector'].dropna().unique()))
    selected_sector = st.sidebar.selectbox("Sector Filter", sectors)
    
    filtered_df = df[df['sector'] == selected_sector] if selected_sector != "All" else df.copy()

    # 2. Asset / Ticker Slicer
    tickers = ["All"] + sorted(list(filtered_df['ticker'].dropna().unique()))
    selected_ticker = st.sidebar.selectbox("Asset / Ticker Slicer", tickers)
    
    if selected_ticker != "All":
        filtered_df = filtered_df[filtered_df['ticker'] == selected_ticker]

    # --- TOP KPI CARDS HEADER ---
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    
    avg_close = filtered_df['close_price'].mean()
    total_vol = filtered_df['volume'].sum()
    avg_volatility = filtered_df['rolling_volatility'].mean()
    max_return = filtered_df['daily_return'].max() * 100
    min_return = filtered_df['daily_return'].min() * 100

    kpi1.metric("Avg Close Price", f"${avg_close:.2f}" if not np.isnan(avg_close) else "N/A")
    kpi2.metric("Total Volume", f"{total_vol/1e6:.1f}M")
    kpi3.metric("Avg 30D Volatility", f"{avg_volatility:.2f}%" if not np.isnan(avg_volatility) else "0.00%")
    kpi4.metric("Max Daily Gain", f"+{max_return:.2f}%" if not np.isnan(max_return) else "0.00%")
    kpi5.metric("Max Daily Loss", f"{min_return:.2f}%" if not np.isnan(min_return) else "0.00%")

    st.markdown("---")

    # --- ROW 1: CLICKABLE BAR CHART & TIME SERIES TREND ---
    col_chart1, col_chart2 = st.columns([1, 2])

    with col_chart1:
        st.subheader("1️⃣ Select Asset (Click Bar)")
        st.caption("Click any bar to dynamically filter the rest of the report.")
        
        # Aggregation for horizontal bar chart
        ticker_summary = filtered_df.groupby('ticker', as_index=False).agg({
            'dollar_volume': 'sum',
            'daily_return': 'mean'
        }).sort_values('dollar_volume', ascending=False)

        bar_fig = px.bar(
            ticker_summary, 
            x='dollar_volume', 
            y='ticker', 
            orientation='h',
            title="Total Dollar Liquidity ($)",
            color='daily_return',
            color_continuous_scale="RdYlGn",
            template="plotly_dark"
        )
        bar_fig.update_layout(height=380, margin=dict(l=10, r=10, t=40, b=10))
        
        # Power BI Click-to-Filter behavior
        selected_bar = st.plotly_chart(bar_fig, use_container_width=True, on_select="rerun")
        
        clicked_ticker = None
        if selected_bar and "selection" in selected_bar and selected_bar["selection"]["points"]:
            clicked_ticker = selected_bar["selection"]["points"][0]["y"]
            st.success(f"Filtered for: **{clicked_ticker}**")

    # Filter data based on bar click selection
    active_df = filtered_df[filtered_df['ticker'] == clicked_ticker] if clicked_ticker else filtered_df

    with col_chart2:
        st.subheader("2️⃣ Price Performance & Volatility Trend")
        
        line_fig = go.Figure()
        line_fig.add_trace(go.Scatter(
            x=active_df['date'], y=active_df['close_price'],
            name="Close Price ($)", line=dict(color='#2962FF', width=2)
        ))
        
        line_fig.add_trace(go.Scatter(
            x=active_df['date'], y=active_df['rolling_volatility'],
            name="Volatility (%)", yaxis="y2", line=dict(color='#FF6D00', dash='dot')
        ))

        line_fig.update_layout(
            template="plotly_dark",
            height=380,
            margin=dict(l=10, r=10, t=40, b=10),
            yaxis=dict(title="Close Price ($)"),
            yaxis2=dict(title="Volatility (%)", overlaying="y", side="right"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(line_fig, use_container_width=True)

    # --- ROW 2: AUTOMATED INSIGHTS & MATRIX ---
    st.markdown("---")
    col_insight, col_matrix = st.columns([1, 1.5])

    with col_insight:
        st.subheader("💡 Automated Gold Insights")
        
        high_vol_asset = active_df.loc[active_df['rolling_volatility'].idxmax()] if not active_df.empty and active_df['rolling_volatility'].notna().any() else None
        best_day = active_df.loc[active_df['daily_return'].idxmax()] if not active_df.empty and active_df['daily_return'].notna().any() else None

        st.markdown(f"""
        <div class="insight-box">
            <h4>📌 Executive Callouts</h4>
            <ul>
                <li><b>Dataset Scope:</b> Analyzing <code>{len(active_df):,}</code> Gold Star Schema records.</li>
                <li><b>Highest Risk Period:</b> Peak 30-day volatility reached <b>{high_vol_asset['rolling_volatility']:.2f}%</b> on <i>{high_vol_asset['date'].strftime('%Y-%m-%d') if high_vol_asset is not None else 'N/A'}</i>.</li>
                <li><b>Max Gain Spike:</b> Single-day gain peak of <b>+{best_day['daily_return']*100:.2f}%</b> observed for <b>{best_day['ticker'] if best_day is not None else 'N/A'}</b>.</li>
                <li><b>Engine:</b> DuckDB in-memory OLAP SQL over Gold Parquet storage.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    with col_matrix:
        st.subheader("📋 Star Schema Data Matrix")
        
        display_cols = ['date_str', 'ticker', 'company_name', 'close_price', 'volume', 'daily_return', 'rolling_volatility']
        st.dataframe(
            active_df[display_cols].sort_values('date_str', ascending=False),
            column_config={
                "date_str": "Date Key",
                "close_price": st.column_config.NumberColumn("Close ($)", format="$%.2f"),
                "volume": st.column_config.NumberColumn("Volume", format="%d"),
                "daily_return": st.column_config.NumberColumn("Daily Return", format="%.4f"),
                "rolling_volatility": st.column_config.NumberColumn("Volatility (%)", format="%.2f%%"),
            },
            use_container_width=True,
            height=250
        )

    # --- SAFE SCHEMA INSPECTION FOR UK ECONOMY ---
    with st.expander("🔍 Inspect UK Economy Parquet File Schema (Diagnostics)"):
        try:
            uk_df = duckdb.connect().execute("SELECT * FROM 'data/gold_exports/gold_dim_uk_economy.parquet' LIMIT 5").df()
            st.write("Columns inside `gold_dim_uk_economy.parquet`:", list(uk_df.columns))
            st.dataframe(uk_df)
        except Exception as e:
            st.info(f"Notice inspecting UK economy file: {e}")

except Exception as e:
    st.error(f"Error rendering Command Center: {e}")