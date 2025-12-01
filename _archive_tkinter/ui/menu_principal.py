# menu_principal.py - Portfolio Analysis Control Panel (Orchestrator)
import tkinter as tk
from tkinter import messagebox

# Import configuration
from core.config import WEIGHTS_RAW, BENCH_DEF

# Import modules
from ui.ui_builder import UIBuilder
from managers.symbol_handler import SymbolValidator, SymbolUIHandler
from core.analysis_runner import AnalysisRunner
from ui.theme_colors import LightPremiumTheme as T

# Import new specialized modules
from managers.currency_manager import CurrencyManager
from managers.portfolio_manager import PortfolioManager
from managers.market_data_manager import MarketDataManager


class ChartControlPanel:
    """
    Main orchestrator for the Portfolio Analysis application
    
    Responsibilities:
    - Initialize all modules (UI, symbol handler, analysis runner)
    - Coordinate user interactions
    - Delegate heavy lifting to specialized modules
    
    Delegation Strategy:
    - CurrencyManager: Handles currency symbols and formatting
    - PortfolioManager: Manages weights, amounts, calculations
    - MarketDataManager: Fetches and updates market data
    - UIBuilder: Creates all UI components
    - SymbolHandler: Validates tickers and benchmarks
    - AnalysisRunner: Executes portfolio analysis
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Portfolio Architect")
        self.root.geometry("1200x900")
        self.root.configure(bg=T.MAIN_BG)
        
        # Bind window close event to cleanup
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Chart selection variables
        self.chart_vars = {}
        
        # Chart groups for UI organization
        self.chart_groups = {
            "Portfolio & Sector (1-6)": list(range(1, 7)),
            "Monte Carlo (7-12)": list(range(7, 13)),
            "Risk Metrics (13-17)": list(range(13, 18)),
            "Benchmarks (18-21)": list(range(18, 22)),
            "Sector & Regime (22-24)": list(range(22, 25)),
        }
        
        # Chart names for display
        self.chart_names = {
            1: "Portfolio Allocation", 2: "Correlation Matrix", 3: "Risk Contribution",
            4: "Performance vs Benchmarks", 5: "Sector Decomposition", 6: "Sector Risk Contribution",
            7: "MC Paths (Normal)", 8: "MC Paths (Randomness)", 9: "Volatility (Normal)",
            10: "Volatility (Randomness)", 11: "Max Drawdown (Normal)", 12: "Max Drawdown (Randomness)",
            13: "VaR 95%", 14: "Expected Shortfall", 15: "Max DD Duration", 16: "Calmar Ratio",
            17: "Sharpe Ratio", 18: "Risk vs Indexes", 19: "Forward Excess", 
            20: "Portfolio vs Benchmarks (Normal)", 21: "Portfolio vs Benchmarks (Random)", 
            22: "Sector Performance", 23: "Regime Analysis", 24: "Sector Rotation"
        }
        
        # UI state
        self.ticker_rows = []
        self.benchmark_rows = []
        self.weight_total_label = None
        self.weight_normalize_btn = None
        self.status_label = None
        
        # Left panel widgets (for dynamic updates)
        self.portfolio_text = None
        self.benchmark_text = None
        
        # Portfolio settings
        self.capital_var = None
        self.currency_var = None
        self.capital_display = None
        
        # Local hints for autocomplete fallback
        self.local_ticker_hints = [
            "NVDA", "AAPL", "MSFT", "GOOG", "AMZN", "TSLA", "META", "PLTR",
            "SPY", "QQQ", "VOO", "VTI", "GLD", "SLV", "IWDA.AS", "CSPX.L", "VUSA.L", "CW8.PA"
        ]
        self.local_bench_hints = [
            "^GSPC", "^NDX", "^DJI", "^GDAXI", "^FCHI", "^STOXX50E", "^IBEX", "^N225", "FTSEMIB.MI", "GC=F"
        ]
        
        # Initialize modules (will be set after UI creation)
        self.symbol_handler = None
        self.analysis_runner = AnalysisRunner()
        self.currency_manager = CurrencyManager(default_currency="USD")
        self.portfolio_manager = None  # Created after ticker_rows exist
        self.market_data_manager = None  # Created after UI panels exist
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Setup complete UI by delegating to UIBuilder"""
        # Create main layout
        main_canvas, main_scrollbar, content_wrapper = UIBuilder.create_main_layout(self.root)
        
        # Create title
        UIBuilder.create_title(content_wrapper)
        
        # Create content frame
        content_frame = tk.Frame(content_wrapper, bg=T.MAIN_BG)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create left panel (portfolio summary and benchmarks)
        left_panel, self.portfolio_text, self.benchmark_text = UIBuilder.create_left_panel(content_frame, WEIGHTS_RAW, BENCH_DEF)
        
        # Create right panel
        right_panel = tk.Frame(content_frame, bg=T.MAIN_BG)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create capital and currency panel (at the top)
        capital_panel, self.capital_var, self.currency_var, self.capital_display, self.update_capital_display = \
            UIBuilder.create_capital_currency_panel(right_panel, default_capital=10000, default_currency="USD")
        
        # Create container for forex and indexes panels (side by side)
        market_info_container = tk.Frame(right_panel, bg=T.MAIN_BG)
        market_info_container.pack(fill=tk.BOTH, expand=False, pady=(0, 10))
        
        # Left column: Forex rates panel (smaller)
        forex_column = tk.Frame(market_info_container, bg=T.MAIN_BG)
        forex_column.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        forex_panel = UIBuilder.create_forex_rates_panel(forex_column)
        forex_update_callback = forex_panel['update_callback']
        forex_refresh_btn = forex_panel['refresh_btn']
        
        # Right column: Major indexes panel (larger)
        indexes_column = tk.Frame(market_info_container, bg=T.MAIN_BG)
        indexes_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        indexes_panel = UIBuilder.create_major_indexes_panel(indexes_column)
        indexes_update_callback = indexes_panel['update_callback']
        indexes_refresh_btn = indexes_panel['refresh_btn']
        
        # Initialize MarketDataManager
        self.market_data_manager = MarketDataManager(
            self.root,
            forex_update_callback,
            indexes_update_callback,
            forex_refresh_btn,
            indexes_refresh_btn,
            auto_refresh_interval=300000  # 5 minutes
        )
        
        # Bind refresh buttons to manager methods
        forex_refresh_btn.config(command=self.market_data_manager.refresh_forex)
        indexes_refresh_btn.config(command=self.market_data_manager.refresh_indexes)
        
        # Add trace to currency var to update currency symbols when changed
        self.currency_var.trace_add("write", lambda *args: self._on_currency_change())
        
        # Add trace to capital var to recalculate amounts when capital changes
        self.capital_var.trace_add("write", lambda *args: self._on_capital_change())
        
        # Top cards container
        cards_container = tk.Frame(right_panel, bg=T.MAIN_BG)
        cards_container.pack(fill=tk.X, pady=(0, 10))
        
        # Temporary callbacks (will be replaced after symbol_handler initialization)
        temp_callbacks = {
            'on_focus_in': lambda e, p: None,
            'queue_validate': lambda k, i: None,
            'browse_benchmarks': lambda i: None,
            'on_weight_change': self._on_weight_change,
            'on_amount_change': self._on_amount_change,
            'update_weight_total': self._update_weight_total,
            'normalize_weights': self._normalize_weights,
            'equal_weights': self._equal_weights,
            'clear_weights': self._clear_weights,
            'clear_portfolio': self._clear_portfolio
        }
        
        # Create ticker and benchmark cards
        tickers_card, self.ticker_rows, self.weight_total_label, self.weight_normalize_btn = \
            UIBuilder.create_ticker_card(cards_container, temp_callbacks)
        bench_card, self.benchmark_rows = UIBuilder.create_benchmark_card(cards_container, temp_callbacks)
        
        # Initialize PortfolioManager now that ticker_rows exist
        self.portfolio_manager = PortfolioManager(
            self.ticker_rows,
            self.get_capital_amount,
            self.get_currency_symbol
        )
        
        # Initialize symbol handler now that we have the rows
        self.symbol_handler = SymbolUIHandler(
            self.root, self.ticker_rows, self.benchmark_rows,
            self.local_ticker_hints, self.local_bench_hints,
            on_validation_complete=self._on_symbol_validated
        )
        
        # Rebind all symbol-related callbacks
        self._rebind_symbol_callbacks()
        
        # Create info panel
        info_frame = UIBuilder.create_info_panel(right_panel)
        
        # Create chart selector
        selection_frame, self.chart_vars = UIBuilder.create_chart_selector(
            right_panel, self.chart_groups, self.chart_names
        )
        
        # Create status panel
        control_panel, self.status_label = UIBuilder.create_status_panel(right_panel)
        
        # Create bottom toolbar
        toolbar_callbacks = {
            'select_all': self.select_all,
            'deselect_all': self.deselect_all,
            'run_analysis': self.run_analysis
        }
        bottom_toolbar = UIBuilder.create_bottom_toolbar(content_wrapper, toolbar_callbacks)
        
        # Initialize currency symbols and amounts
        self.root.after(100, self._on_currency_change)
        
        # Load forex rates and major indexes in background after UI is ready
        self.root.after(500, self.market_data_manager.load_all_market_data)
        
        # Start auto-refresh timer
        self.root.after(300000, self.market_data_manager.start_auto_refresh)
    
    def _rebind_symbol_callbacks(self):
        """Rebind entry widgets to use symbol_handler methods"""
        # Rebind ticker rows
        for i, row in enumerate(self.ticker_rows):
            entry = row["entry"]
            placeholder = row["placeholder"]
            
            # Clear and rebind (removed autocomplete bindings: KeyRelease, Down, Escape)
            for event in ["<FocusIn>", "<FocusOut>", "<Return>"]:
                entry.unbind(event)
            
            entry.bind("<FocusIn>", lambda e, ent=entry, ph=placeholder: self.symbol_handler.on_focus_in(ent, ph))
            entry.bind("<FocusOut>", lambda e, idx=i: self.symbol_handler.queue_validate("ticker", idx))
            entry.bind("<Return>", lambda e, idx=i: self.symbol_handler.queue_validate("ticker", idx))
        
        # Rebind benchmark rows
        for i, row in enumerate(self.benchmark_rows):
            entry = row["entry"]
            placeholder = row["placeholder"]
            browse_btn = row.get("browse_btn")
            
            # Clear and rebind (removed autocomplete bindings: KeyRelease, Down, Escape)
            for event in ["<FocusIn>", "<FocusOut>", "<Return>"]:
                entry.unbind(event)
            
            entry.bind("<FocusIn>", lambda e, ent=entry, ph=placeholder, idx=i: self.symbol_handler.on_focus_in(ent, ph, kind="bench", idx=idx))
            entry.bind("<FocusOut>", lambda e, idx=i: self.symbol_handler.queue_validate("bench", idx))
            entry.bind("<Return>", lambda e, idx=i: self.symbol_handler.queue_validate("bench", idx))
            
            # Bind browse button
            if browse_btn:
                browse_btn.config(command=lambda idx=i: self.symbol_handler.show_benchmark_selection("bench", idx))
    
    # -------------------- Currency & Capital Management --------------------
    
    def _on_currency_change(self):
        """Called when currency selection changes - delegates to PortfolioManager"""
        currency_symbol = self.get_currency_symbol()
        
        # Update all currency labels
        self.portfolio_manager.update_currency_labels(currency_symbol)
        
        # Recalculate all amounts
        self.portfolio_manager.update_all_amounts()
        
        # Update total
        self._update_weight_total()
    
    def _on_capital_change(self):
        """Called when capital amount changes - delegates to PortfolioManager"""
        # Recalculate all amounts based on new capital
        self.portfolio_manager.update_all_amounts()
        
        # Update total
        self._update_weight_total()
    
    # -------------------- Weight Management (Delegates to PortfolioManager) --------------------
    
    def _on_weight_change(self, idx):
        """Called when weight (%) changes - delegates to PortfolioManager"""
        self.portfolio_manager.update_amount_from_weight(idx)
        self._update_weight_total()
    
    def _on_amount_change(self, idx):
        """Called when amount (currency) changes - delegates to PortfolioManager"""
        self.portfolio_manager.update_weight_from_amount(idx)
        self._update_weight_total()
    
    def _update_weight_total(self):
        """Calculate and display total weight percentage"""
        total = self.portfolio_manager.calculate_weight_total()
        
        # Color-code based on total
        if abs(total - 100.0) < 0.01:
            color = T.PANEL_HEADER  # Green if 100%
            self.weight_total_label.config(text=f"{total:.1f}%", fg=color)
        elif total > 100.0:
            color = T.ERROR  # Red if over 100%
            self.weight_total_label.config(text=f"{total:.1f}% (over)", fg=color)
        else:
            color = T.WARNING  # Orange if under 100%
            self.weight_total_label.config(text=f"{total:.1f}%", fg=color)
        
        # Update portfolio summary when weights change
        self._update_portfolio_summary()
    
    def _normalize_weights(self):
        """Normalize all weights to sum to 100% - delegates to PortfolioManager"""
        count = self.portfolio_manager.normalize_weights()
        self._update_weight_total()
    
    def _equal_weights(self):
        """Set equal weights for all validated tickers - delegates to PortfolioManager"""
        validated_count, equal_weight = self.portfolio_manager.set_equal_weights()
        
        if validated_count == 0:
            messagebox.showinfo(
                "No Tickers", 
                "Please select and validate at least one ticker first."
            )
            return
        
        self._update_weight_total()
        
        messagebox.showinfo(
            "Equal Weights", 
            f"Set equal weights of {equal_weight:.2f}% for {validated_count} validated tickers."
        )
    
    def _clear_weights(self):
        """Clear all weight and amount values - delegates to PortfolioManager"""
        result = messagebox.askyesno(
            "Clear Weights",
            "This will reset all weights and amounts to 0. Continue?"
        )
        
        if not result:
            return
        
        self.portfolio_manager.clear_all_weights()
        self._update_weight_total()
    
    def _clear_portfolio(self):
        """Clear all tickers and weights"""
        result = messagebox.askyesno(
            "Clear Portfolio",
            "This will remove all tickers and weights. This action cannot be undone. Continue?"
        )
        
        if not result:
            return
        
        for idx, row in enumerate(self.ticker_rows):
            # Clear ticker entry
            entry = row.get("entry")
            placeholder = row.get("placeholder")
            if entry and placeholder:
                entry.delete(0, tk.END)
                entry.insert(0, placeholder)
                entry.config(fg=T.TEXT_MUTED, bg=T.INPUT_BG)
            
            # Reset status
            status_lbl = row.get("status")
            if status_lbl:
                status_lbl.config(text="•", fg=T.TEXT_MUTED)
            
            # Clear name label
            name_label = row.get("name_label")
            if name_label:
                name_label.config(text="")
        
        # Clear weights using manager
        self.portfolio_manager.clear_all_weights()
        self._update_weight_total()
        self._update_portfolio_summary()
    
    # -------------------- Helper Methods --------------------
    
    def _on_closing(self):
        """Handle window closing - cleanup timers and resources"""
        # Cleanup market data manager
        if self.market_data_manager:
            self.market_data_manager.cleanup()
        
        # Destroy window
        self.root.destroy()
    
    def _on_symbol_validated(self, kind):
        """
        Called after a symbol is validated
        
        Args:
            kind: "ticker" or "bench"
        """
        if kind == "ticker":
            self._update_portfolio_summary()
        elif kind == "bench":
            self._update_benchmark_summary()
    
    def get_capital_amount(self):
        """
        Get the capital amount entered by user
        
        Returns:
            float: Capital amount, or 10000 if invalid
        """
        try:
            capital_str = self.capital_var.get().replace(",", "")
            return float(capital_str)
        except (ValueError, AttributeError):
            return 10000.0
    
    def get_currency(self):
        """
        Get the selected currency
        
        Returns:
            str: Currency code (USD, EUR, GBP, JPY, CHF)
        """
        try:
            return self.currency_var.get()
        except AttributeError:
            return "USD"
    
    def get_currency_symbol(self):
        """
        Get the currency symbol for display - delegates to CurrencyManager
        
        Returns:
            str: Currency symbol ($ € £ ¥ CHF)
        """
        return self.currency_manager.get_symbol(self.get_currency())
    
    # -------------------- Summary Panel Updates --------------------
    
    def _update_portfolio_summary(self):
        """Update the Portfolio Composition panel with current validated tickers"""
        if not self.portfolio_text:
            return
        
        # Collect validated tickers with weights
        ticker_weights = []
        for row in self.ticker_rows:
            entry = row.get("entry")
            placeholder = row.get("placeholder")
            status_lbl = row.get("status")
            weight_entry = row.get("weight_entry")
            
            if not entry or not status_lbl:
                continue
            
            symbol = self.symbol_handler.get_symbol(entry, placeholder)
            status = status_lbl.cget("text")
            
            if symbol and status == "✓":
                try:
                    weight = float(weight_entry.get().strip()) if weight_entry else 0.0
                except ValueError:
                    weight = 0.0
                ticker_weights.append((symbol, weight))
        
        # Update the text widget
        self.portfolio_text.config(state=tk.NORMAL)
        self.portfolio_text.delete("1.0", tk.END)
        self.portfolio_text.insert("1.0", "Ticker    Weight\n")
        self.portfolio_text.insert("end", "-" * 25 + "\n")
        
        if ticker_weights:
            total_weight = sum(w for _, w in ticker_weights)
            for ticker, weight in ticker_weights:
                self.portfolio_text.insert("end", f"{ticker:<10}{weight:>6.1f}%\n")
            self.portfolio_text.insert("end", "-" * 25 + "\n")
            self.portfolio_text.insert("end", f"{'TOTAL':<10}{total_weight:>6.1f}%\n")
        else:
            self.portfolio_text.insert("end", "No tickers selected\n")
        
        self.portfolio_text.config(state=tk.DISABLED)
    
    def _update_benchmark_summary(self):
        """Update the Benchmarks panel with current validated benchmarks"""
        if not self.benchmark_text:
            return
        
        # Collect validated benchmarks
        benchmarks = []
        for row in self.benchmark_rows:
            entry = row.get("entry")
            placeholder = row.get("placeholder")
            status_lbl = row.get("status")
            name_label = row.get("name_label")
            
            if not entry or not status_lbl:
                continue
            
            symbol = self.symbol_handler.get_symbol(entry, placeholder)
            status = status_lbl.cget("text")
            
            if symbol and status == "✓":
                # Try to get name from label, otherwise use symbol
                name = ""
                if name_label:
                    name_text = name_label.cget("text")
                    # Clean the text
                    name = name_text.strip()
                    if name and len(name) > 15:
                        name = name[:12] + "..."
                
                if not name:
                    name = symbol
                
                benchmarks.append((name, symbol))
        
        # Update the text widget
        self.benchmark_text.config(state=tk.NORMAL)
        self.benchmark_text.delete("1.0", tk.END)
        self.benchmark_text.insert("1.0", "Index          Ticker\n")
        self.benchmark_text.insert("end", "-" * 25 + "\n")
        
        if benchmarks:
            for name, ticker in benchmarks:
                self.benchmark_text.insert("end", f"{name:<15}{ticker}\n")
        else:
            self.benchmark_text.insert("end", "No benchmarks selected\n")
        
        self.benchmark_text.config(state=tk.DISABLED)
    
    # -------------------- Chart Selection --------------------
    
    def select_all(self):
        """Select all charts"""
        for var in self.chart_vars.values():
            var.set(True)
        self.status_label.config(text="All charts selected", fg=T.SUCCESS)
    
    def deselect_all(self):
        """Deselect all charts"""
        for var in self.chart_vars.values():
            var.set(False)
        self.status_label.config(text="All charts deselected", fg=T.WARNING)
    
    # -------------------- Analysis Execution --------------------
    
    def run_analysis(self):
        """Run complete portfolio analysis by delegating to AnalysisRunner"""
        selected = [num for num, var in self.chart_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("No Selection", "Please select at least one chart!")
            return
        
        self.root.update()
        
        # Collect validated tickers with weights and benchmarks
        ticker_weights = self.symbol_handler.collect_valid_symbols("ticker")
        benches = self.symbol_handler.collect_valid_symbols("bench")
        
        # Get capital and currency from UI
        try:
            capital = float(self.capital_var.get())
        except (ValueError, AttributeError):
            capital = None  # Will use default START_CAPITAL
        
        currency = self.currency_var.get() if hasattr(self, 'currency_var') else "USD"
        
        # Status callback for real-time updates
        def status_callback(msg, color):
            self.status_label.config(text=msg, fg=color)
            self.root.update()
        
        # Run analysis using AnalysisRunner
        result = self.analysis_runner.run_analysis(
            ticker_weights=ticker_weights,
            benches=benches,
            selected_charts=selected,
            status_callback=status_callback,
            sanitize_func=SymbolValidator.sanitize_symbols,
            capital=capital,
            currency=currency
        )
        
        # Show result
        if result["success"]:
            messagebox.showinfo(
                "Complete", 
                f"{result['message']}\n\nSaved to: {result['output_dir']}"
            )
        else:
            messagebox.showerror("Error", result["message"])


def main():
    """Application entry point"""
    root = tk.Tk()
    app = ChartControlPanel(root)
    root.mainloop()


if __name__ == "__main__":
    main()
