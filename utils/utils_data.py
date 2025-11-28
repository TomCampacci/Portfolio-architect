# utils_data.py - Data loading and processing functions
import os, glob, numpy as np, pandas as pd
from datetime import datetime

def read_csv_file(path: str) -> pd.Series:
    """Accepte Time/Date/Datetime, Close/Adj Close (insensible à la casse)."""
    df = pd.read_csv(path)
    cols = {c.lower(): c for c in df.columns}
    dt = cols.get("time") or cols.get("date") or cols.get("datetime")
    cl = cols.get("close") or cols.get("adj close") or cols.get("adj_close")
    if dt is None or cl is None:
        raise ValueError("Missing time/close columns")
    idx = pd.to_datetime(df[dt], utc=True, errors="coerce")
    s = pd.Series(df[cl].astype(float).values, index=idx)
    s = s.tz_convert(None).sort_index()
    s = s[~s.index.duplicated(keep="last")].dropna()
    return s.rename(os.path.splitext(os.path.basename(path))[0])

def load_prices_from_dir(data_dir: str) -> pd.DataFrame:
    files = glob.glob(os.path.join(data_dir, "*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV found in {data_dir}")
    series = []
    for f in files:
        try: series.append(read_csv_file(f))
        except Exception as e:
            print(f"Skip {os.path.basename(f)}: {e}")
    return pd.concat(series, axis=1).sort_index()

def align_business_days(prices: pd.DataFrame) -> pd.DataFrame:
    idx = pd.date_range(prices.index.min(), prices.index.max(), freq="B")
    return prices.reindex(idx).ffill()

def slice_recent_safe(prices: pd.DataFrame, years: int, min_rows: int = 60) -> pd.DataFrame:
    if not years or years <= 0: return prices
    end = prices.index.max(); start = end - pd.DateOffset(years=years)
    out = prices.loc[prices.index >= start]
    if len(out) < min_rows: return prices
    return out

def bench_daily(prices: pd.DataFrame, col: str) -> pd.Series:
    """Calculate daily benchmark returns."""
    return np.log(prices[col] / prices[col].shift(1))

# ===================== CSV CONFIG LOADERS (Agnostic) =====================
def _normalize_columns(df: pd.DataFrame) -> dict:
    """Build a case-insensitive column map for flexible CSV headers."""
    return {c.lower().strip(): c for c in df.columns}

def load_weights_config(weights_csv_path: str):
    """
    Load portfolio weights and optional sector/color mapping from a CSV.

    Accepted headers (case-insensitive):
      - ticker | symbol
      - weight | w
      - sector (optional)
      - color  (optional)

    Returns:
      weights_dict, sector_mapping (or {}), sector_colors (or {})
    """
    if not os.path.exists(weights_csv_path):
        raise FileNotFoundError(f"Weights CSV not found: {weights_csv_path}")

    df = pd.read_csv(weights_csv_path)
    cols = _normalize_columns(df)

    ticker_col = cols.get("ticker") or cols.get("symbol")
    weight_col = cols.get("weight") or cols.get("w")
    sector_col = cols.get("sector")
    color_col  = cols.get("color")

    if ticker_col is None or weight_col is None:
        raise ValueError("Weights CSV must contain 'ticker' (or 'symbol') and 'weight' (or 'w') columns")

    # Clean and aggregate by ticker in case of duplicates
    df = df[[ticker_col, weight_col] + ([sector_col] if sector_col else []) + ([color_col] if color_col else [])].copy()
    df[weight_col] = pd.to_numeric(df[weight_col], errors="coerce").fillna(0.0)
    df[ticker_col] = df[ticker_col].astype(str).str.strip()
    df = df.groupby(ticker_col, as_index=False).agg({weight_col: "sum", **({sector_col: "last"} if sector_col else {}), **({color_col: "last"} if color_col else {})})

    # Normalize weights to sum to 1.0
    total = float(df[weight_col].sum())
    if total <= 0:
        raise ValueError("Sum of weights must be > 0 in weights CSV")
    df[weight_col] = df[weight_col] / total

    weights = {row[ticker_col]: float(row[weight_col]) for _, row in df.iterrows()}
    sector_mapping = {row[ticker_col]: str(row[sector_col]) for _, row in df.iterrows()} if sector_col else {}
    sector_colors  = {}

    if color_col:
        # Build color map keyed by sector if both provided, else by ticker
        if sector_col:
            for _, row in df.iterrows():
                sec = str(row[sector_col])
                col = str(row[color_col])
                if sec and col and sec not in sector_colors:
                    sector_colors[sec] = col
        else:
            # Fallback: map ticker->color
            sector_colors = {row[ticker_col]: str(row[color_col]) for _, row in df.iterrows() if str(row[color_col])}

    return weights, sector_mapping, sector_colors

def load_benchmarks_config(bench_csv_path: str):
    """
    Load benchmark definitions from a CSV.

    Accepted headers (case-insensitive):
      - label | name
      - ticker | symbol

    Returns:
      List of (label, ticker)
    """
    if not os.path.exists(bench_csv_path):
        raise FileNotFoundError(f"Benchmarks CSV not found: {bench_csv_path}")

    df = pd.read_csv(bench_csv_path)
    cols = _normalize_columns(df)

    label_col  = cols.get("label") or cols.get("name")
    ticker_col = cols.get("ticker") or cols.get("symbol")

    if label_col is None or ticker_col is None:
        raise ValueError("Benchmarks CSV must contain 'label' (or 'name') and 'ticker' (or 'symbol') columns")

    df = df[[label_col, ticker_col]].dropna()
    df[label_col] = df[label_col].astype(str).strip()
    df[ticker_col] = df[ticker_col].astype(str).strip()

    # Remove duplicates while preserving order
    seen = set(); out = []
    for _, row in df.iterrows():
        key = (row[label_col], row[ticker_col])
        if key not in seen:
            out.append((row[label_col], row[ticker_col]))
            seen.add(key)
    return out

# ===================== Yahoo Finance helpers (Step 1 only) =====================
def _import_yfinance():
    """Safely import yfinance with a clear error if missing."""
    try:
        import yfinance as yf  # type: ignore
        return yf
    except Exception as exc:
        raise ImportError("yfinance is required. Install with: pip install yfinance") from exc

# ===================== European suffix auto-resolution =====================
_EU_SUFFIX_CACHE_FILE = "data/eu_suffix_cache.json"
_EU_SUFFIX_CACHE = {}
_EU_SUFFIXES_PRIORITY = [
    ".PA",  # Euronext Paris (Amundi, Lyxor ETFs)
    ".MI",  # Milan (Borsa Italiana)
    ".DE",  # XETRA/Frankfurt (German ETFs)
    ".AS",  # Amsterdam (Euronext Amsterdam)
    ".L",   # London Stock Exchange
    ".SW",  # Swiss Exchange
    ".MC",  # Madrid (BME)
    ".BR",  # Brussels (Euronext Brussels)
]

def _load_suffix_cache():
    """Load European suffix cache from disk."""
    global _EU_SUFFIX_CACHE
    if _EU_SUFFIX_CACHE:
        return  # Already loaded
    try:
        if os.path.exists(_EU_SUFFIX_CACHE_FILE):
            import json
            with open(_EU_SUFFIX_CACHE_FILE, 'r') as f:
                _EU_SUFFIX_CACHE = json.load(f)
    except Exception:
        _EU_SUFFIX_CACHE = {}

def _save_suffix_cache():
    """Save European suffix cache to disk."""
    try:
        import json
        with open(_EU_SUFFIX_CACHE_FILE, 'w') as f:
            json.dump(_EU_SUFFIX_CACHE, f, indent=2)
    except Exception:
        pass

def auto_resolve_european_suffix(base_symbol: str, return_name: bool = False):
    """
    Automatically resolve European ticker by trying common suffixes.
    
    Args:
        base_symbol: Base ticker without suffix (e.g., "ANXU")
        return_name: If True, also return instrument name
    
    Returns:
        If return_name=False: resolved_symbol or None
        If return_name=True: (resolved_symbol, name) or (None, "")
    
    Example:
        >>> auto_resolve_european_suffix("ANXU")
        "ANXU.PA"
    """
    _load_suffix_cache()
    
    # Normalize input
    base = base_symbol.strip().upper()
    
    # Check cache first
    if base in _EU_SUFFIX_CACHE:
        cached = _EU_SUFFIX_CACHE[base]
        if return_name:
            return (cached, "")  # Name will be fetched separately if needed
        return cached
    
    # Try each suffix in priority order
    for suffix in _EU_SUFFIXES_PRIORITY:
        candidate = f"{base}{suffix}"
        try:
            # Quick validation check
            result = validate_yahoo_symbol(candidate, return_name=False)
            if result:
                # Found! Cache it
                _EU_SUFFIX_CACHE[base] = candidate
                _save_suffix_cache()
                
                if return_name:
                    name = get_instrument_name(candidate)
                    return (candidate, name)
                return candidate
        except Exception:
            continue
    
    # No valid suffix found
    return (None, "") if return_name else None

def get_instrument_name(symbol: str) -> str:
    """
    Get the long name of an instrument from Yahoo Finance.
    Returns empty string if not found.
    """
    try:
        yf = _import_yfinance()
        ticker = yf.Ticker(symbol)
        info = ticker.info
        # Try multiple name fields
        name = info.get("longName") or info.get("shortName") or info.get("name") or ""
        return name
    except Exception:
        return ""

def validate_yahoo_symbol(symbol: str, return_name: bool = False) -> bool | tuple:
    """
    Validate a Yahoo Finance symbol via a lightweight fetch.
    Tries 1y then max if needed. Always returns a bool or (bool, name) if return_name=True.
    """
    try:
        yf = _import_yfinance()
    except Exception:
        return (False, "") if return_name else False
    try:
        data = yf.download(symbol, period="1y", progress=False, auto_adjust=True)
        if (data is None) or data.empty or ("Close" not in getattr(data, "columns", [])):
            data = yf.download(symbol, period="max", progress=False, auto_adjust=True)
        is_valid = (data is not None) and (not data.empty) and ("Close" in data.columns)
        
        if return_name and is_valid:
            name = get_instrument_name(symbol)
            return (True, name)
        return (is_valid, "") if return_name else is_valid
    except Exception:
        return (False, "") if return_name else False

def fetch_prices_yahoo(tickers, start_date=None, end_date=None):
    """
    Fetch adjusted close prices from Yahoo Finance.

    Args:
        tickers: str or List[str]
        start_date: optional datetime-like
        end_date: optional datetime-like

    Returns:
        pd.DataFrame with DatetimeIndex and columns per ticker (Close prices)
    """
    import pandas as pd  # local import to avoid global dependency order
    yf = _import_yfinance()

    # Normalize tickers input
    if isinstance(tickers, str):
        tickers_list = [tickers]
    else:
        tickers_list = list(tickers)

    # Determine download parameters
    kwargs = {
        "tickers": tickers_list,
        "progress": False,
        "auto_adjust": True,
        "threads": True,
    }
    if start_date is not None or end_date is not None:
        kwargs["start"] = start_date
        kwargs["end"] = end_date
    else:
        kwargs["period"] = "max"

    data = yf.download(**kwargs)

    # Extract Close prices (handle single vs multi)
    if isinstance(data.columns, pd.MultiIndex):
        prices = data.get("Close")
    else:
        # Single ticker case: ensure DataFrame with proper column name
        if "Close" not in data.columns:
            raise RuntimeError("Unexpected Yahoo Finance response: 'Close' column missing")
        prices = pd.DataFrame(data["Close"]).copy()
        prices.columns = [tickers_list[0]]

    # Clean
    prices = prices.dropna(how="all").sort_index()
    # Ensure tz-naive index
    if getattr(prices.index, "tz", None) is not None:
        prices.index = prices.index.tz_localize(None)
    # Drop duplicate index entries, keep last
    if prices.index.has_duplicates:
        prices = prices[~prices.index.duplicated(keep="last")]

    return prices

def fetch_risk_free_rate():
    """
    Fetch the current risk-free rate using FRED API (Federal Reserve Economic Data).
    
    Primary source: FRED API for official SOFR (Secured Overnight Financing Rate)
    Fallback hierarchy:
    1. FRED API - SOFR (official Federal Reserve data)
    2. ^IRX - 13 Week Treasury Bill yield (Yahoo Finance)
    3. 4.33% - Default fallback (approximate current SOFR rate)
    
    To use FRED API, set environment variable: FRED_API_KEY
    Get a free API key at: https://fred.stlouisfed.org/docs/api/api_key.html
    
    Returns:
        tuple: (rate_decimal, rate_source, rate_date)
        Example: (0.0433, "SOFR (FRED)", "2024-10-19")
    """
    import pandas as pd
    from datetime import datetime, timedelta
    import os
    
    # Try FRED API first (requires API key)
    fred_api_key = os.getenv("FRED_API_KEY")
    
    if fred_api_key:
        try:
            import requests
            
            # Fetch SOFR from FRED (series ID: SOFR)
            url = f"https://api.stlouisfed.org/fred/series/observations"
            params = {
                "series_id": "SOFR",
                "api_key": fred_api_key,
                "file_type": "json",
                "sort_order": "desc",
                "limit": 1  # Get only the most recent observation
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "observations" in data and len(data["observations"]) > 0:
                    observation = data["observations"][0]
                    rate_str = observation.get("value")
                    date_str = observation.get("date")
                    
                    if rate_str and rate_str != ".":  # FRED uses "." for missing values
                        rate_pct = float(rate_str)
                        rate_decimal = rate_pct / 100.0
                        
                        print(f"[Risk-Free Rate] Using SOFR from FRED: {rate_pct:.2f}% (as of {date_str})")
                        return (rate_decimal, "SOFR (FRED)", date_str)
        except Exception as e:
            print(f"[Risk-Free Rate] Could not fetch SOFR from FRED: {e}")
    else:
        print("[Risk-Free Rate] FRED_API_KEY not found. Set it to use official SOFR data.")
        print("                 Get free API key: https://fred.stlouisfed.org/docs/api/api_key.html")
    
    # Fallback 1: Try 13-week Treasury Bill (^IRX) from Yahoo Finance
    yf = _import_yfinance()
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=10)
        
        irx = yf.download("^IRX", start=start_date, end=end_date, progress=False, auto_adjust=True)
        
        if not irx.empty and 'Close' in irx.columns:
            latest_rate = irx['Close'].dropna().iloc[-1]
            latest_date = pd.Timestamp(irx['Close'].dropna().index[-1]).strftime('%Y-%m-%d')
            
            rate_decimal = latest_rate / 100.0
            
            print(f"[Risk-Free Rate] Using 13-Week T-Bill: {latest_rate:.2f}% (as of {latest_date})")
            return (rate_decimal, "13-Week T-Bill (^IRX)", latest_date)
    except Exception as e:
        print(f"[Risk-Free Rate] Could not fetch ^IRX: {e}")
    
    # Fallback 2: Default rate (current SOFR rate as of Oct 2024)
    default_rate = 0.0433  # 4.33% - approximate current SOFR rate
    print(f"[Risk-Free Rate] Using default rate: {default_rate*100:.2f}% (SOFR proxy)")
    return (default_rate, "Default (4.33% - SOFR proxy)", datetime.now().strftime('%Y-%m-%d'))

def fetch_prices_stooq(tickers, start_date=None, end_date=None):
    """
    Fetch EOD close prices from Stooq via pandas-datareader.
    Tries each ticker individually and concatenates available series.
    """
    import pandas as pd
    try:
        from pandas_datareader import data as pdr
    except Exception as exc:
        raise ImportError("pandas-datareader is required for Stooq. Install with: pip install pandas-datareader") from exc

    if isinstance(tickers, str):
        tickers_list = [tickers]
    else:
        tickers_list = list(tickers)

    series_list = []
    for sym in tickers_list:
        try:
            df = pdr.DataReader(sym, "stooq", start=start_date, end=end_date)
            # Stooq often returns descending index; ensure ascending
            df = df.sort_index()
            close_col = None
            for c in ["Close", "close", "Adj Close", "adjclose", "AdjClose"]:
                if c in df.columns:
                    close_col = c; break
            if close_col is None:
                continue
            s = pd.Series(df[close_col].astype(float).values, index=pd.to_datetime(df.index), name=sym)
            s = s.sort_index().dropna()
            series_list.append(s)
        except Exception:
            # Skip symbol on failure
            continue

    if not series_list:
        return pd.DataFrame()
    prices = pd.concat(series_list, axis=1)
    prices = prices.dropna(how="all").sort_index()
    if getattr(prices.index, "tz", None) is not None:
        prices.index = prices.index.tz_localize(None)
    if prices.index.has_duplicates:
        prices = prices[~prices.index.duplicated(keep="last")]
    return prices

def fetch_prices_alpha_vantage(tickers, start_date=None, end_date=None):
    """Optional: Fetch EOD from Alpha Vantage via pandas-datareader if API key present."""
    import os as _os
    import pandas as pd
    api_key = _os.getenv("ALPHAVANTAGE_API_KEY") or _os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        return pd.DataFrame()
    try:
        from pandas_datareader import data as pdr
    except Exception:
        return pd.DataFrame()

    if isinstance(tickers, str):
        tickers_list = [tickers]
    else:
        tickers_list = list(tickers)

    series_list = []
    for sym in tickers_list:
        got = False
        for src in ["av-daily-adjusted", "av-daily"]:
            try:
                df = pdr.DataReader(sym, src, start=start_date, end=end_date, api_key=api_key)
                df = df.sort_index()
                close_col = None
                for c in ["adjusted close", "close", "Adj Close", "adjclose", "AdjClose", "close"]:
                    if c in df.columns:
                        close_col = c; break
                if close_col is None:
                    continue
                s = pd.Series(df[close_col].astype(float).values, index=pd.to_datetime(df.index), name=sym)
                s = s.sort_index().dropna()
                series_list.append(s)
                got = True
                break
            except Exception:
                continue
        if not got:
            continue

    if not series_list:
        return pd.DataFrame()
    prices = pd.concat(series_list, axis=1)
    prices = prices.dropna(how="all").sort_index()
    if getattr(prices.index, "tz", None) is not None:
        prices.index = prices.index.tz_localize(None)
    if prices.index.has_duplicates:
        prices = prices[~prices.index.duplicated(keep="last")]
    return prices

def fetch_prices_tiingo(tickers, start_date=None, end_date=None):
    """Optional: Fetch EOD from Tiingo via pandas-datareader if API key present."""
    import os as _os
    import pandas as pd
    api_key = _os.getenv("TIINGO_API_KEY")
    if not api_key:
        return pd.DataFrame()
    try:
        from pandas_datareader import data as pdr
    except Exception:
        return pd.DataFrame()

    if isinstance(tickers, str):
        tickers_list = [tickers]
    else:
        tickers_list = list(tickers)

    series_list = []
    for sym in tickers_list:
        try:
            df = pdr.DataReader(sym, "tiingo", start=start_date, end=end_date, api_key=api_key)
            df = df.sort_index()
            close_col = None
            for c in ["adjClose", "close", "Adj Close", "adjclose", "AdjClose"]:
                if c in df.columns:
                    close_col = c; break
            if close_col is None:
                continue
            s = pd.Series(df[close_col].astype(float).values, index=pd.to_datetime(df.index), name=sym)
            s = s.sort_index().dropna()
            series_list.append(s)
        except Exception:
            continue

    if not series_list:
        return pd.DataFrame()
    prices = pd.concat(series_list, axis=1)
    prices = prices.dropna(how="all").sort_index()
    if getattr(prices.index, "tz", None) is not None:
        prices.index = prices.index.tz_localize(None)
    if prices.index.has_duplicates:
        prices = prices[~prices.index.duplicated(keep="last")]
    return prices

def fetch_prices_multi(tickers, start_date=None, end_date=None):
    """
    Unified fetcher that tries Yahoo first, then Stooq, then optional Alpha Vantage and Tiingo.
    Returns a DataFrame of Close prices with as many requested symbols as possible.
    """
    import pandas as pd
    # Normalize input
    if isinstance(tickers, str):
        req = [tickers]
    else:
        req = list(tickers)
    req = [t for t in req if t]
    if not req:
        return pd.DataFrame()

    collected = {}
    # Try Yahoo (batch)
    try:
        yf_df = fetch_prices_yahoo(req, start_date=start_date, end_date=end_date)
    except Exception:
        yf_df = pd.DataFrame()
    if not yf_df.empty:
        for c in yf_df.columns:
            s = yf_df[c].dropna()
            if not s.empty:
                collected[c] = s.rename(c)

    missing = [t for t in req if t not in collected]

    # Try Stooq (per symbol)
    if missing:
        try:
            stq_df = fetch_prices_stooq(missing, start_date=start_date, end_date=end_date)
        except Exception:
            stq_df = pd.DataFrame()
        if not stq_df.empty:
            for c in stq_df.columns:
                s = stq_df[c].dropna()
                if not s.empty and c not in collected:
                    collected[c] = s.rename(c)

    missing = [t for t in req if t not in collected]

    # Optional: Alpha Vantage
    if missing:
        av_df = fetch_prices_alpha_vantage(missing, start_date=start_date, end_date=end_date)
        if not av_df.empty:
            for c in av_df.columns:
                s = av_df[c].dropna()
                if not s.empty and c not in collected:
                    collected[c] = s.rename(c)

    missing = [t for t in req if t not in collected]

    # Optional: Tiingo
    if missing:
        ti_df = fetch_prices_tiingo(missing, start_date=start_date, end_date=end_date)
        if not ti_df.empty:
            for c in ti_df.columns:
                s = ti_df[c].dropna()
                if not s.empty and c not in collected:
                    collected[c] = s.rename(c)

    if not collected:
        return pd.DataFrame()
    prices = pd.concat(collected.values(), axis=1)
    prices = prices.dropna(how="all").sort_index()
    if getattr(prices.index, "tz", None) is not None:
        prices.index = prices.index.tz_localize(None)
    if prices.index.has_duplicates:
        prices = prices[~prices.index.duplicated(keep="last")]
    # Ensure requested column order
    cols = [c for c in req if c in prices.columns]
    return prices[cols]

# ===================== ISIN to Ticker conversion =====================
_ISIN_CACHE = {}

def is_isin(code: str) -> bool:
    """
    Check if a string is a valid ISIN code.
    ISIN format: 2-letter country code + 9 alphanumeric + 1 check digit (total 12 chars)
    """
    import re
    if not code or len(code) != 12:
        return False
    # Pattern: 2 letters + 10 alphanumeric
    pattern = re.compile(r'^[A-Z]{2}[A-Z0-9]{9}[0-9]$')
    return bool(pattern.match(code.upper()))

def isin_to_ticker_openfigi(isin: str, return_all_exchanges: bool = False):
    """
    Convert ISIN to Yahoo Finance ticker using OpenFIGI API (free, no key required).
    
    Args:
        isin: ISIN code to convert
        return_all_exchanges: If True, return all available exchanges; if False, return best match only
    
    Returns:
        If return_all_exchanges=False: dict with keys: ticker (Yahoo format), name, exchange, or None if not found
        If return_all_exchanges=True: list of dicts with all exchanges, or None if not found
    """
    import requests
    import time
    
    # Check cache first (only for single ticker mode)
    if not return_all_exchanges and isin in _ISIN_CACHE:
        return _ISIN_CACHE[isin]
    
    url = "https://api.openfigi.com/v3/mapping"
    headers = {"Content-Type": "application/json"}
    payload = [{
        "idType": "ID_ISIN",
        "idValue": isin
        # Don't include exchCode to get all exchanges
    }]
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        if resp.status_code != 200:
            print(f"OpenFIGI API error for {isin}: {resp.status_code}")
            return None
        
        data = resp.json()
        if not data or not isinstance(data, list) or len(data) == 0:
            return None
        
        # Get first result
        result = data[0]
        if "error" in result:
            print(f"OpenFIGI error for {isin}: {result.get('error')}")
            return None
        
        figi_data = result.get("data", [])
        if not figi_data:
            return None
        
        # Priority: Find ticker with Yahoo-compatible exchange
        # Common Yahoo suffixes: .PA (Paris), .MI (Milan), .L (London), .AS (Amsterdam), etc.
        yahoo_exchange_map = {
            "PA": ".PA",    # Euronext Paris
            "FP": ".PA",    # Paris
            "MI": ".MI",    # Milan
            "IM": ".MI",    # Milan
            "LN": ".L",     # London
            "AS": ".AS",    # Amsterdam
            "NA": ".AS",    # Amsterdam
            "BB": ".BR",    # Brussels
            "SM": ".MC",    # Madrid
            "SW": ".SW",    # Swiss
            "GR": ".DE",    # XETRA/Frankfurt
            "GY": ".DE",    # XETRA
            "US": "",       # US stocks (no suffix)
            "UN": "",       # NYSE
            "UW": "",       # Nasdaq
        }
        
        all_matches = []
        best_match = None
        us_match = None
        
        for item in figi_data:
            ticker = item.get("ticker", "")
            name = item.get("name", "")
            exch_code = item.get("exchCode", "")
            market_sector = item.get("marketSector", "")
            
            if not ticker:
                continue
            
            # Filter out OTC markets - focus on major exchanges only
            if exch_code and any(otc in exch_code.upper() for otc in ["OTC", "PINK", "GREY"]):
                continue
            if market_sector and any(otc in market_sector.upper() for otc in ["OTC", "PINK"]):
                continue
            
            # Build Yahoo ticker
            yahoo_ticker = ticker
            if exch_code in yahoo_exchange_map:
                suffix = yahoo_exchange_map[exch_code]
                yahoo_ticker = f"{ticker}{suffix}" if suffix else ticker
            
            match_info = {
                "ticker": yahoo_ticker,
                "name": name,
                "exchange": exch_code,
                "market_sector": market_sector,
                "raw_ticker": ticker
            }
            
            all_matches.append(match_info)
            
            # Prioritize US exchanges (most reliable on Yahoo)
            if exch_code in ["US", "UN", "UW"]:
                us_match = match_info
            
            # Otherwise take first valid match
            if not best_match:
                best_match = match_info
        
        # Return all exchanges if requested
        if return_all_exchanges:
            # Rate limiting: OpenFIGI allows 25 req/minute for free tier
            time.sleep(0.05)  # 50ms delay
            return all_matches if all_matches else None
        
        # Prefer US match if available, otherwise best match
        final = us_match or best_match
        
        if final:
            # Cache result
            _ISIN_CACHE[isin] = final
            # Rate limiting: OpenFIGI allows 25 req/minute for free tier
            time.sleep(0.05)  # 50ms delay
            return final
        
        return None
        
    except Exception as e:
        print(f"Error converting ISIN {isin}: {e}")
        return None

def isin_to_ticker(isin: str, fallback_search: bool = True) -> dict:
    """
    Main ISIN to ticker converter with fallback strategies.
    
    Args:
        isin: ISIN code (12 characters)
        fallback_search: If True, try Yahoo search as fallback
    
    Returns:
        dict with ticker, name, exchange or None
    """
    if not is_isin(isin):
        return None
    
    # Try OpenFIGI first
    result = isin_to_ticker_openfigi(isin)
    
    # Fallback: Try Yahoo search with ISIN (sometimes works)
    if not result and fallback_search:
        try:
            search_results = search_yahoo_symbols(isin, count=5)
            if search_results:
                first = search_results[0]
                result = {
                    "ticker": first["symbol"],
                    "name": first["name"],
                    "exchange": first.get("exchange", ""),
                    "source": "yahoo_search"
                }
        except Exception:
            pass
    
    return result

def convert_isin_list(identifiers: list) -> dict:
    """
    Convert a list of identifiers (mixed ISIN/tickers) to Yahoo tickers.
    
    Returns:
        dict mapping original identifier -> {ticker, name, is_isin}
    """
    result = {}
    for ident in identifiers:
        ident = ident.strip().upper()
        if is_isin(ident):
            conversion = isin_to_ticker(ident)
            if conversion:
                result[ident] = {
                    "ticker": conversion["ticker"],
                    "name": conversion["name"],
                    "is_isin": True,
                    "original": ident
                }
            else:
                result[ident] = {
                    "ticker": None,
                    "name": f"ISIN {ident} not found",
                    "is_isin": True,
                    "original": ident,
                    "error": True
                }
        else:
            # Keep as-is (assume it's already a ticker)
            result[ident] = {
                "ticker": ident,
                "name": "",
                "is_isin": False,
                "original": ident
            }
    return result

# ===================== Yahoo symbol search (autocomplete) =====================
_YAHOO_SEARCH_CACHE = {}

def search_symbol_all_exchanges(query: str, max_results: int = 10):
    """
    Search for a symbol across all exchanges and return all variants.
    Used to show exchange selection popup for stocks/ETFs.
    
    Args:
        query: Symbol to search (e.g., "LVMH", "TTE", "NVDA")
        max_results: Maximum number of results to return
    
    Returns:
        list: List of dicts with {symbol, name, exchange, type, currency}
              Returns None if no results or only one exact match
    """
    import requests
    
    q = (query or "").strip().upper()
    if not q:
        return None
    
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {
        "q": q,
        "quotesCount": 25,  # Get more results to find all exchanges
        "lang": "en-US",
        "region": "US"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=6)
        if resp.status_code != 200:
            return None
        
        data = resp.json() or {}
        quotes = data.get("quotes", [])
        
        if not quotes:
            return None
        
        # Filter and normalize results
        results = []
        seen_symbols = set()
        base_name = None  # We'll use the first name as reference
        
        for item in quotes:
            symbol = (item.get("symbol") or "").strip()
            if not symbol or symbol in seen_symbols:
                continue
            
            name = item.get("shortname") or item.get("longname") or item.get("name") or ""
            exchange = item.get("exchDisp") or item.get("exchange") or ""
            quote_type = (item.get("quoteType") or item.get("typeDisp") or "").upper()
            
            # Only include stocks, ETFs, and indexes
            if quote_type not in ["EQUITY", "ETF", "INDEX", "MUTUALFUND"]:
                continue
            
            # Filter to ONLY major exchanges - exclude OTC and minor exchanges
            # Major exchanges: NYSE, NASDAQ, Euronext (Paris, Amsterdam, Brussels, Milan), LSE, XETRA, Swiss, etc.
            exchange_upper = exchange.upper()
            
            # Exclude OTC markets
            if any(otc in exchange_upper for otc in ["OTC", "PINK", "GREY", "OTCBB"]):
                continue
            
            # Focus on major exchanges only (whitelist approach)
            major_exchanges = [
                "NYSE", "NASDAQ", "NMS", "NGM", "NCM",  # US major exchanges
                "EURONEXT", "PAR", "AMS", "BRU",  # Euronext (Paris, Amsterdam, Brussels)
                "LSE", "LON",  # London Stock Exchange
                "XETRA", "GER", "FRA", "DUS", "STU",  # German exchanges
                "SWX", "VTX",  # Swiss Exchange
                "BIT", "MIL",  # Borsa Italiana (Milan)
                "BME", "MCE",  # Bolsa de Madrid
                "TSE", "TYO",  # Tokyo Stock Exchange
                "HKEX", "HKG",  # Hong Kong Exchange
                "ASX",  # Australian Securities Exchange
                "TSX",  # Toronto Stock Exchange
            ]
            
            is_major_exchange = any(major in exchange_upper for major in major_exchanges)
            if not is_major_exchange:
                continue
            
            # Store base name from first result
            if not base_name and name:
                base_name = name
            
            # Check if this is a variant of the same instrument
            # (same base name or similar symbol)
            symbol_base = symbol.split('.')[0].upper()
            query_upper = q.upper()
            
            # Include if:
            # 1. Symbol starts with query (e.g., LVMH for LVMH, MC.PA)
            # 2. Symbol base matches query
            # 3. Has similar name to first result
            if (symbol_base == query_upper or 
                symbol.upper().startswith(query_upper) or
                (base_name and name and base_name.lower() in name.lower())):
                
                # Detect currency from exchange and symbol suffix
                currency = "USD"  # Default
                exchange_clean = exchange.upper()
                
                # EUR - Eurozone exchanges
                if any(x in symbol for x in [".PA", ".MI", ".AS", ".BR", ".MC", ".DE", ".VI", ".HE", ".LS"]):
                    currency = "EUR"
                elif any(x in exchange_clean for x in ["EURONEXT", "XETRA", "BORSA", "BME", "MILAN", "MADRID", "FRANKFURT", "PARIS", "AMSTERDAM", "BRUSSELS"]):
                    currency = "EUR"
                # GBP - UK exchanges
                elif ".L" in symbol or "LSE" in exchange_clean or "LONDON" in exchange_clean:
                    currency = "GBP"
                # CHF - Swiss exchanges
                elif ".SW" in symbol or "SWX" in exchange_clean or "VTX" in exchange_clean or "SWISS" in exchange_clean:
                    currency = "CHF"
                # JPY - Japanese exchanges
                elif ".T" in symbol or "TSE" in exchange_clean or "TOKYO" in exchange_clean:
                    currency = "JPY"
                # HKD - Hong Kong
                elif ".HK" in symbol or "HKEX" in exchange_clean or "HONG KONG" in exchange_clean:
                    currency = "HKD"
                # AUD - Australian exchanges
                elif ".AX" in symbol or "ASX" in exchange_clean:
                    currency = "AUD"
                # CAD - Canadian exchanges
                elif ".TO" in symbol or "TSX" in exchange_clean or "TORONTO" in exchange_clean:
                    currency = "CAD"
                
                # Enhance exchange name for clarity
                exchange_display = exchange
                if "NASDAQ" in exchange_clean:
                    exchange_display = "NASDAQ (US)"
                elif "NYSE" in exchange_clean:
                    exchange_display = "NYSE (US)"
                elif "EURONEXT" in exchange_clean or "PAR" in exchange_clean:
                    exchange_display = "Euronext Paris"
                elif "AMS" in exchange_clean:
                    exchange_display = "Euronext Amsterdam"
                elif "BRU" in exchange_clean:
                    exchange_display = "Euronext Brussels"
                elif "LSE" in exchange_clean or "LON" in exchange_clean:
                    exchange_display = "London Stock Exchange"
                elif "XETRA" in exchange_clean or "FRA" in exchange_clean:
                    exchange_display = "XETRA (Germany)"
                elif "SWX" in exchange_clean or "VTX" in exchange_clean:
                    exchange_display = "Swiss Exchange"
                elif "MIL" in exchange_clean or "BIT" in exchange_clean:
                    exchange_display = "Borsa Italiana (Milan)"
                elif "MCE" in exchange_clean or "BME" in exchange_clean:
                    exchange_display = "Bolsa de Madrid"
                
                results.append({
                    "symbol": symbol,
                    "name": name,
                    "exchange": exchange_display,
                    "type": quote_type,
                    "currency": currency
                })
                seen_symbols.add(symbol)
        
        # If we only found one result or no results, return None (no need for selection)
        if len(results) <= 1:
            return None
        
        # Sort by relevance: exact match first, then others
        def sort_key(r):
            sym = r["symbol"].upper()
            if sym == q:
                return (0, sym)  # Exact match first
            elif sym.startswith(q):
                return (1, sym)  # Starts with query
            else:
                return (2, sym)  # Others
        
        results.sort(key=sort_key)
        
        return results[:max_results]
        
    except Exception as e:
        print(f"Error searching for {query}: {e}")
        return None

def search_yahoo_symbols(
    query: str,
    count: int = 10,
    lang: str = "en-US",
    region: str = "US",
    include_futures: bool = True,
    allowed_types: list | None = None,
):
    """
    Lightweight Yahoo symbol search used for autocomplete suggestions.
    - Filters by quote types (ETF/EQUITY/INDEX by default, optionally FUTURE).
    - Prioritizes startswith(query) over contains(query).
    Returns a list of dicts: {symbol, name, exchange, type}.
    """
    import time
    import requests
    q = (query or "").strip()
    if not q:
        return []
    key = (q.lower(), count, lang, region)
    now = time.time()
    cached = _YAHOO_SEARCH_CACHE.get(key)
    if cached and (now - cached[0] < 60.0):  # 60s TTL
        return cached[1]
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": q, "quotesCount": count, "lang": lang, "region": region}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://finance.yahoo.com/"
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=6)
        if resp.status_code != 200:
            # Rate limited or blocked - return empty, heuristics will be used
            return []
        data = resp.json() or {}
        quotes = data.get("quotes", [])
        # Normalize and filter by type
        default_types = ["ETF", "EQUITY", "INDEX"] + (["FUTURE"] if include_futures else [])
        allowed = [t.upper() for t in (allowed_types or default_types)]

        normalized = []
        for it in quotes:
            sym = (it.get("symbol") or "").strip()
            if not sym:
                continue
            name = it.get("shortname") or it.get("longname") or it.get("name") or ""
            exch = it.get("exchDisp") or it.get("exchange") or ""
            qtype = (it.get("quoteType") or it.get("typeDisp") or "").upper()
            if allowed and qtype and qtype not in allowed:
                continue
            normalized.append({"symbol": sym, "name": name, "exchange": exch, "type": qtype})

        # Rank: startswith first, then contains
        low = q.lower()
        starts = [r for r in normalized if r["symbol"].lower().startswith(low)]
        contains = [r for r in normalized if (low in r["symbol"].lower()) and (r not in starts)]
        ranked = starts + contains

        # Deduplicate by symbol preserving order
        seen = set(); out = []
        for r in ranked:
            if r["symbol"] in seen:
                continue
            out.append(r); seen.add(r["symbol"])
        out = out[:count]
        _YAHOO_SEARCH_CACHE[key] = (now, out)
        return out
    except Exception:
        return []

# ===================== Heuristic suggestions =====================
_EU_SUFFIXES = [".PA", ".MI", ".L", ".AS", ".DE", ".SW", ".MC", ".BR"]

# Popular company name to ticker mapping
_COMPANY_SUGGESTIONS = {
    # US Tech Giants
    "apple": ["AAPL"],
    "microsoft": ["MSFT"],
    "google": ["GOOGL", "GOOG"],
    "alphabet": ["GOOGL", "GOOG"],
    "amazon": ["AMZN"],
    "tesla": ["TSLA"],
    "meta": ["META"],
    "facebook": ["META"],
    "nvidia": ["NVDA"],
    "amd": ["AMD"],
    "intel": ["INTC"],
    "netflix": ["NFLX"],
    "paypal": ["PYPL"],
    "salesforce": ["CRM"],
    "adobe": ["ADBE"],
    "oracle": ["ORCL"],
    "cisco": ["CSCO"],
    "ibm": ["IBM"],
    
    # Finance
    "visa": ["V"],
    "mastercard": ["MA"],
    "jpmorgan": ["JPM"],
    "bank of america": ["BAC"],
    "goldman": ["GS"],
    "morgan stanley": ["MS"],
    "wells fargo": ["WFC"],
    "american express": ["AXP"],
    "paypal": ["PYPL"],
    
    # European Companies
    "total": ["TTE", "TTE.PA"],
    "totalenergies": ["TTE", "TTE.PA"],
    "lvmh": ["MC.PA"],
    "hermes": ["RMS.PA"],
    "sap": ["SAP.DE", "SAP"],
    "siemens": ["SIE.DE"],
    "bmw": ["BMW.DE"],
    "volkswagen": ["VOW3.DE"],
    "mercedes": ["MBG.DE"],
    "airbus": ["AIR.PA"],
    "nestle": ["NESN.SW"],
    "novartis": ["NOVN.SW"],
    "roche": ["ROG.SW"],
    "bnp": ["BNP.PA"],
    "bnp paribas": ["BNP.PA"],
    "credit agricole": ["ACA.PA"],
    "societe generale": ["GLE.PA"],
    "axa": ["CS.PA"],
    "allianz": ["ALV.DE"],
    "shell": ["SHEL", "SHEL.L"],
    "bp": ["BP", "BP.L"],
    
    # Asian Companies
    "toyota": ["TM"],
    "sony": ["SONY"],
    "nintendo": ["NTDOY"],
    "alibaba": ["BABA"],
    "tencent": ["TCEHY"],
    "samsung": ["005930.KS"],
}

_KEYWORD_SUGGESTIONS = {
    # Indexes
    "nasdaq": ["^NDX", "QQQ", "QQQM", "CSPX.L", "NQ=F"],
    "ndx": ["^NDX", "QQQ", "QQQM", "NQ=F"],
    "sp500": ["^GSPC", "SPY", "VOO", "CSPX.L"],
    "s&p": ["^GSPC", "SPY", "VOO", "CSPX.L"],
    "dow": ["^DJI"],
    "dax": ["^GDAXI", "EXS1.DE"],
    "cac": ["^FCHI"],
    "euro stoxx": ["^STOXX50E"],
    "nikkei": ["^N225"],
    "ibex": ["^IBEX"],
    # Commodities / futures tickers on Yahoo
    "gold": ["GC=F", "GLD"],
    "oil": ["CL=F", "USO"],
}

# Popular benchmark indexes for dropdown suggestions
_POPULAR_BENCHMARKS = [
    {"symbol": "^GSPC", "name": "S&P 500 (US Large Cap - 500 companies)"},
    {"symbol": "^IXIC", "name": "Nasdaq Composite (US Tech & Growth)"},
    {"symbol": "^DJI", "name": "Dow Jones Industrial (US Blue Chip - 30 companies)"},
    {"symbol": "^NDX", "name": "Nasdaq 100 (US Top 100 Tech & Innovation)"},
    {"symbol": "^GDAXI", "name": "DAX (Germany - Top 40 companies)"},
    {"symbol": "^FCHI", "name": "CAC 40 (France - Top 40 companies)"},
    {"symbol": "^FTSE", "name": "FTSE 100 (UK - Top 100 companies)"},
    {"symbol": "^STOXX50E", "name": "Euro Stoxx 50 (Eurozone - Top 50 companies)"},
    {"symbol": "^N225", "name": "Nikkei 225 (Japan - Top 225 companies)"},
    {"symbol": "^IBEX", "name": "IBEX 35 (Spain - Top 35 companies)"},
    {"symbol": "FTSEMIB.MI", "name": "FTSE MIB (Italy - Top 40 companies)"},
    {"symbol": "^HSI", "name": "Hang Seng (Hong Kong - Top companies)"},
    {"symbol": "GC=F", "name": "Gold Futures (Commodity benchmark)"},
    {"symbol": "CL=F", "name": "Crude Oil Futures (Energy benchmark)"},
]

def get_popular_benchmarks():
    """
    Get list of popular benchmark indexes for suggestions
    
    Returns:
        list: List of dicts with {symbol, name}
    """
    return _POPULAR_BENCHMARKS.copy()

def get_benchmark_display_name(symbol):
    """
    Get human-readable display name for a benchmark symbol
    
    Args:
        symbol: Ticker symbol (e.g., "^GSPC", "GC=F")
    
    Returns:
        str: Display name (e.g., "S&P 500", "Gold Futures")
    """
    # Check in popular benchmarks first
    for bench in _POPULAR_BENCHMARKS:
        if bench["symbol"] == symbol:
            # Extract just the main name without the details in parentheses
            name = bench["name"]
            # For cleaner chart labels, extract the core name
            if " (" in name:
                return name.split(" (")[0]
            return name
    
    # Fallback: return the symbol itself
    return symbol

def generate_symbol_heuristics(query: str, max_count: int = 8):
    """
    Generate heuristic symbol suggestions for autocomplete:
    - Company name to ticker mapping (e.g., "tesla" → TSLA)
    - EU exchange suffix combinations for ticker-like inputs
    - Keyword-based popular symbols (indices, futures, ETFs)
    Returns list of dicts: {symbol, name}
    """
    q = (query or "").strip()
    if not q:
        return []
    out = []
    low = q.lower()

    # Company name suggestions (highest priority)
    for company_name, tickers in _COMPANY_SUGGESTIONS.items():
        if company_name in low or low in company_name:
            for ticker in tickers:
                out.append({"symbol": ticker, "name": company_name.title()})

    # Keyword suggestions (indices, commodities)
    for key, symbols in _KEYWORD_SUGGESTIONS.items():
        if key in low:
            for s in symbols:
                out.append({"symbol": s, "name": ""})

    # EU suffix heuristics for ticker-like short inputs
    # If user typed a short base (<= 6 chars, alnum), propose base + EU suffixes
    base = q.upper()
    if 1 <= len(base) <= 6 and base.replace('-', '').replace('.', '').isalnum():
        # Don't add EU suffixes if we already have company suggestions
        if not any(r.get("name") for r in out):
            for suf in _EU_SUFFIXES:
                out.append({"symbol": f"{base}{suf}", "name": ""})

    # Deduplicate preserving order and cap
    seen = set(); uniq = []
    for r in out:
        sym = r.get("symbol")
        if sym and sym not in seen:
            uniq.append(r); seen.add(sym)
    return uniq[:max_count]

# ===================== Persistence helpers =====================
def save_weights_csv(path: str, weights: dict, sector_mapping: dict = None, sector_colors: dict = None):
    """Save weights (and optional sector/color) to CSV."""
    import pandas as pd
    sector_mapping = sector_mapping or {}
    sector_colors = sector_colors or {}
    rows = []
    for t, w in weights.items():
        row = {
            "ticker": t,
            "weight": float(w),
        }
        if t in sector_mapping:
            row["sector"] = sector_mapping[t]
            # if sector color exists, prefer sector color; else ticker color (if any)
            if isinstance(sector_colors, dict) and sector_mapping[t] in sector_colors:
                row["color"] = sector_colors[sector_mapping[t]]
        rows.append(row)
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)

def save_benchmarks_csv(path: str, pairs: list):
    """Save benchmark pairs (label, ticker) to CSV."""
    import pandas as pd
    df = pd.DataFrame(pairs, columns=["label", "ticker"])
    df.to_csv(path, index=False)

def save_prices_to_dir(prices: pd.DataFrame, out_dir: str):
    """Cache prices DataFrame to CSV files (one file per column)."""
    import pandas as pd
    os.makedirs(out_dir, exist_ok=True)
    for col in prices.columns:
        s = prices[col].dropna()
        if s.empty:
            continue
        df = pd.DataFrame({
            "Date": s.index,
            "Close": s.values
        })
        # Ensure date formatted ISO
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
        out_path = os.path.join(out_dir, f"{col}.csv")
        df.to_csv(out_path, index=False)


# ===================== SECTOR DETECTION SYSTEM (Hybrid) =====================
_SECTOR_CACHE_FILE = "data/sectors_cache.json"
_SECTOR_CACHE = {}

def _load_sector_cache():
    """Load the persistent sector cache from JSON."""
    global _SECTOR_CACHE
    if os.path.exists(_SECTOR_CACHE_FILE):
        try:
            import json
            with open(_SECTOR_CACHE_FILE, "r", encoding="utf-8") as f:
                _SECTOR_CACHE = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load sector cache: {e}")
            _SECTOR_CACHE = {}

def _save_sector_cache():
    """Save the sector cache to JSON."""
    try:
        import json
        with open(_SECTOR_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_SECTOR_CACHE, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save sector cache: {e}")

def detect_asset_sector(ticker: str, manual_mapping: dict = None, default_sector: str = "Unknown"):
    """
    Detect the sector of an asset using a hybrid approach:
    1. Check manual mapping (from config.py or weights.csv)
    2. Check persistent cache (sectors_cache.json)
    3. Query Yahoo Finance API for sector info
    4. Return default if all fail
    
    Args:
        ticker: Asset ticker symbol
        manual_mapping: Optional manual sector mapping dict
        default_sector: Fallback sector if detection fails
    
    Returns:
        str: Detected sector name
    """
    # Load cache if not loaded yet
    if not _SECTOR_CACHE:
        _load_sector_cache()
    
    # Step 1: Check manual mapping
    if manual_mapping and ticker in manual_mapping:
        return manual_mapping[ticker]
    
    # Step 2: Check cache
    if ticker in _SECTOR_CACHE:
        return _SECTOR_CACHE[ticker]
    
    # Step 3: Query Yahoo Finance
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Try to get sector from info
        sector = info.get("sector", None)
        if sector:
            _SECTOR_CACHE[ticker] = sector
            _save_sector_cache()
            return sector
        
        # If no sector, try to infer from quote type
        quote_type = info.get("quoteType", "")
        if quote_type == "ETF":
            category = info.get("category", "")
            if category:
                _SECTOR_CACHE[ticker] = category
                _save_sector_cache()
                return category
        
        # Try industry as fallback
        industry = info.get("industry", None)
        if industry:
            _SECTOR_CACHE[ticker] = industry
            _save_sector_cache()
            return industry
            
    except Exception as e:
        print(f"Yahoo sector lookup failed for {ticker}: {e}")
    
    # Step 4: Return default
    return default_sector

# Initialize cache on import
_load_sector_cache()


# ===================== CURRENCY DETECTION SYSTEM (Hybrid) =====================
_CURRENCY_CACHE_FILE = "data/currency_cache.json"
_CURRENCY_CACHE = {}

# Manual mapping for known patterns
_SUFFIX_TO_CURRENCY = {
    ".PA": "EUR",  # Euronext Paris
    ".DE": "EUR",  # Xetra (Germany)
    ".MI": "EUR",  # Milan
    ".MC": "EUR",  # Madrid
    ".AS": "EUR",  # Amsterdam
    ".BR": "EUR",  # Brussels
    ".L": "GBP",   # London Stock Exchange
    ".IL": "GBP",  # London (alternative)
    ".SW": "CHF",  # Switzerland (if needed later)
    ".T": "JPY",   # Tokyo (if needed later)
}

def _load_currency_cache():
    """Load the persistent currency cache from JSON."""
    global _CURRENCY_CACHE
    if os.path.exists(_CURRENCY_CACHE_FILE):
        try:
            import json
            with open(_CURRENCY_CACHE_FILE, "r", encoding="utf-8") as f:
                _CURRENCY_CACHE = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load currency cache: {e}")
            _CURRENCY_CACHE = {}

def _save_currency_cache():
    """Save the currency cache to JSON."""
    try:
        import json
        with open(_CURRENCY_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_CURRENCY_CACHE, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save currency cache: {e}")

def detect_asset_currency(ticker: str, manual_mapping: dict = None, default_currency: str = "USD"):
    """
    Detect the currency of an asset using a hybrid approach:
    1. Check manual mapping (from config.py or user input)
    2. Check suffix patterns (.PA = EUR, .L = GBP)
    3. Check persistent cache (currency_cache.json)
    4. Query Yahoo Finance API for currency info
    5. Return default (USD) if all fail
    
    Args:
        ticker: Asset ticker symbol
        manual_mapping: Optional manual currency mapping dict
        default_currency: Fallback currency if detection fails (default: USD)
    
    Returns:
        str: Currency code (EUR, USD, GBP)
    """
    # Load cache if not loaded yet
    if not _CURRENCY_CACHE:
        _load_currency_cache()
    
    # Step 1: Check manual mapping
    if manual_mapping and ticker in manual_mapping:
        return manual_mapping[ticker]
    
    # Step 2: Check suffix patterns
    for suffix, currency in _SUFFIX_TO_CURRENCY.items():
        if ticker.endswith(suffix):
            # Cache it for future use
            _CURRENCY_CACHE[ticker] = currency
            _save_currency_cache()
            return currency
    
    # Step 3: Check cache
    if ticker in _CURRENCY_CACHE:
        return _CURRENCY_CACHE[ticker]
    
    # Step 4: Query Yahoo Finance
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Try to get currency from info
        currency = info.get("currency", None)
        if currency:
            # Normalize currency codes
            currency = currency.upper()
            # Only accept our 3 supported currencies
            if currency in ["EUR", "USD", "GBP"]:
                _CURRENCY_CACHE[ticker] = currency
                _save_currency_cache()
                return currency
            # Map known currency codes
            elif currency in ["GBP", "GBX"]:  # GBX = pence
                _CURRENCY_CACHE[ticker] = "GBP"
                _save_currency_cache()
                return "GBP"
            
    except Exception as e:
        print(f"Yahoo currency lookup failed for {ticker}: {e}")
    
    # Step 5: Return default (USD)
    # Most international stocks without suffix are USD
    return default_currency

# Initialize cache on import
_load_currency_cache()


# ===================== FOREX RATES (Current) =====================
def get_current_forex_rates():
    """
    Get current forex rates for EUR/USD, GBP/USD, JPY/USD, CHF/USD from Yahoo Finance with % change.
    Returns the latest available rates and daily change percentage.
    
    Returns:
        dict: {
            'EURUSD': float,
            'GBPUSD': float,
            'JPYUSD': float,
            'CHFUSD': float,
            'EURUSD_change_pct': float,
            'GBPUSD_change_pct': float,
            'JPYUSD_change_pct': float,
            'CHFUSD_change_pct': float,
            'timestamp': str (ISO format),
            'success': bool
        }
    """
    try:
        import yfinance as yf
        from datetime import datetime
        
        # Define currency pairs
        currencies = {
            'EUR': 'EURUSD=X',
            'GBP': 'GBPUSD=X',
            'JPY': 'JPY=X',
            'CHF': 'CHF=X'
        }
        
        result = {'success': True}
        latest_timestamp = None
        
        # Fetch each currency pair
        for curr_code, yahoo_symbol in currencies.items():
            try:
                ticker = yf.Ticker(yahoo_symbol)
                data = ticker.history(period="2d")
                
                if not data.empty:
                    rate = data['Close'].iloc[-1]
                    timestamp = data.index[-1]
                    
                    # Calculate % change and absolute change
                    change_pct = 0.0
                    change_pts = 0.0
                    if len(data) >= 2:
                        prev_rate = data['Close'].iloc[-2]
                        change_pct = ((rate - prev_rate) / prev_rate) * 100
                        change_pts = rate - prev_rate
                    
                    # Store results
                    key = f"{curr_code}USD"
                    result[key] = round(float(rate), 4)
                    result[f"{key}_change_pct"] = round(float(change_pct), 2)
                    result[f"{key}_change_pts"] = round(float(change_pts), 4)
                    
                    if latest_timestamp is None:
                        latest_timestamp = timestamp
                else:
                    # No data for this currency
                    key = f"{curr_code}USD"
                    result[key] = None
                    result[f"{key}_change_pct"] = None
                    result[f"{key}_change_pts"] = None
                    
            except Exception as e:
                print(f"Warning: Failed to fetch {curr_code}/USD: {e}")
                key = f"{curr_code}USD"
                result[key] = None
                result[f"{key}_change_pct"] = None
                result[f"{key}_change_pts"] = None
        
        # Set timestamp
        if latest_timestamp:
            result['timestamp'] = latest_timestamp.strftime("%Y-%m-%d %H:%M")
        else:
            result['timestamp'] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        from datetime import datetime
        print(f"Warning: Failed to fetch forex rates: {e}")
        return {
            'EURUSD': None,
            'GBPUSD': None,
            'JPYUSD': None,
            'CHFUSD': None,
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': str(e)
        }


# ===================== MAJOR INDEXES PRICES (Current) =====================
def get_major_indexes_prices():
    """
    Get current prices for major indexes, commodities, and bonds from Yahoo Finance.
    Returns the latest available prices (typically from previous close).
    
    Returns:
        dict: {
            'indexes': [
                {'name': 'S&P 500', 'symbol': '^GSPC', 'price': float},
                ...
            ],
            'timestamp': str (ISO format),
            'success': bool
        }
    """
    # Define major indexes, commodities, and bonds
    indexes = [
        # Major Indexes
        {'name': 'S&P 500', 'symbol': '^GSPC'},
        {'name': 'Nasdaq', 'symbol': '^IXIC'},
        {'name': 'Dow Jones', 'symbol': '^DJI'},
        {'name': 'DAX', 'symbol': '^GDAXI'},
        {'name': 'CAC 40', 'symbol': '^FCHI'},
        {'name': 'FTSE 100', 'symbol': '^FTSE'},
        {'name': 'Nikkei 225', 'symbol': '^N225'},
        {'name': 'Hang Seng', 'symbol': '^HSI'},
        # Commodities
        {'name': 'Gold', 'symbol': 'GC=F'},
        {'name': 'Silver', 'symbol': 'SI=F'},
        {'name': 'Oil (WTI)', 'symbol': 'CL=F'},
        # Bonds
        {'name': 'US 10Y Treasury', 'symbol': '^TNX'},
    ]
    
    try:
        import yfinance as yf
        from datetime import datetime
        
        results = []
        latest_timestamp = None
        
        for index_info in indexes:
            try:
                ticker = yf.Ticker(index_info['symbol'])
                # Get 2 days to calculate change percentage
                data = ticker.history(period="2d")
                
                if not data.empty:
                    price = data['Close'].iloc[-1]
                    timestamp = data.index[-1]
                    
                    # Calculate % change and absolute change
                    change_pct = 0.0
                    change_pts = 0.0
                    if len(data) >= 2:
                        prev_price = data['Close'].iloc[-2]
                        change_pct = ((price - prev_price) / prev_price) * 100
                        change_pts = price - prev_price
                    
                    results.append({
                        'name': index_info['name'],
                        'symbol': index_info['symbol'],
                        'price': round(float(price), 2),
                        'change_pct': round(float(change_pct), 2),
                        'change_pts': round(float(change_pts), 2),
                        'success': True
                    })
                    
                    # Track latest timestamp
                    if latest_timestamp is None or timestamp > latest_timestamp:
                        latest_timestamp = timestamp
                else:
                    results.append({
                        'name': index_info['name'],
                        'symbol': index_info['symbol'],
                        'price': None,
                        'change_pct': None,
                        'success': False
                    })
            except Exception as e:
                print(f"Warning: Failed to fetch {index_info['name']}: {e}")
                results.append({
                    'name': index_info['name'],
                    'symbol': index_info['symbol'],
                    'price': None,
                    'success': False
                })
        
        # Format timestamp
        if latest_timestamp:
            timestamp_str = latest_timestamp.strftime("%Y-%m-%d %H:%M")
        else:
            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return {
            'indexes': results,
            'timestamp': timestamp_str,
            'success': len([r for r in results if r['success']]) > 0
        }
        
    except Exception as e:
        from datetime import datetime
        print(f"Warning: Failed to fetch major indexes: {e}")
        return {
            'indexes': [],
            'timestamp': datetime.now().isoformat(),
            'success': False,
            'error': str(e)
        }


# ===================== FOREX HISTORICAL DATA (Infrastructure) =====================
_FOREX_CACHE_FILE = "data/forex_cache.json"
_FOREX_CACHE = {}

def _load_forex_cache():
    """Load the persistent forex cache from JSON."""
    global _FOREX_CACHE
    if os.path.exists(_FOREX_CACHE_FILE):
        try:
            import json
            with open(_FOREX_CACHE_FILE, "r", encoding="utf-8") as f:
                _FOREX_CACHE = json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load forex cache: {e}")
            _FOREX_CACHE = {}

def _save_forex_cache():
    """Save the forex cache to JSON."""
    try:
        import json
        with open(_FOREX_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_FOREX_CACHE, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to save forex cache: {e}")

def identify_forex_pairs_needed(portfolio_currency, asset_currencies):
    """
    Identify which forex pairs need to be downloaded based on portfolio and asset currencies.
    
    Args:
        portfolio_currency: Base currency of the portfolio ("EUR", "USD", "GBP")
        asset_currencies: List of asset currencies (e.g., ["USD", "EUR", "GBP"])
    
    Returns:
        list: List of tuples (pair_symbol, invert_flag)
              Example: [("EURUSD=X", False), ("EURGBP=X", False)]
              invert_flag=True means we need to take 1/rate
    """
    pairs_needed = []
    unique_currencies = set(asset_currencies)
    
    # Remove portfolio currency (no conversion needed for same currency)
    unique_currencies.discard(portfolio_currency)
    
    for asset_currency in unique_currencies:
        if portfolio_currency == "EUR":
            if asset_currency == "USD":
                pairs_needed.append(("EURUSD=X", False))  # EUR to USD, use directly
            elif asset_currency == "GBP":
                pairs_needed.append(("EURGBP=X", False))  # EUR to GBP, use directly
                
        elif portfolio_currency == "USD":
            if asset_currency == "EUR":
                pairs_needed.append(("EURUSD=X", True))   # EUR to USD, invert to get USD to EUR
            elif asset_currency == "GBP":
                pairs_needed.append(("GBPUSD=X", False))  # GBP to USD, use directly
                
        elif portfolio_currency == "GBP":
            if asset_currency == "EUR":
                pairs_needed.append(("EURGBP=X", True))   # EUR to GBP, invert to get GBP to EUR
            elif asset_currency == "USD":
                pairs_needed.append(("GBPUSD=X", True))   # GBP to USD, invert to get USD to GBP
    
    return pairs_needed

def _validate_forex_rates(rates_series, pair_name):
    """
    Validate forex rates for obvious errors (outliers, zeros, etc.)
    
    Args:
        rates_series: pandas Series with forex rates
        pair_name: Name of the forex pair (e.g., "EURUSD")
    
    Returns:
        tuple: (is_valid, cleaned_series, warnings)
    """
    warnings = []
    
    # Check for zeros or negative values
    if (rates_series <= 0).any():
        warnings.append(f"{pair_name}: Found zero or negative rates")
        rates_series = rates_series[rates_series > 0]
    
    # Check for extreme outliers (more than 10x median)
    median_rate = rates_series.median()
    outlier_threshold = median_rate * 10
    outliers = rates_series[rates_series > outlier_threshold]
    
    if len(outliers) > 0:
        warnings.append(f"{pair_name}: Found {len(outliers)} extreme outliers (>10x median)")
        # Remove extreme outliers
        rates_series = rates_series[rates_series <= outlier_threshold]
    
    # Check for unrealistic rates based on pair
    if pair_name == "EURUSD":
        # EUR/USD should typically be between 0.5 and 2.0
        unrealistic = rates_series[(rates_series < 0.5) | (rates_series > 2.0)]
        if len(unrealistic) > 0:
            warnings.append(f"{pair_name}: Found {len(unrealistic)} unrealistic EUR/USD rates")
    elif pair_name == "EURGBP":
        # EUR/GBP should typically be between 0.6 and 1.2
        unrealistic = rates_series[(rates_series < 0.6) | (rates_series > 1.2)]
        if len(unrealistic) > 0:
            warnings.append(f"{pair_name}: Found {len(unrealistic)} unrealistic EUR/GBP rates")
    elif pair_name == "GBPUSD":
        # GBP/USD should typically be between 1.0 and 2.5
        unrealistic = rates_series[(rates_series < 1.0) | (rates_series > 2.5)]
        if len(unrealistic) > 0:
            warnings.append(f"{pair_name}: Found {len(unrealistic)} unrealistic GBP/USD rates")
    
    is_valid = len(rates_series) > 100  # Need at least 100 valid data points
    
    return is_valid, rates_series, warnings

def _download_single_forex_pair(pair_symbol, invert_flag, start_date, end_date, years, max_retries=3):
    """
    Download a single forex pair with retry logic and validation.
    
    Args:
        pair_symbol: Yahoo Finance symbol (e.g., "EURUSD=X")
        invert_flag: Whether to invert the rates
        start_date: Start date for download
        end_date: End date for download
        years: Number of years (for cache key)
        max_retries: Maximum number of retry attempts
    
    Returns:
        tuple: (success, rates_series, clean_name)
    """
    import yfinance as yf
    import time
    
    clean_name = pair_symbol.replace("=X", "")
    
    for attempt in range(max_retries):
        try:
            if attempt > 0:
                print(f"    Retry attempt {attempt + 1}/{max_retries} for {pair_symbol}...")
                time.sleep(2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
            
            ticker = yf.Ticker(pair_symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            if hist.empty:
                print(f"    WARNING: No data for {pair_symbol}")
                continue
            
            # Use Close prices
            rates_series = hist['Close']
            
            # Validate rates
            is_valid, cleaned_rates, warnings = _validate_forex_rates(rates_series, clean_name)
            
            if warnings:
                for warning in warnings:
                    print(f"    WARNING: {warning}")
            
            if not is_valid:
                print(f"    ERROR: {clean_name} failed validation (insufficient valid data)")
                continue
            
            # Invert if needed
            if invert_flag:
                cleaned_rates = 1 / cleaned_rates
            
            print(f"    -> {len(cleaned_rates)} valid data points downloaded")
            return True, cleaned_rates, clean_name
            
        except Exception as e:
            print(f"    ERROR: Attempt {attempt + 1} failed for {pair_symbol}: {e}")
            if attempt == max_retries - 1:
                print(f"    FAILED: All {max_retries} attempts failed for {pair_symbol}")
                return False, None, clean_name
    
    return False, None, clean_name

def download_historical_forex(portfolio_currency, asset_currencies, years=25):
    """
    Download historical forex rates for multi-currency portfolio.
    Uses cache to avoid re-downloading. Includes validation and retry logic.
    
    Args:
        portfolio_currency: Base currency of the portfolio ("EUR", "USD", "GBP")
        asset_currencies: List of asset currencies (e.g., ["USD", "EUR", "GBP"])
        years: Number of years of historical data (default: 25)
    
    Returns:
        dict: {
            'rates': {
                'EURUSD': pd.Series with historical rates (indexed by date),
                'EURGBP': pd.Series with historical rates,
                ...
            },
            'metadata': {
                'portfolio_currency': str,
                'pairs_downloaded': list,
                'timestamp': str,
                'warnings': list
            },
            'success': bool
        }
    """
    # Load cache
    if not _FOREX_CACHE:
        _load_forex_cache()
    
    # Identify needed pairs
    pairs_needed = identify_forex_pairs_needed(portfolio_currency, asset_currencies)
    
    if not pairs_needed:
        # No forex conversion needed (all assets in same currency as portfolio)
        return {
            'rates': {},
            'metadata': {
                'portfolio_currency': portfolio_currency,
                'pairs_downloaded': [],
                'timestamp': pd.Timestamp.now().isoformat(),
                'warnings': []
            },
            'success': True
        }
    
    print(f"\n=== DOWNLOADING FOREX RATES ===")
    print(f"Portfolio currency: {portfolio_currency}")
    print(f"Asset currencies: {asset_currencies}")
    print(f"Pairs needed: {[p[0] for p in pairs_needed]}")
    
    try:
        from datetime import datetime, timedelta
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=years * 365 + 30)  # +30 days buffer
        
        rates = {}
        pairs_downloaded = []
        all_warnings = []
        
        # Check cache first
        cached_pairs = []
        pairs_to_download = []
        
        for pair_symbol, invert_flag in pairs_needed:
            cache_key = f"{pair_symbol}_{years}y"
            
            if cache_key in _FOREX_CACHE:
                cached_data = _FOREX_CACHE[cache_key]
                cached_date = pd.Timestamp(cached_data['timestamp'])
                
                # Use cache if less than 1 day old
                if (pd.Timestamp.now() - cached_date).days < 1:
                    print(f"  Using cached data for {pair_symbol}")
                    rates_series = pd.Series(
                        cached_data['rates'],
                        index=pd.to_datetime(cached_data['dates'])
                    )
                    
                    if invert_flag:
                        rates_series = 1 / rates_series
                    
                    # Store with clean name (remove =X)
                    clean_name = pair_symbol.replace("=X", "")
                    rates[clean_name] = rates_series
                    pairs_downloaded.append(pair_symbol)
                    cached_pairs.append(pair_symbol)
                    continue
            
            # Add to download list
            pairs_to_download.append((pair_symbol, invert_flag))
        
        # Download missing pairs in parallel
        if pairs_to_download:
            print(f"  Downloading {len(pairs_to_download)} pairs in parallel...")
            
            with ThreadPoolExecutor(max_workers=3) as executor:
                # Submit all download tasks
                future_to_pair = {
                    executor.submit(
                        _download_single_forex_pair,
                        pair_symbol,
                        invert_flag,
                        start_date,
                        end_date,
                        years
                    ): (pair_symbol, invert_flag)
                    for pair_symbol, invert_flag in pairs_to_download
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_pair):
                    pair_symbol, invert_flag = future_to_pair[future]
                    try:
                        success, rates_series, clean_name = future.result()
                        
                        if success and rates_series is not None:
                            # Cache the data
                            cache_key = f"{pair_symbol}_{years}y"
                            _FOREX_CACHE[cache_key] = {
                                'rates': rates_series.tolist(),
                                'dates': rates_series.index.strftime('%Y-%m-%d').tolist(),
                                'timestamp': pd.Timestamp.now().isoformat()
                            }
                            
                            # Store with clean name
                            rates[clean_name] = rates_series
                            pairs_downloaded.append(pair_symbol)
                        else:
                            print(f"  FAILED: Could not download {pair_symbol}")
                            
                    except Exception as e:
                        print(f"  ERROR: Exception downloading {pair_symbol}: {e}")
        
        # Save cache
        _save_forex_cache()
        
        print(f"\n[OK] Successfully processed {len(pairs_downloaded)} forex pairs")
        print(f"  - Cached: {len(cached_pairs)}")
        print(f"  - Downloaded: {len(pairs_downloaded) - len(cached_pairs)}")
        
        return {
            'rates': rates,
            'metadata': {
                'portfolio_currency': portfolio_currency,
                'pairs_downloaded': pairs_downloaded,
                'timestamp': pd.Timestamp.now().isoformat(),
                'warnings': all_warnings
            },
            'success': True
        }
        
    except Exception as e:
        print(f"\n[ERROR] Failed to download forex rates: {e}")
        import traceback
        traceback.print_exc()
        return {
            'rates': {},
            'metadata': {
                'portfolio_currency': portfolio_currency,
                'pairs_downloaded': [],
                'timestamp': pd.Timestamp.now().isoformat()
            },
            'success': False,
            'error': str(e)
        }

def _get_forex_pair(portfolio_currency, asset_currency):
    """
    Determine the forex pair name and whether to invert the rate.
    
    Args:
        portfolio_currency: Base currency of the portfolio
        asset_currency: Currency of the asset
    
    Returns:
        tuple: (pair_name, invert_flag)
    """
    pair_name = None
    invert_rate = False
    
    if portfolio_currency == "EUR":
        if asset_currency == "USD":
            pair_name = "EURUSD"
        elif asset_currency == "GBP":
            pair_name = "EURGBP"
    elif portfolio_currency == "USD":
        if asset_currency == "EUR":
            pair_name = "EURUSD"
            invert_rate = True  # We have EUR/USD, need USD/EUR
        elif asset_currency == "GBP":
            pair_name = "GBPUSD"
    elif portfolio_currency == "GBP":
        if asset_currency == "EUR":
            pair_name = "EURGBP"
            invert_rate = True  # We have EUR/GBP, need GBP/EUR
        elif asset_currency == "USD":
            pair_name = "GBPUSD"
            invert_rate = True  # We have GBP/USD, need USD/GBP
    
    return pair_name, invert_rate

def convert_prices_to_base_currency(prices_data, tickers, portfolio_currency, forex_rates=None):
    """
    Convert all asset prices to the portfolio's base currency.
    
    This function:
    1. Detects the currency of each asset
    2. Aligns forex rates with asset price dates
    3. Applies conversions where needed
    4. Returns all prices in the portfolio currency
    
    Args:
        prices_data: pd.DataFrame with Close prices (columns = tickers) OR
                     dict of {ticker: pd.DataFrame with OHLCV data}
        tickers: list of ticker symbols
        portfolio_currency: Base currency ("EUR", "USD", "GBP")
        forex_rates: dict of {pair_name: pd.Series} from download_historical_forex()
                     If None, will be downloaded automatically
    
    Returns:
        pd.DataFrame (if input was DataFrame) OR dict (if input was dict): {
            'prices_converted': Converted prices in same format as input,
            'metadata': {
                'portfolio_currency': str,
                'conversions_applied': list of (ticker, from_currency, to_currency),
                'no_conversion_needed': list of tickers
            },
            'success': bool
        }
    """
    print(f"\n=== CONVERTING PRICES TO {portfolio_currency} ===")
    
    try:
        import pandas as pd
        
        # Detect input format
        is_dataframe = isinstance(prices_data, pd.DataFrame)
        
        # Step 1: Detect currency of each asset
        asset_currencies = {}
        for ticker in tickers:
            currency = detect_asset_currency(ticker)
            asset_currencies[ticker] = currency
            print(f"  {ticker}: {currency}")
        
        # Step 2: Download forex rates if not provided
        if forex_rates is None:
            unique_currencies = list(set(asset_currencies.values()))
            forex_result = download_historical_forex(portfolio_currency, unique_currencies, years=25)
            
            if not forex_result['success']:
                return {
                    'prices_converted': prices_data if is_dataframe else {},
                    'metadata': {},
                    'success': False,
                    'error': 'Failed to download forex rates'
                }
            
            forex_rates = forex_result['rates']
        
        # Step 3: Convert prices based on input format
        if is_dataframe:
            # DataFrame input: columns are tickers
            prices_converted = prices_data.copy()
            conversions_applied = []
            no_conversion_needed = []
            
            for ticker in tickers:
                if ticker not in prices_converted.columns:
                    print(f"  WARNING: {ticker} not in price data")
                    continue
                
                asset_currency = asset_currencies[ticker]
                
                # No conversion needed if same currency
                if asset_currency == portfolio_currency:
                    no_conversion_needed.append(ticker)
                    print(f"  {ticker}: No conversion needed ({asset_currency})")
                    continue
                
                # Determine forex pair
                pair_name, invert_rate = _get_forex_pair(portfolio_currency, asset_currency)
                
                if pair_name is None or pair_name not in forex_rates:
                    print(f"  WARNING: No forex rate for {asset_currency} → {portfolio_currency}")
                    continue
                
                # Get and align forex rates
                fx_rates = forex_rates[pair_name].copy()
                if invert_rate:
                    fx_rates = 1 / fx_rates
                
                fx_rates_aligned = fx_rates.reindex(prices_converted.index).ffill().bfill()
                
                if fx_rates_aligned.isna().any():
                    fx_rates_aligned = fx_rates_aligned.fillna(fx_rates_aligned.median())
                
                # Apply conversion
                original_price = prices_converted[ticker].iloc[-1]
                prices_converted[ticker] = prices_converted[ticker] * fx_rates_aligned
                converted_price = prices_converted[ticker].iloc[-1]
                fx_rate = fx_rates_aligned.iloc[-1]
                
                conversions_applied.append((ticker, asset_currency, portfolio_currency))
                print(f"  {ticker}: {original_price:.2f} {asset_currency} × {fx_rate:.4f} = {converted_price:.2f} {portfolio_currency}")
            
            result_prices = prices_converted
            
        else:
            # Dict input: {ticker: DataFrame with OHLCV}
            prices_converted = {}
            conversions_applied = []
            no_conversion_needed = []
            
            for ticker in tickers:
                if ticker not in prices_data or prices_data[ticker].empty:
                    print(f"  WARNING: No price data for {ticker}")
                    continue
                
                asset_currency = asset_currencies[ticker]
                prices_df = prices_data[ticker].copy()
            
                # No conversion needed if same currency
                if asset_currency == portfolio_currency:
                    prices_converted[ticker] = prices_df
                    no_conversion_needed.append(ticker)
                    print(f"  {ticker}: No conversion needed ({asset_currency})")
                    continue
                
                # Determine forex pair
                pair_name, invert_rate = _get_forex_pair(portfolio_currency, asset_currency)
                
                if pair_name is None or pair_name not in forex_rates:
                    print(f"  WARNING: No forex rate for {asset_currency} → {portfolio_currency}")
                    prices_converted[ticker] = prices_df
                    continue
                
                # Get and align forex rates
                fx_rates = forex_rates[pair_name].copy()
                if invert_rate:
                    fx_rates = 1 / fx_rates
                
                fx_rates_aligned = fx_rates.reindex(prices_df.index).ffill().bfill()
                
                if fx_rates_aligned.isna().any():
                    fx_rates_aligned = fx_rates_aligned.fillna(fx_rates_aligned.median())
                
                # Apply conversion to all price columns
                price_columns = ['Open', 'High', 'Low', 'Close']
                for col in price_columns:
                    if col in prices_df.columns:
                        prices_df[col] = prices_df[col] * fx_rates_aligned
                
                prices_converted[ticker] = prices_df
                conversions_applied.append((ticker, asset_currency, portfolio_currency))
                
                # Show conversion example
                original_close = prices_data[ticker]['Close'].iloc[-1]
                converted_close = prices_df['Close'].iloc[-1]
                fx_rate = fx_rates_aligned.iloc[-1]
                print(f"  {ticker}: {original_close:.2f} {asset_currency} × {fx_rate:.4f} = {converted_close:.2f} {portfolio_currency}")
            
            result_prices = prices_converted
        
        print(f"\n[OK] Converted {len(conversions_applied)} assets to {portfolio_currency}")
        print(f"  - No conversion needed: {len(no_conversion_needed)} assets")
        
        return {
            'prices_converted': result_prices,
            'metadata': {
                'portfolio_currency': portfolio_currency,
                'conversions_applied': conversions_applied,
                'no_conversion_needed': no_conversion_needed,
                'asset_currencies': asset_currencies
            },
            'success': True
        }
        
    except Exception as e:
        print(f"\n[ERROR] Failed to convert prices: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'prices_converted': {},
            'metadata': {},
            'success': False,
            'error': str(e)
        }

# Initialize forex cache on import
_load_forex_cache()