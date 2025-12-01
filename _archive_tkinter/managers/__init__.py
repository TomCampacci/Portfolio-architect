# managers/__init__.py - Managers Module
"""
Business logic managers for Portfolio Analysis.

Contains:
- CurrencyManager: Currency operations
- PortfolioManager: Portfolio weight management  
- MarketDataManager: Real-time market data
- SymbolValidator/SymbolUIHandler: Symbol validation
"""

# Imports are done on-demand to avoid circular imports
__all__ = [
    'CurrencyManager',
    'PortfolioManager',
    'MarketDataManager',
    'SymbolValidator',
    'SymbolUIHandler'
]
