"""
Configuration et constantes pour l'application Portfolio Architect
"""

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
    
    # US Finance
    "JPM": {"name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
    "V": {"name": "Visa Inc.", "exchange": "NYSE"},
    "MA": {"name": "Mastercard Inc.", "exchange": "NYSE"},
    
    # US ETFs
    "SPY": {"name": "SPDR S&P 500 ETF", "exchange": "NYSE"},
    "QQQ": {"name": "Invesco QQQ Trust", "exchange": "NASDAQ"},
    "VOO": {"name": "Vanguard S&P 500 ETF", "exchange": "NYSE"},
    "GLD": {"name": "SPDR Gold Shares", "exchange": "NYSE"},
    
    # European Stocks
    "MC.PA": {"name": "LVMH", "exchange": "Euronext Paris"},
    "OR.PA": {"name": "L'Oréal", "exchange": "Euronext Paris"},
    "TTE.PA": {"name": "TotalEnergies", "exchange": "Euronext Paris"},
    "SAP.DE": {"name": "SAP SE", "exchange": "XETRA"},
    "ASML.AS": {"name": "ASML Holding", "exchange": "Euronext Amsterdam"},
}

# ===================== QUICK SELECT OPTIONS =====================

QUICK_SELECT_OPTIONS = [
    ("", "— Select or type to search —"),
    ("AAPL", "Apple Inc."),
    ("MSFT", "Microsoft Corporation"),
    ("GOOGL", "Alphabet Inc."),
    ("NVDA", "NVIDIA Corporation"),
    ("TSLA", "Tesla Inc."),
    ("META", "Meta Platforms"),
    ("AMZN", "Amazon.com"),
    ("SPY", "SPDR S&P 500 ETF"),
    ("QQQ", "Invesco QQQ Trust"),
    ("MC.PA", "LVMH (Euronext Paris)"),
    ("OR.PA", "L'Oréal (Euronext Paris)"),
]

# ===================== CHART DESCRIPTIONS =====================

CHART_DESCRIPTIONS = {
    # Portfolio Charts (1-6)
    1: "Asset Allocation - Shows the percentage distribution of assets in your portfolio as a pie chart.",
    2: "Portfolio Value Distribution - Displays the monetary value allocated to each asset in your portfolio.",
    3: "Cumulative Returns - Tracks the cumulative performance of your portfolio over time compared to initial investment.",
    4: "Daily Returns Distribution - Shows the statistical distribution of daily returns with normal distribution overlay.",
    5: "Asset Correlation Heatmap - Visualizes the correlation coefficients between different assets in your portfolio.",
    6: "Rolling Volatility - Displays how portfolio volatility changes over time using a rolling window calculation.",
    
    # Monte Carlo Simulations (7-12)
    7: "Monte Carlo Price Projections - Simulates thousands of possible future price paths for your portfolio.",
    8: "Monte Carlo Returns Distribution - Shows the probability distribution of potential portfolio returns.",
    9: "Value at Risk Analysis - Calculates the maximum expected loss at different confidence levels (95%, 99%).",
    10: "Confidence Intervals - Displays the range of possible outcomes with statistical confidence bands.",
    11: "Risk-Adjusted Performance - Compares returns adjusted for risk across different scenarios.",
    12: "Scenario Analysis - Shows best case, worst case, and expected scenarios for portfolio performance.",
    
    # Risk Metrics (13-18)
    13: "Sharpe Ratio Evolution - Tracks the risk-adjusted return metric over time.",
    14: "Maximum Drawdown - Identifies the largest peak-to-trough decline in portfolio value.",
    15: "Risk-Return Scatter - Plots assets on a risk vs return chart to identify efficient investments.",
    16: "Beta Analysis - Measures portfolio sensitivity to market movements.",
    17: "Value at Risk History - Tracks how VaR changes over different time periods.",
    18: "Conditional VaR - Shows expected loss given that loss exceeds VaR threshold.",
    
    # Market Analysis (19-24)
    19: "Benchmark Comparison - Compares portfolio performance against major market indices.",
    20: "Relative Performance - Shows outperformance or underperformance vs benchmark.",
    21: "Sector Allocation - Breaks down portfolio exposure by industry sectors.",
    22: "Geographic Exposure - Shows portfolio allocation across different countries/regions.",
    23: "Market Regime Analysis - Identifies bull, bear, and neutral market periods.",
    24: "Correlation with Markets - Shows how portfolio correlates with major global indices.",
}

# ===================== COLOR SCHEMES =====================

# Couleurs pour les graphiques (dark theme)
CHART_COLORS = {
    'primary': ['#e94560', '#00d26a', '#3742fa', '#ffa502', '#ff6b6b', 
                '#1e90ff', '#9b59b6', '#2ecc71', '#e74c3c', '#f39c12'],
    'positive': '#00d26a',
    'negative': '#e94560',
    'neutral': '#3742fa',
    'background': 'rgba(0,0,0,0)',
    'text': 'white'
}

# ===================== DEFAULT VALUES =====================

DEFAULT_CAPITAL = 10000.0
DEFAULT_CURRENCY = "USD"
DEFAULT_PERIOD = "1y"
DEFAULT_MONTE_CARLO_SIMULATIONS = 1000
DEFAULT_VAR_CONFIDENCE = 0.95

# ===================== API SETTINGS =====================

YAHOO_FINANCE_TIMEOUT = 5
MAX_SEARCH_RESULTS = 10
CACHE_TTL_SECONDS = 300  # 5 minutes

