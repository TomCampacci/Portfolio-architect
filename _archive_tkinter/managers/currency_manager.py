# currency_manager.py - Currency Management Module
"""
Handles currency-related operations for the Portfolio Analysis application.

Responsibilities:
- Get currency symbols ($ € £ ¥ CHF)
- Validate currency codes
- Provide currency conversion helpers
"""


class CurrencyManager:
    """
    Manages currency symbols and conversions
    """
    
    # Supported currencies with their symbols
    CURRENCY_SYMBOLS = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CHF": "CHF"
    }
    
    # Display names for UI
    CURRENCY_NAMES = {
        "USD": "US Dollar",
        "EUR": "Euro",
        "GBP": "British Pound",
        "JPY": "Japanese Yen",
        "CHF": "Swiss Franc"
    }
    
    def __init__(self, default_currency="USD"):
        """
        Initialize currency manager
        
        Args:
            default_currency: Default currency code (USD, EUR, GBP, JPY, CHF)
        """
        self.default_currency = default_currency
    
    @classmethod
    def get_symbol(cls, currency_code):
        """
        Get currency symbol for display
        
        Args:
            currency_code: Currency code (USD, EUR, GBP, JPY, CHF)
        
        Returns:
            str: Currency symbol ($ € £ ¥ CHF)
        """
        return cls.CURRENCY_SYMBOLS.get(currency_code, "$")
    
    @classmethod
    def get_name(cls, currency_code):
        """
        Get currency full name
        
        Args:
            currency_code: Currency code (USD, EUR, GBP, JPY, CHF)
        
        Returns:
            str: Currency name (e.g., "US Dollar")
        """
        return cls.CURRENCY_NAMES.get(currency_code, "Unknown")
    
    @classmethod
    def get_display_text(cls, currency_code):
        """
        Get formatted display text for UI
        
        Args:
            currency_code: Currency code
        
        Returns:
            str: Formatted text (e.g., "USD - US Dollar")
        """
        name = cls.get_name(currency_code)
        return f"{currency_code} - {name}"
    
    @classmethod
    def is_valid_currency(cls, currency_code):
        """
        Check if currency code is valid
        
        Args:
            currency_code: Currency code to validate
        
        Returns:
            bool: True if valid, False otherwise
        """
        return currency_code in cls.CURRENCY_SYMBOLS
    
    @classmethod
    def get_all_currencies(cls):
        """
        Get list of all supported currencies
        
        Returns:
            list: List of tuples (display_text, code)
        """
        return [
            (cls.get_display_text(code), code)
            for code in cls.CURRENCY_SYMBOLS.keys()
        ]
    
    @classmethod
    def format_amount(cls, amount, currency_code, decimals=2):
        """
        Format amount with currency symbol
        
        Args:
            amount: Numeric amount
            currency_code: Currency code
            decimals: Number of decimal places (default: 2)
        
        Returns:
            str: Formatted amount with symbol (e.g., "$1,234.56")
        """
        symbol = cls.get_symbol(currency_code)
        
        if decimals == 0:
            formatted = f"{amount:,.0f}"
        else:
            formatted = f"{amount:,.{decimals}f}"
        
        # Place symbol based on currency convention
        if currency_code in ["USD", "GBP"]:
            return f"{symbol}{formatted}"
        else:
            return f"{formatted} {symbol}"

