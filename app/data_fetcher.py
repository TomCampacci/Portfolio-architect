"""
Module de récupération de données depuis Yahoo Finance
Gère : validation tickers, recherche, récupération prix historiques
"""

import yfinance as yf
import requests
import streamlit as st
from .config import POPULAR_TICKERS, YAHOO_FINANCE_TIMEOUT, MAX_SEARCH_RESULTS, CACHE_TTL_SECONDS

# ===================== TICKER VALIDATION =====================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def validate_and_get_ticker_info(symbol):
    """
    Valide un ticker et récupère ses informations
    
    Args:
        symbol (str): Symbole du ticker (ex: "AAPL", "MC.PA")
    
    Returns:
        dict: {'valid': bool, 'symbol': str, 'name': str, 'exchange': str, 'price': float}
    """
    if not symbol or not symbol.strip():
        return None
    
    symbol = symbol.strip().upper()
    
    # Check local database first (fast)
    if symbol in POPULAR_TICKERS:
        info = POPULAR_TICKERS[symbol]
        return {
            'valid': True,
            'symbol': symbol,
            'name': info['name'],
            'exchange': info['exchange'],
            'price': None  # Prix non nécessaire pour validation
        }
    
    # Try Yahoo Finance (slower)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if info and info.get('regularMarketPrice'):
            exchange = info.get('exchange', '')
            exchange_map = {
                'NMS': 'NASDAQ', 'NYQ': 'NYSE', 'PCX': 'NYSE Arca',
                'PAR': 'Euronext Paris', 'GER': 'XETRA', 'AMS': 'Euronext Amsterdam'
            }
            exchange_display = exchange_map.get(exchange, exchange or 'Unknown')
            
            return {
                'valid': True,
                'symbol': symbol,
                'name': info.get('longName') or info.get('shortName') or symbol,
                'exchange': exchange_display,
                'price': info.get('regularMarketPrice')
            }
    except:
        pass
    
    return {'valid': False, 'symbol': symbol}

# ===================== TICKER SEARCH =====================

def search_tickers(query):
    """
    Recherche des tickers par symbole ou nom de société
    
    Args:
        query (str): Requête de recherche (ex: "LVMH", "apple")
    
    Returns:
        list: Liste de dicts avec 'symbol', 'name', 'exchange'
    """
    if not query or len(query) < 1:
        return []
    
    query_upper = query.upper()
    results = []
    
    # Search in local database first (instant)
    for ticker, info in POPULAR_TICKERS.items():
        if query_upper in ticker or query_upper in info['name'].upper():
            results.append({
                'symbol': ticker,
                'name': info['name'],
                'exchange': info['exchange']
            })
    
    # Sort by relevance (starts with query first)
    results.sort(key=lambda x: (not x['symbol'].startswith(query_upper), x['symbol']))
    
    # If not enough results, try Yahoo Finance API
    if len(results) < 5:
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {"q": query, "quotesCount": MAX_SEARCH_RESULTS, "lang": "en-US"}
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            resp = requests.get(url, params=params, headers=headers, timeout=YAHOO_FINANCE_TIMEOUT)
            
            if resp.status_code == 200:
                data = resp.json()
                for quote in data.get('quotes', []):
                    symbol = quote.get('symbol', '')
                    if symbol and symbol not in [r['symbol'] for r in results]:
                        quote_type = quote.get('quoteType', '')
                        if quote_type in ['EQUITY', 'ETF', 'INDEX', 'MUTUALFUND']:
                            results.append({
                                'symbol': symbol,
                                'name': quote.get('shortname') or quote.get('longname') or symbol,
                                'exchange': quote.get('exchDisp') or quote.get('exchange') or 'Unknown'
                            })
        except:
            pass  # Fail silently, return local results
    
    return results[:MAX_SEARCH_RESULTS]

# ===================== PRICE DATA =====================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_historical_prices(tickers, period="1y"):
    """
    Récupère les prix historiques pour une liste de tickers
    
    Args:
        tickers (list): Liste de symboles (ex: ["AAPL", "NVDA"])
        period (str): Période (1mo, 3mo, 6mo, 1y, 2y, 5y, max)
    
    Returns:
        pandas.DataFrame: DataFrame avec prix de clôture ajustés
    """
    try:
        data = yf.download(tickers, period=period, progress=False)['Adj Close']
        if data.empty:
            return None
        # Convert to DataFrame if single ticker (returns Series)
        if len(tickers) == 1:
            data = data.to_frame()
            data.columns = tickers
        return data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_current_price(symbol):
    """
    Récupère le prix actuel d'un ticker
    
    Args:
        symbol (str): Symbole du ticker
    
    Returns:
        float: Prix actuel ou None si erreur
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get('currentPrice') or info.get('regularMarketPrice')
    except:
        return None

# ===================== MARKET DATA =====================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_market_data():
    """
    Récupère les données de marché actuelles (forex, indices, commodités)
    
    Returns:
        dict: {'forex': {}, 'indexes': {}, 'commodities': {}}
    """
    data = {'forex': {}, 'indexes': {}, 'commodities': {}}
    
    # Forex pairs
    forex_pairs = {
        'EURUSD=X': 'EUR/USD', 'GBPUSD=X': 'GBP/USD',
        'JPYUSD=X': 'JPY/USD', 'AUDUSD=X': 'AUD/USD'
    }
    
    # Major indexes
    indexes = {
        '^GSPC': 'S&P 500', '^DJI': 'Dow Jones', '^IXIC': 'NASDAQ',
        '^FTSE': 'FTSE 100', '^FCHI': 'CAC 40', '^GDAXI': 'DAX'
    }
    
    # Commodities
    commodities = {
        'GC=F': 'Gold', 'SI=F': 'Silver',
        'CL=F': 'Crude Oil', 'BTC-USD': 'Bitcoin'
    }
    
    # Fetch all at once
    all_symbols = {**forex_pairs, **indexes, **commodities}
    try:
        tickers_data = yf.download(list(all_symbols.keys()), period="1d", progress=False)
        for symbol, name in forex_pairs.items():
            try:
                price = tickers_data['Close'][symbol].iloc[-1]
                data['forex'][name] = price
            except:
                pass
        
        for symbol, name in indexes.items():
            try:
                price = tickers_data['Close'][symbol].iloc[-1]
                data['indexes'][name] = price
            except:
                pass
        
        for symbol, name in commodities.items():
            try:
                price = tickers_data['Close'][symbol].iloc[-1]
                data['commodities'][name] = price
            except:
                pass
    except:
        pass
    
    return data

