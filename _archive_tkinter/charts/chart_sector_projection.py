# chart_sector_projection.py - Sector Projection Charts (Charts 17-18)
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.utils_math import mc_gaussian
from utils.utils_plot import save_and_show

# Comprehensive sector colors mapping (GICS sectors + common categories)
COMPREHENSIVE_SECTOR_COLORS = {
    # GICS Sectors
    "Technology": "#1f77b4",
    "Healthcare": "#ff7f0e",
    "Financials": "#2ca02c",
    "Consumer Discretionary": "#d62728",
    "Consumer Staples": "#9467bd",
    "Industrials": "#8c564b",
    "Energy": "#e377c2",
    "Materials": "#7f7f7f",
    "Communication Services": "#bcbd22",
    "Utilities": "#17becf",
    "Real Estate": "#aec7e8",
    # Alternative names and categories
    "Consumer Cyclical": "#d62728",  # Same as Consumer Discretionary
    "Information Technology": "#1f77b4",  # Same as Technology
    "Telecommunication Services": "#bcbd22",  # Same as Communication Services
    "Financial Services": "#2ca02c",  # Same as Financials
    # Commodities and other
    "Commodities": "#DDA0DD",
    "Broad Market": "#4ECDC4",
    "US / Technology": "#FF6B6B",
    "Europe": "#96CEB4",
    "Asia Pacific": "#FFEAA7",
    # Default fallback
    "Unknown": "#999999",
    "Other": "#666666"
}

def ensure_comprehensive_sector_detection(tickers, sector_mapping):
    """
    Ensure all tickers have sector information by querying Yahoo Finance if needed.

    Args:
        tickers: List of ticker symbols
        sector_mapping: Current sector mapping dict

    Returns:
        dict: Enhanced sector mapping with all tickers covered
    """
    from utils.utils_data import detect_asset_sector

    enhanced_mapping = sector_mapping.copy()
    sectors_found = set()

    print(f"🔍 Vérification des secteurs pour {len(tickers)} tickers...")

    for ticker in tickers:
        if ticker not in enhanced_mapping:
            print(f"  📊 Détection automatique du secteur pour {ticker}...")
            sector = detect_asset_sector(ticker, manual_mapping=None, default_sector="Unknown")
            enhanced_mapping[ticker] = sector
            sectors_found.add(sector)
            print(f"    ✅ {ticker} → {sector}")

    unique_sectors = set(enhanced_mapping.values())
    print(f"📈 Total secteurs détectés: {len(unique_sectors)}")
    print(f"   Secteurs: {sorted(unique_sectors)}")

    return enhanced_mapping

def build_sector_weight_vectors(all_tickers, sector_mapping):
    """Return dict: sector -> normalized weight vector over all_tickers (zeros elsewhere)."""
    sector_to_indices = {}
    for idx, t in enumerate(all_tickers):
        sector = sector_mapping.get(t, "Other")
        sector_to_indices.setdefault(sector, []).append(idx)

    sector_weight_vectors = {}
    n = len(all_tickers)
    for sector, indices in sector_to_indices.items():
        w = np.zeros(n)
        if len(indices) > 0:
            w[indices] = 1.0 / len(indices)
        sector_weight_vectors[sector] = w
    return sector_weight_vectors

def simulate_sector_paths(mu_a, cov_a, tickers, sector_mapping, start_capital, mc_steps, mc_paths, month_factor):
    """Simulate MC paths for each sector using equal weights within sector."""
    sector_w_vecs = build_sector_weight_vectors(tickers, sector_mapping)
    sector_paths = {}
    for sector, w in sector_w_vecs.items():
        # Skip sectors with no assets
        if np.allclose(w.sum(), 0):
            continue
        sector_paths[sector] = mc_gaussian(mu_a, cov_a, w, start_capital, mc_steps, mc_paths, month_factor)
    return sector_paths

def compute_sector_risk_return(sector_paths, mc_steps):
    """Compute median annualized return (CAGR) and annualized vol for each sector from MC paths."""
    sector_stats = {}
    for sector, paths in sector_paths.items():
        # Compute per-path CAGR over the full horizon
        end_vals = paths[-1, :]
        cagr = (end_vals / paths[0, 0])**(1.0 / (mc_steps / 12.0)) - 1.0
        # Compute per-path monthly returns then annualize volatility
        monthly_rets = paths[1:, :] / paths[:-1, :] - 1.0
        vol_ann_per_path = monthly_rets.std(axis=0) * np.sqrt(12.0)
        sector_stats[sector] = {
            "cagr_median": np.median(cagr),
            "vol_median": np.median(vol_ann_per_path),
            "cagr_all": cagr
        }
    return sector_stats

def plot_sector_risk_return_projection(sector_stats, sector_portfolio_weights, sector_colors, portfolio_median_cagr=None):
    """Chart 17: Sector Risk-Return Projection (3 Years)"""
    fig, ax = plt.subplots(figsize=(10, 7))
    sectors = list(sector_stats.keys())
    x = [sector_stats[s]["vol_median"]*100 for s in sectors]
    y = [sector_stats[s]["cagr_median"]*100 for s in sectors]
    sizes = [max(sector_portfolio_weights.get(s, 0.0), 0.0)*2000 for s in sectors]

    # Determine colors (blue for leaders, light red for laggards)
    base_blue = "#1f77b4"
    light_red = "#f28e8e"
    c = []
    for yy in y:
        if portfolio_median_cagr is None or yy >= portfolio_median_cagr*100:
            c.append(base_blue)
        else:
            c.append(light_red)

    ax.scatter(x, y, s=sizes, c=c, alpha=0.75, edgecolors='black', linewidths=0.8)
    for i, s in enumerate(sectors):
        ax.text(x[i]+0.3, y[i], s, fontsize=9, va='center')

    if portfolio_median_cagr is not None:
        ax.axhline(portfolio_median_cagr*100, color=base_blue, linestyle='--', linewidth=1.2, alpha=0.5, label='Portfolio Median CAGR')

    ax.set_xlabel('Projected Volatility (annualized, %)', fontsize=12)
    ax.set_ylabel('Projected Return (annualized, %)', fontsize=12)
    ax.set_title('Sector Risk-Return Projection (3 Years, Median MC)', fontsize=14, fontweight='bold', pad=16)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left')
    fig.tight_layout()
    return fig

def plot_sector_performance_distribution(sector_stats, sector_colors, portfolio_paths, mc_steps):
    """Chart 22: Sector Performance Distribution - Professional Design"""
    # Prepare stats
    rows = []
    for sector, stats in sector_stats.items():
        cagr_pct = stats["cagr_all"] * 100
        rows.append({
            "sector": sector,
            "p10": np.percentile(cagr_pct, 10),
            "p25": np.percentile(cagr_pct, 25),
            "p50": np.percentile(cagr_pct, 50),
            "p75": np.percentile(cagr_pct, 75),
            "p90": np.percentile(cagr_pct, 90),
        })
    # Sort by median
    rows.sort(key=lambda r: r["p50"], reverse=True)

    sectors = [r["sector"] for r in rows]
    medians = [r["p50"] for r in rows]
    p25 = [r["p25"] for r in rows]
    p75 = [r["p75"] for r in rows]
    p10 = [r["p10"] for r in rows]
    p90 = [r["p90"] for r in rows]

    # Portfolio reference
    port_end_vals = portfolio_paths[-1, :]
    port_cagr = (port_end_vals / portfolio_paths[0, 0])**(1.0 / (mc_steps / 12.0)) - 1.0
    port_median = np.median(port_cagr) * 100

    fig, ax = plt.subplots(figsize=(14, 8))

    y = np.arange(len(sectors))
    
    # Professional color scheme
    for i, sector in enumerate(sectors):
        color = COMPREHENSIVE_SECTOR_COLORS.get(sector, "#999999")
        # IQR band (thick)
        ax.hlines(y[i], p25[i], p75[i], colors=color, linewidth=12, alpha=0.6, label=None)
        # 10–90 whiskers (thin)
        ax.hlines(y[i], p10[i], p90[i], colors=color, linewidth=3, alpha=0.8, label=None)
    
    # Median markers
    ax.plot(medians, y, "o", color="#2C3E50", markersize=8, markeredgewidth=2, 
            markeredgecolor='white', label="Sector Median", zorder=10)

    # Portfolio median line
    ax.axvline(port_median, color='#E74C3C', linestyle='--', linewidth=3, 
              label=f'Portfolio Median: {port_median:.1f}%', zorder=5)

    # Labels and styling
    ax.set_yticks(y)
    ax.set_yticklabels(sectors, fontsize=10)
    ax.set_xlabel('Projected 3-Year CAGR (%)', fontsize=11, fontweight='bold')
    ax.set_title('Sector Performance Distribution (3-Year MC Projection)', 
                fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.legend(loc='lower right', frameon=True, fancybox=True, shadow=True, fontsize=10)
    
    fig.tight_layout()
    return fig

def plot_sector_rotation_analysis():
    """Chart 24: Sector Rotation Analysis - Professional Design"""
    fig, ax = plt.subplots(figsize=(14, 9))
    
    # Define market regimes and sector performance multipliers
    regimes = ["Bull Market", "Bear Market", "Sideways", "Volatile"]
    sectors = ["Technology", "Europe", "Financials", "Commodities", "Asia Pacific", "Broad Market"]
    
    # Realistic sector rotation data based on historical patterns
    rotation_data = {
        "Technology": [1.8, 0.3, 0.8, 1.1],      # Tech: Strong in bull, crashes in bear
        "Europe": [1.2, 0.6, 1.0, 0.8],          # Europe: Moderate performance
        "Financials": [1.4, 0.4, 0.9, 0.7],      # Financials: Cyclical
        "Commodities": [0.9, 0.7, 1.1, 1.3],     # Commodities: Defensive, volatile
        "Asia Pacific": [1.3, 0.5, 0.9, 0.9],    # Asia: Growth-dependent
        "Broad Market": [1.5, 0.4, 0.9, 1.0],    # Broad: Market beta
    }
    
    # Create heatmap data
    heatmap_data = []
    for sector in sectors:
        heatmap_data.append(rotation_data[sector])
    heatmap_data = np.array(heatmap_data)
    
    # Create professional heatmap
    im = ax.imshow(heatmap_data, cmap='RdYlGn', aspect='auto', vmin=0.2, vmax=2.0)
    
    # Set ticks and labels
    ax.set_xticks(range(len(regimes)))
    ax.set_yticks(range(len(sectors)))
    ax.set_xticklabels(regimes, fontsize=11, fontweight='bold')
    ax.set_yticklabels(sectors, fontsize=11, fontweight='bold')
    
    # Add text annotations with better formatting
    for i in range(len(sectors)):
        for j in range(len(regimes)):
            value = heatmap_data[i, j]
            # Choose text color for readability
            color = 'white' if value < 1.0 else 'black'
            ax.text(j, i, f'{value:.2f}×', ha='center', va='center', 
                   color=color, fontweight='bold', fontsize=12)
    
    # Add professional colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.85, pad=0.02)
    cbar.set_label('Performance Multiplier', rotation=270, labelpad=25, 
                  fontsize=11, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)
    
    # Labels and title
    ax.set_xlabel('Market Regimes', fontsize=11, fontweight='bold')
    ax.set_ylabel('Portfolio Sectors', fontsize=11, fontweight='bold')
    ax.set_title('Sector Rotation Analysis — Performance Across Market Regimes', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add gridlines for clarity
    ax.set_xticks(np.arange(len(regimes)) - 0.5, minor=True)
    ax.set_yticks(np.arange(len(sectors)) - 0.5, minor=True)
    ax.grid(which='minor', color='white', linestyle='-', linewidth=2)
    
    fig.tight_layout()
    return fig

def generate_sector_projection_charts(portfolio_metrics, sector_mapping, sector_colors, mc_paths, 
                                    mc_steps, start_capital, month_factor, portfolio_paths_normal, results_dir="./results", show_plots=True, selected_charts=None):
    """Generate Charts 21, 23: Sector Projection Charts.
    
    Args:
        selected_charts: List of chart numbers to generate (e.g., [21]). If None, generates all.
    """
    if selected_charts is None:
        selected_charts = [21, 23]
    
    print(f"=== SECTOR PROJECTION CHARTS (Selected: {selected_charts}) ===")

    # Ensure comprehensive sector detection for all tickers
    if any(chart in selected_charts for chart in [21, 23]):
        all_tickers = list(portfolio_metrics["cols"])
        sector_mapping = ensure_comprehensive_sector_detection(all_tickers, sector_mapping)

    # Simulate sector paths (needed for chart 21)
    sector_paths = None
    sector_stats = None
    if 21 in selected_charts:
        sector_paths = simulate_sector_paths(
            portfolio_metrics["mu_a"], portfolio_metrics["cov_a"], portfolio_metrics["cols"],
            sector_mapping, start_capital, mc_steps, mc_paths, month_factor
        )
        sector_stats = compute_sector_risk_return(sector_paths, mc_steps)
    
    # Chart 22: Sector Performance Distribution
    if 22 in selected_charts:
        print("Generating Chart 22: Sector Performance Distribution...")
        fig = plot_sector_performance_distribution(sector_stats, sector_colors, portfolio_paths_normal, mc_steps)
        save_and_show(fig, "22_sector_performance_distribution_mc.png", results_dir, show_plots)
        plt.close(fig)
    
    # Chart 24: Sector Rotation Analysis
    if 24 in selected_charts:
        print("Generating Chart 24: Sector Rotation Analysis...")
        fig = plot_sector_rotation_analysis()
        save_and_show(fig, "24_sector_rotation_analysis.png", results_dir, show_plots)
        plt.close(fig)
    
    print("=== SECTOR PROJECTION CHARTS COMPLETED ===")
    
    return sector_stats

def main():
    """Standalone execution for sector projection charts only."""
    print("=== RUNNING SECTOR PROJECTION CHARTS ONLY ===")
    
    # Import here to avoid circular imports
    from utils.utils_data import load_prices_from_dir, align_business_days, slice_recent_safe
    from utils.utils_math import compute_portfolio_metrics
    from chart_monte_carlo import generate_monte_carlo_charts
    
    # Configuration
    DATA_DIR = r"C:\Users\CAMPACCI\Desktop\Portefeuille"
    RESULTS_DIR = r"./results"
    ESTIMATION_YEARS = 3
    START_CAPITAL = 10_000
    MC_PATHS = 50_000
    MC_STEPS = 36
    ANNUALIZATION = 252
    MONTH_FACTOR = 12
    
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
        
        # Generate Monte Carlo results first
        mc_results = generate_monte_carlo_charts(
            portfolio_metrics, MC_PATHS, MC_STEPS, 0.30, 
            START_CAPITAL, ANNUALIZATION, MONTH_FACTOR, True, 
            RESULTS_DIR, False  # Don't show plots for MC, we'll show projections
        )
        
        # Generate sector projection charts
        sector_stats = generate_sector_projection_charts(
            portfolio_metrics, SECTOR_MAPPING, SECTOR_COLORS, MC_PATHS, 
            MC_STEPS, START_CAPITAL, MONTH_FACTOR, mc_results["paths_normal"], RESULTS_DIR, True
        )
        
        print("Sector projection charts completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Portefeuille folder exists with ETF CSV files.")

if __name__ == "__main__":
    main()
