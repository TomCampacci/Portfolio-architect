# menu_principal_v3.py - Compact Portfolio Analysis (Single Page)
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import configuration
from core.config import WEIGHTS_RAW, BENCH_DEF

# Import modules
from managers.symbol_handler import SymbolValidator, SymbolUIHandler
from core.analysis_runner import AnalysisRunner
from ui.theme_colors import LightPremiumTheme as T

# Import specialized modules
from managers.currency_manager import CurrencyManager
from managers.portfolio_manager import PortfolioManager
from managers.market_data_manager import MarketDataManager
from utils.utils_data import get_current_forex_rates, get_major_indexes_prices
import threading


class CompactPortfolioPanel:
    """Compact Portfolio Analysis - Everything on one page"""
    
    # Chart groups
    CHART_GROUPS = {
        "Portfolio & Sector": [1, 2, 3, 4, 5, 6],
        "Monte Carlo": [7, 8, 9, 10, 11, 12],
        "Risk Metrics": [13, 14, 15, 16, 17],
        "Benchmarks": [18, 19, 20, 21],
        "Sector & Regime": [22, 23, 24],
    }
    
    CHART_NAMES = {
        1: "Allocation", 2: "Correlation", 3: "Risk Contrib",
        4: "vs Benchmarks", 5: "Sector Decomp", 6: "Sector Risk",
        7: "MC Normal", 8: "MC Random", 9: "Vol Normal",
        10: "Vol Random", 11: "DD Normal", 12: "DD Random",
        13: "VaR 95%", 14: "ES", 15: "DD Duration", 16: "Calmar",
        17: "Sharpe Ratio", 18: "Risk vs Idx", 19: "Fwd Excess", 
        20: "Port vs B. (N)", 21: "Port vs B. (R)", 22: "Sector Perf", 
        23: "Regime", 24: "Rotation"
    }
    
    CHART_DESCRIPTIONS = {
        1: "Shows weight distribution across portfolio assets", 
        2: "Correlation matrix between all assets", 
        3: "Individual asset contribution to total risk",
        4: "Compare portfolio performance vs benchmarks", 
        5: "Portfolio breakdown by market sectors", 
        6: "Risk distribution across different sectors",
        7: "Monte Carlo simulation with normal distribution", 
        8: "Monte Carlo simulation with random walk", 
        9: "Volatility forecast using normal distribution",
        10: "Volatility forecast using random scenarios", 
        11: "Maximum drawdown paths (normal dist.)", 
        12: "Maximum drawdown paths (random dist.)",
        13: "Value at Risk at 95% confidence", 
        14: "Expected Shortfall beyond VaR threshold", 
        15: "Duration of maximum drawdown periods", 
        16: "Calmar ratio (return/max drawdown)",
        17: "Sharpe Ratio (risk-adjusted return efficiency)",
        18: "Risk-return comparison with major indexes", 
        19: "Forward looking excess return analysis", 
        20: "Portfolio vs benchmark (normal scenario)",
        21: "Portfolio vs benchmark (random scenario)", 
        22: "Individual sector performance analysis", 
        23: "Market regime detection and analysis",
        24: "Sector rotation patterns over time"
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Architect")
        
        # Detect screen resolution and adapt window size dynamically
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Adapt window size based on actual screen resolution
        if screen_width >= 2560:  # 2.8K/4K display (ThinkPad P14 Gen5 with 2880x1800)
            window_width = 1920
            window_height = 1080
        elif screen_width >= 1920:  # Full HD (1920x1200)
            window_width = 1600
            window_height = 900
        else:  # Lower resolution
            window_width = 1400
            window_height = 800
        
        # Center the window on screen
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.configure(bg=T.MAIN_BG)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # State
        self.ticker_rows = []
        self.benchmark_rows = []
        self.chart_vars = {}
        
        # Local hints for autocomplete fallback
        self.local_ticker_hints = [
            "NVDA", "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "PLTR",
            "SPY", "QQQ", "VOO", "VTI", "GLD", "SLV", "IWDA.AS", "CSPX.L", "VUSA.L", "CW8.PA"
        ]
        self.local_bench_hints = [
            "^GSPC", "^NDX", "^DJI", "^GDAXI", "^FCHI", "^STOXX50E", "^IBEX", "^N225", "FTSEMIB.MI", "GC=F"
        ]
        
        # Initialize managers
        self.currency_manager = CurrencyManager(default_currency="USD")
        self.portfolio_manager = None
        self.market_data_manager = None
        self.symbol_handler = None
        self.analysis_runner = AnalysisRunner()
        
        # Setup UI
        self.setup_ui()
        
        # Initialize symbol handler after UI is created
        self._init_symbol_handler()
        
        # Start automatic refresh every 15 seconds (includes initial fetch)
        self._start_auto_refresh()
    
    def setup_ui(self):
        """Create the layout with Portfolio+Benchmarks side by side"""
        # Top toolbar
        self._create_toolbar()
        
        # Bottom button - CREATE FIRST so it reserves space at bottom
        self._create_run_button()
        
        # Main container - now it will fill remaining space
        main_frame = tk.Frame(self.root, bg=T.MAIN_BG)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # LEFT SIDE (50%) - Market Data + Portfolio + Benchmarks
        left_container = tk.Frame(main_frame, bg=T.MAIN_BG)
        left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        
        # Market Data at top
        self._create_market_data(left_container)
        
        # Portfolio and Benchmarks side by side
        middle_frame = tk.Frame(left_container, bg=T.MAIN_BG)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Portfolio left
        portfolio_frame = tk.Frame(middle_frame, bg=T.MAIN_BG)
        portfolio_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 3))
        self._create_portfolio(portfolio_frame)
        
        # Benchmarks right
        benchmark_frame = tk.Frame(middle_frame, bg=T.MAIN_BG)
        benchmark_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 0))
        self._create_benchmarks(benchmark_frame)
        
        # RIGHT SIDE (50%) - Chart Selection - MAXIMIZED
        right_container = tk.Frame(main_frame, bg=T.MAIN_BG)
        right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(3, 0))
        self._create_chart_selector(right_container)
    
    def _create_toolbar(self):
        """Top toolbar with capital and currency"""
        toolbar = tk.Frame(self.root, bg=T.PANEL_HEADER, height=50)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        tk.Label(
            toolbar,
            text="Portfolio Architect",
            font=("Segoe UI", 14, "bold"),
            bg=T.PANEL_HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(side=tk.LEFT, padx=20)
        
        # Credit signature (top right)
        tk.Label(
            toolbar,
            text="Built by Tom Campacci - Financial Student",
            font=("Segoe UI", 9, "italic"),
            bg=T.PANEL_HEADER,
            fg="#d0d0d0"
        ).pack(side=tk.RIGHT, padx=20)
        
        # Capital
        tk.Label(toolbar, text="Capital:", font=("Segoe UI", 10), bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK).pack(side=tk.LEFT, padx=(20, 5))
        self.capital_var = tk.StringVar(value="10000")
        tk.Entry(toolbar, textvariable=self.capital_var, font=("Segoe UI", 10), width=12, bg=T.INPUT_BG, relief=tk.FLAT).pack(side=tk.LEFT, padx=5)
        
        # Currency
        tk.Label(toolbar, text="Currency:", font=("Segoe UI", 10), bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK).pack(side=tk.LEFT, padx=(20, 5))
        self.currency_var = tk.StringVar(value="USD")
        currencies = ["USD", "EUR", "GBP"]
        currency_menu = ttk.Combobox(toolbar, textvariable=self.currency_var, values=currencies, width=8, state="readonly")
        currency_menu.pack(side=tk.LEFT, padx=5)
    
    def _create_market_data(self, parent):
        """Market data section with forex, commodities, bonds, and indexes"""
        section = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        section.pack(fill=tk.X, pady=(0, 10), padx=0)
        
        # Header
        header = tk.Frame(section, bg=T.PANEL_HEADER, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="💱 Market Data - Real-time Prices", font=("Segoe UI", 11, "bold"), 
                bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK).pack(side=tk.LEFT, padx=5, pady=8)
        
        # Content - Split in THREE columns (Forex+Commodities | Major Indexes | Others)
        content = tk.Frame(section, bg=T.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # LEFT COLUMN: Forex Rates + Commodities
        left_column = tk.Frame(content, bg=T.CARD_BG)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Forex Rates subsection
        tk.Label(left_column, text="Forex Rates (vs USD)", font=("Segoe UI", 9, "bold"), 
                bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        self.forex_labels = {}
        for currency in ["EUR", "GBP", "JPY", "CHF"]:
            row = tk.Frame(left_column, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=1)
            
            tk.Label(row, text=f"{currency}/USD:", font=("Segoe UI", 8), bg=T.CARD_BG, 
                    fg=T.TEXT_SECONDARY, width=10, anchor="w").pack(side=tk.LEFT)
            
            # Container for change% and price
            value_container = tk.Frame(row, bg=T.CARD_BG)
            value_container.pack(side=tk.RIGHT)
            
            # Change label (points + %) - Wider to show full values with colored background
            change_label = tk.Label(value_container, text="", font=("Segoe UI", 7), bg=T.CARD_BG, 
                                   fg=T.TEXT_SECONDARY, anchor="e", width=20)
            change_label.pack(side=tk.LEFT, padx=(0, 3))
            
            # Price label (right) - Same as commodities
            value_label = tk.Label(value_container, text="Loading...", font=("Segoe UI", 8), bg=T.CARD_BG, 
                                  fg=T.TEXT_PRIMARY, anchor="e", width=8)
            value_label.pack(side=tk.LEFT)
            
            self.forex_labels[currency] = {
                'price': value_label,
                'change': change_label,
                'container': value_container
            }
        
        # Spacing
        tk.Frame(left_column, bg=T.CARD_BG, height=8).pack()
        
        # Commodities subsection
        tk.Label(left_column, text="Commodities", font=("Segoe UI", 9, "bold"), 
                bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        self.commodity_labels = {}
        commodities = [
            ("GC=F", "Gold"),
            ("SI=F", "Silver"),
            ("CL=F", "Oil (WTI)")
        ]
        for symbol, name in commodities:
            row = tk.Frame(left_column, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=1)
            
            tk.Label(row, text=f"{name}:", font=("Segoe UI", 8), bg=T.CARD_BG, 
                    fg=T.TEXT_SECONDARY, width=10, anchor="w").pack(side=tk.LEFT)
            
            # Container for change% and price
            value_container = tk.Frame(row, bg=T.CARD_BG)
            value_container.pack(side=tk.RIGHT)
            
            # Change label (points + %) - Wider to show full values with colored background
            change_label = tk.Label(value_container, text="", font=("Segoe UI", 7), bg=T.CARD_BG, 
                                   fg=T.TEXT_SECONDARY, anchor="e", width=20)
            change_label.pack(side=tk.LEFT, padx=(0, 3))
            
            # Price label (right)
            value_label = tk.Label(value_container, text="Loading...", font=("Segoe UI", 8), bg=T.CARD_BG, 
                                  fg=T.TEXT_PRIMARY, anchor="e", width=8)
            value_label.pack(side=tk.LEFT)
            
            self.commodity_labels[symbol] = {
                'price': value_label,
                'change': change_label,
                'container': value_container
            }
        
        # Spacing
        tk.Frame(left_column, bg=T.CARD_BG, height=8).pack()
        
        # Bonds subsection
        tk.Label(left_column, text="Bonds", font=("Segoe UI", 9, "bold"), 
                bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        self.bond_labels = {}
        bonds = [("^TNX", "US 10Y")]
        for symbol, name in bonds:
            row = tk.Frame(left_column, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=1)
            
            tk.Label(row, text=f"{name}:", font=("Segoe UI", 8), bg=T.CARD_BG, 
                    fg=T.TEXT_SECONDARY, width=10, anchor="w").pack(side=tk.LEFT)
            
            # Container for change% and price
            value_container = tk.Frame(row, bg=T.CARD_BG)
            value_container.pack(side=tk.RIGHT)
            
            # Change label (points + %) - Wider to show full values with colored background
            change_label = tk.Label(value_container, text="", font=("Segoe UI", 7), bg=T.CARD_BG, 
                                   fg=T.TEXT_SECONDARY, anchor="e", width=20)
            change_label.pack(side=tk.LEFT, padx=(0, 3))
            
            # Price label (right)
            value_label = tk.Label(value_container, text="Loading...", font=("Segoe UI", 8), bg=T.CARD_BG, 
                                  fg=T.TEXT_PRIMARY, anchor="e", width=8)
            value_label.pack(side=tk.LEFT)
            
            self.bond_labels[symbol] = {
                'price': value_label,
                'change': change_label,
                'container': value_container
            }
        
        # MIDDLE COLUMN: Major Indexes
        indexes_frame = tk.Frame(content, bg=T.CARD_BG)
        indexes_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(indexes_frame, text="Major Indexes", font=("Segoe UI", 9, "bold"), 
                bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        self.index_labels = {}
        indexes = [
            ("^GSPC", "S&P 500"), 
            ("^DJI", "Dow Jones"), 
            ("^IXIC", "Nasdaq"),
            ("^GDAXI", "DAX"),
            ("^FCHI", "CAC 40"),
            ("^FTSE", "FTSE 100"),
            ("^N225", "Nikkei 225"),
            ("^HSI", "Hang Seng")
        ]
        for symbol, name in indexes:
            row = tk.Frame(indexes_frame, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=1)
            
            tk.Label(row, text=f"{name}:", font=("Segoe UI", 8), bg=T.CARD_BG, 
                    fg=T.TEXT_SECONDARY, width=12, anchor="w").pack(side=tk.LEFT)
            
            # Container for change% and price
            value_container = tk.Frame(row, bg=T.CARD_BG)
            value_container.pack(side=tk.RIGHT)
            
            # Change label (points + %) - Wider to show full values with colored background
            change_label = tk.Label(value_container, text="", font=("Segoe UI", 7), bg=T.CARD_BG, 
                                   fg=T.TEXT_SECONDARY, anchor="e", width=20)
            change_label.pack(side=tk.LEFT, padx=(0, 3))
            
            # Price label (right)
            value_label = tk.Label(value_container, text="Loading...", font=("Segoe UI", 8), bg=T.CARD_BG, 
                                  fg=T.TEXT_PRIMARY, anchor="e", width=8)
            value_label.pack(side=tk.LEFT)
            
            self.index_labels[symbol] = {
                'price': value_label,
                'change': change_label,
                'container': value_container
            }
    
    def _create_portfolio(self, parent):
        """Portfolio section - 10 rows"""
        section = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        section.pack(fill=tk.BOTH, expand=True, padx=0)
        
        # Header
        header = tk.Frame(section, bg=T.PANEL_HEADER, height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Portfolio Positions", font=("Segoe UI", 12, "bold"), 
                bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK).pack(side=tk.LEFT, padx=5, pady=10)
        
        # Buttons
        btn_frame = tk.Frame(header, bg=T.PANEL_HEADER)
        btn_frame.pack(side=tk.RIGHT, padx=5)
        
        equal_btn = tk.Button(btn_frame, text="Equal", font=("Segoe UI", 9), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, 
                     relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self._equal_weights)
        equal_btn.pack(side=tk.LEFT, padx=2)
        
        auto_btn = tk.Button(btn_frame, text="Auto 100%", font=("Segoe UI", 9), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, 
                     relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self._auto_100_percent)
        auto_btn.pack(side=tk.LEFT, padx=2)
        
        clear_btn = tk.Button(btn_frame, text="Clear", font=("Segoe UI", 9), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, 
                     relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self._clear_weights)
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Content
        content = tk.Frame(section, bg=T.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Headers
        hdr = tk.Frame(content, bg=T.CARD_BG)
        hdr.pack(fill=tk.X, pady=(0, 5))
        tk.Label(hdr, text="#", font=("Segoe UI", 8, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, width=2).pack(side=tk.LEFT, padx=1)
        tk.Label(hdr, text="Ticker/ISIN", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Label(hdr, text="Weight %", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w", width=9).pack(side=tk.LEFT, padx=2)
        tk.Label(hdr, text="Amount", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w", width=9).pack(side=tk.LEFT, padx=2)
        tk.Label(hdr, text="", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, width=2).pack(side=tk.LEFT, padx=0)
        
        # 10 rows
        for i in range(10):
            self._create_portfolio_row(content, i)
        
        # Total
        total_frame = tk.Frame(section, bg=T.HIGHLIGHT, height=40)
        total_frame.pack(fill=tk.X)
        total_frame.pack_propagate(False)
        self.weight_total_label = tk.Label(total_frame, text="Total: 0%", font=("Segoe UI", 10, "bold"), 
                                           bg=T.HIGHLIGHT, fg=T.TEXT_PRIMARY)
        self.weight_total_label.pack(side=tk.LEFT, padx=5)
    
    def _create_portfolio_row(self, parent, idx):
        """Create portfolio row with name label"""
        # Main row container
        row_container = tk.Frame(parent, bg=T.CARD_BG)
        row_container.pack(fill=tk.BOTH, expand=True, pady=1, padx=0)
        
        # Top row: Number + Entry + Weight + Amount + Status
        top_row = tk.Frame(row_container, bg=T.CARD_BG)
        top_row.pack(fill=tk.X)
        
        # Number
        tk.Label(top_row, text=str(idx+1), font=("Segoe UI", 8), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, width=2).pack(side=tk.LEFT, padx=1)
        
        # Ticker
        ticker_frame = tk.Frame(top_row, bg=T.CARD_BG)
        ticker_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ticker_entry = tk.Entry(ticker_frame, font=("Segoe UI", 10), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=1)
        ticker_entry.pack(fill=tk.BOTH, expand=True)
        
        # Weight %
        weight_frame = tk.Frame(top_row, bg=T.CARD_BG)
        weight_frame.pack(side=tk.LEFT, padx=2)
        weight_entry = tk.Entry(weight_frame, font=("Segoe UI", 10), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=1, width=10)
        weight_entry.pack(fill=tk.BOTH, expand=True)
        
        # Amount
        amount_frame = tk.Frame(top_row, bg=T.CARD_BG)
        amount_frame.pack(side=tk.LEFT, padx=2)
        amount_entry = tk.Entry(amount_frame, font=("Segoe UI", 10), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=1, width=10)
        amount_entry.pack(fill=tk.BOTH, expand=True)
        
        # Status
        status_label = tk.Label(top_row, text="●", font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.BORDER, width=2)
        status_label.pack(side=tk.LEFT)
        
        # Bottom row: Name label (for displaying asset name after validation)
        name_label = tk.Label(row_container, text="", font=("Segoe UI", 8), bg=T.CARD_BG, 
                             fg=T.TEXT_SECONDARY, anchor="w", wraplength=400)
        name_label.pack(fill=tk.X, padx=(20, 0))
        
        # Bind auto-calculation
        weight_entry.bind("<KeyRelease>", lambda e, idx=idx: self._on_weight_change(idx))
        amount_entry.bind("<KeyRelease>", lambda e, idx=idx: self._on_amount_change(idx))
        
        self.ticker_rows.append({
            "entry": ticker_entry,
            "weight_entry": weight_entry,
            "amount_entry": amount_entry,
            "status": status_label,
            "name_label": name_label,
            "placeholder": f"Ticker {idx+1}"
        })
    
    def _create_benchmarks(self, parent):
        """Benchmarks section - 6 rows"""
        section = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        section.pack(fill=tk.BOTH, expand=True, padx=0)
        
        # Header
        header = tk.Frame(section, bg=T.PANEL_HEADER, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📈 Benchmark Indexes", font=("Segoe UI", 11, "bold"), 
                bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK).pack(side=tk.LEFT, padx=5, pady=8)
        
        # Content
        content = tk.Frame(section, bg=T.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Headers
        hdr = tk.Frame(content, bg=T.CARD_BG)
        hdr.pack(fill=tk.X, pady=(0, 5))
        tk.Label(hdr, text="#", font=("Segoe UI", 8, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, width=2).pack(side=tk.LEFT, padx=1)
        tk.Label(hdr, text="Benchmark", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Label(hdr, text="", font=("Segoe UI", 9), bg=T.CARD_BG, width=2).pack(side=tk.LEFT)
        
        # 6 rows
        for i in range(6):
            self._create_benchmark_row(content, i)
    
    def _create_benchmark_row(self, parent, idx):
        """Create benchmark row with name label"""
        # Main row container
        row_container = tk.Frame(parent, bg=T.CARD_BG)
        row_container.pack(fill=tk.BOTH, expand=True, pady=1, padx=0)
        
        # Top row: Number + Entry + Browse + Status
        top_row = tk.Frame(row_container, bg=T.CARD_BG)
        top_row.pack(fill=tk.X)
        
        # Number
        tk.Label(top_row, text=str(idx+1), font=("Segoe UI", 8), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, width=2).pack(side=tk.LEFT, padx=1)
        
        # Benchmark entry
        bench_entry = tk.Entry(top_row, font=("Segoe UI", 10), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=1)
        bench_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        # Browse button
        browse_btn = tk.Button(top_row, text="📋", font=("Segoe UI", 9), bg=T.PRIMARY, fg=T.TEXT_ON_DARK,
                              relief=tk.FLAT, padx=8, pady=2, cursor="hand2",
                              command=lambda: self._open_benchmark_selector(idx))
        browse_btn.pack(side=tk.LEFT, padx=2)
        
        # Status
        status_label = tk.Label(top_row, text="●", font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.BORDER, width=2)
        status_label.pack(side=tk.LEFT)
        
        # Bottom row: Name label (for displaying benchmark name after validation)
        name_label = tk.Label(row_container, text="", font=("Segoe UI", 8), bg=T.CARD_BG, 
                             fg=T.TEXT_SECONDARY, anchor="w", wraplength=400)
        name_label.pack(fill=tk.X, padx=(20, 0))
        
        self.benchmark_rows.append({
            "entry": bench_entry,
            "status": status_label,
            "name_label": name_label,
            "browse_btn": browse_btn,
            "placeholder": f"Benchmark {idx+1}"
        })
    
    def _create_chart_selector(self, parent):
        """Chart selection panel - 3 COLUMNS LAYOUT with centered titles"""
        section = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        section.pack(fill=tk.BOTH, expand=True, padx=0)
        
        # Header
        header = tk.Frame(section, bg=T.PANEL_HEADER, height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Analysis Charts Selection", font=("Segoe UI", 12, "bold"), 
                bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK).pack(side=tk.LEFT, padx=8, pady=10)
        
        # Select All/None buttons
        btn_frame = tk.Frame(header, bg=T.PANEL_HEADER)
        btn_frame.pack(side=tk.RIGHT, padx=8)
        
        tk.Button(btn_frame, text="All", font=("Segoe UI", 9), bg=T.PRIMARY, fg=T.TEXT_ON_DARK,
                 relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self._select_all_charts).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="None", font=("Segoe UI", 9), bg=T.ERROR, fg=T.TEXT_ON_DARK,
                 relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self._select_no_charts).pack(side=tk.LEFT, padx=2)
        
        # Scrollable content
        canvas = tk.Canvas(section, bg=T.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(section, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=T.CARD_BG)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Categories
        for category, charts in self.CHART_GROUPS.items():
            # Category header - CENTERED TEXT - FULL WIDTH - 15PX BREATHING ROOM
            cat_header = tk.Frame(scrollable_frame, bg=T.HIGHLIGHT, height=30)
            cat_header.pack(fill=tk.X, pady=(15, 0), padx=0)
            cat_header.pack_propagate(False)
            
            # Center the category label - MEDIUM FONT
            tk.Label(cat_header, text=category, font=("Segoe UI", 10, "bold"), 
                    bg=T.HIGHLIGHT, fg=T.TEXT_PRIMARY).pack(expand=True, pady=6)
            
            # Charts container (3 columns) - FULL WIDTH - MORE SPACING
            charts_container = tk.Frame(scrollable_frame, bg=T.CARD_BG)
            charts_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=(4, 8))
            
            # Three columns - FULL WIDTH to edges
            col1 = tk.Frame(charts_container, bg=T.CARD_BG)
            col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 1))
            
            col2 = tk.Frame(charts_container, bg=T.CARD_BG)
            col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(1, 1))
            
            col3 = tk.Frame(charts_container, bg=T.CARD_BG)
            col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(1, 0))
            
            # Distribute charts in 3 columns
            for i, chart_num in enumerate(charts):
                # Determine target column (0, 1, or 2)
                col_index = i % 3
                target_col = [col1, col2, col3][col_index]
                
                # Chart item
                var = tk.BooleanVar(value=False)
                self.chart_vars[chart_num] = var
                
                item_frame = tk.Frame(target_col, bg=T.CARD_BG)
                item_frame.pack(fill=tk.BOTH, expand=True, pady=2, padx=0)
                
                # Checkbox - medium padding
                cb = tk.Checkbutton(item_frame, variable=var, bg=T.CARD_BG, activebackground=T.CARD_BG, 
                                   relief=tk.FLAT, bd=0, highlightthickness=0)
                cb.pack(side=tk.LEFT, padx=(1, 4))
                
                # Chart number and name
                chart_name = f"{chart_num}. {self.CHART_NAMES[chart_num]}"
                chart_desc = self.CHART_DESCRIPTIONS[chart_num]
                
                name_frame = tk.Frame(item_frame, bg=T.CARD_BG)
                name_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0)
                
                # MEDIUM FONTS - balanced readability and space usage
                tk.Label(name_frame, text=chart_name, font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_PRIMARY, 
                        anchor="w").pack(fill=tk.X, pady=(0, 1))
                # Smaller font for better description readability
                tk.Label(name_frame, text=chart_desc, font=("Segoe UI", 7), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, 
                        anchor="w", wraplength=260).pack(fill=tk.X)
    
    def _create_run_button(self):
        """Large run analysis button"""
        btn_frame = tk.Frame(self.root, bg=T.MAIN_BG, height=60)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        btn_frame.pack_propagate(False)
        
        run_btn = tk.Button(
            btn_frame,
            text="Run Portfolio Analysis",
            font=("Segoe UI", 12, "bold"),
            bg="#27ae60",
            fg="white",
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor="hand2",
            command=self._run_analysis
        )
        run_btn.pack(expand=True)
    
    def _open_benchmark_selector(self, idx):
        """Open enhanced benchmark selector with two tabs: Major Indexes and Search"""
        # Create modal dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Select Benchmark")
        dialog.geometry("900x650")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=T.MAIN_BG)
        
        # Header
        header_frame = tk.Frame(dialog, bg=T.PANEL_HEADER, height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        tk.Label(
            header_frame, text="📈 Benchmark Selection",
            font=("Segoe UI", 14, "bold"), bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK
        ).pack(pady=18)
        
        # Notebook (Tabs)
        notebook = ttk.Notebook(dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Major Indexes
        major_indexes_frame = tk.Frame(notebook, bg=T.CARD_BG)
        notebook.add(major_indexes_frame, text="  Major Indexes  ")
        self._create_major_indexes_tab(major_indexes_frame, dialog, idx)
        
        # Tab 2: Search Stock/ETF
        search_frame = tk.Frame(notebook, bg=T.CARD_BG)
        notebook.add(search_frame, text="  Search Stock/ETF  ")
        self._create_search_tab(search_frame, dialog, idx)
        
        # Bottom buttons
        button_frame = tk.Frame(dialog, bg=T.MAIN_BG)
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Button(
            button_frame, text="Close", 
            command=dialog.destroy,
            font=("Segoe UI", 10), bg=T.BORDER, fg=T.TEXT_PRIMARY,
            padx=20, pady=8, relief=tk.FLAT, cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
    
    def _create_major_indexes_tab(self, parent, dialog, bench_idx):
        """Create the Major Indexes tab with regional organization"""
        from utils.utils_data import get_popular_benchmarks
        
        # Info label
        info_frame = tk.Frame(parent, bg=T.HIGHLIGHT, height=40)
        info_frame.pack(fill=tk.X, padx=0, pady=(0, 10))
        info_frame.pack_propagate(False)
        
        tk.Label(
            info_frame, 
            text="Select from popular benchmark indexes organized by region",
            font=("Segoe UI", 10), bg=T.HIGHLIGHT, fg=T.TEXT_PRIMARY
        ).pack(pady=10, padx=15)
        
        # Scrollable content
        canvas = tk.Canvas(parent, bg=T.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=T.CARD_BG)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Get and organize popular benchmarks
        popular_benchmarks = get_popular_benchmarks()
        
        # Organize by region
        regions = {
            "🇺🇸 United States": [],
            "🇪🇺 Europe": [],
            "🌏 Asia Pacific": [],
            "💰 Commodities": []
        }
        
        for bench in popular_benchmarks:
            symbol = bench["symbol"]
            name = bench["name"]
            
            if "S&P" in name or "Nasdaq" in name or "Dow Jones" in name:
                regions["🇺🇸 United States"].append(bench)
            elif "DAX" in name or "CAC" in name or "FTSE" in name or "Stoxx" in name or "IBEX" in name or "MIB" in name:
                regions["🇪🇺 Europe"].append(bench)
            elif "Nikkei" in name or "Hang Seng" in name:
                regions["🌏 Asia Pacific"].append(bench)
            elif "Gold" in name or "Oil" in name or "Crude" in name:
                regions["💰 Commodities"].append(bench)
        
        # Display by region
        for region_name, benchmarks in regions.items():
            if not benchmarks:
                continue
            
            # Region header
            region_header = tk.Frame(scrollable_frame, bg=T.PANEL_HEADER, height=40)
            region_header.pack(fill=tk.X, pady=(10, 5), padx=5)
            region_header.pack_propagate(False)
            
            tk.Label(
                region_header, text=region_name,
                font=("Segoe UI", 11, "bold"), bg=T.PANEL_HEADER, fg=T.TEXT_ON_DARK
            ).pack(side=tk.LEFT, padx=15, pady=10)
            
            # Add benchmarks as clickable items
            for bench in benchmarks:
                symbol = bench["symbol"]
                name = bench["name"]
                
                # Create clickable item
                item_frame = tk.Frame(scrollable_frame, bg=T.INPUT_BG, relief=tk.RAISED, bd=1, cursor="hand2")
                item_frame.pack(fill=tk.X, pady=3, padx=15)
                
                # Left side: Symbol and name
                info_container = tk.Frame(item_frame, bg=T.INPUT_BG)
                info_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=12)
                
                tk.Label(
                    info_container, text=symbol,
                    font=("Segoe UI", 11, "bold"), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, anchor="w"
                ).pack(anchor="w")
                
                tk.Label(
                    info_container, text=name,
                    font=("Segoe UI", 9), bg=T.INPUT_BG, fg=T.TEXT_SECONDARY, anchor="w"
                ).pack(anchor="w")
                
                # Right side: Select button
                select_btn = tk.Button(
                    item_frame, text="Select",
                    font=("Segoe UI", 9, "bold"), bg=T.SUCCESS, fg=T.TEXT_ON_DARK,
                    relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                    command=lambda s=symbol, d=dialog, idx=bench_idx: self._select_benchmark(s, d, idx)
                )
                select_btn.pack(side=tk.RIGHT, padx=10, pady=8)
                
                # Hover effects
                def on_enter(e, frame=item_frame):
                    frame.config(bg=T.HIGHLIGHT)
                    for child in frame.winfo_children():
                        if isinstance(child, tk.Frame):
                            child.config(bg=T.HIGHLIGHT)
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    subchild.config(bg=T.HIGHLIGHT)
                
                def on_leave(e, frame=item_frame):
                    frame.config(bg=T.INPUT_BG)
                    for child in frame.winfo_children():
                        if isinstance(child, tk.Frame):
                            child.config(bg=T.INPUT_BG)
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    subchild.config(bg=T.INPUT_BG)
                
                item_frame.bind("<Enter>", on_enter)
                item_frame.bind("<Leave>", on_leave)
                info_container.bind("<Enter>", on_enter)
                info_container.bind("<Leave>", on_leave)
    
    def _create_search_tab(self, parent, dialog, bench_idx):
        """Create the Search tab for looking up any stock/ETF"""
        # Info label
        info_frame = tk.Frame(parent, bg=T.HIGHLIGHT, height=40)
        info_frame.pack(fill=tk.X, padx=0, pady=(0, 10))
        info_frame.pack_propagate(False)
        
        tk.Label(
            info_frame, 
            text="Search for any stock, ETF, or index to use as a benchmark",
            font=("Segoe UI", 10), bg=T.HIGHLIGHT, fg=T.TEXT_PRIMARY
        ).pack(pady=10, padx=15)
        
        # Search bar
        search_frame = tk.Frame(parent, bg=T.CARD_BG)
        search_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(
            search_frame, text="Search:",
            font=("Segoe UI", 10, "bold"), bg=T.CARD_BG, fg=T.TEXT_PRIMARY
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        search_entry = tk.Entry(
            search_frame, font=("Segoe UI", 11), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY,
            relief=tk.FLAT, bd=2
        )
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=5)
        
        search_btn = tk.Button(
            search_frame, text="🔍 Search",
            font=("Segoe UI", 10, "bold"), bg=T.PRIMARY, fg=T.TEXT_ON_DARK,
            relief=tk.FLAT, padx=20, pady=8, cursor="hand2",
            command=lambda: self._perform_search(search_entry.get(), results_frame, dialog, bench_idx)
        )
        search_btn.pack(side=tk.LEFT)
        
        # Bind Enter key to search
        search_entry.bind("<Return>", lambda e: self._perform_search(search_entry.get(), results_frame, dialog, bench_idx))
        
        # Results frame (scrollable)
        results_container = tk.Frame(parent, bg=T.CARD_BG)
        results_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        canvas = tk.Canvas(results_container, bg=T.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(results_container, orient="vertical", command=canvas.yview)
        results_frame = tk.Frame(canvas, bg=T.CARD_BG)
        
        results_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=results_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initial help text
        tk.Label(
            results_frame,
            text="Enter a symbol or company name to search\nExamples: AAPL, SPY, QQQ, VWCE.DE, IWDA.AS",
            font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.TEXT_SECONDARY,
            justify=tk.CENTER
        ).pack(pady=50)
        
        # Focus search entry
        search_entry.focus_set()
    
    def _perform_search(self, query, results_frame, dialog, bench_idx):
        """Perform symbol search and display results"""
        from utils.utils_data import search_yahoo_symbols
        
        # Clear previous results
        for widget in results_frame.winfo_children():
            widget.destroy()
        
        if not query or not query.strip():
            tk.Label(
                results_frame,
                text="Please enter a search term",
                font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.ERROR
            ).pack(pady=20)
            return
        
        # Show loading message
        loading_label = tk.Label(
            results_frame,
            text=f"Searching for '{query}'...",
            font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.TEXT_SECONDARY
        )
        loading_label.pack(pady=20)
        results_frame.update()
        
        # Perform search
        try:
            results = search_yahoo_symbols(query, count=20)
            
            # Clear loading message
            loading_label.destroy()
            
            if not results:
                tk.Label(
                    results_frame,
                    text=f"No results found for '{query}'\nTry a different search term",
                    font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.TEXT_SECONDARY,
                    justify=tk.CENTER
                ).pack(pady=20)
                return
            
            # Display results
            tk.Label(
                results_frame,
                text=f"Found {len(results)} result(s):",
                font=("Segoe UI", 10, "bold"), bg=T.CARD_BG, fg=T.TEXT_PRIMARY,
                anchor="w"
            ).pack(fill=tk.X, pady=(5, 10), padx=5)
            
            for result in results:
                symbol = result.get("symbol", "")
                name = result.get("name", "Unknown")
                exchange = result.get("exchange", "")
                result_type = result.get("type", "")
                
                # Create result item
                item_frame = tk.Frame(results_frame, bg=T.INPUT_BG, relief=tk.RAISED, bd=1, cursor="hand2")
                item_frame.pack(fill=tk.X, pady=3, padx=5)
                
                # Left side: Symbol info
                info_container = tk.Frame(item_frame, bg=T.INPUT_BG)
                info_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=10)
                
                tk.Label(
                    info_container, text=symbol,
                    font=("Segoe UI", 11, "bold"), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, anchor="w"
                ).pack(anchor="w")
                
                tk.Label(
                    info_container, text=name,
                    font=("Segoe UI", 9), bg=T.INPUT_BG, fg=T.TEXT_SECONDARY, anchor="w"
                ).pack(anchor="w")
                
                if exchange or result_type:
                    detail_text = f"{exchange} • {result_type}" if exchange and result_type else (exchange or result_type)
                    tk.Label(
                        info_container, text=detail_text,
                        font=("Segoe UI", 8), bg=T.INPUT_BG, fg="#999", anchor="w"
                    ).pack(anchor="w")
                
                # Right side: Select button
                select_btn = tk.Button(
                    item_frame, text="Select",
                    font=("Segoe UI", 9, "bold"), bg=T.SUCCESS, fg=T.TEXT_ON_DARK,
                    relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                    command=lambda s=symbol, d=dialog, idx=bench_idx: self._select_benchmark(s, d, idx)
                )
                select_btn.pack(side=tk.RIGHT, padx=10, pady=8)
                
                # Hover effects
                def on_enter(e, frame=item_frame):
                    frame.config(bg=T.HIGHLIGHT)
                    for child in frame.winfo_children():
                        if isinstance(child, tk.Frame):
                            child.config(bg=T.HIGHLIGHT)
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    subchild.config(bg=T.HIGHLIGHT)
                
                def on_leave(e, frame=item_frame):
                    frame.config(bg=T.INPUT_BG)
                    for child in frame.winfo_children():
                        if isinstance(child, tk.Frame):
                            child.config(bg=T.INPUT_BG)
                            for subchild in child.winfo_children():
                                if isinstance(subchild, tk.Label):
                                    subchild.config(bg=T.INPUT_BG)
                
                item_frame.bind("<Enter>", on_enter)
                item_frame.bind("<Leave>", on_leave)
                info_container.bind("<Enter>", on_enter)
                info_container.bind("<Leave>", on_leave)
                
        except Exception as e:
            # Clear loading message
            loading_label.destroy()
            
            tk.Label(
                results_frame,
                text=f"Error during search: {str(e)}",
                font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.ERROR
            ).pack(pady=20)
    
    def _select_benchmark(self, symbol, dialog, bench_idx):
        """Select a benchmark and fill it in the row"""
        if 0 <= bench_idx < len(self.benchmark_rows):
            row = self.benchmark_rows[bench_idx]
            entry = row["entry"]
            
            # Fill the entry
            entry.delete(0, tk.END)
            entry.insert(0, symbol)
            entry.config(fg=T.TEXT_PRIMARY)
            
            # Trigger validation
            if self.symbol_handler:
                self.symbol_handler.queue_validate("bench", bench_idx)
        
        # Close dialog
        dialog.destroy()
    
    def _start_auto_refresh(self):
        """Start automatic market data refresh every 5 seconds"""
        def auto_refresh_loop():
            self._refresh_market_data()
            # Schedule next refresh in 5 seconds (5000 milliseconds)
            self.root.after(5000, auto_refresh_loop)
        
        # Start the loop
        auto_refresh_loop()
    
    def _refresh_market_data(self):
        """Refresh market data in background"""
        def fetch():
            print("Fetching market data...")
            forex_rates = get_current_forex_rates()
            indexes_prices = get_major_indexes_prices()
            print(f"Forex rates: {forex_rates}")
            print(f"Indexes prices: {indexes_prices}")
            self.root.after(0, lambda: self._update_market_data(forex_rates, indexes_prices))
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def _update_market_data(self, forex_rates, indexes_prices):
        """Update UI with market data including % change with colors"""
        print("Updating UI with market data...")
        try:
            # Update forex (EUR, GBP, JPY, CHF)
            if forex_rates and forex_rates.get('success'):
                for currency in ["EUR", "GBP", "JPY", "CHF"]:
                    key = f"{currency}USD"
                    value = forex_rates.get(key, 0)
                    change_pct = forex_rates.get(f"{key}_change_pct", 0)
                    change_pts = forex_rates.get(f"{key}_change_pts", 0)
                    
                    if currency in self.forex_labels:
                        labels = self.forex_labels[currency]
                        
                        # Update price (different formats for JPY)
                        if currency == "JPY":
                            labels['price'].config(text=f"{value:.2f}")
                        else:
                            labels['price'].config(text=f"{value:.4f}")
                        
                        # Update change (points + %) with color
                        if change_pct is not None and change_pct != 0:
                            if currency == "JPY":
                                change_text = f"{change_pts:+.2f} ({change_pct:+.2f}%)"
                            else:
                                change_text = f"{change_pts:+.4f} ({change_pct:+.2f}%)"
                            
                            if change_pct > 0:
                                # Light green background
                                labels['change'].config(text=change_text, bg="#d4edda", fg="#155724")
                                # Flash effect
                                self.root.after(1000, lambda l=labels['change']: l.config(bg=T.CARD_BG, fg=T.TEXT_SECONDARY))
                            else:
                                # Light red background
                                labels['change'].config(text=change_text, bg="#f8d7da", fg="#721c24")
                                # Flash effect
                                self.root.after(1000, lambda l=labels['change']: l.config(bg=T.CARD_BG, fg=T.TEXT_SECONDARY))
                        else:
                            labels['change'].config(text="0.00 (0.00%)", bg=T.CARD_BG, fg=T.TEXT_SECONDARY)
                        
                        print(f"Updated {currency}: {value:.4f} ({change_pts:+.4f} / {change_pct:+.2f}%)")
            
            # Update indexes, commodities, and bonds
            if indexes_prices and indexes_prices.get('success'):
                for idx_data in indexes_prices.get('indexes', []):
                    symbol = idx_data.get('symbol')
                    price = idx_data.get('price', 0)
                    change_pct = idx_data.get('change_pct', 0)
                    change_pts = idx_data.get('change_pts', 0)
                    
                    if not idx_data.get('success'):
                        continue
                    
                    # Determine which label dictionary to use
                    labels = None
                    if symbol in self.index_labels:
                        labels = self.index_labels[symbol]
                        price_format = f"{price:,.0f}"
                        change_format = f"{change_pts:+.1f} ({change_pct:+.2f}%)"
                    elif symbol in self.commodity_labels:
                        labels = self.commodity_labels[symbol]
                        price_format = f"${price:,.2f}"
                        change_format = f"${change_pts:+.2f} ({change_pct:+.2f}%)"
                    elif symbol in self.bond_labels:
                        labels = self.bond_labels[symbol]
                        price_format = f"{price:.2f}%"  # Treasury yields are in percentage
                        change_format = f"{change_pts:+.2f} ({change_pct:+.2f}%)"
                    
                    if labels:
                        # Update price
                        labels['price'].config(text=price_format)
                        
                        # Update change (points + %) with color
                        if change_pct is not None and change_pct != 0:
                            if change_pct > 0:
                                # Light green background
                                labels['change'].config(text=change_format, bg="#d4edda", fg="#155724")
                                # Flash effect
                                self.root.after(1000, lambda l=labels['change']: l.config(bg=T.CARD_BG, fg=T.TEXT_SECONDARY))
                            else:
                                # Light red background
                                labels['change'].config(text=change_format, bg="#f8d7da", fg="#721c24")
                                # Flash effect
                                self.root.after(1000, lambda l=labels['change']: l.config(bg=T.CARD_BG, fg=T.TEXT_SECONDARY))
                        else:
                            labels['change'].config(text="0.0 (0.00%)", bg=T.CARD_BG, fg=T.TEXT_SECONDARY)
                        
                        print(f"Updated {symbol}: {price_format} ({change_format})")
            
            print("Market data update complete")
        except Exception as e:
            print(f"Error updating market data: {e}")
    
    def _select_all_charts(self):
        """Select all charts"""
        for var in self.chart_vars.values():
            var.set(True)
    
    def _select_no_charts(self):
        """Deselect all charts"""
        for var in self.chart_vars.values():
            var.set(False)
    
    def _run_analysis(self):
        """Run portfolio analysis and generate charts"""
        print("DEBUG: Run Analysis button clicked!")  # Debug message
        
        # Check if charts are selected
        selected = [num for num, var in self.chart_vars.items() if var.get()]
        print(f"DEBUG: Selected charts: {selected}")  # Debug message
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one chart!")
            return
        
        self.root.update()
        
        # Collect validated tickers with weights
        ticker_weights = []
        for row in self.ticker_rows:
            entry = row.get("entry")
            status_lbl = row.get("status")
            weight_entry = row.get("weight_entry")
            
            if not entry or not status_lbl:
                continue
            
            symbol = entry.get().strip().upper()
            status = status_lbl.cget("text")
            
            if symbol and status == "✓":
                try:
                    weight = float(weight_entry.get().strip()) if weight_entry else 0.0
                except ValueError:
                    weight = 0.0
                ticker_weights.append((symbol, weight))
        
        print(f"DEBUG: Validated tickers: {ticker_weights}")  # Debug message
        
        # Collect benchmarks
        benches = []
        for row in self.benchmark_rows:
            entry = row.get("entry")
            status_lbl = row.get("status")
            
            if not entry or not status_lbl:
                continue
            
            symbol = entry.get().strip().upper()
            status = status_lbl.cget("text")
            
            if symbol and status == "✓":
                benches.append(symbol)
        
        # Validate we have tickers
        if not ticker_weights:
            messagebox.showwarning("No Tickers", "Please add at least one validated ticker!")
            return
        
        # Get capital and currency
        try:
            capital = float(self.capital_var.get())
        except (ValueError, AttributeError):
            capital = None
        
        currency = self.currency_var.get() if hasattr(self, 'currency_var') else "USD"
        
        # Status callback to update UI
        def status_callback(msg):
            self.root.title(f"Portfolio Architect - {msg}")
            self.root.update()
        
        # Run analysis
        result = self.analysis_runner.run_analysis(
            ticker_weights=ticker_weights,
            benches=benches,
            selected_charts=selected,
            status_callback=status_callback,
            sanitize_func=SymbolValidator.sanitize_symbols,
            capital=capital,
            currency=currency
        )
        
        # Reset title
        self.root.title("Portfolio Architect")
        
        # Show result
        if result["success"]:
            messagebox.showinfo(
                "Complete", 
                f"{result['message']}\n\nSaved to: {result['output_dir']}"
            )
        else:
            messagebox.showerror("Error", result["message"])
    
    def _init_symbol_handler(self):
        """Initialize symbol handler and bind callbacks"""
        self.symbol_handler = SymbolUIHandler(
            self.root, self.ticker_rows, self.benchmark_rows,
            self.local_ticker_hints, self.local_bench_hints,
            on_validation_complete=self._on_symbol_validated
        )
        self._rebind_symbol_callbacks()
    
    def _rebind_symbol_callbacks(self):
        """Rebind entry widgets to use symbol_handler methods - with proper closure handling"""
        # Rebind ticker rows - using proper closure for each index
        for i, row in enumerate(self.ticker_rows):
            entry = row["entry"]
            placeholder = row["placeholder"]
            
            # Clear and rebind
            for event in ["<FocusIn>", "<FocusOut>", "<Return>"]:
                try:
                    entry.unbind(event)
                except:
                    pass
            
            # Create proper closures with default arguments to capture current values
            def make_focus_in_handler(ent, ph):
                return lambda e: self.symbol_handler.on_focus_in(ent, ph)
            
            def make_validate_handler(kind, index):
                return lambda e: self.symbol_handler.queue_validate(kind, index)
            
            entry.bind("<FocusIn>", make_focus_in_handler(entry, placeholder))
            entry.bind("<FocusOut>", make_validate_handler("ticker", i))
            entry.bind("<Return>", make_validate_handler("ticker", i))
        
        # Rebind benchmark rows - using proper closure for each index
        for i, row in enumerate(self.benchmark_rows):
            entry = row["entry"]
            placeholder = row["placeholder"]
            
            # Clear and rebind
            for event in ["<FocusIn>", "<FocusOut>", "<Return>"]:
                try:
                    entry.unbind(event)
                except:
                    pass
            
            # Create proper closures
            def make_focus_in_bench_handler(ent, ph, index):
                return lambda e: self.symbol_handler.on_focus_in(ent, ph, kind="bench", idx=index)
            
            def make_validate_bench_handler(kind, index):
                return lambda e: self.symbol_handler.queue_validate(kind, index)
            
            entry.bind("<FocusIn>", make_focus_in_bench_handler(entry, placeholder, i))
            entry.bind("<FocusOut>", make_validate_bench_handler("bench", i))
            entry.bind("<Return>", make_validate_bench_handler("bench", i))
    
    def _on_symbol_validated(self, kind):
        """Callback when symbol validation completes"""
        # This is called after a symbol is validated
        # You can add additional logic here if needed
        pass
    
    def _on_weight_change(self, idx):
        """Auto-calculate amount when weight changes"""
        try:
            row = self.ticker_rows[idx]
            weight_str = row["weight_entry"].get().strip()
            if not weight_str:
                self._update_weight_total()
                return
            
            weight = float(weight_str)
            capital = float(self.capital_var.get())
            amount = (weight / 100.0) * capital
            
            # Update amount field
            row["amount_entry"].delete(0, tk.END)
            row["amount_entry"].insert(0, f"{amount:.2f}")
            
            # Update total
            self._update_weight_total()
        except (ValueError, KeyError, IndexError):
            self._update_weight_total()
            pass
    
    def _on_amount_change(self, idx):
        """Auto-calculate weight when amount changes"""
        try:
            row = self.ticker_rows[idx]
            amount_str = row["amount_entry"].get().strip()
            if not amount_str:
                self._update_weight_total()
                return
            
            amount = float(amount_str)
            capital = float(self.capital_var.get())
            if capital > 0:
                weight = (amount / capital) * 100.0
                
                # Update weight field
                row["weight_entry"].delete(0, tk.END)
                row["weight_entry"].insert(0, f"{weight:.2f}")
                
                # Update total
                self._update_weight_total()
        except (ValueError, KeyError, IndexError, ZeroDivisionError):
            self._update_weight_total()
            pass
    
    def _on_closing(self):
        """Handle window close"""
        self.root.destroy()
    
    def _equal_weights(self):
        """Distribute weights equally among all non-empty ticker entries"""
        from tkinter import messagebox
        
        # Count non-empty ticker entries
        filled_rows = []
        for idx, row in enumerate(self.ticker_rows):
            entry = row.get("entry")
            if entry:
                ticker = entry.get().strip()
                if ticker:
                    filled_rows.append(idx)
        
        if not filled_rows:
            messagebox.showinfo("Equal Weights", "Please enter at least one ticker first.")
            return
        
        # Calculate equal weight
        equal_weight = 100.0 / len(filled_rows)
        
        # Apply to all filled rows
        for idx in filled_rows:
            row = self.ticker_rows[idx]
            weight_entry = row.get("weight_entry")
            if weight_entry:
                weight_entry.delete(0, tk.END)
                weight_entry.insert(0, f"{equal_weight:.2f}")
                # Trigger amount calculation
                self._on_weight_change(idx)
        
        # Update total
        self._update_weight_total()
        
        messagebox.showinfo("Equal Weights", 
                          f"Set equal weights of {equal_weight:.2f}% for {len(filled_rows)} positions.")
    
    def _auto_100_percent(self):
        """Auto-scale weights to reach 100% proportionally"""
        from tkinter import messagebox
        
        # Collect current weights
        current_weights = []
        for idx, row in enumerate(self.ticker_rows):
            entry = row.get("entry")
            weight_entry = row.get("weight_entry")
            
            if not entry or not weight_entry:
                continue
            
            ticker = entry.get().strip()
            if ticker:
                try:
                    weight = float(weight_entry.get().strip())
                    if weight > 0:
                        current_weights.append((idx, weight))
                except (ValueError, AttributeError):
                    pass
        
        if not current_weights:
            messagebox.showinfo("Auto 100%", "Please enter weights first.\n\nExample:\n  BNP: 20%\n  GLDA: 15%\n  ANXU: 30%\n  LVMH: 10%")
            return
        
        # Calculate total
        total = sum(w for _, w in current_weights)
        
        if total == 0:
            messagebox.showwarning("Auto 100%", "Total weight is 0%. Please enter valid weights.")
            return
        
        if abs(total - 100.0) < 0.01:
            messagebox.showinfo("Auto 100%", f"Weights already sum to 100.0%!")
            return
        
        # Calculate scaling factor
        scale_factor = 100.0 / total
        
        # Apply scaled weights
        for idx, old_weight in current_weights:
            new_weight = old_weight * scale_factor
            row = self.ticker_rows[idx]
            weight_entry = row.get("weight_entry")
            if weight_entry:
                weight_entry.delete(0, tk.END)
                weight_entry.insert(0, f"{new_weight:.2f}")
                # Trigger amount calculation
                self._on_weight_change(idx)
        
        # Update total
        self._update_weight_total()
        
        messagebox.showinfo("Auto 100%", 
                          f"Scaled {len(current_weights)} positions from {total:.2f}% to 100.0%!")
    
    def _clear_weights(self):
        """Clear all weights and amounts"""
        from tkinter import messagebox
        
        result = messagebox.askyesno("Clear Weights", 
                                     "This will reset all weights and amounts to 0.\n\nContinue?")
        if not result:
            return
        
        # Clear all weight and amount entries
        for row in self.ticker_rows:
            weight_entry = row.get("weight_entry")
            amount_entry = row.get("amount_entry")
            
            if weight_entry:
                weight_entry.delete(0, tk.END)
            if amount_entry:
                amount_entry.delete(0, tk.END)
        
        # Update total
        self._update_weight_total()
        
        messagebox.showinfo("Clear Weights", "All weights and amounts have been cleared.")
    
    def _update_weight_total(self):
        """Calculate and display total weight percentage"""
        total = 0.0
        
        for row in self.ticker_rows:
            weight_entry = row.get("weight_entry")
            if weight_entry:
                try:
                    weight = float(weight_entry.get().strip())
                    total += weight
                except (ValueError, AttributeError):
                    pass
        
        # Update label with color coding
        if abs(total - 100.0) < 0.01:
            self.weight_total_label.config(text=f"Total: {total:.2f}%", fg="#155724")  # Green
        elif total > 100.0:
            self.weight_total_label.config(text=f"Total: {total:.2f}% (over)", fg="#721c24")  # Red
        elif total > 0:
            self.weight_total_label.config(text=f"Total: {total:.2f}%", fg="#856404")  # Orange
        else:
            self.weight_total_label.config(text=f"Total: {total:.2f}%", fg=T.TEXT_PRIMARY)


def main():
    """Launch Portfolio Architect with high-DPI support"""
    # Enable DPI awareness BEFORE creating Tk() window (critical for Windows HiDPI)
    try:
        from ctypes import windll
        # Try Windows 10+ method (per-monitor DPI awareness v2)
        windll.shcore.SetProcessDpiAwareness(2)
    except:
        try:
            # Fallback: system DPI awareness (Windows 7+)
            from ctypes import windll
            windll.user32.SetProcessDPIAware()
        except:
            pass  # Not on Windows or unavailable
    
    root = tk.Tk()
    
    # Additional Tkinter scaling for crisp rendering
    try:
        root.tk.call('tk', 'scaling', 2.0)  # Adjust for HiDPI screens
    except:
        pass
    
    app = CompactPortfolioPanel(root)
    root.mainloop()


if __name__ == "__main__":
    main()

