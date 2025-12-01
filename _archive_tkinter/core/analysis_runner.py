# analysis_runner.py - Analysis orchestration and chart generation
import os
import numpy as np
from tkinter import messagebox

from core.config import (
    DATA_DIR, BENCH_DIR, RESULTS_DIR, WEIGHTS_RAW, BENCH_DEF,
    SECTOR_MAPPING, SECTOR_COLORS, START_CAPITAL, ESTIMATION_YEARS,
    MC_PATHS, MC_STEPS, RANDOMNESS_FACTOR, FORWARD_YEARS,
    ANNUALIZATION, MONTH_FACTOR, PLOT_ALL_PATHS, SHOW_PLOTS
)
from utils.utils_data import detect_asset_sector

from utils.utils_data import (
    fetch_prices_yahoo, load_prices_from_dir, align_business_days,
    slice_recent_safe, save_weights_csv, save_benchmarks_csv, save_prices_to_dir,
    convert_prices_to_base_currency
)

from utils.utils_math import compute_portfolio_metrics, mc_gaussian, mc_gaussian_with_randomness


class AnalysisRunner:
    """
    Orchestrates complete portfolio analysis workflow (data provider agnostic)
    
    This class handles:
    - Data loading from multiple sources (Yahoo Finance, CSV files)
    - Portfolio metrics computation
    - Monte Carlo simulations
    - Chart generation coordination
    - Results persistence
    """
    
    def __init__(self, weights_raw=None, bench_def=None, data_dir=None, bench_dir=None):
        """
        Initialize analysis runner
        
        Args:
            weights_raw: dict of {ticker: weight} (defaults to config)
            bench_def: list of (name, ticker) tuples (defaults to config)
            data_dir: Path to portfolio data directory
            bench_dir: Path to benchmark data directory
        """
        self.weights_raw = weights_raw or WEIGHTS_RAW.copy()
        self.bench_def = bench_def or BENCH_DEF.copy()
        self.data_dir = data_dir or DATA_DIR
        self.bench_dir = bench_dir or BENCH_DIR
        
        # Results from last run
        self.etf_prices = None
        self.bench_prices = None
        self.portfolio_metrics = None
        self.mc_results = None
    
    def run_analysis(self, ticker_weights, benches, selected_charts, 
                     status_callback=None, sanitize_func=None, capital=None, currency=None):
        """
        Run complete portfolio analysis
        
        Args:
            ticker_weights: list of (symbol, weight) tuples
            benches: list of benchmark symbols
            selected_charts: list of chart numbers to generate
            status_callback: Optional callback(message, color) for status updates
            sanitize_func: Optional function to sanitize symbols
            capital: Initial capital amount (defaults to START_CAPITAL)
            currency: Currency code (defaults to "USD")
        
        Returns:
            dict: Results summary with success status and message
        """
        
        def update_status(msg, color="#2196F3"):
            if status_callback:
                status_callback(msg, color)
        
        try:
            # Use provided capital or default
            start_capital = capital if capital is not None else START_CAPITAL
            portfolio_currency = currency if currency is not None else "USD"
            
            # Update status
            update_status(f"Running analysis for {len(selected_charts)} charts... (Capital: {start_capital:,.0f} {portfolio_currency})", "#2196F3")
            
            # Sanitize symbols if function provided
            if sanitize_func and ticker_weights:
                ticker_symbols = [sym for sym, _ in ticker_weights]
                sanitized_symbols = sanitize_func(ticker_symbols)
                ticker_weights = [(sym, w) for sym, w in ticker_weights if sym in sanitized_symbols]
            
            if sanitize_func and benches:
                benches = sanitize_func(benches)
            
            use_yahoo = bool(ticker_weights or benches)
            
            # Load data (Yahoo or CSV)
            if use_yahoo:
                if not ticker_weights:
                    ticker_weights = [(t, w) for t, w in self.weights_raw.items()]
                if not benches:
                    benches = [t for _, t in self.bench_def]
                
                # Update weights configuration
                if ticker_weights:
                    self.weights_raw = self._normalize_weights(ticker_weights)
                
                if benches:
                    # Create bench_def with proper display names
                    from utils.utils_data import get_benchmark_display_name
                    self.bench_def = [(get_benchmark_display_name(b), b) for b in benches]
                
                # Try Yahoo, fallback to CSV
                try:
                    ticker_symbols = [sym for sym, _ in ticker_weights]
                    etf_prices_raw = fetch_prices_yahoo(ticker_symbols)
                    bench_prices_raw = fetch_prices_yahoo(benches)
                    
                    # MULTI-CURRENCY CONVERSION
                    update_status(f"Converting prices to {portfolio_currency}...", "#2196F3")
                    conversion_result = convert_prices_to_base_currency(
                        etf_prices_raw, 
                        ticker_symbols, 
                        portfolio_currency
                    )
                    
                    if conversion_result['success']:
                        etf_prices_converted = conversion_result['prices_converted']
                        print(f"\n[OK] Multi-currency conversion successful!")
                        print(f"  - Conversions applied: {len(conversion_result['metadata']['conversions_applied'])}")
                        print(f"  - No conversion needed: {len(conversion_result['metadata']['no_conversion_needed'])}")
                    else:
                        print(f"\n[WARNING] Currency conversion failed, using original prices")
                        etf_prices_converted = etf_prices_raw
                    
                    self.etf_prices = slice_recent_safe(
                        align_business_days(etf_prices_converted), ESTIMATION_YEARS
                    )
                    self.bench_prices = slice_recent_safe(
                        align_business_days(bench_prices_raw), ESTIMATION_YEARS
                    )
                except Exception as fetch_err:
                    print(f"Yahoo fetch failed, falling back to local CSVs: {fetch_err}")
                    try:
                        messagebox.showwarning(
                            "Yahoo fetch failed",
                            f"Yahoo download failed. Falling back to local CSVs.\n\n{fetch_err}"
                        )
                    except Exception:
                        pass
                    self.etf_prices = slice_recent_safe(
                        align_business_days(load_prices_from_dir(self.data_dir)), ESTIMATION_YEARS
                    )
                    self.bench_prices = slice_recent_safe(
                        align_business_days(load_prices_from_dir(self.bench_dir)), ESTIMATION_YEARS
                    )
                
                # Persist selections
                self._persist_selections(ticker_weights, benches, 
                                        locals().get('etf_prices_raw'), 
                                        locals().get('bench_prices_raw'))
            else:
                # Load from CSV only
                self.etf_prices = slice_recent_safe(
                    align_business_days(load_prices_from_dir(self.data_dir)), ESTIMATION_YEARS
                )
                self.bench_prices = slice_recent_safe(
                    align_business_days(load_prices_from_dir(self.bench_dir)), ESTIMATION_YEARS
                )
            
            # Compute portfolio metrics
            update_status("Computing portfolio metrics...", "#2196F3")
            self.portfolio_metrics = compute_portfolio_metrics(
                self.etf_prices, self.weights_raw, start_capital, ANNUALIZATION
            )
            
            # Generate Monte Carlo simulations if needed
            self.mc_results = None
            if any(i in selected_charts for i in range(7, 24)):
                update_status("Running Monte Carlo simulations...", "#2196F3")
                self.mc_results = self._run_monte_carlo(self.portfolio_metrics, start_capital)
            
            # Generate selected charts
            update_status(f"Generating {len(selected_charts)} charts...", "#2196F3")
            self.generate_selected_charts(selected_charts, self.mc_results, start_capital, portfolio_currency)
            
            # Success
            update_status(f"SUCCESS! {len(selected_charts)} charts generated", "#4CAF50")
            
            return {
                "success": True,
                "message": f"Successfully generated {len(selected_charts)} charts!",
                "output_dir": os.path.abspath(RESULTS_DIR),
                "chart_count": len(selected_charts)
            }
            
        except Exception as e:
            update_status("ERROR - Check console", "red")
            print(f"\nERROR: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "message": f"Analysis failed: {str(e)}",
                "error": str(e)
            }
    
    def _normalize_weights(self, ticker_weights):
        """
        Normalize weights to sum to 1.0
        
        Args:
            ticker_weights: list of (symbol, weight) tuples
        
        Returns:
            dict: Normalized {symbol: weight}
        """
        total_weight = sum(w for _, w in ticker_weights)
        if total_weight > 0:
            return {sym: w / total_weight for sym, w in ticker_weights}
        else:
            # Fallback to equal weights
            eq_w = 1.0 / max(len(ticker_weights), 1)
            return {sym: eq_w for sym, _ in ticker_weights}
    
    def _persist_selections(self, ticker_weights, benches, etf_prices_raw, bench_prices_raw):
        """
        Save user selections to CSV files and cache prices
        
        Args:
            ticker_weights: list of (symbol, weight) tuples
            benches: list of benchmark symbols
            etf_prices_raw: Raw ETF price data
            bench_prices_raw: Raw benchmark price data
        """
        try:
            base_dir = os.path.dirname(__file__)
            weights_csv = os.path.join(base_dir, "weights.csv")
            benches_csv = os.path.join(base_dir, "benchmarks.csv")
            
            if ticker_weights:
                save_weights_csv(weights_csv, self.weights_raw)
            if benches:
                save_benchmarks_csv(benches_csv, self.bench_def)
            
            # Cache price data
            try:
                if etf_prices_raw is not None:
                    save_prices_to_dir(etf_prices_raw, self.data_dir)
                if bench_prices_raw is not None:
                    save_prices_to_dir(bench_prices_raw, self.bench_dir)
            except Exception as cache_err:
                print(f"Cache warning: {cache_err}")
                
        except Exception as persist_err:
            print(f"Persist warning: {persist_err}")
    
    def _build_dynamic_sector_mapping(self, tickers):
        """
        Build sector mapping dynamically using the hybrid detection system
        
        Args:
            tickers: list of ticker symbols
        
        Returns:
            dict: sector mapping {ticker: sector}
        """
        sector_mapping = {}
        for ticker in tickers:
            sector_mapping[ticker] = detect_asset_sector(
                ticker, 
                manual_mapping=SECTOR_MAPPING,  # Use config.py as fallback
                default_sector="Unknown"
            )
        return sector_mapping
    
    def _get_ticker_info(self, tickers):
        """
        Get ticker information (name and currency) for display
        
        Args:
            tickers: List of ticker symbols
        
        Returns:
            dict: Ticker info {ticker: {'name': str, 'currency': str}}
        """
        import yfinance as yf
        
        ticker_info = {}
        
        for ticker in tickers:
            try:
                # Get ticker info from yfinance
                stock = yf.Ticker(ticker)
                info = stock.info
                
                # Get company name
                name = info.get('longName') or info.get('shortName') or ticker
                
                # Detect currency from ticker suffix or info
                currency = info.get('currency', 'USD')
                
                # Override currency based on exchange suffix if available
                if '.PA' in ticker or '.MI' in ticker or '.AS' in ticker or '.BR' in ticker or '.MC' in ticker or '.DE' in ticker:
                    currency = 'EUR'
                elif '.L' in ticker:
                    currency = 'GBP'
                elif '.SW' in ticker:
                    currency = 'CHF'
                elif '.T' in ticker:
                    currency = 'JPY'
                elif '.HK' in ticker:
                    currency = 'HKD'
                elif '.AX' in ticker:
                    currency = 'AUD'
                elif '.TO' in ticker:
                    currency = 'CAD'
                
                ticker_info[ticker] = {
                    'name': name,
                    'currency': currency
                }
                
                print(f"  {ticker}: {name} ({currency})")
                
            except Exception as e:
                print(f"Warning: Could not get info for {ticker}: {e}")
                ticker_info[ticker] = {
                    'name': ticker,
                    'currency': 'USD'
                }
        
        return ticker_info
    
    def _run_monte_carlo(self, portfolio_metrics, start_capital=None):
        """
        Run Monte Carlo simulations (normal and with randomness)
        
        Args:
            portfolio_metrics: dict with portfolio metrics
            start_capital: Initial capital amount (defaults to START_CAPITAL)
        
        Returns:
            dict: MC simulation results
        """
        capital = start_capital if start_capital is not None else START_CAPITAL
        
        paths_normal = mc_gaussian(
            portfolio_metrics["mu_a"], portfolio_metrics["cov_a"], 
            portfolio_metrics["w"], capital, MC_STEPS, MC_PATHS, MONTH_FACTOR
        )
        
        paths_random = mc_gaussian_with_randomness(
            portfolio_metrics["mu_a"], portfolio_metrics["cov_a"], 
            portfolio_metrics["w"], capital, MC_STEPS, MC_PATHS, 
            RANDOMNESS_FACTOR, MONTH_FACTOR
        )
        
        return {
            "paths_normal": paths_normal,
            "paths_random": paths_random,
            "median_normal": np.median(paths_normal, axis=1),
            "median_random": np.median(paths_random, axis=1)
        }
    
    def generate_selected_charts(self, selected, mc_results=None, start_capital=None, portfolio_currency="USD"):
        """
        Generate all selected charts by delegating to specialized chart modules
        
        Args:
            selected: list of chart numbers to generate
            mc_results: Monte Carlo results (optional, uses self.mc_results if None)
            start_capital: Initial capital amount (defaults to START_CAPITAL)
            portfolio_currency: Currency code (defaults to "USD")
        """
        if mc_results is None:
            mc_results = self.mc_results
        
        capital = start_capital if start_capital is not None else START_CAPITAL
        
        # Build dynamic sector mapping from portfolio tickers
        tickers = list(self.weights_raw.keys())
        dynamic_sector_mapping = self._build_dynamic_sector_mapping(tickers)
        
        # Get ticker info (name and currency) for display
        ticker_info = self._get_ticker_info(tickers)
        
        # Charts 1-4: Portfolio
        portfolio_charts = [i for i in range(1, 5) if i in selected]
        if portfolio_charts:
            from charts.chart_portfolio import generate_portfolio_charts
            generate_portfolio_charts(
                self.etf_prices, self.bench_prices, self.weights_raw, self.bench_def,
                capital, RESULTS_DIR, SHOW_PLOTS, selected_charts=portfolio_charts,
                ticker_info=ticker_info
            )
        
        # Charts 5-6: Sector
        sector_charts = [i for i in [5, 6] if i in selected]
        if sector_charts:
            from charts.chart_sector import generate_sector_charts
            generate_sector_charts(
                self.portfolio_metrics, dynamic_sector_mapping, SECTOR_COLORS,
                capital, RESULTS_DIR, SHOW_PLOTS, selected_charts=sector_charts,
                currency=portfolio_currency
            )
        
        # Charts 7-12: Monte Carlo
        mc_charts = [i for i in range(7, 13) if i in selected]
        if mc_charts:
            from charts.chart_monte_carlo import generate_monte_carlo_charts
            generate_monte_carlo_charts(
                self.portfolio_metrics, MC_PATHS, MC_STEPS, RANDOMNESS_FACTOR,
                capital, ANNUALIZATION, MONTH_FACTOR, PLOT_ALL_PATHS,
                RESULTS_DIR, SHOW_PLOTS, selected_charts=mc_charts
            )
        
        # Charts 13-16: Risk Metrics
        risk_charts = [i for i in range(13, 17) if i in selected]
        if risk_charts:
            from charts.chart_risk_metrics import generate_risk_metrics_charts
            generate_risk_metrics_charts(
                self.portfolio_metrics, mc_results, capital,
                FORWARD_YEARS, ANNUALIZATION, RESULTS_DIR, SHOW_PLOTS, selected_charts=risk_charts
            )
        
        # Charts 17-20: Benchmarks
        benchmark_charts = [i for i in range(17, 21) if i in selected]
        if benchmark_charts:
            from charts.chart_benchmarks import generate_benchmark_charts
            bench_params = generate_benchmark_charts(
                self.bench_prices, self.portfolio_metrics, mc_results, self.bench_def,
                MC_PATHS, MC_STEPS, capital, FORWARD_YEARS,
                ANNUALIZATION, RANDOMNESS_FACTOR, MONTH_FACTOR,
                RESULTS_DIR, SHOW_PLOTS, selected_charts=benchmark_charts
            )
        else:
            bench_params = {}
            if 23 in selected:
                from charts.chart_benchmarks import compute_benchmark_params
                bench_params = compute_benchmark_params(self.bench_prices, self.bench_def, ANNUALIZATION)
        
        # Charts 22, 24: Sector Projections
        sector_proj_charts = [i for i in [22, 24] if i in selected]
        if sector_proj_charts:
            from charts.chart_sector_projection import generate_sector_projection_charts
            generate_sector_projection_charts(
                self.portfolio_metrics, dynamic_sector_mapping, SECTOR_COLORS,
                MC_PATHS, MC_STEPS, capital, MONTH_FACTOR,
                mc_results["paths_normal"], RESULTS_DIR, SHOW_PLOTS, selected_charts=sector_proj_charts
            )
        
        # Chart 23: Regime
        if 23 in selected:
            from charts.chart_regime import generate_regime_charts
            generate_regime_charts(
                mc_results, bench_params, MC_PATHS, MC_STEPS,
                capital, RESULTS_DIR, SHOW_PLOTS, selected_charts=[23]
            )

