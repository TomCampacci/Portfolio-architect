# chart_sector.py - Sector Analysis Charts (Charts 5-6)
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.utils_plot import save_and_show, placeholder_figure, eur_fmt

# ---------- SECTOR ANALYSIS FUNCTIONS ----------
def calculate_sector_decomposition(weights_series, sector_mapping):
    """Calculate portfolio sector decomposition."""
    sector_weights = {}
    
    for ticker, weight in weights_series.items():
        sector = sector_mapping.get(ticker, "Other")
        if sector in sector_weights:
            sector_weights[sector] += weight
        else:
            sector_weights[sector] = weight
    
    return pd.Series(sector_weights).sort_values(ascending=False)

def plot_sector_decomposition(sector_weights, sector_colors, start_capital, currency="USD"):
    """Chart 5: Portfolio Sector Decomposition - Professional Design"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Professional sector color palette (10 vibrant colors)
    professional_palette = [
        '#3498db',  # Bright Blue
        '#e74c3c',  # Vivid Red
        '#2ecc71',  # Emerald Green
        '#f39c12',  # Orange
        '#9b59b6',  # Purple
        '#1abc9c',  # Turquoise
        '#34495e',  # Dark Blue-Gray
        '#e67e22',  # Carrot Orange
        '#95a5a6',  # Light Gray
        '#c0392b',  # Dark Red
    ]
    
    # Enhanced sector color mapping with fallback to professional palette
    enhanced_colors = {
        "Technology": '#3498db',
        "US / Technology": '#3498db',
        "Healthcare": '#e74c3c',
        "Financials": '#2ecc71',
        "Financial Services": '#2ecc71',
        "Consumer Cyclical": '#f39c12',
        "Consumer Defensive": '#9b59b6',
        "Industrials": '#1abc9c',
        "Energy": '#e67e22',
        "Real Estate": '#34495e',
        "Materials": '#95a5a6',
        "Communication Services": '#c0392b',
        "Utilities": '#16a085',
        "Broad Market": '#8e44ad',
        "Europe": '#d35400',
        "Asia Pacific": '#c0392b',
        "Commodities": '#7f8c8d',
        "Other": '#bdc3c7',
        "Unknown": '#95a5a6',
    }
    
    # Prepare data
    sectors = sector_weights.index
    weights = sector_weights.values * 100
    
    # Assign colors: use enhanced_colors first, then sector_colors, then professional_palette
    colors = []
    for i, sector in enumerate(sectors):
        if sector in enhanced_colors:
            colors.append(enhanced_colors[sector])
        elif sector in sector_colors:
            colors.append(sector_colors[sector])
        else:
            colors.append(professional_palette[i % len(professional_palette)])
    
    # Currency symbol mapping
    currency_symbols = {
        "USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥", 
        "CHF": "CHF", "CAD": "C$", "AUD": "A$"
    }
    curr_symbol = currency_symbols.get(currency, currency)
    
    # Build labels with sector name, percentage, and amount with currency
    labels = []
    for sector, weight in zip(sectors, weights):
        amount = weight * start_capital / 100
        # Format sector name (remove unnecessary prefixes)
        clean_sector = sector.replace("US / ", "").replace("Consumer ", "C.")
        labels.append(f"{clean_sector}\n{weight:.1f}% ({curr_symbol}{amount:,.0f})")
    
    # Create pie chart with optimized radius
    wedges, texts = ax.pie(
        weights, 
        labels=labels, 
        colors=colors,
        startangle=90,
        labeldistance=1.15,
        textprops={'fontsize': 9, 'weight': 'bold'},
        radius=0.85
    )
    
    # Add subtle shadow/depth circle
    circle = plt.Circle((0, 0), 0.75, color='white', linewidth=1.5, fill=False, alpha=0.3)
    ax.add_artist(circle)
    
    # Title at top right corner (higher position, no overlap)
    ax.text(1.35, 1.25, 'Sector Allocation', 
           fontsize=16, fontweight='bold', 
           ha='right', va='top',
           transform=ax.transData)
    
    ax.axis('equal')
    fig.tight_layout()
    return fig

def plot_sector_risk_contribution(sector_weights, sector_colors, tickers, risk_contribution, sector_mapping):
    """Chart 6: Sector Weight vs Risk Contribution - Professional Design"""
    # Calculate sector risk contributions
    sector_risk = {}
    # Support both dict-like and array-like inputs cleanly
    if hasattr(risk_contribution, "items"):
        iterator = risk_contribution.items()
    else:
        iterator = zip(tickers, np.asarray(risk_contribution).ravel())
    for ticker, risk_contrib in iterator:
        sector = sector_mapping.get(ticker, "Other")
        if sector in sector_risk:
            sector_risk[sector] += float(risk_contrib)
        else:
            sector_risk[sector] = float(risk_contrib)
    
    sector_risk_series = pd.Series(sector_risk) * 100
    sector_weight_series = sector_weights * 100
    
    # Align series and sort by risk contribution
    common_sectors = sector_risk_series.index.intersection(sector_weight_series.index)
    sector_risk_aligned = sector_risk_series[common_sectors].sort_values(ascending=False)
    sector_weight_aligned = sector_weight_series[sector_risk_aligned.index]
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Professional colors
    weight_color = '#3498DB'  # Blue
    risk_color = '#E74C3C'    # Red
    
    x = np.arange(len(sector_risk_aligned))
    width = 0.4
    
    bars1 = ax.bar(x - width/2, sector_weight_aligned.values, width, 
                  label='Sector Weight %', color=weight_color, alpha=0.8, 
                  edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x + width/2, sector_risk_aligned.values, width,
                  label='Risk Contribution %', color=risk_color, alpha=0.8,
                  edgecolor='black', linewidth=0.5)
    
    # Labels and title
    ax.set_xlabel('Sectors', fontsize=11, fontweight='bold')
    ax.set_ylabel('Percentage (%)', fontsize=11, fontweight='bold')
    ax.set_title('Sector Weight vs Risk Contribution', fontsize=14, fontweight='bold', pad=20)
    
    # X-axis
    ax.set_xticks(x)
    ax.set_xticklabels(sector_risk_aligned.index, rotation=45, ha='right', fontsize=10)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        if height > 0.5:  # Only show label if bar is visible enough
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    for bar in bars2:
        height = bar.get_height()
        if height > 0.5:  # Only show label if bar is visible enough
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{height:.1f}%', ha='center', va='bottom', fontsize=8, fontweight='bold')
    
    # Legend and grid
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=10)
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    return fig

def generate_sector_charts(portfolio_metrics, sector_mapping, sector_colors, start_capital, results_dir="./results", show_plots=True, selected_charts=None, currency="USD"):
    """Generate Charts 5-6: Sector Analysis Charts.
    
    Args:
        selected_charts: List of chart numbers to generate (e.g., [5]). If None, generates all.
        currency: Portfolio currency (USD, EUR, GBP, etc.)
    """
    if selected_charts is None:
        selected_charts = [5, 6]
    
    print(f"=== SECTOR ANALYSIS CHARTS (Selected: {selected_charts}) ===")
    
    # Calculate sector decomposition (always needed)
    sector_weights = calculate_sector_decomposition(portfolio_metrics["w_series"], sector_mapping)
    
    if 5 in selected_charts:
        print("\nGenerating Chart 5: Sector Decomposition...")
        fig = plot_sector_decomposition(sector_weights, sector_colors, start_capital, currency=currency)
        save_and_show(fig, "05_sector_decomposition.png", results_dir, show_plots)
        plt.close(fig)
    
    if 6 in selected_charts:
        print("Generating Chart 6: Sector Risk Contribution...")
        fig = plot_sector_risk_contribution(sector_weights, sector_colors, portfolio_metrics["cols"], portfolio_metrics["cr_pct"], sector_mapping)
        save_and_show(fig, "06_sector_risk_contribution.png", results_dir, show_plots)
        plt.close(fig)
    
    print("=== SECTOR CHARTS COMPLETED ===")
    
    return sector_weights

def main():
    """Standalone execution for sector charts only."""
    print("=== RUNNING SECTOR CHARTS ONLY ===")
    
    # Import here to avoid circular imports
    from utils.utils_data import load_prices_from_dir, align_business_days, slice_recent_safe
    from utils.utils_math import compute_portfolio_metrics
    
    # Configuration (same as main.py)
    DATA_DIR = r"C:\Users\CAMPACCI\Desktop\Portefeuille"
    BENCH_DIR = os.path.join(DATA_DIR, "Benchmarks")
    RESULTS_DIR = r"./results"
    ESTIMATION_YEARS = 3
    START_CAPITAL = 10_000
    
    # Portfolio weights
    WEIGHTS_RAW = {
        "ANXU":0.20, "NVDA":0.07, "PLTR":0.07, "IUS2":0.06, "BNK": 0.13,
        "CS1": 0.07, "MIB": 0.07, "CNKY":0.07, "GLDA":0.13, "CG1": 0.13,
    }
    
    # Sector mapping
    SECTOR_MAPPING = {
        "ANXU": "US / Technology", "NVDA": "US / Technology", "PLTR": "US / Technology",
        "IUS2": "Broad Market", "BNK": "Financials", "CS1": "Europe",
        "MIB": "Europe", "CNKY": "Asia Pacific", "GLDA": "Commodities", "CG1": "Europe",
    }
    
    SECTOR_COLORS = {
        "US / Technology": "#1f77b4", "Broad Market": "#ff7f0e", "Financials": "#2ca02c",
        "Europe": "#d62728", "Asia Pacific": "#9467bd", "Commodities": "#8c564b",
    }
    
    try:
        # Load and prepare data
        etf_prices_raw = load_prices_from_dir(DATA_DIR)
        etf_prices = align_business_days(etf_prices_raw)
        etf_prices = slice_recent_safe(etf_prices, ESTIMATION_YEARS)
        
        # Compute portfolio metrics
        portfolio_metrics = compute_portfolio_metrics(etf_prices, WEIGHTS_RAW)
        
        # Generate sector charts
        sector_weights = generate_sector_charts(
            portfolio_metrics, SECTOR_MAPPING, SECTOR_COLORS, 
            START_CAPITAL, RESULTS_DIR, True
        )
        
        print("Sector charts completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Portefeuille folder exists with ETF CSV files.")

if __name__ == "__main__":
    main()
