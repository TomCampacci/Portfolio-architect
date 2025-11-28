# Portfolio Architect v4 - Quick Start Guide

## Getting Started in 5 Minutes

This guide will help you run your first portfolio analysis using the new two-page architecture.

## Step 1: Launch the Application

### Windows
Double-click `Lancer_Portfolio.bat` or run:
```bash
python app.py
```

### macOS/Linux
```bash
python3 app.py
```

## Step 2: Configure Capital & Currency

In the **top toolbar**, set:
- **Capital:** Your portfolio size (e.g., `10000`)
- **Currency:** Your base currency (`USD`, `EUR`, or `GBP`)

## Step 3: Add Your Portfolio (Page 1)

You should now be on **📊 Portfolio Setup** (Page 1).

### Add Tickers
In the **Portfolio Positions** section (left side):

1. **Enter ticker symbols** (one per row):
   ```
   Row 1: AAPL
   Row 2: MSFT
   Row 3: NVDA
   Row 4: GOOGL
   Row 5: AMZN
   ```

2. **Wait for validation**: 
   - Symbol turns green ✓ when valid
   - Asset name appears below entry

3. **Set weights** using one of three methods:

   **Method A: Equal Weights (Fastest)**
   - Click the **Equal** button
   - All tickers get equal weight (e.g., 5 tickers = 20% each)
   
   **Method B: Manual Entry**
   ```
   AAPL:  30%
   MSFT:  25%
   NVDA:  20%
   GOOGL: 15%
   AMZN:  10%
   ───────────
   Total: 100%
   ```
   
   **Method C: Auto Scale**
   - Enter approximate weights:
     ```
     AAPL:  60
     MSFT:  50
     NVDA:  40
     GOOGL: 30
     AMZN:  20
     ```
   - Click **Auto 100%**
   - Weights automatically scale to 100%

4. **Check Total**: Ensure "Total: 100%" shows in green

### Add Benchmarks
In the **Benchmark Indexes** section (right side):

**Option A: Type Symbol Directly**
```
Row 1: ^GSPC    (S&P 500)
Row 2: ^NDX     (Nasdaq 100)
Row 3: ^GDAXI   (DAX)
```

**Option B: Use Browse Button**
1. Click the **📋** button next to any row
2. **Tab 1 - Major Indexes**: Select from popular indexes
3. **Tab 2 - Search**: Search for any stock/ETF
4. Click **Select** on your choice

## Step 4: Review Market Data

At the top of Page 1, you'll see **real-time market data**:
- **Forex rates** (EUR, GBP, JPY, CHF vs USD)
- **Commodities** (Gold, Silver, Oil)
- **Bonds** (US 10Y Treasury)
- **Major indexes** (S&P 500, Nasdaq, DAX, etc.)

This updates automatically every 5 seconds with color-coded changes.

## Step 5: Select Charts (Page 2)

1. **Switch to Page 2**: Click the **📈 Analysis Charts** tab

2. **Select charts** you want to generate:

   **For Beginners - Start with these 5:**
   ```
   ☑ 1. Portfolio Allocation
   ☑ 2. Correlation Matrix
   ☑ 4. Performance vs Benchmarks
   ☑ 13. VaR 95%
   ☑ 17. Sharpe Ratio
   ```

   **For Detailed Analysis - Add these:**
   ```
   ☑ 3. Risk Contribution
   ☑ 5. Sector Decomposition
   ☑ 7. Monte Carlo (Normal)
   ☑ 14. Expected Shortfall
   ☑ 18. Risk vs Indexes
   ```

   **For Complete Analysis:**
   - Click **All** button to select all 24 charts

3. **Quick selection tips:**
   - **All** button: Select everything
   - **None** button: Deselect everything
   - Individual checkboxes: Pick specific charts

## Step 6: Run Analysis

1. Click the large green button at the bottom:
   ```
   ▶ Run Portfolio Analysis
   ```

2. **Wait for completion**:
   - Progress shown in window title
   - Takes 30 seconds to 2 minutes depending on:
     - Number of tickers
     - Number of charts selected
     - Internet speed (for data download)

3. **Success!** 
   - Pop-up shows: "Complete! Charts saved to: results/..."
   - All charts saved as PNG files
   - Ready to view or share

## Example Session

### Quick 5-Ticker Portfolio

**Setup (2 minutes):**
```
Capital: 10000
Currency: USD

Tickers:
1. AAPL   - 20%
2. MSFT   - 20%
3. NVDA   - 20%
4. GOOGL  - 20%
5. TSLA   - 20%

Benchmarks:
1. ^GSPC  (S&P 500)
2. ^NDX   (Nasdaq 100)

Charts: Select "All" (24 charts)
```

**Result:**
- ✅ 24 professional charts generated
- ✅ Saved to `results/portfolio_YYYYMMDD_HHMMSS/`
- ✅ Ready for presentation or reporting

## Common Workflows

### Workflow 1: Stock Portfolio Analysis
```
Page 1:
├─ 5-10 individual stocks (AAPL, MSFT, etc.)
├─ Weights: Equal or custom
└─ Benchmarks: ^GSPC, ^NDX

Page 2:
├─ Portfolio & Sector (Charts 1-6)
├─ Risk Metrics (Charts 13-17)
└─ Benchmarks (Charts 18-21)
```

### Workflow 2: ETF Portfolio Analysis
```
Page 1:
├─ 3-5 ETFs (SPY, QQQ, GLD)
├─ Weights: Strategic allocation
└─ Benchmarks: ^GSPC, GC=F

Page 2:
├─ Portfolio Allocation (Chart 1)
├─ Correlation (Chart 2)
├─ Risk vs Indexes (Chart 18)
└─ Performance vs Benchmarks (Chart 4)
```

### Workflow 3: European Stock Analysis
```
Page 1:
├─ European tickers with suffixes
│  ├─ BNP.PA  (BNP Paribas - Euronext Paris)
│  ├─ SAN.MC  (Santander - Madrid)
│  └─ VOW3.DE (Volkswagen - Frankfurt)
├─ Weights: Custom
└─ Benchmarks: ^STOXX50E, ^GDAXI, ^FCHI

Page 2:
├─ All Portfolio & Sector charts
└─ Risk Metrics
```

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Switch tabs | `Ctrl+Tab` (Windows) / `Cmd+Tab` (Mac) |
| Run analysis | Focus on button, press `Enter` |
| Clear entry | `Ctrl+A` then `Delete` |
| Validate ticker | `Enter` (while in entry field) |

## Tips for Best Results

### ✅ DO:
1. **Validate all symbols** before running (wait for green ✓)
2. **Check total weight** equals 100%
3. **Use suffixes** for non-US stocks (`.PA`, `.L`, `.DE`)
4. **Start small** (5 tickers, 5 charts) for first run
5. **Save results** - charts are overwritten on next run

### ❌ DON'T:
1. **Don't mix currencies** without consideration
2. **Don't use invalid symbols** (wait for validation)
3. **Don't run with 0% weights** (set weights first)
4. **Don't close window** during analysis
5. **Don't select charts** you don't need (saves time)

## Troubleshooting

### Problem: "No tickers validated"
**Solution:** 
- Wait for green ✓ to appear after entering each ticker
- Check symbol is correct (e.g., `AAPL` not `APPLE`)
- Try adding exchange suffix (e.g., `AAPL.US`)

### Problem: "Total weight not 100%"
**Solution:**
- Click **Auto 100%** button to scale proportionally
- Or click **Equal** to distribute equally
- Or manually adjust weights

### Problem: "Benchmark not found"
**Solution:**
- Use Yahoo Finance format (e.g., `^GSPC` for S&P 500)
- Click 📋 button to browse available benchmarks
- Check spelling and prefix (usually `^` for indexes)

### Problem: Analysis is slow
**Solution:**
- Reduce number of charts selected
- Check internet connection
- Use fewer tickers (5-10 optimal)
- Close other applications

### Problem: Charts not displaying properly
**Solution:**
- Check `results/` folder for PNG files
- Update matplotlib: `pip install --upgrade matplotlib`
- Restart application

## What's Next?

### Explore More Features:
1. **Market Data**: Watch real-time price updates on Page 1
2. **ISIN Support**: Try entering ISINs (e.g., `US0378331005` for Apple)
3. **Benchmark Browser**: Explore the visual benchmark selector
4. **Chart Descriptions**: Read tooltips on each chart
5. **Multiple Runs**: Compare different portfolio allocations

### Advanced Topics:
- **Custom Benchmarks**: Use any stock/ETF as a benchmark
- **International Portfolios**: Mix stocks from different exchanges
- **Sector Analysis**: See how sector charts work with diverse portfolios
- **Risk Analysis**: Deep dive into VaR, Sharpe, and Calmar ratios

## Support

### Need Help?
1. **Documentation**: Check `_docs/` folder for detailed guides
2. **Examples**: Look in `results/` for sample outputs
3. **Code**: Review `ui/menu_principal_v4.py` for implementation

### Report Issues:
- Include: Tickers used, error message, screenshots
- Check: `test_generate_charts.py` works
- Verify: Dependencies installed (`pip install -r requirements.txt`)

## Summary

**In 5 steps:**
1. Launch app (`python app.py`)
2. Enter tickers and weights (Page 1)
3. Select benchmarks (Page 1)
4. Choose charts (Page 2)
5. Click **Run Analysis**

**That's it!** You now have professional portfolio analysis charts ready to use.

---

**Version:** v4.0  
**Last Updated:** November 2024  
**Estimated Time:** 5-10 minutes for first analysis  
**Difficulty:** Beginner-friendly

Happy analyzing! 📊📈



