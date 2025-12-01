# chart_portfolio.py - Portfolio Analysis Charts (Charts 1-4)
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.utils_data import load_prices_from_dir, align_business_days, slice_recent_safe, bench_daily
from utils.utils_math import compute_portfolio_metrics
from utils.utils_plot import save_and_show, add_bar_labels, placeholder_figure, eur_fmt

# ---------- CHART FUNCTIONS ----------
def plot_allocation(w_series: pd.Series, start_capital, ticker_info=None):
    """
    Chart 1: Portfolio Allocation with professional design
    
    Args:
        w_series: Portfolio weights
        start_capital: Total portfolio capital
        ticker_info: Dict with ticker info {ticker: {'name': str, 'currency': str}}
    """
    # Professional color palette (10 colors with good contrast)
    colors = [
        '#4A90E2',  # Blue
        '#F5A623',  # Orange
        '#7ED321',  # Green
        '#D0021B',  # Red
        '#9013FE',  # Purple
        '#50E3C2',  # Teal
        '#F8E71C',  # Yellow
        '#BD10E0',  # Magenta
        '#417505',  # Dark Green
        '#B8E986',  # Light Green
    ]
    
    # Create figure with good spacing
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Prepare data
    weights = list(w_series.values)
    tickers = list(w_series.keys())
    
    # Build labels with company name, percentage, and amount with currency
    labels = []
    for ticker, weight in zip(tickers, weights):
        # Get company name and currency if available
        if ticker_info and ticker in ticker_info:
            info = ticker_info[ticker]
            company_name = info.get('name', ticker)
            currency = info.get('currency', 'EUR')
            
            # Currency symbols
            currency_symbols = {
                'USD': '$', 'EUR': '€', 'GBP': '£', 'CHF': 'CHF', 
                'JPY': '¥', 'CAD': 'C$', 'AUD': 'A$', 'HKD': 'HK$'
            }
            symbol = currency_symbols.get(currency, currency)
        else:
            company_name = ticker
            symbol = '€'
        
        # Format amount
        amount = weight * start_capital
        
        # Create label with name (truncated if too long)
        if len(company_name) > 20:
            company_name = company_name[:17] + "..."
        
        label = f"{ticker}\n{company_name}\n{weight*100:.1f}% ({symbol}{amount:,.0f})"
        labels.append(label)
    
    # Create pie chart with better styling (slightly smaller radius)
    wedges, texts = ax.pie(
        weights,
        labels=labels,
        colors=colors[:len(weights)],
        startangle=90,
        counterclock=False,
        labeldistance=1.15,  # Move labels outside
        textprops={'fontsize': 9, 'weight': 'bold'},
        radius=0.85  # Slightly smaller circle (default is 1.0)
    )
    
    # Add subtle shadow/depth effect by drawing a slightly larger circle behind
    circle = plt.Circle((0, 0), 0.60, color='white', alpha=0.3, linewidth=2, 
                        fill=False, linestyle='--')
    ax.add_artist(circle)
    
    # Set title at top right corner - higher and closer
    ax.text(1.35, 1.25, "Portfolio Allocation", 
            fontsize=16, weight='bold', ha='right', va='top',
            transform=ax.transData)
    
    # Equal aspect ratio ensures circular pie
    ax.axis('equal')
    
    plt.tight_layout()
    return fig

def plot_correlation_green(corr: pd.DataFrame, order_cols, ticker_info=None):
    """Chart 2: Correlation Matrix - Professional Design"""
    c = corr.reindex(index=order_cols, columns=order_cols)
    
    # Prepare display labels (use company names if available)
    display_labels = []
    for col in order_cols:
        if ticker_info and col in ticker_info:
            name = ticker_info[col].get('name', col)
            # Use short names for correlation matrix
            if len(name) > 15:
                display_labels.append(col)  # Use ticker if name too long
            else:
                display_labels.append(name[:12])  # Truncate to 12 chars
        else:
            display_labels.append(col)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Professional colormap: Blue (negative) to Red (positive) with light transitions
    im = ax.imshow(c, vmin=-1, vmax=1, cmap="RdBu_r")
    
    # Colorbar styling
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.set_label("Correlation (ρ)", rotation=270, labelpad=20, fontsize=11, fontweight='bold')
    
    # Set ticks and labels
    ax.set_xticks(range(len(c.columns)))
    ax.set_xticklabels(display_labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(c.index)))
    ax.set_yticklabels(display_labels, fontsize=9)
    
    # Add correlation values
    for i in range(c.shape[0]):
        for j in range(c.shape[1]):
            val = c.iloc[i, j]
            # Choose text color for readability
            text_color = "white" if abs(val) > 0.6 else "black"
            ax.text(j, i, f"{val:.2f}",
                    ha="center", va="center",
                    color=text_color,
                    fontsize=9, fontweight='bold')
    
    # Title positioning (centered at top)
    ax.set_title("Asset Correlation Matrix", fontsize=14, fontweight='bold', pad=20)
    
    fig.tight_layout()
    return fig

def plot_risk_contribution(cols, cr_pct, w_series, ticker_info=None):
    """Chart 3: Risk Contribution vs Weight - Professional Design"""
    s_rc = pd.Series(cr_pct, index=cols)*100
    s_w  = w_series[cols]*100
    order = s_rc.sort_values(ascending=False).index
    
    # Prepare display labels (use company names if available)
    display_labels = []
    for ticker in order:
        if ticker_info and ticker in ticker_info:
            name = ticker_info[ticker].get('name', ticker)
            # Use ticker + short name for clarity
            if len(name) > 20:
                display_labels.append(ticker)
            else:
                display_labels.append(f"{ticker}\n{name[:15]}")
        else:
            display_labels.append(ticker)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Professional colors
    risk_color = '#E74C3C'  # Red for risk
    weight_color = '#3498DB'  # Blue for weight
    
    # Create bars
    x_pos = np.arange(len(order))
    width = 0.38
    bars1 = ax.bar(x_pos - width/2, s_rc[order].values, width, 
                   label="Risk Contribution %", color=risk_color, alpha=0.8, edgecolor='black', linewidth=0.5)
    bars2 = ax.bar(x_pos + width/2, s_w[order].values, width, 
                   label="Weight %", color=weight_color, alpha=0.8, edgecolor='black', linewidth=0.5)
    
    # Set x-axis
    ax.set_xticks(x_pos)
    ax.set_xticklabels(display_labels, rotation=45, ha="right", fontsize=9)
    
    # Labels and title
    ax.set_ylabel("Percentage (%)", fontsize=11, fontweight='bold')
    ax.set_title("Risk Contribution vs Portfolio Weight", fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for bar in bars1:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
               f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    for bar in bars2:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
               f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # Legend
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)
    
    # Grid
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    return fig

def plot_perf_vs_benchmarks(bench_prices, port_ret_d, bench_def):
    """Chart 4: Portfolio vs Benchmarks — Professional Design"""
    series = {"Portfolio": (1+port_ret_d).cumprod()}
    for label, tick in bench_def:
        if tick in bench_prices.columns:
            series[label] = (1+bench_daily(bench_prices, tick)).cumprod()
    df = pd.concat(series, axis=1).dropna()
    if df.empty:
        return placeholder_figure("Portfolio vs Benchmarks — Indexed to 100 (historical)",
                                  "No common dates or benchmarks available.")
    df = df/df.iloc[0]*100
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Professional color palette
    colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', '#1ABC9C', '#34495E']
    
    # Plot each series with professional styling
    for i, (col, color) in enumerate(zip(df.columns, colors)):
        if col == "Portfolio":
            # Portfolio gets special treatment (thicker line)
            ax.plot(df.index, df[col], label=col, linewidth=3.5, color=color, alpha=0.9)
        else:
            # Benchmarks with thinner lines
            ax.plot(df.index, df[col], label=col, linewidth=2, color=color, alpha=0.7, linestyle='--')
    
    # Formatting
    ax.set_title("Portfolio Performance vs Benchmarks (Indexed to 100)", 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Date", fontsize=11, fontweight='bold')
    ax.set_ylabel("Index Value (100 = Start)", fontsize=11, fontweight='bold')
    
    # Grid and legend
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10)
    
    # Set y-axis to start at reasonable minimum
    y_min = max(0, df.min().min() * 0.95)
    ax.set_ylim(bottom=y_min)
    
    fig.tight_layout()
    return fig

# ---------- MAIN EXECUTION ----------
def generate_portfolio_charts(etf_prices, bench_prices, weights_raw, bench_def, start_capital, results_dir="./results", show_plots=True, selected_charts=None, ticker_info=None):
    """Generate Charts 1-4: Portfolio Analysis Charts.
    
    Args:
        selected_charts: List of chart numbers to generate (e.g., [1, 3]). If None, generates all.
        ticker_info: Dict with ticker info {ticker: {'name': str, 'currency': str}}
    """
    if selected_charts is None:
        selected_charts = [1, 2, 3, 4]
    
    print(f"=== PORTFOLIO ANALYSIS CHARTS (Selected: {selected_charts}) ===")
    
    # Compute metrics (always needed)
    res = compute_portfolio_metrics(etf_prices, weights_raw)
    print(f"Applied weights (available columns): {dict(res['w_series'].round(4))}")
    
    # Generate selected charts only
    if 1 in selected_charts:
        print("\nGenerating Chart 1: Portfolio Allocation...")
        fig = plot_allocation(res["w_series"], start_capital, ticker_info=ticker_info)
        save_and_show(fig, "01_portfolio_pie.png", results_dir, show_plots)
        plt.close(fig)
    
    if 2 in selected_charts:
        print("Generating Chart 2: Correlation Matrix...")
        fig = plot_correlation_green(res["corr"], res["cols"], ticker_info=ticker_info)
        save_and_show(fig, "02_correlation_matrix.png", results_dir, show_plots)
        plt.close(fig)
    
    if 3 in selected_charts:
        print("Generating Chart 3: Risk Contribution...")
        fig = plot_risk_contribution(res["cols"], res["cr_pct"], res["w_series"], ticker_info=ticker_info)
        save_and_show(fig, "03_risk_contribution.png", results_dir, show_plots)
        plt.close(fig)
    
    if 4 in selected_charts:
        print("Generating Chart 4: Performance vs Benchmarks...")
        fig = plot_perf_vs_benchmarks(bench_prices, res["port_ret_d"], bench_def)
        save_and_show(fig, "04_perf_vs_benchmarks.png", results_dir, show_plots)
        plt.close(fig)
    
    print(f"\n=== PORTFOLIO CHARTS COMPLETED ===")
    print(f"Annualized volatility (portfolio): {res['vol_a']:.2%}")
    
    return res  # Return metrics for use by other chart modules

def main():
    """Standalone execution for portfolio charts only."""
    print("=== RUNNING PORTFOLIO CHARTS ONLY ===")
    
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
    
    # Benchmarks
    BENCH_DEF = [
        ("US (NASDAQ)", "NQ1!"), ("EU (DAX)", "FDAX1!"), ("Spain (IBEX)", "IBEX35"),
        ("Italy (MIB)", "FTSEMIB"), ("Japan (Nikkei)", "NIY1!"), ("Gold", "GC1!"),
    ]
    
    try:
        # Load and prepare data
        etf_prices_raw = load_prices_from_dir(DATA_DIR)
        bench_prices_raw = load_prices_from_dir(BENCH_DIR)
        
        etf_prices = align_business_days(etf_prices_raw)
        bench_prices = align_business_days(bench_prices_raw)
        
        etf_prices = slice_recent_safe(etf_prices, ESTIMATION_YEARS)
        bench_prices = slice_recent_safe(bench_prices, ESTIMATION_YEARS)
        
        # Generate portfolio charts
        portfolio_metrics = generate_portfolio_charts(
            etf_prices, bench_prices, WEIGHTS_RAW, BENCH_DEF, 
            START_CAPITAL, RESULTS_DIR, True
        )
        
        print("Portfolio charts completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Portefeuille folder exists with ETF CSV files.")

if __name__ == "__main__":
    main()
