# menu_principal_v4.py - Two-Page Portfolio Analysis Architecture
"""
Modern 2-page architecture:
- Page 1: Market Data + Portfolio + Benchmarks
- Page 2: Analysis Charts Selection
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import threading

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


class TwoPagePortfolioArchitect:
    """Two-page Portfolio Architect with Tabs"""
    
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
        self.root.title("Portfolio Architect - Two-Page Edition")
        
        # Detect screen resolution and adapt window size
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        if screen_width >= 2560:
            window_width = 1920
            window_height = 1080
        elif screen_width >= 1920:
            window_width = 1600
            window_height = 900
        else:
            window_width = 1400
            window_height = 800
        
        # Center the window
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.root.configure(bg=T.MAIN_BG)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # State
        self.ticker_rows = []
        self.benchmark_rows = []
        self.chart_vars = {}
        
        # Local hints for autocomplete
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
        
        # Market data labels
        self.forex_labels = {}
        self.index_labels = {}
        self.commodity_labels = {}
        self.bond_labels = {}
        
        # Setup UI
        self.setup_ui()
        
        # Initialize symbol handler after UI is created
        self._init_symbol_handler()
        
        # Start automatic refresh
        self._start_auto_refresh()
    
    def setup_ui(self):
        """Create the two-page tabbed interface"""
        # Top toolbar (always visible)
        self._create_toolbar()
        
        # Create notebook (tabs)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=T.MAIN_BG, borderwidth=0, tabmargins=[10, 10, 10, 0])
        style.configure('TNotebook.Tab', 
                       background=T.CARD_BG,
                       foreground=T.TEXT_PRIMARY,
                       padding=[30, 12],
                       font=('Segoe UI', 12, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', T.PRIMARY)],
                 foreground=[('selected', T.TEXT_ON_DARK)])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))
        
        # PAGE 1: Portfolio Setup
        page1 = tk.Frame(self.notebook, bg=T.MAIN_BG)
        self.notebook.add(page1, text='  📊 Portfolio Setup  ')
        self._create_page1_portfolio_setup(page1)
        
        # PAGE 2: Charts Selection
        page2 = tk.Frame(self.notebook, bg=T.MAIN_BG)
        self.notebook.add(page2, text='  📈 Analysis Charts  ')
        self._create_page2_charts_selection(page2)
        
        # Bottom button (always visible)
        self._create_run_button()
    
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
        
        # Credit signature
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
    
    def _create_page1_portfolio_setup(self, parent):
        """PAGE 1: Market Data + Portfolio + Benchmarks"""
        # Create scrollable container for page 1
        canvas = tk.Canvas(parent, bg=T.MAIN_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=T.MAIN_BG)
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 1. Market Data Section (full width)
        self._create_market_data(scrollable_frame)
        
        # 2. Portfolio + Benchmarks (side by side)
        positions_container = tk.Frame(scrollable_frame, bg=T.MAIN_BG)
        positions_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left: Portfolio Positions
        portfolio_frame = tk.Frame(positions_container, bg=T.MAIN_BG)
        portfolio_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self._create_portfolio(portfolio_frame)
        
        # Right: Benchmarks
        benchmark_frame = tk.Frame(positions_container, bg=T.MAIN_BG)
        benchmark_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        self._create_benchmarks(benchmark_frame)
    
    def _create_page2_charts_selection(self, parent):
        """PAGE 2: Analysis Charts Selection (full screen)"""
        # Info banner
        info_frame = tk.Frame(parent, bg=T.HIGHLIGHT, height=50)
        info_frame.pack(fill=tk.X, padx=15, pady=(10, 15))
        info_frame.pack_propagate(False)
        
        tk.Label(
            info_frame,
            text="📊 Select the analysis charts you want to generate for your portfolio",
            font=("Segoe UI", 11, "bold"),
            bg=T.HIGHLIGHT,
            fg=T.TEXT_PRIMARY
        ).pack(expand=True)
        
        # Chart selector (maximized)
        self._create_chart_selector(parent)
    
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
        
        # Content - Split in THREE columns
        content = tk.Frame(section, bg=T.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # LEFT COLUMN: Forex + Commodities
        left_column = tk.Frame(content, bg=T.CARD_BG)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Forex Rates subsection
        tk.Label(left_column, text="Forex Rates (vs USD)", font=("Segoe UI", 9, "bold"), 
                bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        for currency in ["EUR", "GBP", "JPY", "CHF"]:
            row = tk.Frame(left_column, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=1)
            
            tk.Label(row, text=f"{currency}/USD:", font=("Segoe UI", 8), bg=T.CARD_BG, 
                    fg=T.TEXT_SECONDARY, width=10, anchor="w").pack(side=tk.LEFT)
            
            value_container = tk.Frame(row, bg=T.CARD_BG)
            value_container.pack(side=tk.RIGHT)
            
            change_label = tk.Label(value_container, text="", font=("Segoe UI", 7), bg=T.CARD_BG, 
                                   fg=T.TEXT_SECONDARY, anchor="e", width=20)
            change_label.pack(side=tk.LEFT, padx=(0, 3))
            
            value_label = tk.Label(value_container, text="Loading...", font=("Segoe UI", 8), bg=T.CARD_BG, 
                                  fg=T.TEXT_PRIMARY, anchor="e", width=8)
            value_label.pack(side=tk.LEFT)
            
            self.forex_labels[currency] = {
                'price': value_label,
                'change': change_label,
                'container': value_container
            }
        
        tk.Frame(left_column, bg=T.CARD_BG, height=8).pack()
        
        # Commodities subsection
        tk.Label(left_column, text="Commodities", font=("Segoe UI", 9, "bold"), 
                bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
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
            
            value_container = tk.Frame(row, bg=T.CARD_BG)
            value_container.pack(side=tk.RIGHT)
            
            change_label = tk.Label(value_container, text="", font=("Segoe UI", 7), bg=T.CARD_BG, 
                                   fg=T.TEXT_SECONDARY, anchor="e", width=20)
            change_label.pack(side=tk.LEFT, padx=(0, 3))
            
            value_label = tk.Label(value_container, text="Loading...", font=("Segoe UI", 8), bg=T.CARD_BG, 
                                  fg=T.TEXT_PRIMARY, anchor="e", width=8)
            value_label.pack(side=tk.LEFT)
            
            self.commodity_labels[symbol] = {
                'price': value_label,
                'change': change_label,
                'container': value_container
            }
        
        tk.Frame(left_column, bg=T.CARD_BG, height=8).pack()
        
        # Bonds subsection
        tk.Label(left_column, text="Bonds", font=("Segoe UI", 9, "bold"), 
                bg=T.CARD_BG, fg=T.TEXT_PRIMARY, anchor="w").pack(fill=tk.X, pady=(0, 3))
        
        bonds = [("^TNX", "US 10Y")]
        for symbol, name in bonds:
            row = tk.Frame(left_column, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=1)
            
            tk.Label(row, text=f"{name}:", font=("Segoe UI", 8), bg=T.CARD_BG, 
                    fg=T.TEXT_SECONDARY, width=10, anchor="w").pack(side=tk.LEFT)
            
            value_container = tk.Frame(row, bg=T.CARD_BG)
            value_container.pack(side=tk.RIGHT)
            
            change_label = tk.Label(value_container, text="", font=("Segoe UI", 7), bg=T.CARD_BG, 
                                   fg=T.TEXT_SECONDARY, anchor="e", width=20)
            change_label.pack(side=tk.LEFT, padx=(0, 3))
            
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
            
            value_container = tk.Frame(row, bg=T.CARD_BG)
            value_container.pack(side=tk.RIGHT)
            
            change_label = tk.Label(value_container, text="", font=("Segoe UI", 7), bg=T.CARD_BG, 
                                   fg=T.TEXT_SECONDARY, anchor="e", width=20)
            change_label.pack(side=tk.LEFT, padx=(0, 3))
            
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
        
        tk.Button(btn_frame, text="Equal", font=("Segoe UI", 9), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, 
                 relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self._equal_weights).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="Auto 100%", font=("Segoe UI", 9), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, 
                 relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self._auto_100_percent).pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="Clear", font=("Segoe UI", 9), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, 
                 relief=tk.FLAT, padx=10, pady=3, cursor="hand2", command=self._clear_weights).pack(side=tk.LEFT, padx=2)
        
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
        """Create portfolio row"""
        row_container = tk.Frame(parent, bg=T.CARD_BG)
        row_container.pack(fill=tk.BOTH, expand=True, pady=1, padx=0)
        
        top_row = tk.Frame(row_container, bg=T.CARD_BG)
        top_row.pack(fill=tk.X)
        
        tk.Label(top_row, text=str(idx+1), font=("Segoe UI", 8), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, width=2).pack(side=tk.LEFT, padx=1)
        
        ticker_frame = tk.Frame(top_row, bg=T.CARD_BG)
        ticker_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        ticker_entry = tk.Entry(ticker_frame, font=("Segoe UI", 10), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=1)
        ticker_entry.pack(fill=tk.BOTH, expand=True)
        
        weight_frame = tk.Frame(top_row, bg=T.CARD_BG)
        weight_frame.pack(side=tk.LEFT, padx=2)
        weight_entry = tk.Entry(weight_frame, font=("Segoe UI", 10), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=1, width=10)
        weight_entry.pack(fill=tk.BOTH, expand=True)
        
        amount_frame = tk.Frame(top_row, bg=T.CARD_BG)
        amount_frame.pack(side=tk.LEFT, padx=2)
        amount_entry = tk.Entry(amount_frame, font=("Segoe UI", 10), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=1, width=10)
        amount_entry.pack(fill=tk.BOTH, expand=True)
        
        status_label = tk.Label(top_row, text="●", font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.BORDER, width=2)
        status_label.pack(side=tk.LEFT)
        
        name_label = tk.Label(row_container, text="", font=("Segoe UI", 8), bg=T.CARD_BG, 
                             fg=T.TEXT_SECONDARY, anchor="w", wraplength=400)
        name_label.pack(fill=tk.X, padx=(20, 0))
        
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
        """Create benchmark row"""
        row_container = tk.Frame(parent, bg=T.CARD_BG)
        row_container.pack(fill=tk.BOTH, expand=True, pady=1, padx=0)
        
        top_row = tk.Frame(row_container, bg=T.CARD_BG)
        top_row.pack(fill=tk.X)
        
        tk.Label(top_row, text=str(idx+1), font=("Segoe UI", 8), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, width=2).pack(side=tk.LEFT, padx=1)
        
        bench_entry = tk.Entry(top_row, font=("Segoe UI", 10), bg=T.INPUT_BG, fg=T.TEXT_PRIMARY, relief=tk.FLAT, bd=1)
        bench_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        browse_btn = tk.Button(top_row, text="📋", font=("Segoe UI", 9), bg=T.PRIMARY, fg=T.TEXT_ON_DARK,
                              relief=tk.FLAT, padx=8, pady=2, cursor="hand2",
                              command=lambda: self._open_benchmark_selector(idx))
        browse_btn.pack(side=tk.LEFT, padx=2)
        
        status_label = tk.Label(top_row, text="●", font=("Segoe UI", 10), bg=T.CARD_BG, fg=T.BORDER, width=2)
        status_label.pack(side=tk.LEFT)
        
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
        """Chart selection panel - MAXIMIZED with 3 columns"""
        section = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        section.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))
        
        # Header
        header = tk.Frame(section, bg=T.PANEL_HEADER, height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="📊 Select Analysis Charts", font=("Segoe UI", 12, "bold"), 
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
            cat_header = tk.Frame(scrollable_frame, bg=T.HIGHLIGHT, height=30)
            cat_header.pack(fill=tk.X, pady=(15, 0), padx=0)
            cat_header.pack_propagate(False)
            
            tk.Label(cat_header, text=category, font=("Segoe UI", 10, "bold"), 
                    bg=T.HIGHLIGHT, fg=T.TEXT_PRIMARY).pack(expand=True, pady=6)
            
            # Charts container (3 columns)
            charts_container = tk.Frame(scrollable_frame, bg=T.CARD_BG)
            charts_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=(4, 8))
            
            col1 = tk.Frame(charts_container, bg=T.CARD_BG)
            col1.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 1))
            
            col2 = tk.Frame(charts_container, bg=T.CARD_BG)
            col2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(1, 1))
            
            col3 = tk.Frame(charts_container, bg=T.CARD_BG)
            col3.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(1, 0))
            
            for i, chart_num in enumerate(charts):
                col_index = i % 3
                target_col = [col1, col2, col3][col_index]
                
                var = tk.BooleanVar(value=False)
                self.chart_vars[chart_num] = var
                
                item_frame = tk.Frame(target_col, bg=T.CARD_BG)
                item_frame.pack(fill=tk.BOTH, expand=True, pady=2, padx=0)
                
                cb = tk.Checkbutton(item_frame, variable=var, bg=T.CARD_BG, activebackground=T.CARD_BG, 
                                   relief=tk.FLAT, bd=0, highlightthickness=0)
                cb.pack(side=tk.LEFT, padx=(1, 4))
                
                chart_name = f"{chart_num}. {self.CHART_NAMES[chart_num]}"
                chart_desc = self.CHART_DESCRIPTIONS[chart_num]
                
                name_frame = tk.Frame(item_frame, bg=T.CARD_BG)
                name_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=0)
                
                tk.Label(name_frame, text=chart_name, font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_PRIMARY, 
                        anchor="w").pack(fill=tk.X, pady=(0, 1))
                tk.Label(name_frame, text=chart_desc, font=("Segoe UI", 7), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, 
                        anchor="w", wraplength=260).pack(fill=tk.X)
    
    def _create_run_button(self):
        """Large run analysis button"""
        btn_frame = tk.Frame(self.root, bg=T.MAIN_BG, height=60)
        btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(0, 5))
        btn_frame.pack_propagate(False)
        
        run_btn = tk.Button(
            btn_frame,
            text="▶ Run Portfolio Analysis",
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
        """Open benchmark selector (placeholder - reuse from v3)"""
        messagebox.showinfo("Benchmark Selector", "Feature coming soon - use v3 implementation")
    
    def _start_auto_refresh(self):
        """Start automatic market data refresh"""
        def auto_refresh_loop():
            self._refresh_market_data()
            self.root.after(5000, auto_refresh_loop)
        auto_refresh_loop()
    
    def _refresh_market_data(self):
        """Refresh market data in background"""
        def fetch():
            forex_rates = get_current_forex_rates()
            indexes_prices = get_major_indexes_prices()
            self.root.after(0, lambda: self._update_market_data(forex_rates, indexes_prices))
        threading.Thread(target=fetch, daemon=True).start()
    
    def _update_market_data(self, forex_rates, indexes_prices):
        """Update UI with market data (same logic as v3)"""
        try:
            # Update forex
            if forex_rates and forex_rates.get('success'):
                for currency in ["EUR", "GBP", "JPY", "CHF"]:
                    key = f"{currency}USD"
                    value = forex_rates.get(key, 0)
                    change_pct = forex_rates.get(f"{key}_change_pct", 0)
                    change_pts = forex_rates.get(f"{key}_change_pts", 0)
                    
                    if currency in self.forex_labels:
                        labels = self.forex_labels[currency]
                        if currency == "JPY":
                            labels['price'].config(text=f"{value:.2f}")
                        else:
                            labels['price'].config(text=f"{value:.4f}")
                        
                        if change_pct is not None and change_pct != 0:
                            if currency == "JPY":
                                change_text = f"{change_pts:+.2f} ({change_pct:+.2f}%)"
                            else:
                                change_text = f"{change_pts:+.4f} ({change_pct:+.2f}%)"
                            
                            if change_pct > 0:
                                labels['change'].config(text=change_text, bg="#d4edda", fg="#155724")
                                self.root.after(1000, lambda l=labels['change']: l.config(bg=T.CARD_BG, fg=T.TEXT_SECONDARY))
                            else:
                                labels['change'].config(text=change_text, bg="#f8d7da", fg="#721c24")
                                self.root.after(1000, lambda l=labels['change']: l.config(bg=T.CARD_BG, fg=T.TEXT_SECONDARY))
                        else:
                            labels['change'].config(text="0.00 (0.00%)", bg=T.CARD_BG, fg=T.TEXT_SECONDARY)
            
            # Update indexes, commodities, bonds
            if indexes_prices and indexes_prices.get('success'):
                for idx_data in indexes_prices.get('indexes', []):
                    symbol = idx_data.get('symbol')
                    price = idx_data.get('price', 0)
                    change_pct = idx_data.get('change_pct', 0)
                    change_pts = idx_data.get('change_pts', 0)
                    
                    if not idx_data.get('success'):
                        continue
                    
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
                        price_format = f"{price:.2f}%"
                        change_format = f"{change_pts:+.2f} ({change_pct:+.2f}%)"
                    
                    if labels:
                        labels['price'].config(text=price_format)
                        
                        if change_pct is not None and change_pct != 0:
                            if change_pct > 0:
                                labels['change'].config(text=change_format, bg="#d4edda", fg="#155724")
                                self.root.after(1000, lambda l=labels['change']: l.config(bg=T.CARD_BG, fg=T.TEXT_SECONDARY))
                            else:
                                labels['change'].config(text=change_format, bg="#f8d7da", fg="#721c24")
                                self.root.after(1000, lambda l=labels['change']: l.config(bg=T.CARD_BG, fg=T.TEXT_SECONDARY))
                        else:
                            labels['change'].config(text="0.0 (0.00%)", bg=T.CARD_BG, fg=T.TEXT_SECONDARY)
        except Exception as e:
            print(f"Error updating market data: {e}")
    
    def _select_all_charts(self):
        for var in self.chart_vars.values():
            var.set(True)
    
    def _select_no_charts(self):
        for var in self.chart_vars.values():
            var.set(False)
    
    def _run_analysis(self):
        """Run portfolio analysis"""
        selected = [num for num, var in self.chart_vars.items() if var.get()]
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one chart!")
            return
        
        self.root.update()
        
        # Collect validated tickers
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
        
        if not ticker_weights:
            messagebox.showwarning("No Tickers", "Please add at least one validated ticker!")
            return
        
        # Get capital and currency
        try:
            capital = float(self.capital_var.get())
        except (ValueError, AttributeError):
            capital = None
        
        currency = self.currency_var.get() if hasattr(self, 'currency_var') else "USD"
        
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
        
        self.root.title("Portfolio Architect - Two-Page Edition")
        
        if result["success"]:
            messagebox.showinfo(
                "Complete", 
                f"{result['message']}\n\nSaved to: {result['output_dir']}"
            )
        else:
            messagebox.showerror("Error", result["message"])
    
    def _init_symbol_handler(self):
        """Initialize symbol handler"""
        self.symbol_handler = SymbolUIHandler(
            self.root, self.ticker_rows, self.benchmark_rows,
            self.local_ticker_hints, self.local_bench_hints,
            on_validation_complete=self._on_symbol_validated
        )
        self._rebind_symbol_callbacks()
    
    def _rebind_symbol_callbacks(self):
        """Rebind entry widgets to symbol handler"""
        for i, row in enumerate(self.ticker_rows):
            entry = row["entry"]
            placeholder = row["placeholder"]
            
            for event in ["<FocusIn>", "<FocusOut>", "<Return>"]:
                try:
                    entry.unbind(event)
                except:
                    pass
            
            def make_focus_in_handler(ent, ph):
                return lambda e: self.symbol_handler.on_focus_in(ent, ph)
            
            def make_validate_handler(kind, index):
                return lambda e: self.symbol_handler.queue_validate(kind, index)
            
            entry.bind("<FocusIn>", make_focus_in_handler(entry, placeholder))
            entry.bind("<FocusOut>", make_validate_handler("ticker", i))
            entry.bind("<Return>", make_validate_handler("ticker", i))
        
        for i, row in enumerate(self.benchmark_rows):
            entry = row["entry"]
            placeholder = row["placeholder"]
            
            for event in ["<FocusIn>", "<FocusOut>", "<Return>"]:
                try:
                    entry.unbind(event)
                except:
                    pass
            
            def make_focus_in_bench_handler(ent, ph, index):
                return lambda e: self.symbol_handler.on_focus_in(ent, ph, kind="bench", idx=index)
            
            def make_validate_bench_handler(kind, index):
                return lambda e: self.symbol_handler.queue_validate(kind, index)
            
            entry.bind("<FocusIn>", make_focus_in_bench_handler(entry, placeholder, i))
            entry.bind("<FocusOut>", make_validate_bench_handler("bench", i))
            entry.bind("<Return>", make_validate_bench_handler("bench", i))
    
    def _on_symbol_validated(self, kind):
        """Callback when symbol validation completes"""
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
            
            row["amount_entry"].delete(0, tk.END)
            row["amount_entry"].insert(0, f"{amount:.2f}")
            
            self._update_weight_total()
        except (ValueError, KeyError, IndexError):
            self._update_weight_total()
    
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
                
                row["weight_entry"].delete(0, tk.END)
                row["weight_entry"].insert(0, f"{weight:.2f}")
                
                self._update_weight_total()
        except (ValueError, KeyError, IndexError, ZeroDivisionError):
            self._update_weight_total()
    
    def _on_closing(self):
        """Handle window close"""
        self.root.destroy()
    
    def _equal_weights(self):
        """Distribute weights equally"""
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
        
        equal_weight = 100.0 / len(filled_rows)
        
        for idx in filled_rows:
            row = self.ticker_rows[idx]
            weight_entry = row.get("weight_entry")
            if weight_entry:
                weight_entry.delete(0, tk.END)
                weight_entry.insert(0, f"{equal_weight:.2f}")
                self._on_weight_change(idx)
        
        self._update_weight_total()
        
        messagebox.showinfo("Equal Weights", 
                          f"Set equal weights of {equal_weight:.2f}% for {len(filled_rows)} positions.")
    
    def _auto_100_percent(self):
        """Auto-scale weights to reach 100%"""
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
            messagebox.showinfo("Auto 100%", "Please enter weights first.")
            return
        
        total = sum(w for _, w in current_weights)
        
        if total == 0:
            messagebox.showwarning("Auto 100%", "Total weight is 0%. Please enter valid weights.")
            return
        
        if abs(total - 100.0) < 0.01:
            messagebox.showinfo("Auto 100%", f"Weights already sum to 100.0%!")
            return
        
        scale_factor = 100.0 / total
        
        for idx, old_weight in current_weights:
            new_weight = old_weight * scale_factor
            row = self.ticker_rows[idx]
            weight_entry = row.get("weight_entry")
            if weight_entry:
                weight_entry.delete(0, tk.END)
                weight_entry.insert(0, f"{new_weight:.2f}")
                self._on_weight_change(idx)
        
        self._update_weight_total()
        
        messagebox.showinfo("Auto 100%", 
                          f"Scaled {len(current_weights)} positions from {total:.2f}% to 100.0%!")
    
    def _clear_weights(self):
        """Clear all weights and amounts"""
        result = messagebox.askyesno("Clear Weights", 
                                     "This will reset all weights and amounts to 0.\n\nContinue?")
        if not result:
            return
        
        for row in self.ticker_rows:
            weight_entry = row.get("weight_entry")
            amount_entry = row.get("amount_entry")
            
            if weight_entry:
                weight_entry.delete(0, tk.END)
            if amount_entry:
                amount_entry.delete(0, tk.END)
        
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
        
        if abs(total - 100.0) < 0.01:
            self.weight_total_label.config(text=f"Total: {total:.2f}%", fg="#155724")
        elif total > 100.0:
            self.weight_total_label.config(text=f"Total: {total:.2f}% (over)", fg="#721c24")
        elif total > 0:
            self.weight_total_label.config(text=f"Total: {total:.2f}%", fg="#856404")
        else:
            self.weight_total_label.config(text=f"Total: {total:.2f}%", fg=T.TEXT_PRIMARY)


def main():
    """Launch Two-Page Portfolio Architect"""
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(2)
    except:
        try:
            from ctypes import windll
            windll.user32.SetProcessDPIAware()
        except:
            pass
    
    root = tk.Tk()
    
    try:
        root.tk.call('tk', 'scaling', 2.0)
    except:
        pass
    
    app = TwoPagePortfolioArchitect(root)
    root.mainloop()


if __name__ == "__main__":
    main()



