# Two-Page Portfolio Architecture (v4)

## Overview

The Portfolio Architect has been redesigned with a **two-page tabbed interface** for better organization and user experience.

## Architecture

### Page 1: Portfolio Setup 📊
**Purpose:** Configure your portfolio and market context

**Components:**
1. **Market Data Panel** (Top, Full Width)
   - Real-time Forex rates (EUR, GBP, JPY, CHF vs USD)
   - Commodities prices (Gold, Silver, Oil)
   - Bond yields (US 10Y Treasury)
   - Major stock indexes (S&P 500, Nasdaq, DAX, CAC 40, FTSE, Nikkei, Hang Seng)
   - Auto-refresh every 5 seconds
   - Color-coded changes (green/red with flash effects)

2. **Portfolio Positions** (Bottom Left, 50%)
   - Up to 10 ticker positions
   - Ticker/ISIN input with validation
   - Weight % entry
   - Amount calculation (auto-synced with capital)
   - Status indicators (✓ for validated)
   - Asset name display after validation
   - Action buttons:
     - **Equal**: Distribute weights equally
     - **Auto 100%**: Scale proportionally to 100%
     - **Clear**: Reset all weights

3. **Benchmark Indexes** (Bottom Right, 50%)
   - Up to 6 benchmark selections
   - Manual entry or browse button (📋)
   - Browse opens enhanced selector with:
     - Tab 1: Major Indexes (organized by region)
     - Tab 2: Search any stock/ETF
   - Status indicators
   - Benchmark name display after validation

### Page 2: Analysis Charts 📈
**Purpose:** Select which analysis charts to generate

**Components:**
1. **Chart Selection Panel** (Full Screen)
   - 24 professional charts organized in 5 categories:
     - **Portfolio & Sector** (1-6): Allocation, Correlation, Risk Contribution, Performance vs Benchmarks, Sector Decomposition, Sector Risk
     - **Monte Carlo** (7-12): MC Paths (Normal & Random), Volatility (Normal & Random), Max Drawdown (Normal & Random)
     - **Risk Metrics** (13-17): VaR 95%, Expected Shortfall, Max DD Duration, Calmar Ratio, Sharpe Ratio
     - **Benchmarks** (18-21): Risk vs Indexes, Forward Excess, Portfolio vs Benchmarks (Normal & Random)
     - **Sector & Regime** (22-24): Sector Performance, Regime Analysis, Sector Rotation
   
   - **3-column layout** for optimal space usage
   - Each chart shows:
     - Chart number and name
     - Description tooltip
     - Checkbox for selection
   
   - Quick actions:
     - **All**: Select all charts
     - **None**: Deselect all charts

### Common Elements

**Top Toolbar** (Always Visible)
- **Capital Input**: Initial portfolio capital amount
- **Currency Selector**: USD, EUR, GBP
- **Credit**: Built by Tom Campacci - Financial Student

**Bottom Button** (Always Visible)
- **▶ Run Portfolio Analysis**: Execute analysis with selected charts

## Key Features

### Real-time Market Data
- **Auto-refresh**: Every 5 seconds
- **Visual feedback**: Flash green (positive) or red (negative) on changes
- **Comprehensive coverage**: Forex, commodities, bonds, and global indexes

### Smart Weight Management
- **Bi-directional sync**: Change weight → amount updates, or amount → weight updates
- **Auto-calculation**: Amounts automatically recalculate when capital changes
- **Equal weights**: Distribute 100% equally among filled positions
- **Auto 100%**: Proportionally scale existing weights to reach 100%

### Symbol Validation
- **Real-time validation**: Green ✓ for valid symbols
- **ISIN support**: Automatically detects and handles ISINs
- **Multi-exchange**: Choose from multiple exchanges when available
- **Name display**: Shows full asset name after validation

### Enhanced Benchmark Selection
- **Browse mode**: Visual selector with two tabs
- **Major Indexes**: Pre-populated list organized by region (US, Europe, Asia, Commodities)
- **Search mode**: Search any stock, ETF, or index
- **Quick selection**: One-click to select and close

## User Workflow

1. **Start on Page 1** - Setup your portfolio:
   - Review real-time market data
   - Enter your tickers (up to 10)
   - Set weights (Equal, Auto 100%, or manual)
   - Select benchmarks (up to 6)

2. **Switch to Page 2** - Select your analysis:
   - Browse available charts by category
   - Select charts you want to generate
   - Use "All" or "None" for bulk selection

3. **Run Analysis** - Click the green button:
   - Portfolio is validated
   - Selected charts are generated
   - Results saved to `results/` folder

## Technical Architecture

### File Structure
```
ui/
├── menu_principal_v4.py      # Two-page architecture (NEW)
├── menu_principal_v3.py      # Single-page (previous)
├── menu_principal.py          # Original
├── theme_colors.py            # Color theme
└── modern_ui_builder.py       # UI components

managers/
├── symbol_handler.py          # Symbol validation
├── portfolio_manager.py       # Weight calculations
├── currency_manager.py        # Currency handling
└── market_data_manager.py     # Market data fetching

core/
├── analysis_runner.py         # Analysis execution
├── config.py                  # Configuration
└── main.py                    # Analysis logic
```

### Key Classes

**TwoPagePortfolioArchitect** (`menu_principal_v4.py`)
- Main orchestrator for two-page UI
- Manages notebook (tabs) and page navigation
- Coordinates all managers and handlers

**SymbolUIHandler** (`managers/symbol_handler.py`)
- Real-time symbol validation
- ISIN detection and handling
- Multi-exchange resolution

**PortfolioManager** (`managers/portfolio_manager.py`)
- Weight normalization
- Equal weight distribution
- Amount/weight synchronization

**CurrencyManager** (`managers/currency_manager.py`)
- Currency symbol mapping
- Format handling

**MarketDataManager** (`managers/market_data_manager.py`)
- Auto-refresh scheduling
- Forex and index data fetching
- UI update coordination

**AnalysisRunner** (`core/analysis_runner.py`)
- Chart generation orchestration
- Progress tracking
- Error handling

## Advantages of Two-Page Design

### 1. **Better Organization**
- Clear separation of concerns: Setup vs Analysis
- Less clutter on each page
- Focused user experience

### 2. **Improved Usability**
- Larger chart selector on dedicated page
- More space for market data
- Clearer visual hierarchy

### 3. **Flexibility**
- Easy to add more charts without cramping
- Can expand portfolio positions if needed
- Room for future enhancements

### 4. **Performance**
- Only render active tab
- Lighter memory footprint
- Faster UI response

## Future Enhancements

Potential additions to the two-page architecture:

### Page 1 Enhancements
- [ ] Add more market data (crypto, futures)
- [ ] Historical price charts in tooltips
- [ ] Portfolio allocation pie chart preview
- [ ] Risk/return summary dashboard

### Page 2 Enhancements
- [ ] Chart preview thumbnails
- [ ] Custom chart groups (save selections)
- [ ] Chart dependencies (auto-select related charts)
- [ ] Estimated generation time

### Additional Pages (if needed)
- **Page 3: Settings** - Advanced configuration, API keys, preferences
- **Page 4: History** - Previous analyses, comparison tools
- **Page 5: Reports** - Generate PDF reports, export data

## Migration from v3 to v4

To switch between versions, edit `app.py`:

```python
# Use v3 (single-page)
from ui.menu_principal_v3 import main

# Use v4 (two-page)
from ui.menu_principal_v4 import main
```

All functionality is preserved between versions. The two-page design is a UX improvement with no breaking changes to the underlying analysis engine.

## Best Practices

### For Users
1. **Page 1 First**: Always configure portfolio before selecting charts
2. **Validate Symbols**: Ensure all tickers show green ✓ before running
3. **Check Total Weight**: Aim for 100% (use Auto 100% if needed)
4. **Select Relevant Charts**: Don't generate all 24 if you only need a few

### For Developers
1. **Keep Pages Independent**: Each page should be self-contained
2. **Maintain State**: Use instance variables for cross-page data
3. **Optimize Rendering**: Only update active tab
4. **Add Documentation**: Update this file when adding features

## Conclusion

The two-page architecture provides a cleaner, more organized experience while maintaining all the powerful features of the Portfolio Architect. It's designed to scale with future enhancements and provide a professional-grade portfolio analysis tool.

**Version:** v4  
**Date:** November 2024  
**Author:** Tom Campacci  
**Status:** Production Ready



