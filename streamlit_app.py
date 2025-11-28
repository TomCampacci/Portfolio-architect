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

# ===================== PAGE CONFIGURATION =====================
st.set_page_config(
    page_title="Portfolio Architect",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    
    /* Cards */
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 1.2rem;
        backdrop-filter: blur(10px);
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
    
    /* Ticker suggestion box */
    .ticker-suggestion {
        background: rgba(233, 69, 96, 0.1);
        border: 1px solid #e94560;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.25rem 0;
        cursor: pointer;
    }
    
    .ticker-suggestion:hover {
        background: rgba(233, 69, 96, 0.2);
    }
    
    .exchange-badge {
        background: #3742fa;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        margin-left: 8px;
    }
    
    /* Preview card */
    .preview-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
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
POPULAR_TICKERS = {
    # US Tech
    "AAPL": {"name": "Apple Inc.", "exchange": "NASDAQ"},
    "MSFT": {"name": "Microsoft Corporation", "exchange": "NASDAQ"},
    "GOOGL": {"name": "Alphabet Inc.", "exchange": "NASDAQ"},
    "GOOG": {"name": "Alphabet Inc. Class C", "exchange": "NASDAQ"},
    "AMZN": {"name": "Amazon.com Inc.", "exchange": "NASDAQ"},
    "NVDA": {"name": "NVIDIA Corporation", "exchange": "NASDAQ"},
    "META": {"name": "Meta Platforms Inc.", "exchange": "NASDAQ"},
    "TSLA": {"name": "Tesla Inc.", "exchange": "NASDAQ"},
    "NFLX": {"name": "Netflix Inc.", "exchange": "NASDAQ"},
    "AMD": {"name": "Advanced Micro Devices", "exchange": "NASDAQ"},
    "INTC": {"name": "Intel Corporation", "exchange": "NASDAQ"},
    "CRM": {"name": "Salesforce Inc.", "exchange": "NYSE"},
    "ADBE": {"name": "Adobe Inc.", "exchange": "NASDAQ"},
    "PYPL": {"name": "PayPal Holdings", "exchange": "NASDAQ"},
    "PLTR": {"name": "Palantir Technologies", "exchange": "NYSE"},
    
    # US Finance
    "JPM": {"name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
    "V": {"name": "Visa Inc.", "exchange": "NYSE"},
    "MA": {"name": "Mastercard Inc.", "exchange": "NYSE"},
    "BAC": {"name": "Bank of America", "exchange": "NYSE"},
    "GS": {"name": "Goldman Sachs", "exchange": "NYSE"},
    "MS": {"name": "Morgan Stanley", "exchange": "NYSE"},
    "BLK": {"name": "BlackRock Inc.", "exchange": "NYSE"},
    
    # US ETFs
    "SPY": {"name": "SPDR S&P 500 ETF", "exchange": "NYSE"},
    "QQQ": {"name": "Invesco QQQ Trust", "exchange": "NASDAQ"},
    "VOO": {"name": "Vanguard S&P 500 ETF", "exchange": "NYSE"},
    "VTI": {"name": "Vanguard Total Stock Market", "exchange": "NYSE"},
    "IWM": {"name": "iShares Russell 2000", "exchange": "NYSE"},
    "GLD": {"name": "SPDR Gold Shares", "exchange": "NYSE"},
    "SLV": {"name": "iShares Silver Trust", "exchange": "NYSE"},
    "TLT": {"name": "iShares 20+ Year Treasury", "exchange": "NASDAQ"},
    
    # European Stocks
    "MC.PA": {"name": "LVMH", "exchange": "Euronext Paris"},
    "OR.PA": {"name": "L'Oréal", "exchange": "Euronext Paris"},
    "TTE.PA": {"name": "TotalEnergies", "exchange": "Euronext Paris"},
    "SAN.PA": {"name": "Sanofi", "exchange": "Euronext Paris"},
    "AIR.PA": {"name": "Airbus", "exchange": "Euronext Paris"},
    "BNP.PA": {"name": "BNP Paribas", "exchange": "Euronext Paris"},
    "SAP.DE": {"name": "SAP SE", "exchange": "XETRA"},
    "SIE.DE": {"name": "Siemens AG", "exchange": "XETRA"},
    "BMW.DE": {"name": "BMW AG", "exchange": "XETRA"},
    "ASML.AS": {"name": "ASML Holding", "exchange": "Euronext Amsterdam"},
    "SHEL.L": {"name": "Shell plc", "exchange": "London"},
    "AZN.L": {"name": "AstraZeneca", "exchange": "London"},
    "HSBA.L": {"name": "HSBC Holdings", "exchange": "London"},
    
    # European ETFs
    "IWDA.AS": {"name": "iShares Core MSCI World", "exchange": "Euronext Amsterdam"},
    "CSPX.L": {"name": "iShares Core S&P 500", "exchange": "London"},
    "VUSA.L": {"name": "Vanguard S&P 500", "exchange": "London"},
    "CW8.PA": {"name": "Amundi MSCI World", "exchange": "Euronext Paris"},
    "EQQQ.L": {"name": "Invesco EQQQ Nasdaq-100", "exchange": "London"},
}

# ===================== SESSION STATE INITIALIZATION =====================
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = pd.DataFrame({
        'Ticker': [''] * 10,
        'Weight (%)': [0.0] * 10
    })

if 'benchmarks' not in st.session_state:
    st.session_state.benchmarks = ['^GSPC', '^NDX', '', '', '', '']

if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None

if 'validated_tickers' not in st.session_state:
    st.session_state.validated_tickers = {}

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

def search_tickers(query):
    """Search for tickers matching query with exchange info"""
    if not query or len(query) < 1:
        return []
    
    query_upper = query.upper()
    results = []
    
    # Search in local database first
    for ticker, info in POPULAR_TICKERS.items():
        if query_upper in ticker or query_upper in info['name'].upper():
            results.append({
                'symbol': ticker,
                'name': info['name'],
                'exchange': info['exchange']
            })
    
    # If not enough results, try Yahoo Finance search
    if len(results) < 5:
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {"q": query, "quotesCount": 10, "lang": "en-US"}
            headers = {"User-Agent": "Mozilla/5.0"}
            resp = requests.get(url, params=params, headers=headers, timeout=3)
            
            if resp.status_code == 200:
                data = resp.json()
                for quote in data.get('quotes', []):
                    symbol = quote.get('symbol', '')
                    if symbol and symbol not in [r['symbol'] for r in results]:
                        quote_type = quote.get('quoteType', '')
                        if quote_type in ['EQUITY', 'ETF', 'INDEX']:
                            results.append({
                                'symbol': symbol,
                                'name': quote.get('shortname') or quote.get('longname') or symbol,
                                'exchange': quote.get('exchDisp') or quote.get('exchange') or 'Unknown'
                            })
        except:
            pass
    
    return results[:8]

@st.cache_data(ttl=120)
def validate_and_get_ticker_info(symbol):
    """Validate ticker and get detailed info including exchange"""
    if not symbol or not symbol.strip():
        return None
    
    symbol = symbol.strip().upper()
    
    # Check local database first
    if symbol in POPULAR_TICKERS:
        info = POPULAR_TICKERS[symbol]
        return {
            'valid': True,
            'symbol': symbol,
            'name': info['name'],
            'exchange': info['exchange'],
            'price': None
        }
    
    # Try Yahoo Finance
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if info and info.get('regularMarketPrice'):
            # Determine exchange
            exchange = info.get('exchange', '')
            exchange_map = {
                'NMS': 'NASDAQ', 'NGM': 'NASDAQ', 'NCM': 'NASDAQ',
                'NYQ': 'NYSE', 'PCX': 'NYSE',
                'PAR': 'Euronext Paris', 'EPA': 'Euronext Paris',
                'AMS': 'Euronext Amsterdam', 'EAM': 'Euronext Amsterdam',
                'GER': 'XETRA', 'FRA': 'Frankfurt',
                'LSE': 'London', 'LON': 'London',
                'MIL': 'Milan', 'BIT': 'Milan'
            }
            exchange_display = exchange_map.get(exchange, exchange)
            
            return {
                'valid': True,
                'symbol': symbol,
                'name': info.get('longName') or info.get('shortName') or symbol,
                'exchange': exchange_display,
                'price': info.get('regularMarketPrice'),
                'currency': info.get('currency', 'USD')
            }
    except:
        pass
    
    return {'valid': False, 'symbol': symbol}

@st.cache_data(ttl=3600)
def fetch_historical_prices(tickers, years=5):
    """Fetch historical prices for analysis"""
    if not tickers:
        return None
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    try:
        data = yf.download(tickers, start=start_date, end=end_date, progress=False, auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            prices = data['Close']
        else:
            prices = pd.DataFrame(data['Close'])
            prices.columns = [tickers[0]] if isinstance(tickers, list) and len(tickers) == 1 else [tickers]
        return prices.dropna()
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return None

def compute_portfolio_metrics(prices, weights, capital=10000):
    """Compute portfolio metrics"""
    returns = prices.pct_change().dropna()
    ann_factor = 252
    
    weight_array = np.array(list(weights.values()))
    portfolio_returns = (returns * weight_array).sum(axis=1)
    
    cumulative = (1 + portfolio_returns).cumprod()
    portfolio_value = capital * cumulative
    
    total_return = (cumulative.iloc[-1] - 1) * 100
    annual_return = ((1 + total_return/100) ** (ann_factor / len(returns)) - 1) * 100
    volatility = portfolio_returns.std() * np.sqrt(ann_factor) * 100
    
    rf = 0.04
    sharpe = (annual_return/100 - rf) / (volatility/100) if volatility > 0 else 0
    
    running_max = cumulative.cummax()
    drawdowns = (cumulative - running_max) / running_max
    max_drawdown = drawdowns.min() * 100
    
    var_95 = np.percentile(portfolio_returns, 5) * capital
    
    return {
        'total_return': total_return,
        'annual_return': annual_return,
        'volatility': volatility,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'var_95': var_95,
        'portfolio_value': portfolio_value,
        'daily_returns': portfolio_returns,
        'cumulative_returns': cumulative
    }

def create_preview_allocation_chart(portfolio_data, capital):
    """Create live preview allocation chart"""
    if not portfolio_data:
        return None
    
    labels = [p['ticker'] for p in portfolio_data]
    weights = [p['weight'] for p in portfolio_data]
    values = [capital * (w / 100) for w in weights]
    
    # Colors palette
    colors = ['#e94560', '#00d26a', '#3742fa', '#ffa502', '#ff6b6b', 
              '#1e90ff', '#9b59b6', '#2ecc71', '#e74c3c', '#f39c12']
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "bar"}]],
        subplot_titles=("Allocation %", "Value ($)")
    )
    
    # Pie chart
    fig.add_trace(
        go.Pie(
            labels=labels,
            values=weights,
            hole=0.4,
            marker=dict(colors=colors[:len(labels)]),
            textinfo='label+percent',
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Bar chart for values
    fig.add_trace(
        go.Bar(
            x=labels,
            y=values,
            marker_color=colors[:len(labels)],
            text=[f"${v:,.0f}" for v in values],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title=dict(
            text="📊 Portfolio Preview",
            font=dict(size=18, color='white')
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=False,
        height=350
    )
    
    return fig

def create_allocation_chart(weights):
    """Create portfolio allocation pie chart"""
    labels = list(weights.keys())
    values = [v * 100 for v in weights.values()]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        textinfo='label+percent',
        marker=dict(colors=px.colors.qualitative.Set3)
    )])
    
    fig.update_layout(
        title="Portfolio Allocation",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def create_performance_chart(portfolio_value, benchmarks_data=None):
    """Create performance comparison chart"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=portfolio_value.index,
        y=portfolio_value.values,
        name='Portfolio',
        line=dict(color='#e94560', width=3)
    ))
    
    if benchmarks_data is not None:
        colors = ['#00d26a', '#ffa502', '#3742fa', '#ff6b6b', '#1e90ff']
        for i, (name, values) in enumerate(benchmarks_data.items()):
            fig.add_trace(go.Scatter(
                x=values.index,
                y=values.values,
                name=name,
                line=dict(color=colors[i % len(colors)], width=2, dash='dash')
            ))
    
    fig.update_layout(
        title="Portfolio Performance vs Benchmarks",
        xaxis_title="Date",
        yaxis_title="Value ($)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        hovermode='x unified'
    )
    
    return fig

def create_correlation_heatmap(prices):
    """Create correlation heatmap"""
    corr = prices.pct_change().dropna().corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        colorscale='RdBu',
        zmid=0,
        text=np.round(corr.values, 2),
        texttemplate='%{text}',
        textfont={"size": 10}
    ))
    
    fig.update_layout(
        title="Asset Correlation Matrix",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def create_volatility_chart(prices, weights):
    """Create volatility contribution chart"""
    returns = prices.pct_change().dropna()
    volatilities = returns.std() * np.sqrt(252) * 100
    
    tickers = list(weights.keys())
    vols = [volatilities[t] if t in volatilities.index else 0 for t in tickers]
    weight_vals = [weights[t] * 100 for t in tickers]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(name='Volatility (%)', x=tickers, y=vols, marker_color='#e94560'))
    fig.add_trace(go.Bar(name='Weight (%)', x=tickers, y=weight_vals, marker_color='#00d26a'))
    
    fig.update_layout(
        title="Asset Volatility vs Weight",
        xaxis_title="Asset",
        yaxis_title="Percentage (%)",
        barmode='group',
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white')
    )
    
    return fig

def run_monte_carlo(metrics, capital, n_simulations=1000, n_days=252):
    """Run Monte Carlo simulation"""
    daily_returns = metrics['daily_returns']
    mu = daily_returns.mean()
    sigma = daily_returns.std()
    
    simulations = np.zeros((n_days, n_simulations))
    simulations[0] = capital
    
    for t in range(1, n_days):
        random_returns = np.random.normal(mu, sigma, n_simulations)
        simulations[t] = simulations[t-1] * (1 + random_returns)
    
    return simulations

def create_monte_carlo_chart(simulations, capital):
    """Create Monte Carlo simulation chart"""
    fig = go.Figure()
    
    n_paths = min(100, simulations.shape[1])
    for i in range(n_paths):
        fig.add_trace(go.Scatter(
            x=list(range(simulations.shape[0])),
            y=simulations[:, i],
            mode='lines',
            line=dict(width=0.5, color='rgba(233, 69, 96, 0.1)'),
            showlegend=False
        ))
    
    percentiles = [5, 50, 95]
    colors = ['#ff4757', '#00d26a', '#3742fa']
    names = ['5th Percentile (Worst)', 'Median', '95th Percentile (Best)']
    
    for i, p in enumerate(percentiles):
        pct_line = np.percentile(simulations, p, axis=1)
        fig.add_trace(go.Scatter(
            x=list(range(len(pct_line))),
            y=pct_line,
            mode='lines',
            name=names[i],
            line=dict(width=2, color=colors[i])
        ))
    
    fig.add_hline(y=capital, line_dash="dash", line_color="white", 
                  annotation_text=f"Initial: ${capital:,.0f}")
    
    fig.update_layout(
        title=f"Monte Carlo Simulation (1 Year, {simulations.shape[1]} paths)",
        xaxis_title="Trading Days",
        yaxis_title="Portfolio Value ($)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True
    )
    
    return fig

# ===================== MAIN APPLICATION =====================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Portfolio Architect</h1>
        <p>Advanced Portfolio Analysis & Monte Carlo Simulation | Built by Tom Campacci</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        capital = st.number_input("💰 Initial Capital ($)", min_value=100, value=10000, step=1000)
        currency = st.selectbox("💱 Currency", ["USD", "EUR", "GBP"])
        
        st.divider()
        
        st.subheader("📈 Analysis Settings")
        years = st.slider("Historical Data (Years)", 1, 10, 5)
        mc_simulations = st.slider("Monte Carlo Simulations", 100, 5000, 1000, step=100)
        
        st.divider()
        
        st.subheader("⚡ Quick Actions")
        if st.button("🔄 Refresh Market Data"):
            st.cache_data.clear()
            st.rerun()
    
    # Main Content - Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Market Overview", "💼 Portfolio Setup", "📈 Analysis Results"])
    
    # ==================== TAB 1: MARKET OVERVIEW ====================
    with tab1:
        st.markdown('<h2 class="section-header">💱 Live Market Data</h2>', unsafe_allow_html=True)
        
        with st.spinner("Fetching market data..."):
            market_data = fetch_market_data()
        
        st.subheader("📊 Major Indexes")
        cols = st.columns(3)
        for i, (name, data) in enumerate(market_data.get('indexes', {}).items()):
            with cols[i % 3]:
                st.metric(label=name, value=f"{data['price']:,.2f}", delta=f"{data['change']:+.2f}%")
        
        st.divider()
        
        st.subheader("💱 Forex Rates")
        cols = st.columns(4)
        for i, (name, data) in enumerate(market_data.get('forex', {}).items()):
            with cols[i % 4]:
                st.metric(label=name, value=f"{data['price']:.4f}", delta=f"{data['change']:+.2f}%")
        
        st.divider()
        
        st.subheader("🏆 Commodities")
        cols = st.columns(3)
        for i, (name, data) in enumerate(market_data.get('commodities', {}).items()):
            with cols[i % 3]:
                st.metric(label=name, value=f"${data['price']:,.2f}", delta=f"{data['change']:+.2f}%")
    
    # ==================== TAB 2: PORTFOLIO SETUP ====================
    with tab2:
        col_input, col_preview = st.columns([1.2, 1])
        
        with col_input:
            st.markdown('<h2 class="section-header">💼 Portfolio Positions</h2>', unsafe_allow_html=True)
            st.info("🔍 Start typing a ticker symbol - suggestions will appear automatically!")
            
            portfolio_data = []
            
            for i in range(10):
                col1, col2, col3 = st.columns([3, 1.5, 2])
                
                with col1:
                    # Ticker input with search
                    ticker_input = st.text_input(
                        f"Ticker {i+1}",
                        key=f"ticker_{i}",
                        placeholder="Type ticker (e.g., AAPL, NVDA, MC.PA)"
                    ).upper().strip()
                
                with col2:
                    weight = st.number_input(
                        f"Weight %",
                        min_value=0.0,
                        max_value=100.0,
                        value=0.0,
                        step=1.0,
                        key=f"weight_{i}",
                        label_visibility="collapsed"
                    )
                
                with col3:
                    if ticker_input:
                        # Validate and show info
                        ticker_info = validate_and_get_ticker_info(ticker_input)
                        if ticker_info and ticker_info.get('valid'):
                            exchange = ticker_info.get('exchange', 'Unknown')
                            name = ticker_info.get('name', '')[:25]
                            st.success(f"✓ {name}")
                            st.caption(f"📍 {exchange}")
                            
                            if weight > 0:
                                portfolio_data.append({
                                    'ticker': ticker_input,
                                    'weight': weight,
                                    'name': ticker_info.get('name', ticker_input),
                                    'exchange': exchange
                                })
                        else:
                            st.error("✗ Invalid ticker")
                    else:
                        st.empty()
                
                # Show suggestions when typing
                if ticker_input and len(ticker_input) >= 1:
                    suggestions = search_tickers(ticker_input)
                    if suggestions and ticker_input not in [s['symbol'] for s in suggestions]:
                        with st.expander(f"💡 Suggestions for '{ticker_input}'", expanded=False):
                            for sug in suggestions[:5]:
                                st.markdown(
                                    f"**{sug['symbol']}** - {sug['name']} "
                                    f"<span style='background:#3742fa;color:white;padding:2px 8px;border-radius:4px;font-size:0.75rem;'>{sug['exchange']}</span>",
                                    unsafe_allow_html=True
                                )
            
            # Weight Summary
            total_weight = sum([p['weight'] for p in portfolio_data])
            st.divider()
            if total_weight > 0:
                if abs(total_weight - 100) < 0.01:
                    st.success(f"✅ Total Weight: {total_weight:.2f}%")
                elif total_weight > 100:
                    st.error(f"⚠️ Total Weight: {total_weight:.2f}% (exceeds 100%)")
                else:
                    st.warning(f"⚠️ Total Weight: {total_weight:.2f}% (under 100%)")
            
            # Benchmarks
            st.markdown('<h2 class="section-header">📈 Benchmarks</h2>', unsafe_allow_html=True)
            
            benchmark_options = {
                '^GSPC': 'S&P 500',
                '^NDX': 'Nasdaq 100',
                '^DJI': 'Dow Jones',
                '^GDAXI': 'DAX',
                '^FCHI': 'CAC 40',
                '^STOXX50E': 'Euro Stoxx 50',
                '^FTSE': 'FTSE 100',
                '^N225': 'Nikkei 225',
                'GC=F': 'Gold',
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
                # Show allocation chart
                fig_preview = create_preview_allocation_chart(portfolio_data, capital)
                if fig_preview:
                    st.plotly_chart(fig_preview, use_container_width=True)
                
                # Summary table
                st.markdown("**📋 Portfolio Summary**")
                summary_df = pd.DataFrame([
                    {
                        'Ticker': p['ticker'],
                        'Name': p['name'][:30],
                        'Exchange': p['exchange'],
                        'Weight': f"{p['weight']:.1f}%",
                        'Value': f"${capital * p['weight'] / 100:,.0f}"
                    }
                    for p in portfolio_data
                ])
                st.dataframe(summary_df, use_container_width=True, hide_index=True)
                
                # Totals
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("💰 Total Value", f"${capital * total_weight / 100:,.0f}")
                with col2:
                    remaining = 100 - total_weight
                    st.metric("📊 Remaining", f"{remaining:.1f}%", delta=f"-{remaining:.1f}%" if remaining > 0 else None)
            else:
                st.info("👈 Add tickers and weights to see your portfolio preview!")
                
                # Show example
                st.markdown("**💡 Quick Start Example:**")
                st.code("""
AAPL  - 25%
MSFT  - 25%
NVDA  - 20%
GOOGL - 15%
AMZN  - 15%
                """)
        
        st.divider()
        
        # Run Analysis Button
        if st.button("🚀 Run Portfolio Analysis", type="primary", use_container_width=True):
            if not portfolio_data:
                st.error("Please add at least one position to your portfolio!")
            elif abs(total_weight - 100) > 1:
                st.error("Portfolio weights must sum to approximately 100%!")
            else:
                with st.spinner("Running analysis... This may take a moment."):
                    tickers = [p['ticker'] for p in portfolio_data]
                    weights = {p['ticker']: p['weight'] / 100 for p in portfolio_data}
                    
                    prices = fetch_historical_prices(tickers, years)
                    
                    if prices is not None and not prices.empty:
                        metrics = compute_portfolio_metrics(prices, weights, capital)
                        mc_results = run_monte_carlo(metrics, capital, mc_simulations)
                        
                        bench_data = {}
                        if selected_benchmarks:
                            bench_prices = fetch_historical_prices(selected_benchmarks, years)
                            if bench_prices is not None:
                                for bench in selected_benchmarks:
                                    if bench in bench_prices.columns:
                                        bench_returns = bench_prices[bench].pct_change().dropna()
                                        bench_cumulative = (1 + bench_returns).cumprod()
                                        bench_data[benchmark_options.get(bench, bench)] = capital * bench_cumulative
                        
                        st.session_state.analysis_results = {
                            'metrics': metrics,
                            'prices': prices,
                            'weights': weights,
                            'mc_results': mc_results,
                            'benchmarks': bench_data,
                            'capital': capital
                        }
                        
                        st.success("✅ Analysis complete! Check the Results tab.")
                    else:
                        st.error("Could not fetch price data. Please check your tickers.")
    
    # ==================== TAB 3: ANALYSIS RESULTS ====================
    with tab3:
        if st.session_state.analysis_results is None:
            st.info("👆 Set up your portfolio in the Portfolio Setup tab and run the analysis to see results.")
        else:
            results = st.session_state.analysis_results
            metrics = results['metrics']
            
            st.markdown('<h2 class="section-header">📊 Portfolio Metrics</h2>', unsafe_allow_html=True)
            
            cols = st.columns(6)
            with cols[0]:
                st.metric("Total Return", f"{metrics['total_return']:.2f}%")
            with cols[1]:
                st.metric("Annual Return", f"{metrics['annual_return']:.2f}%")
            with cols[2]:
                st.metric("Volatility", f"{metrics['volatility']:.2f}%")
            with cols[3]:
                st.metric("Sharpe Ratio", f"{metrics['sharpe']:.2f}")
            with cols[4]:
                st.metric("Max Drawdown", f"{metrics['max_drawdown']:.2f}%")
            with cols[5]:
                st.metric("VaR 95%", f"${metrics['var_95']:,.2f}")
            
            st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                fig_alloc = create_allocation_chart(results['weights'])
                st.plotly_chart(fig_alloc, use_container_width=True)
            with col2:
                fig_corr = create_correlation_heatmap(results['prices'])
                st.plotly_chart(fig_corr, use_container_width=True)
            
            st.markdown('<h2 class="section-header">📈 Performance</h2>', unsafe_allow_html=True)
            fig_perf = create_performance_chart(metrics['portfolio_value'], results['benchmarks'])
            st.plotly_chart(fig_perf, use_container_width=True)
            
            fig_vol = create_volatility_chart(results['prices'], results['weights'])
            st.plotly_chart(fig_vol, use_container_width=True)
            
            st.markdown('<h2 class="section-header">🎲 Monte Carlo Simulation</h2>', unsafe_allow_html=True)
            
            mc = results['mc_results']
            final_values = mc[-1, :]
            
            cols = st.columns(4)
            with cols[0]:
                st.metric("5th Percentile", f"${np.percentile(final_values, 5):,.0f}")
            with cols[1]:
                st.metric("Median", f"${np.percentile(final_values, 50):,.0f}")
            with cols[2]:
                st.metric("95th Percentile", f"${np.percentile(final_values, 95):,.0f}")
            with cols[3]:
                prob_profit = (final_values > results['capital']).mean() * 100
                st.metric("Probability of Profit", f"{prob_profit:.1f}%")
            
            fig_mc = create_monte_carlo_chart(mc, results['capital'])
            st.plotly_chart(fig_mc, use_container_width=True)
            
            st.divider()
            st.markdown('<h2 class="section-header">📥 Export Results</h2>', unsafe_allow_html=True)
            
            summary_df = pd.DataFrame({
                'Metric': ['Total Return', 'Annual Return', 'Volatility', 'Sharpe Ratio', 'Max Drawdown', 'VaR 95%'],
                'Value': [
                    f"{metrics['total_return']:.2f}%",
                    f"{metrics['annual_return']:.2f}%",
                    f"{metrics['volatility']:.2f}%",
                    f"{metrics['sharpe']:.2f}",
                    f"{metrics['max_drawdown']:.2f}%",
                    f"${metrics['var_95']:,.2f}"
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
