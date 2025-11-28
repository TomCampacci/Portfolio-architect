# 📁 Portfolio Analysis - Project Structure

## 🎯 Essential Files (Required for Application)

### **Main Application**
- `menu_principal.py` - Main application entry point and UI orchestrator
- `analysis_runner.py` - Runs portfolio analysis and generates charts
- `config.py` - Configuration settings and parameters

### **UI Components**
- `ui_builder.py` - UI component builder (panels, cards, layouts)
- `symbol_handler.py` - Symbol validation, autocomplete, ISIN conversion

### **Data & Analysis**
- `utils_data.py` - Data loading, Yahoo Finance integration, EU suffix resolution
- `utils_math.py` - Mathematical calculations (returns, volatility, correlations)
- `utils_plot.py` - Plotting utilities

### **Chart Generators**
- `chart_portfolio.py` - Portfolio allocation and composition charts
- `chart_benchmarks.py` - Benchmark comparison charts
- `chart_monte_carlo.py` - Monte Carlo simulation charts
- `chart_risk_metrics.py` - Risk metrics visualization
- `chart_sector.py` - Sector analysis charts
- `chart_sector_projection.py` - Sector projection charts
- `chart_regime.py` - Market regime analysis

### **Configuration Files**
- `weights.csv` - Portfolio ticker weights
- `benchmarks.csv` - Benchmark definitions
- `eu_suffix_cache.json` - European ticker suffix cache (auto-generated)

## 📊 Output Folders

### **results/**
Generated charts and analysis outputs (PNG files)

## 📚 Documentation & Backups (Not Required)

### **_docs/**
Detailed documentation about features and architecture
- See `_docs/README_DOCS.md` for details

### **_backup/**
Backup copies of previous versions

## 🚀 How to Run

```bash
python menu_principal.py
```

## 📦 Dependencies

Install required packages:
```bash
pip install pandas numpy matplotlib seaborn yfinance requests
```

## 🗂️ File Organization Philosophy

- **Root level**: Only essential files for running the application
- **_docs/**: Documentation (optional, informational only)
- **_backup/**: Old versions and backups (optional)
- **results/**: Generated output files
- **__pycache__/**: Python cache (auto-generated)

## ✅ Minimal Setup

To run the application, you only need:
1. All `.py` files in the root
2. `weights.csv` and `benchmarks.csv`
3. Python with required packages installed

Everything else is optional!

