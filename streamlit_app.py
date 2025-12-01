# streamlit_app.py - Portfolio Architect Web Application
"""
Portfolio Analysis Application - Streamlit Web Version
Built by Tom Campacci - Financial Student

Deploy on Streamlit Cloud: https://streamlit.io/cloud
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

# Import modules personnalisés
from app.config import (
    CHART_COLORS, CHART_DESCRIPTIONS, POPULAR_TICKERS, 
    QUICK_SELECT_OPTIONS, MARKET_DATA_REFRESH_INTERVAL
)
from app.data_fetcher import (
    validate_and_get_ticker_info as validate_ticker_new,
    search_tickers as search_tickers_new,
    fetch_historical_prices as fetch_prices_new,
    get_current_price,
    fetch_market_data
)
from app.calculations import (
    compute_portfolio_metrics,
    mc_gaussian_with_randomness,
    calculate_sharpe_ratio,
    calculate_var,
    calculate_expected_shortfall,
    calculate_max_drawdown,
    calculate_calmar_ratio
)
from app.charts import get_chart_function, CHART_FUNCTIONS

# ===================== PAGE CONFIGURATION =====================
st.set_page_config(
    page_title="Portfolio Architect",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===================== CHART DEFINITIONS (24 Charts) =====================
CHART_GROUPS = {
    "📊 Portfolio & Sector": [1, 2, 3, 4, 5, 6],
    "🎲 Monte Carlo": [7, 8, 9, 10, 11, 12],
    "⚠️ Risk Metrics": [13, 14, 15, 16, 17],
    "📈 Benchmarks": [18, 19, 20, 21],
    "🔄 Sector & Regime": [22, 23, 24],
}

CHART_NAMES = {
    1: "Allocation", 2: "Correlation", 3: "Risk Contrib",
    4: "vs Benchmarks", 5: "Sector Decomp", 6: "Sector Risk",
    7: "MC Normal", 8: "MC Random", 9: "Vol Normal",
    10: "Vol Random", 11: "DD Normal", 12: "DD Random",
    13: "VaR 95%", 14: "ES (CVaR)", 15: "DD Duration", 16: "Calmar",
    17: "Sharpe Ratio", 18: "Risk vs Idx", 19: "Fwd Excess", 
    20: "Port vs B. (N)", 21: "Port vs B. (R)", 22: "Sector Perf", 
    23: "Regime", 24: "Rotation"
}

CHART_DESCRIPTIONS = {
    1: "Pie chart showing the weight distribution of each asset in your portfolio. Visualize how your capital is allocated across different positions.", 
    2: "Heatmap displaying correlation coefficients between all portfolio assets. Identify diversification opportunities and risk concentrations.", 
    3: "Bar chart showing each asset's contribution to total portfolio volatility. Understand which positions drive your portfolio risk.",
    4: "Line chart comparing your portfolio's cumulative performance against selected benchmark indices over time.", 
    5: "Breakdown of portfolio allocation by market sectors (Technology, Healthcare, Finance, etc.). See your sector exposure.", 
    6: "Risk analysis by sector showing volatility contribution and concentration risk across different market segments.",
    7: "Monte Carlo simulation projecting 1000+ possible portfolio paths using normal distribution assumptions. See potential outcomes.", 
    8: "Monte Carlo simulation with random walk model. More realistic scenario modeling with market randomness.", 
    9: "Volatility cone projection showing expected volatility ranges over the next 12 months using normal distribution.",
    10: "Volatility forecast using random scenarios. Stress-test your portfolio under various market conditions.", 
    11: "Drawdown simulation showing potential maximum loss paths under normal market conditions.", 
    12: "Drawdown paths with random market shocks. See worst-case scenarios for your portfolio.",
    13: "Value at Risk (VaR) at 95% confidence - the maximum expected loss in 95% of cases over a given period.", 
    14: "Expected Shortfall (CVaR) - average loss when losses exceed VaR. Critical for tail risk assessment.", 
    15: "Historical analysis of drawdown durations. How long does it typically take to recover from losses?", 
    16: "Calmar Ratio = Annual Return / Max Drawdown. Measures return per unit of downside risk.",
    17: "Sharpe Ratio = (Return - Risk Free Rate) / Volatility. The gold standard of risk-adjusted performance.",
    18: "Scatter plot comparing your portfolio's risk-return profile against major market indices.", 
    19: "Forward-looking analysis of expected excess returns vs benchmarks based on current metrics.", 
    20: "Portfolio vs Benchmark projection under normal market scenario. Expected relative performance.",
    21: "Portfolio vs Benchmark under random market scenarios. Stress-test relative performance.", 
    22: "Individual sector performance analysis - returns, volatility, and trends for each sector in your portfolio.", 
    23: "Market regime detection using volatility clustering. Identify bull/bear/sideways market phases.",
    24: "Sector rotation analysis showing momentum shifts between sectors. Identify trending sectors."
}

# ===================== CUSTOM CSS =====================
st.markdown("""
<style>
    /* Main Theme */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(90deg, #e94560 0%, #ff6b6b 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(233, 69, 96, 0.3);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.5rem 0 0 0;
        font-size: 1rem;
    }
    
    /* Section Headers */
    .section-header {
        color: #e94560;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(233, 69, 96, 0.3);
    }
    
    /* Chart category header */
    .chart-category {
        background: rgba(233, 69, 96, 0.15);
        border-left: 4px solid #e94560;
        padding: 0.5rem 1rem;
        margin: 1rem 0 0.5rem 0;
        border-radius: 0 8px 8px 0;
        font-weight: 600;
        color: white;
    }
    
    /* Suggestion buttons */
    .suggestion-btn {
        background: rgba(55, 66, 250, 0.2);
        border: 1px solid #3742fa;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .suggestion-btn:hover {
        background: rgba(55, 66, 250, 0.4);
        transform: translateY(-2px);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #e94560 0%, #ff6b6b 100%);
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ===================== POPULAR TICKERS DATABASE =====================
# POPULAR_TICKERS maintenant importé depuis app.config

# ===================== SESSION STATE INITIALIZATION =====================
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

if 'selected_charts' not in st.session_state:
    st.session_state.selected_charts = list(range(1, 25))  # All selected by default

# ===================== HELPER FUNCTIONS =====================

@st.cache_data(ttl=300)
def fetch_market_data():
    """Fetch current market data for display"""
    data = {'forex': {}, 'indexes': {}, 'commodities': {}}
    
    forex_pairs = {'EUR/USD': 'EURUSD=X', 'GBP/USD': 'GBPUSD=X', 'USD/JPY': 'JPY=X', 'USD/CHF': 'CHF=X'}
    for name, symbol in forex_pairs.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
                change_pct = ((current - prev) / prev) * 100
                data['forex'][name] = {'price': current, 'change': change_pct}
        except:
            pass
    
    indexes = {'S&P 500': '^GSPC', 'Nasdaq': '^IXIC', 'Dow Jones': '^DJI', 'DAX': '^GDAXI', 'CAC 40': '^FCHI', 'FTSE 100': '^FTSE'}
    for name, symbol in indexes.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
                change_pct = ((current - prev) / prev) * 100
                data['indexes'][name] = {'price': current, 'change': change_pct}
        except:
            pass
    
    commodities = {'Gold': 'GC=F', 'Silver': 'SI=F', 'Oil (WTI)': 'CL=F'}
    for name, symbol in commodities.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                prev = hist['Close'].iloc[-2] if len(hist) >= 2 else current
                change_pct = ((current - prev) / prev) * 100
                data['commodities'][name] = {'price': current, 'change': change_pct}
        except:
            pass
    
    return data

# ===================== WRAPPERS FOR COMPATIBILITY =====================
# Ces fonctions appellent les nouvelles fonctions de app.data_fetcher

def search_tickers(query):
    """Wrapper for search_tickers_new"""
    return search_tickers_new(query)

def validate_and_get_ticker_info(symbol):
    """Wrapper for validate_ticker_new"""
    return validate_ticker_new(symbol)

def fetch_historical_prices(tickers, years="max"):
    """Wrapper for fetch_prices_new with years conversion"""
    if years == "max":
        period = "max"
    else:
        period = f"{years}y"
    return fetch_prices_new(tickers, period=period)

# ===================== LIVE PREVIEW CHART (for Portfolio Setup tab) =====================

def create_preview_allocation_chart(portfolio_data, capital):
    """Create compact live preview allocation chart"""
    if not portfolio_data:
        return None
    
    labels = [p['ticker'] for p in portfolio_data]
    weights = [p['weight'] for p in portfolio_data]
    values = [capital * p['weight'] / 100 for p in portfolio_data]
    
    colors = ['#e94560', '#00d26a', '#3742fa', '#ffa502', '#ff6b6b', 
              '#1e90ff', '#9b59b6', '#2ecc71', '#e74c3c', '#f39c12']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=weights,
        hole=0.5,
        marker=dict(colors=colors[:len(labels)]),
        textinfo='label+percent',
        textposition='outside',
        textfont=dict(size=10, color='white'),
        pull=[0.02] * len(labels)
    )])
    
    total_value = sum(values)
    
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=10),
        showlegend=False,
        height=250,
        margin=dict(t=10, b=10, l=10, r=10),
        annotations=[dict(
            text=f"<b>${total_value:,.0f}</b>",
            x=0.5, y=0.5,
            font=dict(size=14, color='white'),
            showarrow=False
        )]
    )
    
    return fig

# Anciennes fonctions supprimées - Maintenant dans app/charts.py

# ===================== MAIN APPLICATION =====================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Portfolio Architect</h1>
        <p>Advanced Portfolio Analysis & Monte Carlo Simulation | Built by Tom Campacci</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Paramètres d'analyse fixés
    years = "max"  # Toujours le maximum de données disponibles
    mc_simulations = 100000  # 100K simulations pour précision
    mc_display_paths = 5000  # Nombre de paths à afficher (esthétique)
    
    # Configuration du portfolio - À saisir avant les tabs
    st.markdown('<h2 class="section-header">⚙️ Portfolio Configuration</h2>', unsafe_allow_html=True)
    
    config_col1, config_col2 = st.columns(2)
    with config_col1:
        capital = st.number_input(
            "💰 Initial Capital", 
            min_value=100.0, 
            value=10000.0, 
            step=1000.0,
            format="%.0f",
            help="Total capital to invest"
        )
    with config_col2:
        currency = st.selectbox(
            "💱 Currency", 
            options=["USD", "EUR", "GBP", "CHF", "JPY"],
            index=0,
            help="Portfolio currency"
        )
    
    st.divider()
    
    # Main Content - Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Market Overview", "💼 Portfolio Setup", "📈 Chart Selection", "📉 Analysis Results"])
    
    # ==================== TAB 1: MARKET OVERVIEW ====================
    with tab1:
        # Header avec bouton refresh et toggle auto-refresh
        header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
        with header_col1:
            st.markdown('<h2 class="section-header">💱 Live Market Data</h2>', unsafe_allow_html=True)
        with header_col2:
            auto_refresh_enabled = st.checkbox("🔄 Auto-refresh (5s)", value=True, key="auto_refresh_market")
        with header_col3:
            if st.button("⚡ Refresh Now", use_container_width=True):
                st.cache_data.clear()
                st.rerun()
        
        # Afficher l'heure de dernière mise à jour
        current_time = datetime.now().strftime("%H:%M:%S")
        if auto_refresh_enabled:
            st.caption(f"🟢 Live Mode | Last updated: {current_time} | Auto-refresh every {MARKET_DATA_REFRESH_INTERVAL}s")
        else:
            st.caption(f"⚪ Manual Mode | Last updated: {current_time}")
        
        with st.spinner("Fetching market data..."):
            market_data = fetch_market_data()
        
        st.divider()
        
        st.subheader("📊 Major Indexes")
        if market_data.get('indexes'):
            cols = st.columns(3)
            for i, (name, data) in enumerate(market_data.get('indexes', {}).items()):
                with cols[i % 3]:
                    st.metric(label=name, value=f"{data['price']:,.2f}", delta=f"{data['change']:+.2f}%")
        else:
            st.warning("No index data available at the moment.")
        
        st.divider()
        
        st.subheader("💱 Forex Rates")
        if market_data.get('forex'):
            cols = st.columns(4)
            for i, (name, data) in enumerate(market_data.get('forex', {}).items()):
                with cols[i % 4]:
                    st.metric(label=name, value=f"{data['price']:.4f}", delta=f"{data['change']:+.2f}%")
        else:
            st.warning("No forex data available at the moment.")
        
        st.divider()
        
        st.subheader("🏆 Commodities")
        if market_data.get('commodities'):
            cols = st.columns(3)
            for i, (name, data) in enumerate(market_data.get('commodities', {}).items()):
                with cols[i % 3]:
                    st.metric(label=name, value=f"${data['price']:,.2f}", delta=f"{data['change']:+.2f}%")
        else:
            st.warning("No commodity data available at the moment.")
        
        # Auto-refresh mechanism
        if auto_refresh_enabled:
            import time
            time.sleep(MARKET_DATA_REFRESH_INTERVAL)
            st.rerun()
    
    # ==================== TAB 2: PORTFOLIO SETUP ====================
    with tab2:
        col_input, col_preview = st.columns([1.2, 1])
        
        with col_input:
            st.markdown('<h2 class="section-header">💼 Portfolio Positions</h2>', unsafe_allow_html=True)
            st.info("Enter ticker symbols (e.g., AAPL, NVDA, MC.PA) and their weights.")
            
            # Utiliser les options depuis app.config
            popular_options = QUICK_SELECT_OPTIONS
            
            portfolio_data = []
            
            # Column headers
            header_col1, header_col2, header_col3, header_col4 = st.columns([3, 1, 1, 2])
            with header_col1:
                st.markdown("**Asset**")
            with header_col2:
                st.markdown("**Type**")
            with header_col3:
                st.markdown("**Value**")
            with header_col4:
                st.markdown("**Status**")
            
            st.markdown("---")
            
            for i in range(10):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 2])
                
                with col1:
                    # Build selectbox options
                    selectbox_options = [f"{t[0]} - {t[1]}" if t[0] else t[1] for t in popular_options]
                    selectbox_options.append("🔍 Search for another ticker...")
                    
                    # Single selectbox
                    selected_option = st.selectbox(
                        f"Asset {i+1}",
                        options=selectbox_options,
                        key=f"asset_{i}",
                        label_visibility="collapsed",
                        help="Select from popular list or search"
                    )
                    
                    # Check if user wants custom search
                    if "🔍 Search" in selected_option:
                        # Show search input
                        search_query = st.text_input(
                            "Search ticker",
                            key=f"search_{i}",
                            placeholder="Type: LVMH, BNP, SAP...",
                            label_visibility="collapsed"
                        ).upper().strip()
                        
                        if search_query:
                            suggestions = search_tickers(search_query)
                            if suggestions:
                                suggestion_options = [
                                    f"{s['symbol']} - {s['name'][:35]} ({s['exchange']})" 
                                    for s in suggestions[:10]
                                ]
                                
                                selected_sug = st.selectbox(
                                    "Results",
                                    options=suggestion_options,
                                    key=f"sug_result_{i}",
                                    label_visibility="collapsed"
                                )
                                ticker = selected_sug.split(" - ")[0].strip() if selected_sug else ""
                            else:
                                st.warning("No results found")
                                ticker = ""
                        else:
                            ticker = ""
                    else:
                        # Extract ticker from popular selection
                        if selected_option and " - " in selected_option:
                            ticker = selected_option.split(" - ")[0].strip()
                        else:
                            ticker = ""
                
                with col2:
                    # Input type selector
                    input_type = st.selectbox(
                        f"Type {i+1}",
                        options=["Percent %", "Currency $", "Shares"],
                        key=f"input_type_{i}",
                        label_visibility="collapsed",
                        help="Select input type"
                    )
                
                with col3:
                    # Value input (adapts based on type)
                    if input_type == "Percent %":
                        value_input = st.number_input(
                            f"Value {i+1}",
                            min_value=0.0,
                            max_value=100.0,
                            value=0.0,
                            step=5.0,
                            key=f"value_{i}",
                            label_visibility="collapsed",
                            format="%.1f"
                        )
                        weight = value_input  # Direct percentage
                        
                    elif input_type == "Currency $":
                        value_input = st.number_input(
                            f"Value {i+1}",
                            min_value=0.0,
                            max_value=float(capital),
                            value=0.0,
                            step=100.0,
                            key=f"value_{i}",
                            label_visibility="collapsed",
                            format="%.0f"
                        )
                        # Calculate weight from currency amount
                        weight = (value_input / capital * 100) if capital > 0 else 0.0
                        
                    else:  # Shares
                        value_input = st.number_input(
                            f"Value {i+1}",
                            min_value=0.0,
                            max_value=100000.0,
                            value=0.0,
                            step=1.0,
                            key=f"value_{i}",
                            label_visibility="collapsed",
                            format="%.0f"
                        )
                        # Calculate weight from shares (need price)
                        if ticker and value_input > 0:
                            try:
                                ticker_obj = yf.Ticker(ticker)
                                current_price = ticker_obj.info.get('currentPrice') or ticker_obj.info.get('regularMarketPrice') or 0
                                if current_price > 0:
                                    amount = value_input * current_price
                                    weight = (amount / capital * 100) if capital > 0 else 0.0
                                else:
                                    weight = 0.0
                                    st.caption(f"⚠️ Price unavailable")
                            except:
                                weight = 0.0
                                st.caption(f"⚠️ Price error")
                        else:
                            weight = 0.0
                
                with col4:
                    # Validation status
                    if ticker:
                        ticker_info = validate_and_get_ticker_info(ticker)
                        if ticker_info and ticker_info.get('valid'):
                            name = ticker_info.get('name', '')[:18]
                            st.success(f"✓ {name}")
                            
                            # Show conversion info
                            if weight > 0:
                                amount = capital * weight / 100
                                st.caption(f"💰 ${amount:,.0f} ({weight:.1f}%)")
                            
                            # Add to portfolio data (even if weight = 0, for live preview)
                            portfolio_data.append({
                                'ticker': ticker,
                                'weight': weight,
                                'name': ticker_info.get('name', ticker),
                                'exchange': ticker_info.get('exchange', '')
                            })
                        else:
                            st.error("✗ Invalid ticker")
                    else:
                        st.caption("—")
                
                # Small spacer between rows
                if i < 9:  # Don't add after last row
                    st.markdown("<div style='margin-bottom: 4px;'></div>", unsafe_allow_html=True)
            
            st.divider()
            
            # Weight Summary
            total_weight = sum([p['weight'] for p in portfolio_data])
            if total_weight > 0:
                if abs(total_weight - 100) < 0.01:
                    st.success(f"✅ Total Weight: {total_weight:.2f}%")
                elif total_weight > 100:
                    st.error(f"⚠️ Total Weight: {total_weight:.2f}% (exceeds 100%)")
                else:
                    st.warning(f"⚠️ Total Weight: {total_weight:.2f}% (need {100-total_weight:.1f}% more)")
            else:
                st.info("Add tickers with weights to see your allocation.")
            
            st.divider()
            
            # Benchmarks
            st.markdown('<h2 class="section-header">📈 Benchmarks</h2>', unsafe_allow_html=True)
            
            benchmark_options = {
                '^GSPC': 'S&P 500', '^NDX': 'Nasdaq 100', '^DJI': 'Dow Jones',
                '^GDAXI': 'DAX', '^FCHI': 'CAC 40', '^STOXX50E': 'Euro Stoxx 50',
                '^FTSE': 'FTSE 100', '^N225': 'Nikkei 225', 'GC=F': 'Gold',
            }
            
            selected_benchmarks = st.multiselect(
                "Select Benchmarks",
                options=list(benchmark_options.keys()),
                default=['^GSPC', '^NDX'],
                format_func=lambda x: benchmark_options.get(x, x)
            )
        
        # ========== PREVIEW COLUMN ==========
        with col_preview:
            st.markdown('<h2 class="section-header">📊 Live Preview</h2>', unsafe_allow_html=True)
            
            if portfolio_data:
                # Filter only positions with weight > 0 for the chart
                weighted_portfolio = [p for p in portfolio_data if p['weight'] > 0]
                
                if weighted_portfolio:
                    # Show pie chart
                    fig_preview = create_preview_allocation_chart(weighted_portfolio, capital)
                    if fig_preview:
                        st.plotly_chart(fig_preview, use_container_width=True)
                else:
                    st.info("💡 Enter weights to see portfolio allocation")
                
                # Summary table - only show weighted positions
                if weighted_portfolio:
                    st.markdown("**Portfolio Composition**")
                    summary_df = pd.DataFrame([
                        {
                            'Ticker': p['ticker'],
                            'Name': p['name'][:25] + '...' if len(p['name']) > 25 else p['name'],
                            'Weight': f"{p['weight']:.1f}%",
                            'Value': f"${capital * p['weight'] / 100:,.0f}"
                        }
                        for p in weighted_portfolio
                    ])
                    st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # Metrics
                if weighted_portfolio:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Allocated", f"${capital * total_weight / 100:,.0f}")
                    with col2:
                        st.metric("Positions", f"{len(weighted_portfolio)}")
            else:
                st.info("👈 Add tickers with weights > 0 to see the live preview!")
                
                # Show example portfolio
                st.markdown("**Example Portfolio:**")
                example_data = [
                    {'ticker': 'AAPL', 'weight': 25, 'name': 'Apple Inc.', 'exchange': 'NASDAQ'},
                    {'ticker': 'NVDA', 'weight': 25, 'name': 'NVIDIA Corp.', 'exchange': 'NASDAQ'},
                    {'ticker': 'MSFT', 'weight': 20, 'name': 'Microsoft', 'exchange': 'NASDAQ'},
                    {'ticker': 'GOOGL', 'weight': 15, 'name': 'Alphabet', 'exchange': 'NASDAQ'},
                    {'ticker': 'AMZN', 'weight': 15, 'name': 'Amazon', 'exchange': 'NASDAQ'},
                ]
                fig_example = create_preview_allocation_chart(example_data, capital)
                if fig_example:
                    st.plotly_chart(fig_example, use_container_width=True)
                st.caption("This is an example. Enter your own tickers above!")
    
    # ==================== TAB 3: CHART SELECTION ====================
    with tab3:
        st.markdown('<h2 class="section-header">📈 Select Analysis Charts</h2>', unsafe_allow_html=True)
        st.info("Choose which charts you want to generate. Select categories or individual charts.")
        
        # Initialize all chart selection states if not exists
        for i in range(1, 25):
            if f'chart_{i}' not in st.session_state:
                st.session_state[f'chart_{i}'] = True  # Default: all selected
        
        # Quick select buttons
        st.markdown("**Quick Selection:**")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            if st.button("Select All", use_container_width=True, key="btn_all"):
                for i in range(1, 25):
                    st.session_state[f'chart_{i}'] = True
                st.rerun()
        with col2:
            if st.button("Clear All", use_container_width=True, key="btn_none"):
                for i in range(1, 25):
                    st.session_state[f'chart_{i}'] = False
                st.rerun()
        with col3:
            if st.button("Portfolio", use_container_width=True, key="btn_portfolio"):
                for i in range(1, 25):
                    st.session_state[f'chart_{i}'] = (i in [1, 2, 3, 4, 5, 6])
                st.rerun()
        with col4:
            if st.button("Monte Carlo", use_container_width=True, key="btn_mc"):
                for i in range(1, 25):
                    st.session_state[f'chart_{i}'] = (i in [7, 8, 9, 10, 11, 12])
                st.rerun()
        with col5:
            if st.button("Risk Metrics", use_container_width=True, key="btn_risk"):
                for i in range(1, 25):
                    st.session_state[f'chart_{i}'] = (i in [13, 14, 15, 16, 17])
                st.rerun()
        
        st.divider()
        
        # Chart selection by category
        selected_charts = []
        
        for category, chart_nums in CHART_GROUPS.items():
            st.markdown(f'<div class="chart-category">{category}</div>', unsafe_allow_html=True)
            
            cols = st.columns(2)
            for idx, chart_num in enumerate(chart_nums):
                with cols[idx % 2]:
                    chart_name = CHART_NAMES[chart_num]
                    chart_desc = CHART_DESCRIPTIONS[chart_num]
                    
                    # Checkbox - reads directly from session state key
                    is_selected = st.checkbox(
                        f"**{chart_num}. {chart_name}**",
                        key=f"chart_{chart_num}",
                        help=chart_desc
                    )
                    
                    # Show description
                    st.caption(chart_desc)
                    
                    if is_selected:
                        selected_charts.append(chart_num)
            
            st.markdown("")  # Spacing
        
        # Store for other tabs
        st.session_state.selected_charts = selected_charts
        
        st.divider()
        
        # Summary
        st.markdown(f"### 📊 Selected: **{len(selected_charts)}** / 24 charts")
        
        if selected_charts:
            selected_names = [f"{n}. {CHART_NAMES[n]}" for n in sorted(selected_charts)]
            st.success(f"Charts to generate: {', '.join(selected_names)}")
        else:
            st.warning("⚠️ No charts selected. Please select at least one chart.")
        
        st.divider()
        
        # Run Analysis Button
        if st.button("🚀 Run Portfolio Analysis", type="primary", use_container_width=True, key="run_analysis"):
            if not portfolio_data:
                st.error("Please add at least one position in the Portfolio Setup tab!")
            elif not selected_charts:
                st.error("Please select at least one chart to generate!")
            elif abs(total_weight - 100) > 1:
                st.error("Portfolio weights must sum to approximately 100%!")
            else:
                with st.spinner(f"Running analysis for {len(selected_charts)} charts... This may take a moment."):
                    try:
                        # Préparer les données
                        tickers = [p['ticker'] for p in portfolio_data]
                        weights_dict = {p['ticker']: p['weight'] / 100 for p in portfolio_data}
                        
                        # Récupérer les prix historiques (maximum disponible)
                        prices = fetch_prices_new(tickers, period="max")
                        
                        if prices is not None and not prices.empty:
                            # Calculer les métriques complètes avec app.calculations
                            portfolio_metrics = compute_portfolio_metrics(
                                prices=prices,
                                weights_raw=weights_dict,
                                cov_method="ledoit",
                                annualization=252
                            )
                            
                            # Lancer simulations Monte Carlo si nécessaire
                            mc_simulations_data = None
                            if any(n in selected_charts for n in range(7, 13)):  # Charts MC (7-12)
                                mc_simulations_data = mc_gaussian_with_randomness(
                                    mu_a=portfolio_metrics['mu_a'],
                                    cov_a=portfolio_metrics['cov_a'],
                                    w=portfolio_metrics['w'],
                                    start_value=capital,
                                    steps=60,  # 5 ans en mois
                                    paths=mc_simulations,
                                    randomness_factor=0.30
                                )
                            
                            # Récupérer benchmarks si sélectionnés
                            bench_data = {}
                            if selected_benchmarks:
                                bench_prices = fetch_prices_new(selected_benchmarks, period="max")
                                if bench_prices is not None:
                                    for bench in selected_benchmarks:
                                        if bench in bench_prices.columns:
                                            bench_returns = bench_prices[bench].pct_change().dropna()
                                            bench_cumulative = (1 + bench_returns).cumprod()
                                            bench_data[benchmark_options.get(bench, bench)] = {
                                                'returns': bench_returns,
                                                'cumulative': bench_cumulative,
                                                'prices': bench_prices[bench]
                                            }
                            
                            # Stocker tous les résultats
                            st.session_state.analysis_results = {
                                'portfolio_metrics': portfolio_metrics,
                                'prices': prices,
                                'weights_dict': weights_dict,
                                'mc_simulations': mc_simulations_data,
                                'benchmarks': bench_data,
                                'capital': capital,
                                'selected_charts': selected_charts,
                                'tickers': tickers
                            }
                            
                            st.success(f"✅ Analysis complete! {len(selected_charts)} charts ready. Check the Results tab.")
                        else:
                            st.error("Could not fetch price data. Please check your tickers and try again.")
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
    
    # ==================== TAB 4: ANALYSIS RESULTS ====================
    with tab4:
        if st.session_state.analysis_results is None:
            st.info("👆 Set up your portfolio, select charts, and run the analysis to see results.")
        else:
            results = st.session_state.analysis_results
            portfolio_metrics = results['portfolio_metrics']
            selected = results.get('selected_charts', list(range(1, 25)))
            capital = results['capital']
            
            st.markdown('<h2 class="section-header">📊 Portfolio Metrics</h2>', unsafe_allow_html=True)
            
            # Calculer les métriques clés
            port_returns = portfolio_metrics['port_ret_d']
            cumulative_returns = (1 + port_returns).cumprod()
            total_return = (cumulative_returns.iloc[-1] - 1) * 100
            annual_return = portfolio_metrics['mu_a'].mean() * 100 if isinstance(portfolio_metrics['mu_a'], np.ndarray) else port_returns.mean() * 252 * 100
            volatility = portfolio_metrics['vol_a'] * 100
            sharpe = calculate_sharpe_ratio(port_returns.values, risk_free_rate=0.02)
            max_dd = calculate_max_drawdown(cumulative_returns.values) * 100
            var_95 = calculate_var(port_returns.values, 0.95) * capital
            
            # Afficher les métriques
            cols = st.columns(6)
            with cols[0]:
                st.metric("Total Return", f"{total_return:.2f}%")
            with cols[1]:
                st.metric("Annual Return", f"{annual_return:.2f}%")
            with cols[2]:
                st.metric("Volatility", f"{volatility:.2f}%")
            with cols[3]:
                st.metric("Sharpe Ratio", f"{sharpe:.2f}")
            with cols[4]:
                st.metric("Max Drawdown", f"{max_dd:.2f}%")
            with cols[5]:
                st.metric("VaR 95%", f"${var_95:,.2f}")
            
            st.divider()
            
            # Préparer les données pour les graphiques
            prices = results['prices']
            w_series = portfolio_metrics['w_series']
            mc_sims = results.get('mc_simulations')
            benchmarks = results.get('benchmarks', {})
            tickers = results['tickers']
            
            # Afficher les graphiques sélectionnés
            st.markdown('<h2 class="section-header">📈 Generated Charts</h2>', unsafe_allow_html=True)
            
            for chart_num in sorted(selected):
                try:
                    chart_func = get_chart_function(chart_num)
                    if not chart_func:
                        st.warning(f"Chart {chart_num} function not found.")
                        continue
                    
                    st.markdown(f"### {chart_num}. {CHART_NAMES.get(chart_num, f'Chart {chart_num}')}")
                    
                    # Portfolio Charts (1-6)
                    if chart_num == 1:
                        fig = chart_func(w_series, capital)
                    
                    elif chart_num == 2:
                        fig = chart_func(w_series, capital)
                    
                    elif chart_num == 3:
                        fig = chart_func(port_returns, prices, tickers)
                    
                    elif chart_num == 4:
                        fig = chart_func(port_returns)
                    
                    elif chart_num == 5:
                        fig = chart_func(portfolio_metrics['corr'])
                    
                    elif chart_num == 6:
                        fig = chart_func(port_returns, window=252)
                    
                    # Monte Carlo Charts (7-12)
                    elif chart_num in range(7, 13):
                        if mc_sims is None:
                            st.warning("Monte Carlo simulations required. Please select MC charts before running analysis.")
                            continue
                        
                        if chart_num == 7:
                            fig = chart_func(mc_sims, capital, n_display=mc_display_paths)
                        elif chart_num == 8:
                            fig = chart_func(mc_sims)
                        elif chart_num == 9:
                            fig = chart_func(mc_sims, confidence_levels=[0.95, 0.99])
                        elif chart_num == 10:
                            fig = chart_func(mc_sims)
                        elif chart_num == 11:
                            fig = chart_func(mc_sims, risk_free_rate=0.02)
                        elif chart_num == 12:
                            fig = chart_func(mc_sims, capital)
                    
                    # Risk Metrics Charts (13-18)
                    elif chart_num == 13:
                        fig = chart_func(port_returns, window=252, risk_free_rate=0.02)
                    
                    elif chart_num == 14:
                        fig = chart_func(port_returns)
                    
                    elif chart_num == 15:
                        fig = chart_func(portfolio_metrics, benchmarks)
                    
                    elif chart_num == 16:
                        if not benchmarks:
                            st.warning("No benchmark selected. Please add a benchmark for beta analysis.")
                            continue
                        bench_name = list(benchmarks.keys())[0]
                        bench_returns = benchmarks[bench_name]['returns']
                        fig = chart_func(port_returns, bench_returns)
                    
                    elif chart_num == 17:
                        fig = chart_func(port_returns, window=252, confidence=0.95)
                    
                    elif chart_num == 18:
                        fig = chart_func(port_returns, confidence=0.95)
                    
                    # Market Analysis Charts (19-24)
                    elif chart_num == 19:
                        if not benchmarks:
                            st.warning("No benchmark selected for comparison.")
                            continue
                        bench_name = list(benchmarks.keys())[0]
                        bench_cumul = benchmarks[bench_name]['cumulative'] * capital
                        fig = chart_func(cumulative_returns * capital, bench_cumul, bench_name)
                    
                    elif chart_num == 20:
                        if not benchmarks:
                            st.warning("No benchmark selected for relative performance.")
                            continue
                        bench_name = list(benchmarks.keys())[0]
                        bench_returns = benchmarks[bench_name]['returns']
                        fig = chart_func(port_returns, bench_returns, bench_name)
                    
                    elif chart_num == 21:
                        # Sector mapping simple
                        tech_stocks = ["AAPL", "MSFT", "GOOGL", "GOOG", "NVDA", "AMD", "INTC", "META", "NFLX"]
                        finance_stocks = ["JPM", "V", "MA", "BAC", "GS", "MS", "BLK"]
                        sector_map = {}
                        for t in tickers:
                            if t in tech_stocks:
                                sector_map[t] = "Technology"
                            elif t in finance_stocks:
                                sector_map[t] = "Finance"
                            elif "SPY" in t or "QQQ" in t or "VOO" in t:
                                sector_map[t] = "ETF"
                            else:
                                sector_map[t] = "Other"
                        fig = chart_func(w_series, sector_map)
                    
                    elif chart_num == 22:
                        # Geographic mapping
                        country_map = {}
                        for t in tickers:
                            if ".PA" in t:
                                country_map[t] = "France"
                            elif ".DE" in t:
                                country_map[t] = "Germany"
                            elif ".AS" in t:
                                country_map[t] = "Netherlands"
                            else:
                                country_map[t] = "USA"
                        fig = chart_func(w_series, country_map)
                    
                    elif chart_num == 23:
                        fig = chart_func(port_returns, window=60)
                    
                    elif chart_num == 24:
                        if not benchmarks:
                            st.warning("No benchmark selected for market correlation.")
                            continue
                        market_indices = {name: data['returns'] for name, data in benchmarks.items()}
                        fig = chart_func(port_returns, market_indices)
                    
                    # Afficher le graphique
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("---")
                
                except Exception as e:
                    st.error(f"❌ Error generating chart {chart_num}: {str(e)}")
                    with st.expander("Show error details"):
                        import traceback
                        st.code(traceback.format_exc())
            
            st.divider()
            st.markdown('<h2 class="section-header">📥 Export Results</h2>', unsafe_allow_html=True)
            
            summary_df = pd.DataFrame({
                'Metric': ['Total Return', 'Annual Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown', 'VaR 95%', 'CVaR 95%'],
                'Value': [
                    f"{total_return:.2f}%",
                    f"{annual_return:.2f}%",
                    f"{volatility:.2f}%",
                    f"{sharpe:.2f}",
                    f"{max_dd:.2f}%",
                    f"${var_95:,.2f}",
                    f"${calculate_expected_shortfall(port_returns.values, 0.95) * capital:,.2f}"
                ]
            })
            
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Summary (CSV)",
                data=csv,
                file_name="portfolio_analysis.csv",
                mime="text/csv"
            )

# ===================== FOOTER =====================
def render_footer():
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.5); padding: 1rem;">
        <p>📊 Portfolio Architect | Built with ❤️ by Tom Campacci</p>
        <p style="font-size: 0.8rem;">Data provided by Yahoo Finance | For educational purposes only</p>
    </div>
    """, unsafe_allow_html=True)

# ===================== RUN APP =====================
if __name__ == "__main__":
    main()
    render_footer()
