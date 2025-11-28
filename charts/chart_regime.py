# chart_regime.py - Regime Analysis Charts (Charts 19-20)
import os
import numpy as np
import matplotlib.pyplot as plt
from utils.utils_math import mc_single_asset, compute_median_monthly_returns
from utils.utils_plot import save_and_show, eur_fmt

def simulate_regime_performance(paths_portfolio, bench_params, mc_paths, mc_steps, start_capital):
    """Simulate portfolio performance in different market regimes using MC."""
    if not bench_params:
        return {}
    
    # Define realistic market regimes with specific characteristics
    regimes = {
        "Bull Market": {
            "description": "Strong growth, low volatility",
            "tech_mult": 1.8,      # Tech outperforms in bull markets
            "eu_mult": 1.2,        # Europe moderate growth
            "fin_mult": 1.4,       # Financials benefit from growth
            "comm_mult": 0.9,      # Commodities lag in pure bull
            "asia_mult": 1.3,      # Asia benefits from growth
            "broad_mult": 1.5      # Broad market strong
        },
        "Bear Market": {
            "description": "Declining markets, high volatility", 
            "tech_mult": 0.3,      # Tech crashes hardest
            "eu_mult": 0.6,        # Europe declines moderately
            "fin_mult": 0.4,       # Financials hit hard
            "comm_mult": 0.7,      # Commodities defensive
            "asia_mult": 0.5,      # Asia declines
            "broad_mult": 0.4      # Broad market declines
        },
        "Sideways Market": {
            "description": "Low growth, low volatility",
            "tech_mult": 0.8,      # Tech struggles without growth
            "eu_mult": 1.0,        # Europe stable
            "fin_mult": 0.9,       # Financials struggle
            "comm_mult": 1.1,      # Commodities slightly positive
            "asia_mult": 0.9,      # Asia struggles
            "broad_mult": 0.9      # Broad market flat
        },
        "Volatile Market": {
            "description": "High volatility, mixed returns",
            "tech_mult": 1.1,      # Tech volatile but positive
            "eu_mult": 0.8,        # Europe struggles with volatility
            "fin_mult": 0.7,       # Financials hurt by volatility
            "comm_mult": 1.3,      # Commodities benefit from volatility
            "asia_mult": 0.9,      # Asia mixed
            "broad_mult": 1.0      # Broad market neutral
        }
    }
    
    # Get base portfolio parameters
    base_mu = np.median(compute_median_monthly_returns(paths_portfolio)) * 12  # Annualized
    base_vol = np.std(compute_median_monthly_returns(paths_portfolio)) * np.sqrt(12)  # Annualized
    
    regime_results = {}
    
    for regime_name, multipliers in regimes.items():
        # Calculate regime-specific portfolio return based on sector composition
        sector_weights = {
            "US / Technology": 0.34,    # ANXU, NVDA, PLTR
            "Europe": 0.27,             # CS1, MIB, CG1  
            "Financials": 0.13,         # BNK
            "Commodities": 0.13,        # GLDA
            "Asia Pacific": 0.07,        # CNKY
            "Broad Market": 0.06         # IUS2
        }
        
        # Calculate weighted regime multiplier
        regime_mult = (
            sector_weights["US / Technology"] * multipliers["tech_mult"] +
            sector_weights["Europe"] * multipliers["eu_mult"] +
            sector_weights["Financials"] * multipliers["fin_mult"] +
            sector_weights["Commodities"] * multipliers["comm_mult"] +
            sector_weights["Asia Pacific"] * multipliers["asia_mult"] +
            sector_weights["Broad Market"] * multipliers["broad_mult"]
        )
        
        # Adjust portfolio parameters for regime
        regime_mu = base_mu * regime_mult
        regime_vol = base_vol * (1.2 if "Volatile" in regime_name else 1.0)
        
        # Generate regime-specific portfolio paths
        regime_port_paths = mc_single_asset(regime_mu, regime_vol, start_capital, mc_steps, mc_paths)
        
        regime_results[regime_name] = {
            "paths": regime_port_paths,
            "regime_mult": regime_mult,
            "description": multipliers["description"],
            "expected_return": regime_mu,
            "expected_vol": regime_vol
        }
    
    return regime_results

def plot_regime_performance_comparison(regime_results, start_capital):
    """Chart 23: Portfolio Performance Across Market Regimes - Professional Design"""
    fig, ax = plt.subplots(figsize=(14, 8))

    # Professional colors for regimes
    regime_colors = {
        "Bull Market": "#27AE60",      # Green for growth
        "Bear Market": "#E74C3C",      # Red for decline
        "Sideways Market": "#F39C12",  # Orange for neutral
        "Volatile Market": "#9B59B6"   # Purple for volatility
    }

    for regime_name, data in regime_results.items():
        paths = data["paths"]
        median_path = np.median(paths, axis=1)
        
        color = regime_colors.get(regime_name, "#95A5A6")
        ax.plot(median_path, color=color, lw=3.5, alpha=0.85,
               label=f"{regime_name} (×{data['regime_mult']:.2f})")

    # Add initial capital reference line
    ax.axhline(start_capital, color="#2C3E50", ls="--", lw=2, 
              label=f"Initial Capital ({start_capital:,.0f})", zorder=5)

    # Labels and title
    ax.set_xlabel("Time (Months)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Portfolio Value", fontsize=11, fontweight='bold')
    ax.yaxis.set_major_formatter(eur_fmt)
    ax.set_title('Portfolio Performance Across Market Regimes (3-Year Projection)\nBased on Sector-Weighted Analysis', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Legend and grid
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10, ncol=2)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig


def generate_regime_charts(mc_results, bench_params, mc_paths, mc_steps, start_capital, 
                         results_dir="./results", show_plots=True, selected_charts=None):
    """Generate Chart 23: Regime Analysis Chart.
    
    Args:
        selected_charts: List of chart numbers to generate (e.g., [23]). If None, generates all.
    """
    if selected_charts is None:
        selected_charts = [23]
    
    print(f"=== REGIME ANALYSIS CHART (Selected: {selected_charts}) ===")
    
    # Chart 23: Regime Performance Comparison
    if 23 in selected_charts:
        # Simulate regime performance
        regime_results = simulate_regime_performance(
            mc_results["paths_normal"], bench_params, mc_paths, mc_steps, start_capital
        )
        
        if not regime_results:
            print("No regime results available - skipping regime charts")
            return {}
        
        print("\nGenerating Chart 23: Regime Performance Comparison...")
        fig = plot_regime_performance_comparison(regime_results, start_capital)
        save_and_show(fig, "23_regime_performance_comparison.png", results_dir, show_plots)
        plt.close(fig)
        
        print("=== REGIME CHART COMPLETED ===")
        return regime_results
    
    return {}

def main():
    """Standalone execution for regime chart only."""
    print("=== RUNNING REGIME CHART ONLY ===")
    
    # Import here to avoid circular imports
    from utils.utils_data import load_prices_from_dir, align_business_days, slice_recent_safe
    from utils.utils_math import compute_portfolio_metrics, compute_benchmark_params
    from chart_monte_carlo import generate_monte_carlo_charts
    
    # Configuration
    DATA_DIR = r"C:\Users\CAMPACCI\Desktop\Portefeuille"
    BENCH_DIR = os.path.join(DATA_DIR, "Benchmarks")
    RESULTS_DIR = r"./results"
    ESTIMATION_YEARS = 3
    START_CAPITAL = 10_000
    MC_PATHS = 50_000
    MC_STEPS = 36
    ANNUALIZATION = 252
    
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
        
        # Compute portfolio metrics
        portfolio_metrics = compute_portfolio_metrics(etf_prices, WEIGHTS_RAW)
        
        # Compute benchmark parameters
        bench_params = compute_benchmark_params(bench_prices, BENCH_DEF, ANNUALIZATION)
        
        # Generate Monte Carlo results first
        mc_results = generate_monte_carlo_charts(
            portfolio_metrics, MC_PATHS, MC_STEPS, 0.30, 
            START_CAPITAL, ANNUALIZATION, 12, True, 
            RESULTS_DIR, False  # Don't show plots for MC, we'll show regime
        )
        
        # Generate regime chart
        regime_results = generate_regime_charts(
            mc_results, bench_params, MC_PATHS, MC_STEPS, START_CAPITAL, 
            RESULTS_DIR, True
        )
        
        print("Regime chart completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Portefeuille folder exists with ETF CSV files.")

if __name__ == "__main__":
    main()
