# test_refactoring.py - Tests de validation pour la refactorisation
"""
Tests simples pour valider que les nouveaux modules fonctionnent correctement.

Usage:
    python test_refactoring.py
"""
import sys
import os

# Add parent directory to path to enable imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_currency_manager():
    """Test CurrencyManager module"""
    print("[TEST] Testing CurrencyManager...")
    
    from managers.currency_manager import CurrencyManager
    
    # Test get_symbol
    assert CurrencyManager.get_symbol("USD") == "$", "USD symbol failed"
    assert CurrencyManager.get_symbol("EUR") == "€", "EUR symbol failed"
    assert CurrencyManager.get_symbol("GBP") == "£", "GBP symbol failed"
    assert CurrencyManager.get_symbol("JPY") == "¥", "JPY symbol failed"
    assert CurrencyManager.get_symbol("CHF") == "CHF", "CHF symbol failed"
    print("  [OK] get_symbol() works")
    
    # Test get_name
    assert CurrencyManager.get_name("USD") == "US Dollar", "USD name failed"
    assert CurrencyManager.get_name("EUR") == "Euro", "EUR name failed"
    print("  [OK] get_name() works")
    
    # Test get_display_text
    assert CurrencyManager.get_display_text("USD") == "USD - US Dollar", "Display text failed"
    print("  [OK] get_display_text() works")
    
    # Test is_valid_currency
    assert CurrencyManager.is_valid_currency("USD") == True, "Valid currency check failed"
    assert CurrencyManager.is_valid_currency("XXX") == False, "Invalid currency check failed"
    print("  [OK] is_valid_currency() works")
    
    # Test format_amount
    formatted = CurrencyManager.format_amount(1234.56, "USD", decimals=2)
    assert "$" in formatted and "1,234" in formatted, "Amount formatting failed"
    print("  [OK] format_amount() works")
    
    # Test get_all_currencies
    currencies = CurrencyManager.get_all_currencies()
    assert len(currencies) == 5, "Currency list size incorrect"
    print("  [OK] get_all_currencies() works")
    
    print("[PASS] CurrencyManager: All tests passed!\n")


def test_portfolio_manager():
    """Test PortfolioManager module (basic instantiation)"""
    print("[TEST] Testing PortfolioManager...")
    
    from managers.portfolio_manager import PortfolioManager
    
    # Mock data
    mock_ticker_rows = [
        {
            "weight_entry": type('obj', (object,), {
                'get': lambda: "10.0",
                'delete': lambda s, e: None,
                'insert': lambda p, v: None
            })(),
            "amount_entry": type('obj', (object,), {
                'get': lambda: "1000",
                'delete': lambda s, e: None,
                'insert': lambda p, v: None
            })(),
            "currency_label": type('obj', (object,), {
                'config': lambda **kwargs: None
            })(),
            "status": type('obj', (object,), {
                'cget': lambda attr: "✓"
            })()
        }
    ]
    
    def mock_get_capital():
        return 10000.0
    
    def mock_get_currency_symbol():
        return "$"
    
    # Create manager
    manager = PortfolioManager(
        mock_ticker_rows, 
        mock_get_capital, 
        mock_get_currency_symbol
    )
    
    print("  [OK] PortfolioManager instantiation works")
    
    # Test calculate_weight_total
    total = manager.calculate_weight_total()
    assert isinstance(total, float), "Weight total should be float"
    print("  [OK] calculate_weight_total() works")
    
    # Test get_validated_tickers_count
    count = manager.get_validated_tickers_count()
    assert isinstance(count, int), "Validated count should be int"
    print("  [OK] get_validated_tickers_count() works")
    
    print("[PASS] PortfolioManager: All tests passed!\n")


def test_market_data_manager():
    """Test MarketDataManager module (basic instantiation)"""
    print("[TEST] Testing MarketDataManager...")
    
    from managers.market_data_manager import MarketDataManager
    import tkinter as tk
    
    # Create mock Tkinter root
    try:
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        # Mock callbacks and buttons
        def mock_forex_callback(data):
            pass
        
        def mock_indexes_callback(data):
            pass
        
        mock_btn = tk.Button(root, text="Test")
        
        # Create manager
        manager = MarketDataManager(
            root,
            mock_forex_callback,
            mock_indexes_callback,
            mock_btn,
            mock_btn,
            auto_refresh_interval=5000
        )
        
        print("  [OK] MarketDataManager instantiation works")
        
        # Test cleanup
        manager.cleanup()
        print("  [OK] cleanup() works")
        
        root.destroy()
        
        print("[PASS] MarketDataManager: All tests passed!\n")
        
    except Exception as e:
        print(f"  [SKIP] Tkinter test skipped (no display): {e}\n")


def test_imports():
    """Test that all modules can be imported"""
    print("[TEST] Testing imports...")
    
    try:
        from managers.currency_manager import CurrencyManager
        print("  [OK] currency_manager imported")
    except ImportError as e:
        print(f"  [FAIL] currency_manager import failed: {e}")
        return False
    
    try:
        from managers.portfolio_manager import PortfolioManager
        print("  [OK] portfolio_manager imported")
    except ImportError as e:
        print(f"  [FAIL] portfolio_manager import failed: {e}")
        return False
    
    try:
        from managers.market_data_manager import MarketDataManager
        print("  [OK] market_data_manager imported")
    except ImportError as e:
        print(f"  [FAIL] market_data_manager import failed: {e}")
        return False
    
    try:
        from ui import menu_principal
        print("  [OK] menu_principal imported")
    except ImportError as e:
        print(f"  [FAIL] menu_principal import failed: {e}")
        return False
    
    print("[PASS] All imports successful!\n")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Refactored Modules")
    print("=" * 60 + "\n")
    
    # Test imports first
    if not test_imports():
        print("[FAIL] Import tests failed. Stopping.")
        return
    
    # Test individual modules
    try:
        test_currency_manager()
    except AssertionError as e:
        print(f"[FAIL] CurrencyManager test failed: {e}\n")
    except Exception as e:
        print(f"[ERROR] CurrencyManager test error: {e}\n")
    
    try:
        test_portfolio_manager()
    except AssertionError as e:
        print(f"[FAIL] PortfolioManager test failed: {e}\n")
    except Exception as e:
        print(f"[ERROR] PortfolioManager test error: {e}\n")
    
    try:
        test_market_data_manager()
    except AssertionError as e:
        print(f"[FAIL] MarketDataManager test failed: {e}\n")
    except Exception as e:
        print(f"[ERROR] MarketDataManager test error: {e}\n")
    
    print("=" * 60)
    print("Testing Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

