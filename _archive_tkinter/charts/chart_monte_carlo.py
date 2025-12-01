# chart_monte_carlo.py - Monte Carlo Simulation Charts (Charts 7-8)
import numpy as np
import matplotlib.pyplot as plt
from utils.utils_math import mc_gaussian, mc_gaussian_with_randomness
from utils.utils_plot import save_and_show, eur_fmt

def plot_mc_paths(paths, median_path, p10_path, p90_path, approx_days, start_capital, plot_all_paths=True, with_randomness=False):
    """Chart 7-8: Monte Carlo Simulation Paths - Professional Design"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # NO normalization - use actual euro values
    # Color paths based on final outcome (below start_capital = losses, above = gains)
    final_values = paths[-1, :]
    positive_mask = final_values >= start_capital  # Gains (above initial capital)
    negative_mask = final_values < start_capital   # Losses (below initial capital)
    
    # Professional colors - RED below initial capital, BLUE above
    pos_color = '#3498DB'  # Blue for gains (paths above initial capital)
    neg_color = '#E74C3C'  # Red for losses (paths below initial capital)
    
    # Always sample 4000 paths for display (regardless of total paths)
    n_display = min(4000, paths.shape[1])
    pos_idx = np.where(positive_mask)[0]
    neg_idx = np.where(negative_mask)[0]
    
    # Calculate how many of each to sample (proportional)
    n_pos_display = int(n_display * len(pos_idx) / paths.shape[1])
    n_neg_display = n_display - n_pos_display
    
    # Plot paths with thicker lines for better visibility
    if len(pos_idx) > 0 and n_pos_display > 0:
        sample_pos = np.random.choice(pos_idx, size=min(n_pos_display, len(pos_idx)), replace=False)
        ax.plot(paths[:, sample_pos], alpha=0.10, color=pos_color, linewidth=0.8)
    if len(neg_idx) > 0 and n_neg_display > 0:
        sample_neg = np.random.choice(neg_idx, size=min(n_neg_display, len(neg_idx)), replace=False)
        ax.plot(paths[:, sample_neg], alpha=0.10, color=neg_color, linewidth=0.8)
    
    # Statistical paths with professional styling (actual values)
    ax.plot(median_path, color="#2C3E50", lw=3.5, label="Median (50th percentile)", zorder=10)
    ax.plot(p10_path, color="#E67E22", lw=2.5, ls="--", label="10th percentile (pessimistic)", zorder=9)
    ax.plot(p90_path, color="#27AE60", lw=2.5, ls="--", label="90th percentile (optimistic)", zorder=9)
    
    # Initial capital line at the actual starting value
    ax.axhline(start_capital, color="#95A5A6", ls="--", lw=2.5, label=f"Initial Capital ({start_capital:,.0f})", zorder=8)
    
    # Add reference lines: 50% below, 50% above, double
    ref_below = start_capital * 0.5  # 50% loss
    ref_above = start_capital * 1.5  # 50% gain
    ref_double = start_capital * 2.0  # 100% gain
    
    for ref_val in [ref_below, ref_above, ref_double]:
        ax.axhline(ref_val, color="#BDC3C7", ls=":", lw=1, alpha=0.3, zorder=3)
    
    # Add shaded regions to show gains/losses
    ax.axhspan(0, start_capital, alpha=0.05, color='red', zorder=1, label='Loss Zone (< Initial Capital)')
    ax.axhspan(start_capital, start_capital * 2, alpha=0.05, color='blue', zorder=1, label='Gain Zone (> Initial Capital)')
    
    # Dynamic title based on randomness
    randomness_text = "WITH 30% Randomness" if with_randomness else "Normal Distribution"
    ax.set_title(f"Monte Carlo Simulation — {randomness_text}\n{paths.shape[1]:,} Paths ({n_display:,} displayed) | {paths.shape[0]-1} Months (~{approx_days} Trading Days)", 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Time (Months)", fontsize=11, fontweight='bold')
    ax.set_ylabel(f"Portfolio Value (EUR)", fontsize=11, fontweight='bold')
    
    # Set y-axis limits: from 20% below to 100% above initial capital
    y_min = start_capital * 0.2  # 80% loss (show down to 20% of initial)
    y_max = start_capital * 2.0  # 100% gain (double)
    ax.set_ylim(y_min, y_max)
    
    # Format Y-axis with euro formatting (e.g., "50,000" instead of "50000")
    ax.yaxis.set_major_formatter(eur_fmt)
    
    # Legend and grid
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    return fig

def plot_projected_volatility(paths, month_factor, with_randomness=False):
    """Chart 9-10: Projected Volatility Distribution - Professional Design"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Calculate monthly returns for each path
    pr_m = paths[1:] / paths[:-1] - 1
    vol_ann_paths = np.std(pr_m, axis=0) * np.sqrt(month_factor)
    
    # Choose color and title based on randomness
    if with_randomness:
        color = '#E74C3C'  # Red for randomness
        title_suffix = "WITH 30% Randomness"
    else:
        color = '#3498DB'  # Blue for normal
        title_suffix = "Normal Distribution"
    
    # Create histogram with professional styling
    n, bins, patches = ax.hist(vol_ann_paths * 100, bins=70, alpha=0.8, 
                               color=color, edgecolor='black', linewidth=0.5)
    
    # Calculate statistics
    median_vol = np.median(vol_ann_paths * 100)
    mean_vol = np.mean(vol_ann_paths * 100)
    p10_vol = np.percentile(vol_ann_paths * 100, 10)
    p90_vol = np.percentile(vol_ann_paths * 100, 90)
    
    # Add statistical lines
    ax.axvline(median_vol, color="#2C3E50", lw=3, label=f"Median: {median_vol:.1f}%", linestyle='-')
    ax.axvline(mean_vol, color="#27AE60", lw=2, label=f"Mean: {mean_vol:.1f}%", linestyle='--')
    ax.axvline(p10_vol, color="#E67E22", lw=1.5, label=f"10th: {p10_vol:.1f}%", linestyle=':')
    ax.axvline(p90_vol, color="#E67E22", lw=1.5, label=f"90th: {p90_vol:.1f}%", linestyle=':')
    
    ax.set_title(f"Projected Volatility Distribution (3-Year MC) — {title_suffix}", 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Annualized Volatility (%)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Frequency (Number of Paths)", fontsize=11, fontweight='bold')
    
    # Legend and grid
    ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    return fig

def plot_projected_max_drawdown(paths, with_randomness=False):
    """Chart 11-12: Projected Max Drawdown Distribution - Professional Design"""
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Calculate max drawdown for each path
    def path_maxdd(v):
        peak = -np.inf
        mdd = 0
        for x in v:
            peak = max(peak, x)
            mdd = min(mdd, x / peak - 1)
        return mdd
    
    max_dd = [path_maxdd(paths[:, i]) for i in range(paths.shape[1])]
    max_dd_pct = np.array(max_dd) * 100
    
    # Choose color and title based on randomness
    if with_randomness:
        color = '#E74C3C'  # Red for randomness
        title_suffix = "WITH 30% Randomness"
    else:
        color = '#3498DB'  # Blue for normal
        title_suffix = "Normal Distribution"
    
    # Create histogram with professional styling
    n, bins, patches = ax.hist(max_dd_pct, bins=70, alpha=0.8, 
                               color=color, edgecolor='black', linewidth=0.5)
    
    # Calculate statistics
    median_dd = np.median(max_dd_pct)
    mean_dd = np.mean(max_dd_pct)
    p10_dd = np.percentile(max_dd_pct, 10)
    p90_dd = np.percentile(max_dd_pct, 90)
    
    # Add statistical lines (note: drawdowns are negative, so "better" is closer to 0)
    ax.axvline(median_dd, color="#2C3E50", lw=3, label=f"Median: {median_dd:.1f}%", linestyle='-')
    ax.axvline(mean_dd, color="#27AE60", lw=2, label=f"Mean: {mean_dd:.1f}%", linestyle='--')
    ax.axvline(p10_dd, color="#E67E22", lw=1.5, label=f"10th (worst): {p10_dd:.1f}%", linestyle=':')
    ax.axvline(p90_dd, color="#E67E22", lw=1.5, label=f"90th (best): {p90_dd:.1f}%", linestyle=':')
    
    ax.set_title(f"Projected Maximum Drawdown Distribution (3-Year MC) — {title_suffix}", 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Maximum Drawdown (%)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Frequency (Number of Paths)", fontsize=11, fontweight='bold')
    
    # Legend and grid
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    return fig

def generate_monte_carlo_charts(portfolio_metrics, mc_paths, mc_steps, randomness_factor, start_capital, 
                               annualization, month_factor, plot_all_paths=True, results_dir="./results", show_plots=True):
    """Generate Charts 7-12: Monte Carlo Simulation Charts."""
    print("=== MONTE CARLO SIMULATION CHARTS (7-12) ===")
    
    # Extract portfolio parameters
    mu_a = portfolio_metrics["mu_a"]
    cov_a = portfolio_metrics["cov_a"]
    w = portfolio_metrics["w"]
    
    approx_days = int(mc_steps * annualization / 12)
    
    # Chart 7: Normal Monte Carlo
    print("\nGenerating Chart 7: Monte Carlo (Standard Gaussian)...")
    print(f"   >> Simulating {mc_paths:,} paths with {mc_steps} steps...")
    paths_normal = mc_gaussian(mu_a, cov_a, w, start_capital, mc_steps, mc_paths, month_factor)
    print(f"   >> Generated paths shape: {paths_normal.shape} (steps x paths)")
    median_path_normal = np.median(paths_normal, axis=1)
    p10_path_normal = np.percentile(paths_normal, 10, axis=1)
    p90_path_normal = np.percentile(paths_normal, 90, axis=1)
    
    fig = plot_mc_paths(paths_normal, median_path_normal, p10_path_normal, p90_path_normal, 
                       approx_days, start_capital, plot_all_paths, with_randomness=False)
    save_and_show(fig, "07_mc_paths_normal.png", results_dir, show_plots)
    plt.close(fig)
    
    # Chart 8: Monte Carlo with Randomness
    print("Generating Chart 8: Monte Carlo (WITH 30% Randomness)...")
    print(f"   >> Simulating {mc_paths:,} paths with {mc_steps} steps and {randomness_factor*100:.0f}% randomness...")
    paths_random = mc_gaussian_with_randomness(mu_a, cov_a, w, start_capital, mc_steps, mc_paths, randomness_factor, month_factor)
    print(f"   >> Generated paths shape: {paths_random.shape} (steps x paths)")
    median_path_random = np.median(paths_random, axis=1)
    p10_path_random = np.percentile(paths_random, 10, axis=1)
    p90_path_random = np.percentile(paths_random, 90, axis=1)
    
    fig = plot_mc_paths(paths_random, median_path_random, p10_path_random, p90_path_random, 
                       approx_days, start_capital, plot_all_paths, with_randomness=True)
    save_and_show(fig, "08_mc_paths_with_randomness.png", results_dir, show_plots)
    plt.close(fig)
    
    # Chart 9: Projected Volatility Distribution (Normal)
    print("Generating Chart 9: Projected Volatility Distribution (Normal)...")
    fig = plot_projected_volatility(paths_normal, month_factor, with_randomness=False)
    save_and_show(fig, "09_projected_volatility_normal.png", results_dir, show_plots)
    plt.close(fig)
    
    # Chart 10: Projected Volatility Distribution (With Randomness)
    print("Generating Chart 10: Projected Volatility Distribution (With Randomness)...")
    fig = plot_projected_volatility(paths_random, month_factor, with_randomness=True)
    save_and_show(fig, "10_projected_volatility_random.png", results_dir, show_plots)
    plt.close(fig)
    
    # Chart 11: Projected Max Drawdown Distribution (Normal)
    print("Generating Chart 11: Projected Max Drawdown Distribution (Normal)...")
    fig = plot_projected_max_drawdown(paths_normal, with_randomness=False)
    save_and_show(fig, "11_projected_max_drawdown_normal.png", results_dir, show_plots)
    plt.close(fig)
    
    # Chart 12: Projected Max Drawdown Distribution (With Randomness)
    print("Generating Chart 12: Projected Max Drawdown Distribution (With Randomness)...")
    fig = plot_projected_max_drawdown(paths_random, with_randomness=True)
    save_and_show(fig, "12_projected_max_drawdown_random.png", results_dir, show_plots)
    plt.close(fig)
    
    print("=== MONTE CARLO CHARTS COMPLETED ===")
    
    return {
        "paths_normal": paths_normal,
        "paths_random": paths_random,
        "median_normal": median_path_normal,
        "median_random": median_path_random
    }

def main():
    """Standalone execution for Monte Carlo charts only."""
    print("=== RUNNING MONTE CARLO CHARTS ONLY ===")
    
    # Import here to avoid circular imports
    from utils.utils_data import load_prices_from_dir, align_business_days, slice_recent_safe
    from utils.utils_math import compute_portfolio_metrics
    
    # Configuration
    DATA_DIR = r"C:\Users\CAMPACCI\Desktop\Portefeuille"
    RESULTS_DIR = r"./results"
    ESTIMATION_YEARS = 3
    START_CAPITAL = 10_000
    MC_PATHS = 50_000
    MC_STEPS = 36
    RANDOMNESS_FACTOR = 0.30
    ANNUALIZATION = 252
    MONTH_FACTOR = 12
    PLOT_ALL_PATHS = True
    
    # Portfolio weights
    WEIGHTS_RAW = {
        "ANXU":0.20, "NVDA":0.07, "PLTR":0.07, "IUS2":0.06, "BNK": 0.13,
        "CS1": 0.07, "MIB": 0.07, "CNKY":0.07, "GLDA":0.13, "CG1": 0.13,
    }
    
    try:
        # Load and prepare data
        etf_prices_raw = load_prices_from_dir(DATA_DIR)
        etf_prices = align_business_days(etf_prices_raw)
        etf_prices = slice_recent_safe(etf_prices, ESTIMATION_YEARS)
        
        # Compute portfolio metrics
        portfolio_metrics = compute_portfolio_metrics(etf_prices, WEIGHTS_RAW)
        
        # Generate Monte Carlo charts
        mc_results = generate_monte_carlo_charts(
            portfolio_metrics, MC_PATHS, MC_STEPS, RANDOMNESS_FACTOR, 
            START_CAPITAL, ANNUALIZATION, MONTH_FACTOR, PLOT_ALL_PATHS, 
            RESULTS_DIR, True
        )
        
        print("Monte Carlo charts completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Portefeuille folder exists with ETF CSV files.")

if __name__ == "__main__":
    main()
