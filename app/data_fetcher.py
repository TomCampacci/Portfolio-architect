"""
Module de récupération de données depuis Yahoo Finance
Gère : validation tickers, recherche, récupération prix historiques, news RSS
"""

import yfinance as yf
import pandas as pd
import requests
import streamlit as st
from datetime import datetime
from .config import POPULAR_TICKERS, YAHOO_FINANCE_TIMEOUT, MAX_SEARCH_RESULTS, CACHE_TTL_SECONDS, MARKET_DATA_CACHE_TTL

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
        # Utiliser auto_adjust=True pour obtenir des prix ajustés dans la colonne 'Close'
        data = yf.download(tickers, period=period, progress=False, auto_adjust=True)
        
        if data.empty:
            return None
        
        # Extraire la colonne 'Close' (déjà ajustée avec auto_adjust=True)
        if isinstance(data.columns, pd.MultiIndex):
            # Cas multi-tickers : MultiIndex (metric, ticker)
            close_data = data['Close']
        else:
            # Cas single ticker : colonnes simples
            if 'Close' in data.columns:
                close_data = data[['Close']]
                close_data.columns = tickers
            else:
                return None
        
        return close_data
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
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

@st.cache_data(ttl=MARKET_DATA_CACHE_TTL)
def fetch_market_data():
    """
    Récupère les données de marché actuelles (forex, indices, commodités)
    avec prix et variation % sur 1 jour
    
    Returns:
        dict: {'forex': {name: {'price': float, 'change': float}}, ...}
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
    
    # Méthode 1: Téléchargement groupé pour forex et indices
    try:
        all_symbols_bulk = list(forex_pairs.keys()) + list(indexes.keys())
        tickers_data = yf.download(all_symbols_bulk, period="5d", progress=False)
        
        # Process forex
        for symbol, name in forex_pairs.items():
            try:
                closes = tickers_data['Close'][symbol].dropna()
                if len(closes) >= 2:
                    current = closes.iloc[-1]
                    previous = closes.iloc[-2]
                    change = ((current - previous) / previous) * 100
                    data['forex'][name] = {'price': current, 'change': change}
            except:
                pass
        
        # Process indexes
        for symbol, name in indexes.items():
            try:
                closes = tickers_data['Close'][symbol].dropna()
                if len(closes) >= 2:
                    current = closes.iloc[-1]
                    previous = closes.iloc[-2]
                    change = ((current - previous) / previous) * 100
                    data['indexes'][name] = {'price': current, 'change': change}
            except:
                pass
    except:
        pass
    
    # Méthode 2: Ticker individuel pour commodités (plus fiable)
    for symbol, name in commodities.items():
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Prix actuel
            current_price = info.get('regularMarketPrice') or info.get('currentPrice')
            
            # Variation depuis ouverture ou précédente clôture
            previous_close = info.get('previousClose') or info.get('regularMarketPreviousClose')
            
            if current_price and previous_close:
                change = ((current_price - previous_close) / previous_close) * 100
                data['commodities'][name] = {'price': current_price, 'change': change}
            elif current_price:
                # Si pas de previous close, mettre 0% de variation
                data['commodities'][name] = {'price': current_price, 'change': 0.0}
        except:
            pass
    
    return data

# ===================== NEWS DATA =====================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_ticker_news(symbol, max_news=5):
    """
    Récupère les dernières actualités pour un ticker via Yahoo Finance
    
    Args:
        symbol (str): Symbole du ticker (ex: "AAPL")
        max_news (int): Nombre maximum de news à retourner
    
    Returns:
        list: Liste de dicts avec 'title', 'link', 'publisher', 'timestamp'
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        
        if not news:
            return []
        
        formatted_news = []
        for item in news[:max_news]:
            formatted_news.append({
                'title': item.get('title', 'No title'),
                'link': item.get('link', '#'),
                'publisher': item.get('publisher', 'Unknown'),
                'timestamp': datetime.fromtimestamp(item.get('providerPublishTime', 0)).strftime('%Y-%m-%d %H:%M') if item.get('providerPublishTime') else 'N/A',
                'type': item.get('type', 'NEWS')
            })
        
        return formatted_news
    except Exception as e:
        return []

@st.cache_data(ttl=300)
def fetch_market_news(max_news=10):
    """
    Récupère les actualités générales du marché via plusieurs indices
    
    Returns:
        list: Liste combinée de news des principaux indices
    """
    market_symbols = ['^GSPC', '^DJI', '^IXIC']  # S&P 500, Dow Jones, NASDAQ
    all_news = []
    seen_titles = set()
    
    for symbol in market_symbols:
        news = fetch_ticker_news(symbol, max_news=5)
        for item in news:
            if item['title'] not in seen_titles:
                seen_titles.add(item['title'])
                all_news.append(item)
    
    # Sort by timestamp (newest first)
    all_news.sort(key=lambda x: x['timestamp'], reverse=True)
    return all_news[:max_news]

# ===================== OHLC DATA (for Candlesticks) =====================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_ohlc_data(symbol, period="1mo", interval="1d"):
    """
    Récupère les données OHLC (Open, High, Low, Close) pour graphiques candlestick
    
    Args:
        symbol (str): Symbole du ticker
        period (str): Période (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
        interval (str): Intervalle (1m, 5m, 15m, 1h, 1d, 1wk, 1mo)
    
    Returns:
        pandas.DataFrame: DataFrame avec Open, High, Low, Close, Volume
    """
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period, interval=interval)
        
        if data.empty:
            return None
        
        # Ensure we have all required columns
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in required_cols:
            if col not in data.columns:
                return None
        
        return data[required_cols]
    except Exception as e:
        return None

# ===================== SPARKLINE DATA =====================

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_sparkline_data(symbol, days=30):
    """
    Récupère les données pour sparkline (mini graphique de tendance)
    
    Args:
        symbol (str): Symbole du ticker
        days (int): Nombre de jours de données
    
    Returns:
        dict: {'prices': list, 'change_pct': float, 'trend': str}
    """
    try:
        ticker = yf.Ticker(symbol)
        period = f"{days}d" if days <= 30 else f"{days // 30}mo"
        data = ticker.history(period=period)
        
        if data.empty or len(data) < 2:
            return None
        
        prices = data['Close'].tolist()
        start_price = prices[0]
        end_price = prices[-1]
        change_pct = ((end_price - start_price) / start_price) * 100
        
        return {
            'prices': prices,
            'dates': data.index.tolist(),
            'change_pct': change_pct,
            'trend': 'up' if change_pct > 0 else 'down' if change_pct < 0 else 'flat',
            'min': min(prices),
            'max': max(prices),
            'current': end_price
        }
    except Exception as e:
        return None

# ===================== SECTOR PERFORMANCE =====================

@st.cache_data(ttl=300)
def fetch_sector_performance():
    """
    Récupère la performance des secteurs via les ETFs sectoriels
    
    Returns:
        dict: {sector_name: {'price': float, 'change_1d': float, 'change_5d': float, 'change_1m': float}}
    """
    sector_etfs = {
        'Technology': 'XLK',
        'Healthcare': 'XLV',
        'Financials': 'XLF',
        'Energy': 'XLE',
        'Consumer Disc.': 'XLY',
        'Consumer Staples': 'XLP',
        'Industrials': 'XLI',
        'Materials': 'XLB',
        'Utilities': 'XLU',
        'Real Estate': 'XLRE',
        'Communication': 'XLC'
    }
    
    sector_data = {}
    
    try:
        # Fetch all sector ETFs at once
        symbols = list(sector_etfs.values())
        data = yf.download(symbols, period="1mo", progress=False)
        
        for sector_name, etf_symbol in sector_etfs.items():
            try:
                if isinstance(data.columns, pd.MultiIndex):
                    closes = data['Close'][etf_symbol].dropna()
                else:
                    closes = data['Close'].dropna()
                
                if len(closes) >= 2:
                    current = closes.iloc[-1]
                    prev_1d = closes.iloc[-2] if len(closes) >= 2 else current
                    prev_5d = closes.iloc[-5] if len(closes) >= 5 else closes.iloc[0]
                    prev_1m = closes.iloc[0]
                    
                    sector_data[sector_name] = {
                        'symbol': etf_symbol,
                        'price': current,
                        'change_1d': ((current - prev_1d) / prev_1d) * 100,
                        'change_5d': ((current - prev_5d) / prev_5d) * 100,
                        'change_1m': ((current - prev_1m) / prev_1m) * 100
                    }
            except:
                pass
    except:
        pass
    
    return sector_data

# ===================== REGIONAL MARKETS =====================

@st.cache_data(ttl=300)
def fetch_regional_markets():
    """
    Récupère la performance des marchés régionaux
    
    Returns:
        dict: {region: {index_name: {'price': float, 'change': float}}}
    """
    regional_indices = {
        'Americas': {
            'S&P 500': '^GSPC',
            'Dow Jones': '^DJI',
            'NASDAQ': '^IXIC',
            'TSX (Canada)': '^GSPTSE',
            'Bovespa (Brazil)': '^BVSP'
        },
        'Europe': {
            'FTSE 100': '^FTSE',
            'DAX': '^GDAXI',
            'CAC 40': '^FCHI',
            'Euro Stoxx 50': '^STOXX50E',
            'IBEX 35': '^IBEX'
        },
        'Asia-Pacific': {
            'Nikkei 225': '^N225',
            'Hang Seng': '^HSI',
            'Shanghai': '000001.SS',
            'ASX 200': '^AXJO',
            'KOSPI': '^KS11'
        }
    }
    
    regional_data = {}
    
    for region, indices in regional_indices.items():
        regional_data[region] = {}
        
        try:
            symbols = list(indices.values())
            data = yf.download(symbols, period="5d", progress=False)
            
            for index_name, symbol in indices.items():
                try:
                    if isinstance(data.columns, pd.MultiIndex):
                        closes = data['Close'][symbol].dropna()
                    else:
                        closes = data['Close'].dropna()
                    
                    if len(closes) >= 2:
                        current = closes.iloc[-1]
                        previous = closes.iloc[-2]
                        change = ((current - previous) / previous) * 100
                        
                        regional_data[region][index_name] = {
                            'symbol': symbol,
                            'price': current,
                            'change': change
                        }
                except:
                    pass
        except:
            pass
    
    return regional_data

