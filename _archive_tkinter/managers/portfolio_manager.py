# portfolio_manager.py - Portfolio Weight Management Module
"""
Handles portfolio weight calculations and management.

Responsibilities:
- Calculate and validate weights
- Normalize weights to 100%
- Calculate equal weights
- Synchronize weights and amounts
- Calculate total portfolio weight
"""
import tkinter as tk


class PortfolioManager:
    """
    Manages portfolio weights, amounts, and calculations
    """
    
    def __init__(self, ticker_rows, get_capital_callback, get_currency_symbol_callback):
        """
        Initialize portfolio manager
        
        Args:
            ticker_rows: List of ticker row dictionaries
            get_capital_callback: Function to get current capital amount
            get_currency_symbol_callback: Function to get currency symbol
        """
        self.ticker_rows = ticker_rows
        self.get_capital = get_capital_callback
        self.get_currency_symbol = get_currency_symbol_callback
    
    def calculate_weight_total(self):
        """
        Calculate total weight percentage across all tickers
        
        Returns:
            float: Total weight percentage
        """
        total = 0.0
        for row in self.ticker_rows:
            try:
                val = row["weight_entry"].get().strip()
                if val:
                    total += float(val)
            except (ValueError, KeyError):
                pass
        return total
    
    def update_amount_from_weight(self, idx):
        """
        Update amount field based on weight percentage
        
        Args:
            idx: Row index
        
        Returns:
            bool: True if successful, False otherwise
        """
        if idx < 0 or idx >= len(self.ticker_rows):
            return False
        
        row = self.ticker_rows[idx]
        weight_entry = row.get("weight_entry")
        amount_entry = row.get("amount_entry")
        
        if not weight_entry or not amount_entry:
            return False
        
        try:
            # Get weight percentage
            weight_str = weight_entry.get().strip()
            if not weight_str:
                amount_entry.delete(0, tk.END)
                amount_entry.insert(0, "0")
                return True
            
            weight = float(weight_str)
            
            # Get capital amount
            capital = self.get_capital()
            
            # Calculate amount
            amount = (weight / 100.0) * capital
            
            # Update amount field with formatted value
            formatted_amount = f"{amount:,.0f}"
            amount_entry.delete(0, tk.END)
            amount_entry.insert(0, formatted_amount)
            
            return True
            
        except ValueError:
            return False
    
    def update_weight_from_amount(self, idx):
        """
        Update weight field based on amount
        
        Args:
            idx: Row index
        
        Returns:
            bool: True if successful, False otherwise
        """
        if idx < 0 or idx >= len(self.ticker_rows):
            return False
        
        row = self.ticker_rows[idx]
        weight_entry = row.get("weight_entry")
        amount_entry = row.get("amount_entry")
        
        if not weight_entry or not amount_entry:
            return False
        
        try:
            # Get amount (remove commas first)
            amount_str = amount_entry.get().strip().replace(",", "")
            if not amount_str:
                weight_entry.delete(0, tk.END)
                weight_entry.insert(0, "0.0")
                return True
            
            amount = float(amount_str)
            
            # Get capital
            capital = self.get_capital()
            
            if capital <= 0:
                return False
            
            # Calculate weight percentage
            weight = (amount / capital) * 100.0
            
            # Update weight field
            weight_entry.delete(0, tk.END)
            weight_entry.insert(0, f"{weight:.2f}")
            
            return True
            
        except ValueError:
            return False
    
    def normalize_weights(self):
        """
        Normalize all weights to sum to 100%
        
        Returns:
            int: Number of weights normalized
        """
        weights = []
        for row in self.ticker_rows:
            try:
                val = row["weight_entry"].get().strip()
                if val:
                    weight = float(val)
                    if weight > 0:  # Only include non-zero weights
                        weights.append((row, weight))
            except (ValueError, KeyError):
                pass
        
        if not weights:
            return 0
        
        total = sum(w for _, w in weights)
        if total <= 0:
            return 0
        
        # Normalize and update
        for row, w in weights:
            normalized = (w / total) * 100.0
            row["weight_entry"].delete(0, tk.END)
            row["weight_entry"].insert(0, f"{normalized:.2f}")
        
        return len(weights)
    
    def set_equal_weights(self):
        """
        Set equal weights for all validated tickers
        
        Returns:
            tuple: (number of validated tickers, equal weight value)
        """
        # Count validated tickers (those with green checkmark)
        validated_rows = []
        for row in self.ticker_rows:
            status_lbl = row.get("status")
            if status_lbl and status_lbl.cget("text") == "✓":
                validated_rows.append(row)
        
        if not validated_rows:
            return (0, 0.0)
        
        # Calculate equal weight
        equal_weight = 100.0 / len(validated_rows)
        
        # Set equal weight for validated tickers, zero for others
        for row in self.ticker_rows:
            weight_entry = row.get("weight_entry")
            status_lbl = row.get("status")
            
            if weight_entry:
                if status_lbl and status_lbl.cget("text") == "✓":
                    weight_entry.delete(0, tk.END)
                    weight_entry.insert(0, f"{equal_weight:.2f}")
                else:
                    weight_entry.delete(0, tk.END)
                    weight_entry.insert(0, "0.0")
        
        return (len(validated_rows), equal_weight)
    
    def clear_all_weights(self):
        """
        Clear all weight and amount values (set to 0)
        
        Returns:
            int: Number of rows cleared
        """
        count = 0
        for row in self.ticker_rows:
            # Clear weight
            weight_entry = row.get("weight_entry")
            if weight_entry:
                weight_entry.delete(0, tk.END)
                weight_entry.insert(0, "0.0")
                count += 1
            
            # Clear amount
            amount_entry = row.get("amount_entry")
            if amount_entry:
                amount_entry.delete(0, tk.END)
                amount_entry.insert(0, "0")
        
        return count
    
    def update_all_amounts(self):
        """
        Recalculate all amounts based on current weights and capital
        
        Returns:
            int: Number of amounts updated
        """
        count = 0
        for idx in range(len(self.ticker_rows)):
            if self.update_amount_from_weight(idx):
                count += 1
        return count
    
    def update_currency_labels(self, symbol):
        """
        Update all currency labels with new symbol
        
        Args:
            symbol: Currency symbol to display
        
        Returns:
            int: Number of labels updated
        """
        count = 0
        for row in self.ticker_rows:
            currency_label = row.get("currency_label")
            if currency_label:
                currency_label.config(text=symbol)
                count += 1
        return count
    
    def get_validated_tickers_count(self):
        """
        Count number of validated tickers
        
        Returns:
            int: Number of validated tickers
        """
        count = 0
        for row in self.ticker_rows:
            status_lbl = row.get("status")
            if status_lbl and status_lbl.cget("text") == "✓":
                count += 1
        return count

