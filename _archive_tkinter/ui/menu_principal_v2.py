# menu_principal_v2.py - Portfolio Analysis Control Panel (Split-View Improved)
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


class ChartControlPanel:
    """
    Portfolio Analysis Control Panel with Split-View
    
    Left Panel (55%): Portfolio Configuration
    - Capital & Currency
    - Ticker entries (10 rows)
    - Benchmark entries (5 rows)
    - Market data (Forex & Indexes)
    
    Right Panel (45%): Chart Selection
    - Organized by categories
    - Visual icons and descriptions
    - Quick actions (Select All/None)
    """
    
    # Chart groups organized like the original menu
    CHART_GROUPS = {
        "Portfolio & Sector (1-6)": list(range(1, 7)),
        "Monte Carlo (7-12)": list(range(7, 13)),
        "Risk Metrics (13-17)": list(range(13, 18)),
        "Benchmarks (18-21)": list(range(18, 22)),
        "Sector & Regime (22-24)": list(range(22, 25)),
    }
    
    CHART_NAMES = {
        1: "Portfolio Allocation", 2: "Correlation Matrix", 3: "Risk Contribution",
        4: "Performance vs Benchmarks", 5: "Sector Decomposition", 6: "Sector Risk Contribution",
        7: "MC Paths (Normal)", 8: "MC Paths (Randomness)", 9: "Volatility (Normal)",
        10: "Volatility (Randomness)", 11: "Max Drawdown (Normal)", 12: "Max Drawdown (Randomness)",
        13: "VaR 95%", 14: "Expected Shortfall", 15: "Max DD Duration", 16: "Calmar Ratio",
        17: "Sharpe Ratio", 18: "Risk vs Indexes", 19: "Forward Excess", 
        20: "Portfolio vs Benchmarks (Normal)", 21: "Portfolio vs Benchmarks (Random)", 
        22: "Sector Performance", 23: "Regime Analysis", 24: "Sector Rotation"
    }
    
    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Architect")
        self.root.geometry("1600x900")
        self.root.configure(bg=T.MAIN_BG)
        
        # Bind window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # State
        self.ticker_rows = []
        self.benchmark_rows = []
        self.chart_vars = {}
        
        # Initialize managers
        self.currency_manager = CurrencyManager(default_currency="USD")
        self.portfolio_manager = None
        self.market_data_manager = None
        self.symbol_handler = None
        self.analysis_runner = AnalysisRunner()
        
        # Local hints for autocomplete fallback
        self.local_ticker_hints = [
            "NVDA", "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "PLTR",
            "SPY", "QQQ", "VOO", "VTI", "GLD", "SLV", "IWDA.AS", "CSPX.L"
        ]
        self.local_bench_hints = [
            "^GSPC", "^NDX", "^DJI", "^GDAXI", "^FCHI", "^STOXX50E"
        ]
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup split-view UI"""
        
        # Top toolbar
        self._create_toolbar()
        
        # Main container with split
        main_container = tk.Frame(self.root, bg=T.MAIN_BG)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # LEFT PANEL (55%) - Portfolio Configuration
        left_panel = tk.Frame(main_container, bg=T.MAIN_BG)
        left_panel.place(relx=0, rely=0, relwidth=0.55, relheight=1)
        
        # RIGHT PANEL (45%) - Chart Selection
        right_panel = tk.Frame(main_container, bg=T.CARD_BG, relief=tk.RIDGE, bd=1)
        right_panel.place(relx=0.55, rely=0, relwidth=0.45, relheight=1)
        
        # Populate panels
        self._create_left_panel(left_panel)
        self._create_right_panel(right_panel)
        
        # Bottom toolbar
        self._create_bottom_toolbar()
        
        # Initialize data
        self.root.after(100, self._initialize_data)
    
    def _create_toolbar(self):
        """Create top toolbar"""
        toolbar = tk.Frame(self.root, bg=T.HEADER, height=60)
        toolbar.pack(fill=tk.X)
        toolbar.pack_propagate(False)
        
        # Title
        title_frame = tk.Frame(toolbar, bg=T.HEADER)
        title_frame.pack(side=tk.LEFT, padx=20, pady=10)
        
        tk.Label(
            title_frame,
            text="Portfolio Architect",
            font=("Segoe UI", 16, "bold"),
            bg=T.HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(anchor="w")
        
        tk.Label(
            title_frame,
            text="Configure your portfolio and select analysis charts",
            font=("Segoe UI", 9),
            bg=T.HEADER,
            fg=T.TEXT_SECONDARY
        ).pack(anchor="w")
        
        # Capital & Currency
        capital_frame = tk.Frame(toolbar, bg=T.HEADER)
        capital_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            capital_frame,
            text="Capital:",
            font=("Segoe UI", 10),
            bg=T.HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.capital_var = tk.StringVar(value="10000")
        self.capital_entry = tk.Entry(
            capital_frame,
            textvariable=self.capital_var,
            width=12,
            font=("Segoe UI", 10),
            bg=T.INPUT_BG,
            relief=tk.FLAT,
            bd=2
        )
        self.capital_entry.pack(side=tk.LEFT, padx=(0, 10))
        
        self.currency_var = tk.StringVar(value="USD")
        currency_menu = ttk.Combobox(
            capital_frame,
            textvariable=self.currency_var,
            values=["USD", "EUR", "GBP", "JPY", "CHF"],
            width=8,
            state="readonly",
            font=("Segoe UI", 10)
        )
        currency_menu.pack(side=tk.LEFT)
        
        # Status
        self.status_label = tk.Label(
            capital_frame,
            text="● Ready",
            font=("Segoe UI", 10, "bold"),
            bg=T.HEADER,
            fg="#4CAF50"
        )
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))
    
    def _create_left_panel(self, parent):
        """Create left panel with portfolio configuration"""
        
        # Market Data section (at the top, not scrollable)
        self._create_market_data_section(parent)
        
        # Scrollable container for the rest
        canvas = tk.Canvas(parent, bg=T.MAIN_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=T.MAIN_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Portfolio section
        self._create_portfolio_section(scrollable_frame)
        
        # Benchmarks section
        self._create_benchmarks_section(scrollable_frame)
    
    def _create_portfolio_section(self, parent):
        """Create portfolio positions section"""
        section = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        section.pack(fill=tk.X, pady=(0, 10), padx=0)
        
        # Header
        header = tk.Frame(section, bg=T.PANEL_HEADER, height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Portfolio Positions",
            font=("Segoe UI", 12, "bold"),
            bg=T.PANEL_HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(side=tk.LEFT, padx=5, pady=10)
        
        # Actions
        action_frame = tk.Frame(header, bg=T.PANEL_HEADER)
        action_frame.pack(side=tk.RIGHT, padx=5)
        
        for text in ["Equal", "Normalize", "Clear"]:
            btn = tk.Button(
                action_frame,
                text=text,
                font=("Segoe UI", 9),
                bg=T.SECONDARY_BG,
                fg=T.TEXT_PRIMARY,
                relief=tk.FLAT,
                padx=10,
                pady=3,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # Content - Same padding as Market Data
        content = tk.Frame(section, bg=T.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Table header
        header_frame = tk.Frame(content, bg=T.CARD_BG)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(header_frame, text="#", font=("Segoe UI", 8, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, width=2).pack(side=tk.LEFT, padx=1)
        tk.Label(header_frame, text="Ticker/ISIN", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Label(header_frame, text="Weight %", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Label(header_frame, text="Amount", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, fg=T.TEXT_SECONDARY, anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Label(header_frame, text="", font=("Segoe UI", 9, "bold"), bg=T.CARD_BG, width=2).pack(side=tk.LEFT, padx=0)
        
        # Rows
        for i in range(15):
            self._create_portfolio_row(content, i)
        
        # Summary
        summary = tk.Frame(section, bg=T.HIGHLIGHT, height=40)
        summary.pack(fill=tk.X)
        summary.pack_propagate(False)
        
        self.weight_total_label = tk.Label(
            summary,
            text="Total: 0%",
            font=("Segoe UI", 10, "bold"),
            bg=T.HIGHLIGHT,
            fg=T.TEXT_PRIMARY
        )
        self.weight_total_label.pack(side=tk.LEFT, padx=5)
    
    def _create_portfolio_row(self, parent, idx):
        """Create portfolio row - full width"""
        row_frame = tk.Frame(parent, bg=T.CARD_BG)
        row_frame.pack(fill=tk.BOTH, expand=True, pady=1, padx=0)
        
        # Row number (fixed width)
        tk.Label(
            row_frame,
            text=f"{idx+1}.",
            font=("Segoe UI", 9),
            bg=T.CARD_BG,
            fg=T.TEXT_MUTED,
            width=2
        ).pack(side=tk.LEFT, padx=(0, 1))
        
        # Ticker (50% of remaining space)
        ticker_frame = tk.Frame(row_frame, bg=T.CARD_BG)
        ticker_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1)
        
        ticker_entry = tk.Entry(
            ticker_frame,
            font=("Segoe UI", 10),
            bg=T.INPUT_BG,
            fg=T.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=1
        )
        ticker_entry.pack(fill=tk.BOTH, expand=True)
        
        # Weight (expand to take more space)
        weight_frame = tk.Frame(row_frame, bg=T.CARD_BG)
        weight_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1)
        
        weight_entry = tk.Entry(
            weight_frame,
            font=("Segoe UI", 10),
            bg=T.INPUT_BG,
            fg=T.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=1
        )
        weight_entry.pack(fill=tk.BOTH, expand=True)
        
        # Amount (expand to take more space)
        amount_frame = tk.Frame(row_frame, bg=T.CARD_BG)
        amount_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1)
        
        amount_entry = tk.Entry(
            amount_frame,
            font=("Segoe UI", 10),
            bg=T.INPUT_BG,
            fg=T.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=1
        )
        amount_entry.pack(fill=tk.BOTH, expand=True)
        
        # Status (fixed width)
        status_label = tk.Label(
            row_frame,
            text="•",
            font=("Segoe UI", 12),
            bg=T.CARD_BG,
            fg=T.TEXT_MUTED,
            width=2
        )
        status_label.pack(side=tk.LEFT, padx=(1, 0))
        
        self.ticker_rows.append({
            "entry": ticker_entry,
            "weight_entry": weight_entry,
            "amount_entry": amount_entry,
            "status": status_label,
            "placeholder": f"Ticker {idx+1}"
        })
    
    def _create_benchmarks_section(self, parent):
        """Create benchmarks section"""
        section = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        section.pack(fill=tk.X, pady=(0, 10), padx=0)
        
        # Header
        header = tk.Frame(section, bg=T.PANEL_HEADER, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📈 Benchmark Indexes",
            font=("Segoe UI", 11, "bold"),
            bg=T.PANEL_HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(side=tk.LEFT, padx=5, pady=8)
        
        # Content - Same padding as Market Data
        content = tk.Frame(section, bg=T.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        for i in range(10):
            self._create_benchmark_row(content, i)
    
    def _create_benchmark_row(self, parent, idx):
        """Create benchmark row - full width"""
        row_frame = tk.Frame(parent, bg=T.CARD_BG)
        row_frame.pack(fill=tk.BOTH, expand=True, pady=1, padx=0)
        
        # Row number (fixed width)
        tk.Label(
            row_frame,
            text=f"{idx+1}.",
            font=("Segoe UI", 9),
            bg=T.CARD_BG,
            fg=T.TEXT_MUTED,
            width=2
        ).pack(side=tk.LEFT, padx=(0, 1))
        
        # Benchmark entry (takes ALL remaining space)
        bench_entry = tk.Entry(
            row_frame,
            font=("Segoe UI", 10),
            bg=T.INPUT_BG,
            fg=T.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=1
        )
        bench_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=1)
        
        # Status (fixed width)
        status_label = tk.Label(
            row_frame,
            text="•",
            font=("Segoe UI", 12),
            bg=T.CARD_BG,
            fg=T.TEXT_MUTED,
            width=2
        )
        status_label.pack(side=tk.LEFT, padx=(1, 0))
        
        self.benchmark_rows.append({
            "entry": bench_entry,
            "status": status_label,
            "placeholder": f"Benchmark {idx+1}"
        })
    
    def _create_market_data_section(self, parent):
        """Create market data section with forex rates and major indexes"""
        section = tk.Frame(parent, bg=T.CARD_BG, relief=tk.FLAT, bd=0)
        section.pack(fill=tk.X, pady=(0, 10), padx=0)
        
        # Header
        header = tk.Frame(section, bg=T.PANEL_HEADER, height=40)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="💱 Market Data - Real-time Prices",
            font=("Segoe UI", 11, "bold"),
            bg=T.PANEL_HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(side=tk.LEFT, padx=5, pady=8)
        
        # Refresh button
        self.market_refresh_btn = tk.Button(
            header,
            text="Refresh",
            font=("Segoe UI", 9),
            bg=T.PRIMARY,
            fg=T.TEXT_ON_DARK,
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._refresh_market_data
        )
        self.market_refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # Content - Split in two columns  
        content = tk.Frame(section, bg=T.CARD_BG)
        content.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Left column: Forex Rates
        forex_frame = tk.Frame(content, bg=T.CARD_BG)
        forex_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            forex_frame,
            text="Forex Rates (vs USD)",
            font=("Segoe UI", 9, "bold"),
            bg=T.CARD_BG,
            fg=T.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))
        
        self.forex_labels = {}
        for currency in ["EUR", "GBP"]:
            row = tk.Frame(forex_frame, bg=T.CARD_BG)
            row.pack(fill=tk.X, pady=1)
            
            tk.Label(
                row,
                text=f"{currency}/USD:",
                font=("Segoe UI", 9),
                bg=T.CARD_BG,
                fg=T.TEXT_SECONDARY,
                width=10,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            value_label = tk.Label(
                row,
                text="Loading...",
                font=("Segoe UI", 9),
                bg=T.CARD_BG,
                fg=T.TEXT_PRIMARY,
                anchor="e"
            )
            value_label.pack(side=tk.RIGHT)
            self.forex_labels[currency] = value_label
        
        # Right column: Major Indexes
        indexes_frame = tk.Frame(content, bg=T.CARD_BG)
        indexes_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            indexes_frame,
            text="Major Indexes",
            font=("Segoe UI", 9, "bold"),
            bg=T.CARD_BG,
            fg=T.TEXT_PRIMARY,
            anchor="w"
        ).pack(fill=tk.X, pady=(0, 5))
        
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
            
            tk.Label(
                row,
                text=f"{name}:",
                font=("Segoe UI", 9),
                bg=T.CARD_BG,
                fg=T.TEXT_SECONDARY,
                width=12,
                anchor="w"
            ).pack(side=tk.LEFT)
            
            value_label = tk.Label(
                row,
                text="Loading...",
                font=("Segoe UI", 9),
                bg=T.CARD_BG,
                fg=T.TEXT_PRIMARY,
                anchor="e"
            )
            value_label.pack(side=tk.RIGHT)
            self.index_labels[symbol] = value_label
    
    def _create_right_panel(self, parent):
        """Create right panel with chart selection"""
        
        # Header
        header = tk.Frame(parent, bg=T.PANEL_HEADER, height=45)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="📊 Analysis Charts Selection",
            font=("Segoe UI", 12, "bold"),
            bg=T.PANEL_HEADER,
            fg=T.TEXT_ON_DARK
        ).pack(side=tk.LEFT, padx=15, pady=10)
        
        # Quick actions
        actions_frame = tk.Frame(header, bg=T.PANEL_HEADER)
        actions_frame.pack(side=tk.RIGHT, padx=10)
        
        tk.Button(
            actions_frame,
            text="All",
            font=("Segoe UI", 9),
            bg=T.SECONDARY_BG,
            fg=T.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._select_all_charts
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            actions_frame,
            text="None",
            font=("Segoe UI", 9),
            bg=T.SECONDARY_BG,
            fg=T.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=10,
            pady=3,
            cursor="hand2",
            command=self._deselect_all_charts
        ).pack(side=tk.LEFT, padx=2)
        
        # Scrollable content
        canvas = tk.Canvas(parent, bg=T.CARD_BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=T.CARD_BG)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=0, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Create categories with charts in 2 columns
        for category_name, chart_ids in self.CHART_GROUPS.items():
            self._create_chart_category(scrollable_frame, category_name, chart_ids)
    
    def _create_chart_category(self, parent, category_name, chart_ids):
        """Create a chart category with charts in 2 columns"""
        # Category header
        category_header = tk.Frame(parent, bg=T.SECONDARY_BG, height=25)
        category_header.pack(fill=tk.X, pady=(5, 2), padx=0)
        category_header.pack_propagate(False)
        
        tk.Label(
            category_header,
            text=category_name,
            font=("Segoe UI", 9, "bold"),
            bg=T.SECONDARY_BG,
            fg=T.TEXT_PRIMARY,
            anchor="w"
        ).pack(side=tk.LEFT, padx=1, fill=tk.BOTH, expand=True)
        
        # Container for 2 columns
        charts_container = tk.Frame(parent, bg=T.CARD_BG)
        charts_container.pack(fill=tk.X, padx=0, pady=0)
        
        # Split charts into 2 columns
        mid = (len(chart_ids) + 1) // 2  # Split in half (round up)
        
        # Left column - MAXIMUM width
        left_col = tk.Frame(charts_container, bg=T.CARD_BG)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(1, 1))
        
        for chart_id in chart_ids[:mid]:
            self._create_chart_item(left_col, chart_id)
        
        # Right column - MAXIMUM width  
        right_col = tk.Frame(charts_container, bg=T.CARD_BG)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(1, 1))
        
        for chart_id in chart_ids[mid:]:
            self._create_chart_item(right_col, chart_id)
    
    def _create_chart_item(self, parent, chart_id):
        """Create a single chart checkbox - full width"""
        item_frame = tk.Frame(parent, bg=T.CARD_BG)
        item_frame.pack(fill=tk.BOTH, expand=True, pady=1, padx=0)
        
        # Initialize variable
        if chart_id not in self.chart_vars:
            self.chart_vars[chart_id] = tk.BooleanVar(value=True)
        
        # Checkbox (fixed width on left)
        cb = tk.Checkbutton(
            item_frame,
            variable=self.chart_vars[chart_id],
            bg=T.CARD_BG,
            activebackground=T.CARD_BG,
            font=("Segoe UI", 9)
        )
        cb.pack(side=tk.LEFT, padx=(1, 0))
        
        # Chart number and name (takes ALL remaining space to the edge)
        chart_text = f"{chart_id}. {self.CHART_NAMES[chart_id]}"
        tk.Label(
            item_frame,
            text=chart_text,
            font=("Segoe UI", 9),
            bg=T.CARD_BG,
            fg=T.TEXT_PRIMARY,
            anchor="w"
        ).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(1, 0))
    
    def _create_bottom_toolbar(self):
        """Create bottom toolbar"""
        toolbar = tk.Frame(self.root, bg=T.MAIN_BG, height=70)
        toolbar.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        toolbar.pack_propagate(False)
        
        # Separator
        tk.Frame(toolbar, bg=T.BORDER, height=1).pack(fill=tk.X)
        
        # Buttons container
        btn_frame = tk.Frame(toolbar, bg=T.MAIN_BG)
        btn_frame.pack(expand=True)
        
        # Run analysis button
        tk.Button(
            btn_frame,
            text="📊 Run Portfolio Analysis",
            font=("Segoe UI", 12, "bold"),
            bg=T.PRIMARY,
            fg=T.TEXT_ON_DARK,
            relief=tk.FLAT,
            padx=40,
            pady=12,
            cursor="hand2",
            command=self.run_analysis
        ).pack()
    
    def _select_all_charts(self):
        """Select all charts"""
        for var in self.chart_vars.values():
            var.set(True)
    
    def _deselect_all_charts(self):
        """Deselect all charts"""
        for var in self.chart_vars.values():
            var.set(False)
    
    def _initialize_data(self):
        """Initialize data and managers"""
        # Load market data
        self._refresh_market_data()
    
    def _refresh_market_data(self):
        """Refresh forex rates and major indexes"""
        self.market_refresh_btn.config(text="Loading...", state=tk.DISABLED, bg=T.TEXT_SECONDARY)
        
        def fetch_data():
            try:
                print("Fetching market data...")
                # Fetch forex rates
                forex_rates = get_current_forex_rates()
                print(f"Forex rates: {forex_rates}")
                
                # Fetch major indexes
                indexes_prices = get_major_indexes_prices()
                print(f"Indexes prices: {indexes_prices}")
                
                # Update UI
                self.root.after(0, lambda: self._update_market_data(forex_rates, indexes_prices))
            except Exception as e:
                print(f"ERROR fetching market data: {e}")
                import traceback
                traceback.print_exc()
                self.root.after(0, lambda: self.market_refresh_btn.config(text="Error", state=tk.NORMAL, bg=T.ERROR))
        
        import threading
        thread = threading.Thread(target=fetch_data, daemon=True)
        thread.start()
    
    def _update_market_data(self, forex_rates, indexes_prices):
        """Update market data in UI"""
        print("Updating UI with market data...")
        
        # Update forex rates
        if isinstance(forex_rates, dict):
            # Handle forex data
            for key, value in forex_rates.items():
                if key == 'EURUSD' and 'EUR' in self.forex_labels:
                    self.forex_labels['EUR'].config(text=f"{value:.4f}", fg=T.TEXT_PRIMARY)
                    print(f"Updated EUR: {value:.4f}")
                elif key == 'GBPUSD' and 'GBP' in self.forex_labels:
                    self.forex_labels['GBP'].config(text=f"{value:.4f}", fg=T.TEXT_PRIMARY)
                    print(f"Updated GBP: {value:.4f}")
        
        # Update indexes - handle the 'indexes' list format
        if isinstance(indexes_prices, dict) and 'indexes' in indexes_prices:
            for index_data in indexes_prices['indexes']:
                symbol = index_data.get('symbol')
                if symbol in self.index_labels:
                    price = index_data.get('price')
                    if price and price > 0:
                        change = index_data.get('change', 0)
                        color = "#4CAF50" if change >= 0 else "#f44336"
                        self.index_labels[symbol].config(
                            text=f"{price:,.0f}",
                            fg=color
                        )
                        print(f"Updated {symbol}: {price:,.0f}")
                    else:
                        self.index_labels[symbol].config(text="N/A", fg=T.ERROR)
        
        # Re-enable button
        self.market_refresh_btn.config(text="Refresh", state=tk.NORMAL, bg=T.PRIMARY)
        print("Market data update complete")
    
    def run_analysis(self):
        """Run portfolio analysis"""
        messagebox.showinfo("Analysis", "Analysis will run here")
    
    def _on_closing(self):
        """Handle window closing"""
        if self.market_data_manager:
            self.market_data_manager.cleanup()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = ChartControlPanel(root)
    root.mainloop()


if __name__ == "__main__":
    main()

