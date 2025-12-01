# chart_risk_metrics.py - Risk Metrics Charts (Charts 13-17)
import numpy as np
import matplotlib.pyplot as plt
from utils.utils_math import calculate_var, calculate_expected_shortfall, calculate_max_drawdown_duration, calculate_calmar_ratio, calculate_sharpe_ratio
from utils.utils_plot import save_and_show
from utils.utils_data import fetch_risk_free_rate

def calculate_risk_metrics(port_ret_d, paths_normal, paths_random, start_capital, forward_years, annualization):
    """Calculate comprehensive risk metrics for both simulations."""
    # Fetch current risk-free rate (SOFR)
    print("\n>> Fetching current risk-free rate...")
    risk_free_rate, rate_source, rate_date = fetch_risk_free_rate()
    print(f"   Using {rate_source}: {risk_free_rate*100:.2f}% (as of {rate_date})")
    
    # Historical metrics
    hist_rets = port_ret_d.values
    hist_annual_ret = hist_rets.mean() * annualization
    hist_vol = hist_rets.std() * np.sqrt(annualization)
    hist_max_dd = calculate_max_drawdown_duration((1 + hist_rets).cumprod())
    
    # Normal MC metrics
    normal_end_vals = paths_normal[-1, :]
    normal_rets = (normal_end_vals / start_capital) ** (1.0 / forward_years) - 1.0
    normal_var_95 = calculate_var(normal_rets, 0.95)
    normal_es_95 = calculate_expected_shortfall(normal_rets, 0.95)
    normal_max_dd_duration = np.max([calculate_max_drawdown_duration(paths_normal[:, i]) for i in range(paths_normal.shape[1])])
    normal_calmar = calculate_calmar_ratio(normal_rets.mean(), normal_rets.min())
    normal_sharpe = calculate_sharpe_ratio(normal_rets, risk_free_rate=risk_free_rate)
    
    # Random MC metrics
    random_end_vals = paths_random[-1, :]
    random_rets = (random_end_vals / start_capital) ** (1.0 / forward_years) - 1.0
    random_var_95 = calculate_var(random_rets, 0.95)
    random_es_95 = calculate_expected_shortfall(random_rets, 0.95)
    random_max_dd_duration = np.max([calculate_max_drawdown_duration(paths_random[:, i]) for i in range(paths_random.shape[1])])
    random_calmar = calculate_calmar_ratio(random_rets.mean(), random_rets.min())
    random_sharpe = calculate_sharpe_ratio(random_rets, risk_free_rate=risk_free_rate)
    
    return {
        "historical": {
            "annual_return": hist_annual_ret,
            "volatility": hist_vol,
            "max_dd_duration": hist_max_dd,
            "var_95": calculate_var(hist_rets, 0.95),
            "es_95": calculate_expected_shortfall(hist_rets, 0.95)
        },
        "normal_mc": {
            "var_95": normal_var_95,
            "es_95": normal_es_95,
            "max_dd_duration": normal_max_dd_duration,
            "calmar_ratio": normal_calmar,
            "sharpe_ratio": normal_sharpe,
            "annual_return": normal_rets.mean(),
            "volatility": normal_rets.std()
        },
        "random_mc": {
            "var_95": random_var_95,
            "es_95": random_es_95,
            "max_dd_duration": random_max_dd_duration,
            "calmar_ratio": random_calmar,
            "sharpe_ratio": random_sharpe,
            "annual_return": random_rets.mean(),
            "volatility": random_rets.std()
        },
        "risk_free_rate": {
            "rate": risk_free_rate,
            "source": rate_source,
            "date": rate_date
        }
    }

def plot_var_95_individual(risk_metrics):
    """Chart 13: Value at Risk (VaR) 95% - Professional Design"""
    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['Normal Distribution', 'With 30% Randomness']
    # VaR is typically shown as a positive loss percentage (absolute value)
    values = [
        abs(risk_metrics['normal_mc']['var_95']) * 100,
        abs(risk_metrics['random_mc']['var_95']) * 100
    ]
    colors = ['#3498DB', '#E74C3C']

    bars = ax.bar(categories, values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5, width=0.6)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.03,
               f'{val:.2f}%', ha='center', va='bottom', fontsize=13, fontweight='bold')

    # Labels
    ax.set_ylabel('Maximum Loss (VaR 95%) - %', fontsize=11, fontweight='bold')
    ax.set_xlabel('Monte Carlo Simulation Method', fontsize=11, fontweight='bold')
    ax.set_title('Value at Risk (VaR 95%) — Maximum Expected Loss', 
                fontsize=14, fontweight='bold', pad=20)

    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ax.set_ylim(0, max(values) * 1.20)

    fig.tight_layout()
    return fig

def plot_expected_shortfall_individual(risk_metrics):
    """Chart 14: Expected Shortfall (ES) 95% - Professional Design"""
    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['Normal Distribution', 'With 30% Randomness']
    # Expected Shortfall is typically shown as a positive loss percentage (absolute value)
    values = [
        abs(risk_metrics['normal_mc']['es_95']) * 100,
        abs(risk_metrics['random_mc']['es_95']) * 100
    ]
    colors = ['#3498DB', '#E74C3C']

    bars = ax.bar(categories, values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5, width=0.6)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.03,
               f'{val:.2f}%', ha='center', va='bottom', fontsize=13, fontweight='bold')

    # Labels
    ax.set_ylabel('Expected Shortfall 95% (CVaR) - %', fontsize=11, fontweight='bold')
    ax.set_xlabel('Monte Carlo Simulation Method', fontsize=11, fontweight='bold')
    ax.set_title('Expected Shortfall (ES 95%) — Tail Risk Assessment', 
                fontsize=14, fontweight='bold', pad=20)

    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ylim_max = min(max(values) * 1.20, 60)
    ax.set_ylim(0, ylim_max)

    fig.tight_layout()
    return fig

def plot_max_dd_duration_individual(risk_metrics):
    """Chart 15: Maximum Drawdown Duration - Professional Design"""
    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['Normal Distribution', 'With 30% Randomness']
    values = [
        risk_metrics['normal_mc']['max_dd_duration'],
        risk_metrics['random_mc']['max_dd_duration']
    ]
    colors = ['#3498DB', '#E74C3C']

    bars = ax.bar(categories, values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5, width=0.6)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.03,
               f'{val:.0f}', ha='center', va='bottom', fontsize=13, fontweight='bold')

    # Labels
    ax.set_ylabel('Duration (Months)', fontsize=11, fontweight='bold')
    ax.set_xlabel('Monte Carlo Simulation Method', fontsize=11, fontweight='bold')
    ax.set_title('Maximum Drawdown Duration — Recovery Time Analysis', 
                fontsize=14, fontweight='bold', pad=20)

    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ylim_max = min(max(values) * 1.20, 60)
    ax.set_ylim(0, ylim_max)

    fig.tight_layout()
    return fig

def plot_calmar_ratio_individual(risk_metrics):
    """Chart 16: Calmar Ratio - Professional Design"""
    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['Normal Distribution', 'With 30% Randomness']
    values = [
        risk_metrics['normal_mc']['calmar_ratio'],
        risk_metrics['random_mc']['calmar_ratio']
    ]
    colors = ['#3498DB', '#E74C3C']

    bars = ax.bar(categories, values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5, width=0.6)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.03,
               f'{val:.2f}', ha='center', va='bottom', fontsize=13, fontweight='bold')

    # Labels
    ax.set_ylabel('Calmar Ratio', fontsize=11, fontweight='bold')
    ax.set_xlabel('Monte Carlo Simulation Method', fontsize=11, fontweight='bold')
    ax.set_title('Calmar Ratio — Risk-Adjusted Performance', 
                fontsize=14, fontweight='bold', pad=20)

    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ylim_max = min(max(values) * 1.20, 60)
    ax.set_ylim(0, ylim_max)

    fig.tight_layout()
    return fig

def plot_sharpe_ratio_individual(risk_metrics):
    """Chart 17: Sharpe Ratio - Professional Design"""
    fig, ax = plt.subplots(figsize=(12, 7))

    categories = ['Normal Distribution', 'With 30% Randomness']
    values = [
        risk_metrics['normal_mc']['sharpe_ratio'],
        risk_metrics['random_mc']['sharpe_ratio']
    ]
    colors = ['#3498DB', '#E74C3C']

    bars = ax.bar(categories, values, color=colors, alpha=0.85, edgecolor='black', linewidth=1.5, width=0.6)

    # Add value labels on bars
    for bar, val in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.03,
               f'{val:.2f}', ha='center', va='bottom', fontsize=13, fontweight='bold')

    # Labels
    ax.set_ylabel('Sharpe Ratio', fontsize=11, fontweight='bold')
    ax.set_xlabel('Monte Carlo Simulation Method', fontsize=11, fontweight='bold')
    
    # Title with risk-free rate info
    rfr_info = risk_metrics.get('risk_free_rate', {})
    rfr_rate = rfr_info.get('rate', 0.02) * 100
    rfr_source = rfr_info.get('source', 'N/A')
    rfr_date = rfr_info.get('date', 'N/A')
    
    ax.set_title(f'Sharpe Ratio — Risk-Adjusted Return Efficiency\n' +
                f'Risk-Free Rate: {rfr_rate:.2f}% ({rfr_source}, {rfr_date})', 
                fontsize=14, fontweight='bold', pad=20)

    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)
    ylim_max = min(max(values) * 1.20, 10)
    ax.set_ylim(0, ylim_max)

    fig.tight_layout()
    return fig

def generate_risk_metrics_charts(portfolio_metrics, mc_results, start_capital, forward_years, 
                              annualization, results_dir="./results", show_plots=True, selected_charts=None):
    """Generate Charts 13-17: Risk Metrics Charts.
    
    Args:
        selected_charts: List of chart numbers to generate (e.g., [13, 15, 17]). If None, generates all.
    """
    if selected_charts is None:
        selected_charts = list(range(13, 18))  # Charts 13-17
    
    print(f"=== RISK METRICS CHARTS (Selected: {selected_charts}) ===")
    
    # Calculate risk metrics (always needed)
    risk_metrics = calculate_risk_metrics(
        portfolio_metrics["port_ret_d"], 
        mc_results["paths_normal"], 
        mc_results["paths_random"],
        start_capital, forward_years, annualization
    )
    
    # Chart 13: VaR 95%
    if 13 in selected_charts:
        print("\nGenerating Chart 13: VaR 95%...")
        fig = plot_var_95_individual(risk_metrics)
        save_and_show(fig, "13_var_95_individual.png", results_dir, show_plots)
        plt.close(fig)
    
    # Chart 14: Expected Shortfall
    if 14 in selected_charts:
        print("Generating Chart 14: Expected Shortfall...")
        fig = plot_expected_shortfall_individual(risk_metrics)
        save_and_show(fig, "14_expected_shortfall_individual.png", results_dir, show_plots)
        plt.close(fig)
    
    # Chart 15: Max DD Duration
    if 15 in selected_charts:
        print("Generating Chart 15: Max DD Duration...")
        fig = plot_max_dd_duration_individual(risk_metrics)
        save_and_show(fig, "15_max_dd_duration_individual.png", results_dir, show_plots)
        plt.close(fig)
    
    # Chart 16: Calmar Ratio
    if 16 in selected_charts:
        print("Generating Chart 16: Calmar Ratio...")
        fig = plot_calmar_ratio_individual(risk_metrics)
        save_and_show(fig, "16_calmar_ratio_individual.png", results_dir, show_plots)
        plt.close(fig)
    
    # Chart 17: Sharpe Ratio
    if 17 in selected_charts:
        print("Generating Chart 17: Sharpe Ratio...")
        fig = plot_sharpe_ratio_individual(risk_metrics)
        save_and_show(fig, "17_sharpe_ratio_individual.png", results_dir, show_plots)
        plt.close(fig)
    
    print("=== RISK METRICS CHARTS COMPLETED ===")
    
    return risk_metrics

def main():
    """Standalone execution for risk metrics charts only."""
    print("=== RUNNING RISK METRICS CHARTS ONLY ===")
    
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
    RANDOMNESS_FACTOR = 0.30
    ANNUALIZATION = 252
    MONTH_FACTOR = 12
    FORWARD_YEARS = MC_STEPS / 12.0
    
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
        
        # Generate Monte Carlo results first
        mc_results = generate_monte_carlo_charts(
            portfolio_metrics, MC_PATHS, MC_STEPS, RANDOMNESS_FACTOR, 
            START_CAPITAL, ANNUALIZATION, MONTH_FACTOR, True, 
            RESULTS_DIR, False  # Don't show plots for MC, we'll show risk metrics
        ) 
        
        # Generate risk metrics charts
        risk_metrics = generate_risk_metrics_charts(
            portfolio_metrics, mc_results, START_CAPITAL, FORWARD_YEARS, 
            ANNUALIZATION, RESULTS_DIR, True
        )
        
        print("Risk metrics charts completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the Portefeuille folder exists with ETF CSV files.")

if __name__ == "__main__":
    main()
