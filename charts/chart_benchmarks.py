# chart_benchmarks.py - Benchmark Comparison Charts (Charts 18-21)
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from utils.utils_math import compute_benchmark_params, mc_single_asset, mc_gaussian_with_randomness
from utils.utils_plot import save_and_show, placeholder_figure, eur_fmt

def plot_risk_vs_indexes(bench_prices, port_ret_d, bench_def, annualization):
    """Chart 18: Risk (volatility) vs Indexes - Professional Design"""
    data = {"Portfolio": port_ret_d}
    for label, tick in bench_def:
        if tick in bench_prices.columns:
            data[label] = np.log(bench_prices[tick] / bench_prices[tick].shift(1))
    df = pd.concat(data, axis=1).dropna()
    if df.empty:
        return placeholder_figure("Risk (volatility) — Portfolio vs Indexes (historical)",
                                  "No common dates or benchmarks available.")
    vol = df.std(ddof=1)*np.sqrt(annualization)*100
    vol = vol.sort_values(ascending=True)  # Ascending for horizontal bars (lowest at bottom)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Professional colors
    colors = ["#E74C3C" if i=="Portfolio" else "#3498DB" for i in vol.index]
    
    bars = ax.barh(vol.index, vol.values, color=colors, alpha=0.85, 
                   edgecolor='black', linewidth=0.8)
    
    # Add value labels
    for bar, val in zip(bars, vol.values):
        ax.text(val + vol.max()*0.02, bar.get_y() + bar.get_height()/2, 
               f"{val:.2f}%", va="center", ha="left", fontsize=10, fontweight='bold')
    
    # Labels and title
    ax.set_xlabel("Annualized Volatility (%)", fontsize=11, fontweight='bold')
    ax.set_title("Portfolio Risk vs Benchmark Indexes — Volatility Comparison", 
                fontsize=14, fontweight='bold', pad=20)
    
    # Grid
    ax.grid(True, axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.set_xlim(0, vol.max()*1.20)
    
    fig.tight_layout()
    return fig

def plot_forward_excess_vs_benchmarks(paths_random, bench_params, mc_paths, mc_steps, start_capital, forward_years):
    """Chart 19: Forward Excess vs Benchmarks - Professional Design"""
    if not bench_params:
        return placeholder_figure("Forward Excess vs Benchmarks (MC)", "No benchmark parameters available.")
    V0 = paths_random[0, 0]
    Vp_end = paths_random[-1, :]
    cagr_port = (Vp_end / V0) ** (1.0 / forward_years) - 1.0

    stats = {}
    for label, pars in bench_params.items():
        mu_ann  = pars["mu_ann"];  vol_ann = pars["vol_ann"]
        bench_paths = mc_single_asset(mu_ann, vol_ann, start_capital, mc_steps, mc_paths)
        Ve = bench_paths[-1, :]
        cagr_bm = (Ve / start_capital) ** (1.0 / forward_years) - 1.0
        excess  = cagr_port - cagr_bm
        stats[label] = {
            "mean": float(np.mean(excess)),
            "p10":  float(np.percentile(excess, 10)),
            "p90":  float(np.percentile(excess, 90)),
            "p_pos": float((excess > 0).mean())
        }

    labels = list(stats.keys())
    means  = np.array([stats[k]["mean"] for k in labels]) * 100
    p10    = np.array([stats[k]["p10"]  for k in labels]) * 100
    p90    = np.array([stats[k]["p90"]  for k in labels]) * 100
    yerr   = np.vstack([means - p10, p90 - means])

    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Professional colors
    colors = ["#27AE60" if m >= 0 else "#E74C3C" for m in means]
    
    bars = ax.bar(labels, means, yerr=yerr, capsize=6, color=colors, alpha=0.85,
                  edgecolor='black', linewidth=1, error_kw={'linewidth': 2, 'ecolor': '#2C3E50'})
    ax.axhline(0, color="#2C3E50", lw=2, linestyle='--')
    
    # Add probability labels
    for i, k in enumerate(labels):
        prob = stats[k]['p_pos']*100
        y_pos = means[i] + (p90[i] - means[i]) + 0.5 if means[i] >= 0 else means[i] - (means[i] - p10[i]) - 0.5
        ax.text(i, y_pos,
                f"P(>0) = {prob:.0f}%",
                ha="center", va="bottom" if means[i] >= 0 else "top",
                fontsize=9, fontweight='bold',
                bbox=dict(facecolor="white", edgecolor="#2C3E50", alpha=0.9, linewidth=1))
    
    # Labels and title
    ax.set_ylabel("Excess CAGR (Portfolio − Benchmark) %", fontsize=11, fontweight='bold')
    ax.set_xlabel("Benchmark Index", fontsize=11, fontweight='bold')
    ax.set_title(f"Portfolio Excess Return vs Benchmarks (WITH 30% Randomness)\n{mc_paths:,} MC Paths, {mc_steps} Months, 10th-90th Percentile Range", 
                fontsize=14, fontweight='bold', pad=20)
    
    # Grid
    ax.grid(axis="y", alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    # Rotate x-labels if needed
    plt.xticks(rotation=30, ha='right')
    
    fig.tight_layout()
    return fig

def plot_mc_portfolio_vs_benchmarks(paths_portfolio, bench_params, mc_paths, mc_steps, start_capital, 
                                   randomness_factor, month_factor, with_randomness=False):
    """Chart 20-21: Portfolio vs Benchmarks Monte Carlo - Professional Design"""
    if not bench_params:
        return placeholder_figure("Portfolio vs Benchmarks (MC)", "No benchmark parameters available.")
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Portfolio median path with emphasis
    portfolio_median = np.median(paths_portfolio, axis=1)
    ax.plot(portfolio_median, color="#E74C3C", lw=4, label="Portfolio (Median)", zorder=10, alpha=0.9)
    
    # Professional benchmark colors
    colors = ['#3498DB', '#27AE60', '#F39C12', '#9B59B6', '#1ABC9C', '#E67E22']
    for i, (label, pars) in enumerate(bench_params.items()):
        mu_ann = pars["mu_ann"]
        vol_ann = pars["vol_ann"]
        
        # Generate benchmark paths
        if with_randomness:
            bench_paths = mc_gaussian_with_randomness(
                np.array([mu_ann]), np.array([[vol_ann**2]]), 
                np.array([1.0]), start_capital, mc_steps, mc_paths, randomness_factor, month_factor
            )
        else:
            bench_paths = mc_single_asset(mu_ann, vol_ann, start_capital, mc_steps, mc_paths)
        
        bench_median = np.median(bench_paths, axis=1)
        color = colors[i % len(colors)]
        ax.plot(bench_median, color=color, lw=2.5, linestyle='--', label=f"{label}", alpha=0.8, zorder=5)
    
    # Add initial capital line
    ax.axhline(start_capital, color="#95A5A6", ls=":", lw=2, label=f"Initial Capital ({start_capital:,.0f})", zorder=3)
    
    # Formatting
    randomness_text = "WITH 30% Randomness" if with_randomness else "Normal Distribution"
    ax.set_title(f"Portfolio vs Benchmarks Monte Carlo — {randomness_text}\n3-Year Projection, {mc_paths:,} Paths", 
                fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel("Time (Months)", fontsize=11, fontweight='bold')
    ax.set_ylabel("Portfolio Value", fontsize=11, fontweight='bold')
    ax.yaxis.set_major_formatter(eur_fmt)
    
    # Legend and grid
    ax.legend(loc='upper left', frameon=True, fancybox=True, shadow=True, fontsize=10)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    
    fig.tight_layout()
    return fig

def generate_benchmark_charts(bench_prices, portfolio_metrics, mc_results, bench_def, 
                            mc_paths, mc_steps, start_capital, forward_years, annualization,
                            randomness_factor, month_factor, results_dir="./results", show_plots=True, selected_charts=None):
    """Generate Charts 18-21: Benchmark Comparison Charts.
    
    Args:
        selected_charts: List of chart numbers to generate (e.g., [18, 20]). If None, generates all.
    """
    if selected_charts is None:
        selected_charts = list(range(18, 22))  # Charts 18-21
    
    print(f"=== BENCHMARK COMPARISON CHARTS (Selected: {selected_charts}) ===")
    
    # Compute benchmark parameters (always needed)
    bench_params = compute_benchmark_params(bench_prices, bench_def, annualization)
    
    # Chart 18: Risk vs Indexes
    if 18 in selected_charts:
        print("\nGenerating Chart 18: Risk vs Indexes...")
        fig = plot_risk_vs_indexes(bench_prices, portfolio_metrics["port_ret_d"], bench_def, annualization)
        save_and_show(fig, "18_risk_vs_indexes.png", results_dir, show_plots)
        plt.close(fig)
    
    # Chart 19: Forward Excess vs Benchmarks
    if 19 in selected_charts:
        print("Generating Chart 19: Forward Excess vs Benchmarks...")
        fig = plot_forward_excess_vs_benchmarks(
            mc_results["paths_random"], bench_params, mc_paths, mc_steps, start_capital, forward_years
        )
        save_and_show(fig, "19_forward_excess_vs_benchmarks_with_randomness_MC.png", results_dir, show_plots)
        plt.close(fig)
    
    # Chart 20: Portfolio vs Benchmarks (Normal)
    if 20 in selected_charts:
        print("Generating Chart 20: Portfolio vs Benchmarks (Normal)...")
        fig = plot_mc_portfolio_vs_benchmarks(
            mc_results["paths_normal"], bench_params, mc_paths, mc_steps, start_capital,
            randomness_factor, month_factor, with_randomness=False
        )
        save_and_show(fig, "20_mc_portfolio_vs_benchmarks_normal.png", results_dir, show_plots)
        plt.close(fig)
    
    # Chart 21: Portfolio vs Benchmarks (Random)
    if 21 in selected_charts:
        print("Generating Chart 21: Portfolio vs Benchmarks (Random)...")
        fig = plot_mc_portfolio_vs_benchmarks(
            mc_results["paths_random"], bench_params, mc_paths, mc_steps, start_capital,
            randomness_factor, month_factor, with_randomness=True
        )
        save_and_show(fig, "21_mc_portfolio_vs_benchmarks_with_randomness.png", results_dir, show_plots)
        plt.close(fig)
    
    print("=== BENCHMARK CHARTS COMPLETED ===")
    
    return bench_params

def main():
    """Standalone execution for benchmark charts only."""
    print("=== RUNNING BENCHMARK CHARTS ONLY ===")
    
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
    RANDOMNESS_FACTOR = 0.30
    ANNUALIZATION = 252
    MONTH_FACTOR = 12
    FORWARD_YEARS = MC_STEPS / 12.0
    
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
        
        # Generate Monte Carlo results first
        mc_results = generate_monte_carlo_charts(
            portfolio_metrics, MC_PATHS, MC_STEPS, RANDOMNESS_FACTOR, 
            START_CAPITAL, ANNUALIZATION, MONTH_FACTOR, True, 
            RESULTS_DIR, False  # Don't show plots for MC, we'll show benchmarks
        )
        
        # Generate benchmark charts
        bench_params = generate_benchmark_charts(
            bench_prices, portfolio_metrics, mc_results, BENCH_DEF, 
            MC_PATHS, MC_STEPS, START_CAPITAL, FORWARD_YEARS, ANNUALIZATION,
            RANDOMNESS_FACTOR, MONTH_FACTOR, RESULTS_DIR, True
        )
        
        print("Benchmark charts completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Portefeuille folder exists with ETF CSV files.")

if __name__ == "__main__":
    main()
