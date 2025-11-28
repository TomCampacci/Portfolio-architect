# Capital and Currency Selection Panel

## Overview
New UI panel that allows users to customize their portfolio's initial capital amount and currency, replacing the hardcoded `START_CAPITAL = 10000` configuration.

## ✅ Features Implemented

### 1. **Capital Amount Input**
- **Text field** for entering custom capital amount
- **Real-time validation** with color-coded feedback
- **Formatted display** showing the amount with thousand separators
- **Default value**: 10,000 (configurable)

### 2. **Currency Selection**
- **Radio buttons** for currency selection
- **5 Major currencies supported**:
  - 💵 USD - US Dollar
  - 💶 EUR - Euro
  - 💷 GBP - British Pound
  - ¥ JPY - Japanese Yen
  - ₣ CHF - Swiss Franc
- **Default**: USD (configurable)

### 3. **Visual Design**
- **Card-style panel** with icon (💰)
- **Consistent styling** matching existing UI
- **Color-coded validation**:
  - ✅ Green: Valid amount
  - ❌ Red: Invalid input
- **Responsive layout** adapts to window size

## 📋 Technical Implementation

### Files Modified

#### `ui_builder.py`
Added new static method:
```python
@staticmethod
def create_capital_currency_panel(parent, default_capital=10000, default_currency="USD"):
    """
    Create panel for capital amount and currency selection
    
    Returns:
        tuple: (panel_frame, capital_var, currency_var, capital_display)
    """
```

**Features:**
- StringVar bindings for capital and currency
- Real-time validation with trace callbacks
- Formatted display with thousand separators
- Error handling for invalid input

#### `menu_principal.py`
Added:
1. **Instance variables**:
   - `self.capital_var` - Capital amount StringVar
   - `self.currency_var` - Currency code StringVar
   - `self.capital_display` - Display label widget

2. **Helper methods**:
   ```python
   def get_capital_amount(self) -> float
   def get_currency(self) -> str
   def get_currency_symbol(self) -> str
   ```

3. **UI Integration**:
   - Panel placed at top of right panel
   - Appears before ticker/benchmark cards
   - Initialized in `setup_ui()` method

## 🎯 Usage

### In UI
1. User enters capital amount (e.g., "25000")
2. Selects currency (e.g., EUR)
3. Real-time validation shows formatted amount
4. Values accessible via getter methods

### In Code
```python
# Get current values
capital = self.get_capital_amount()  # Returns: 25000.0
currency = self.get_currency()       # Returns: "EUR"
symbol = self.get_currency_symbol()  # Returns: "€"

# Use in analysis
portfolio_value = capital * portfolio_return
display_text = f"{symbol}{portfolio_value:,.2f} {currency}"
```

## 📊 Example Scenarios

### Scenario 1: US Investor
```
Capital: 50,000
Currency: USD
Display: $50,000 USD
```

### Scenario 2: European Investor
```
Capital: 25,000
Currency: EUR
Display: €25,000 EUR
```

### Scenario 3: UK Investor
```
Capital: 100,000
Currency: GBP
Display: £100,000 GBP
```

## 🔧 Configuration

### Default Values
Located in `menu_principal.py`, line ~107:
```python
capital_panel, self.capital_var, self.currency_var, self.capital_display = \
    UIBuilder.create_capital_currency_panel(
        right_panel, 
        default_capital=10000,    # Change default capital
        default_currency="USD"    # Change default currency
    )
```

### Adding New Currencies
In `ui_builder.py`, modify the currencies list:
```python
currencies = [
    ("💵 USD - US Dollar", "USD"),
    ("💶 EUR - Euro", "EUR"),
    ("💷 GBP - British Pound", "GBP"),
    ("¥ JPY - Japanese Yen", "JPY"),
    ("₣ CHF - Swiss Franc", "CHF"),
    # Add new currency here:
    ("$ CAD - Canadian Dollar", "CAD"),
]
```

Update currency symbols in `menu_principal.py`:
```python
currency_symbols = {
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "JPY": "¥",
    "CHF": "₣",
    "CAD": "$",  # Add new symbol
}
```

## 🚀 Next Steps (Future Enhancements)

### Potential Improvements
1. **Currency Conversion**
   - Fetch real-time exchange rates
   - Display portfolio value in multiple currencies
   - Historical conversion for backtesting

2. **Preset Amounts**
   - Quick buttons: $10K, $50K, $100K, $500K
   - Save/load user presets

3. **Advanced Settings**
   - Transaction costs per currency
   - Tax rates by country
   - Broker fees

4. **Validation Enhancements**
   - Min/max capital limits
   - Warning for unrealistic values
   - Suggest currency based on portfolio assets

## 📝 Testing

### Manual Test
Run the test script:
```bash
cd Portfolio
python test_capital_panel.py
```

This will show the panel in isolation for testing.

### Integration Test
1. Run main application: `python menu_principal.py`
2. Verify panel appears at top of right panel
3. Enter different capital amounts
4. Select different currencies
5. Check formatted display updates correctly

## ✅ Validation

### Capital Input
- **Valid**: Numeric values (integers or decimals)
- **Invalid**: Text, special characters (except comma)
- **Auto-formatting**: Commas added for readability
- **Fallback**: Returns 10,000 if invalid

### Currency Selection
- **Default**: USD if none selected
- **Validation**: Only predefined currencies accepted
- **Display**: Matching symbol automatically shown

## 🎨 UI Specifications

### Layout
```
┌─────────────────────────────────────────┐
│ 💰 Portfolio Settings                   │
├─────────────────────────────────────────┤
│                                         │
│ Initial Capital:  [10000]  (10,000)    │
│                                         │
│ Currency:  ⚪USD  ⚪EUR  ⚪GBP  ⚪JPY  ⚪CHF │
│                                         │
└─────────────────────────────────────────┘
```

### Colors
- **Background**: White (#FFFFFF)
- **Border**: Light gray (#E0E0E0)
- **Text**: Dark gray (#333333)
- **Valid input**: Green (#4CAF50)
- **Invalid input**: Red (#F44336)
- **Selected currency**: Light blue (#E3F2FD)

### Fonts
- **Title**: Arial 11pt Bold
- **Labels**: Arial 10pt Regular
- **Input**: Arial 12pt Bold
- **Display**: Arial 9pt Regular

## 🐛 Known Limitations

1. **No Real-Time Conversion**: Currency selection is for display only
2. **Static Exchange Rates**: No automatic rate updates
3. **Limited Currencies**: Only 5 major currencies supported
4. **No Persistence**: Values reset on application restart

## 📚 References

- Main implementation: `ui_builder.py` lines 10-104
- Integration: `menu_principal.py` lines 65-68, 106-107, 259-298
- Test script: `test_capital_panel.py`

