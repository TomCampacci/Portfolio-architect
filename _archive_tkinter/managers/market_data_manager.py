# market_data_manager.py - Market Data Management Module
"""
Handles real-time market data fetching and updates.

Responsibilities:
- Fetch and update forex rates (EUR/USD, GBP/USD)
- Fetch and update major index prices
- Auto-refresh market data on timer
- Handle loading states for refresh buttons
"""
import threading
import tkinter as tk
from ui.theme_colors import LightPremiumTheme as T


class MarketDataManager:
    """
    Manages real-time market data (forex rates and major indexes)
    """
    
    def __init__(self, root, forex_update_callback, indexes_update_callback, 
                 forex_refresh_btn, indexes_refresh_btn, auto_refresh_interval=300000):
        """
        Initialize market data manager
        
        Args:
            root: Tkinter root window
            forex_update_callback: Callback to update forex display
            indexes_update_callback: Callback to update indexes display
            forex_refresh_btn: Forex refresh button widget
            indexes_refresh_btn: Indexes refresh button widget
            auto_refresh_interval: Auto-refresh interval in milliseconds (default: 5 minutes)
        """
        self.root = root
        self.forex_update_callback = forex_update_callback
        self.indexes_update_callback = indexes_update_callback
        self.forex_refresh_btn = forex_refresh_btn
        self.indexes_refresh_btn = indexes_refresh_btn
        self.auto_refresh_interval = auto_refresh_interval
        self.auto_refresh_timer = None
    
    def load_all_market_data(self):
        """Load both forex rates and major indexes in background thread"""
        def fetch_market_data():
            """Fetch market data in background"""
            from utils.utils_data import get_current_forex_rates, get_major_indexes_prices
            
            # Fetch forex rates
            rates = get_current_forex_rates()
            self.root.after(0, lambda: self.forex_update_callback(rates))
            
            # Fetch major indexes
            indexes = get_major_indexes_prices()
            self.root.after(0, lambda: self.indexes_update_callback(indexes))
        
        # Run in background to avoid blocking UI
        thread = threading.Thread(target=fetch_market_data, daemon=True)
        thread.start()
    
    def refresh_forex(self):
        """Manually refresh forex rates with loading indicator"""
        # Show loading state
        self.forex_refresh_btn.config(
            text="Loading...", 
            state=tk.DISABLED, 
            bg=T.TEXT_SECONDARY
        )
        
        def fetch_forex():
            """Fetch forex rates in background"""
            from utils.utils_data import get_current_forex_rates
            
            rates = get_current_forex_rates()
            
            def update_ui():
                self.forex_update_callback(rates)
                # Restore button
                self.forex_refresh_btn.config(
                    text="Refresh", 
                    state=tk.NORMAL, 
                    bg=T.PRIMARY
                )
            
            self.root.after(0, update_ui)
        
        # Run in background
        thread = threading.Thread(target=fetch_forex, daemon=True)
        thread.start()
    
    def refresh_indexes(self):
        """Manually refresh major indexes with loading indicator"""
        # Show loading state
        self.indexes_refresh_btn.config(
            text="Loading...", 
            state=tk.DISABLED, 
            bg=T.TEXT_SECONDARY
        )
        
        def fetch_indexes():
            """Fetch indexes in background"""
            from utils.utils_data import get_major_indexes_prices
            
            indexes = get_major_indexes_prices()
            
            def update_ui():
                self.indexes_update_callback(indexes)
                # Restore button
                self.indexes_refresh_btn.config(
                    text="Refresh", 
                    state=tk.NORMAL, 
                    bg=T.PRIMARY
                )
            
            self.root.after(0, update_ui)
        
        # Run in background
        thread = threading.Thread(target=fetch_indexes, daemon=True)
        thread.start()
    
    def start_auto_refresh(self):
        """Start auto-refresh timer for market data"""
        def auto_refresh():
            """Auto-refresh market data"""
            self.load_all_market_data()
            
            # Schedule next refresh
            self.auto_refresh_timer = self.root.after(
                self.auto_refresh_interval, 
                auto_refresh
            )
        
        # Start the timer
        self.root.after(self.auto_refresh_interval, auto_refresh)
    
    def stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if self.auto_refresh_timer:
            self.root.after_cancel(self.auto_refresh_timer)
            self.auto_refresh_timer = None
    
    def cleanup(self):
        """Cleanup resources (call on window close)"""
        self.stop_auto_refresh()

