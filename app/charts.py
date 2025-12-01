"""
Module de génération de graphiques pour Portfolio Architect
Porté depuis charts/*.py (version Tkinter) → Plotly (Streamlit)

Contient les 24 graphiques professionnels :
- Portfolio Charts (1-6)
- Monte Carlo Charts (7-12)
- Risk Metrics Charts (13-18)
- Market Analysis Charts (19-24)
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from app.config import CHART_COLORS

# ===================== PORTFOLIO CHARTS (1-6) =====================

def create_chart_1_allocation(weights_series, capital, ticker_info=None):
    """
    Chart 1: Portfolio Allocation (Pie Chart with Values)
    
    Args:
        weights_series (pd.Series): Weights by ticker
        capital (float): Total capital
        ticker_info (dict): Optional dict with ticker info
    
    Returns:
        plotly.graph_objects.Figure
    """
    tickers = list(weights_series.index)
    weights = list(weights_series.values)
    values = [w * capital for w in weights]
    
    # Build labels with percentage and amount
    labels = []
    for ticker, weight, value in zip(tickers, weights, values):
        labels.append(f"{ticker}<br>{weight*100:.1f}% (${value:,.0f})")
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=weights,
        hole=0.4,
        marker=dict(colors=CHART_COLORS['primary'][:len(weights)]),
        textinfo='label+percent',
        textposition='auto',
        textfont=dict(size=11, color='white'),
        pull=[0.02] * len(weights)
    )])
    
    fig.update_layout(
        title=dict(
            text=f"Portfolio Allocation<br><sub>Total: ${capital:,.0f}</sub>",
            x=0.5,
            xanchor='center',
            font=dict(size=16, color='white')
        ),
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02),
        height=500
    )
    
    return fig

def create_chart_2_value_distribution(weights_series, capital):
    """
    Chart 2: Portfolio Value Distribution (Bar Chart)
    """
    tickers = list(weights_series.index)
    values = [w * capital for w in weights_series.values]
    
    fig = go.Figure(data=[go.Bar(
        x=tickers,
        y=values,
        marker=dict(
            color=values,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Value ($)")
        ),
        text=[f"${v:,.0f}" for v in values],
        textposition='auto',
        textfont=dict(color='white', size=11)
    )])
    
    fig.update_layout(
        title="Portfolio Value Distribution by Asset",
        xaxis_title="Asset",
        yaxis_title="Value ($)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(tickformat="$,.0f"),
        height=500
    )
    
    return fig

def create_chart_3_cumulative_returns(portfolio_returns, prices=None, tickers=None):
    """
    Chart 3: Cumulative Returns Over Time
    
    Args:
        portfolio_returns (pd.Series): Daily portfolio returns
        prices (pd.DataFrame): Optional individual asset prices
        tickers (list): Optional list of tickers to display
    """
    # Calculate cumulative returns
    cumulative_portfolio = (1 + portfolio_returns).cumprod()
    
    fig = go.Figure()
    
    # Portfolio cumulative return
    fig.add_trace(go.Scatter(
        x=cumulative_portfolio.index,
        y=cumulative_portfolio.values,
        mode='lines',
        name='Portfolio',
        line=dict(color=CHART_COLORS['primary'][0], width=3)
    ))
    
    # Individual assets if provided
    if prices is not None and tickers is not None:
        for i, ticker in enumerate(tickers):
            if ticker in prices.columns:
                asset_returns = prices[ticker].pct_change().dropna()
                cumulative_asset = (1 + asset_returns).cumprod()
                fig.add_trace(go.Scatter(
                    x=cumulative_asset.index,
                    y=cumulative_asset.values,
                    mode='lines',
                    name=ticker,
                    line=dict(width=1.5, dash='dot'),
                    opacity=0.6
                ))
    
    fig.update_layout(
        title="Cumulative Returns",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (Normalized to 1.0)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x unified',
        height=500,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    return fig

def create_chart_4_returns_distribution(portfolio_returns):
    """
    Chart 4: Daily Returns Distribution with Normal Overlay
    """
    returns = portfolio_returns.dropna() * 100  # Convert to percentage
    
    fig = go.Figure()
    
    # Histogram of returns
    fig.add_trace(go.Histogram(
        x=returns,
        nbinsx=50,
        name='Actual Returns',
        marker=dict(color=CHART_COLORS['primary'][1], line=dict(color='white', width=1)),
        opacity=0.7
    ))
    
    # Normal distribution overlay
    mean = returns.mean()
    std = returns.std()
    x_range = np.linspace(returns.min(), returns.max(), 100)
    normal_dist = (1 / (std * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x_range - mean) / std) ** 2)
    # Scale normal to match histogram
    normal_dist = normal_dist * len(returns) * (returns.max() - returns.min()) / 50
    
    fig.add_trace(go.Scatter(
        x=x_range,
        y=normal_dist,
        mode='lines',
        name='Normal Distribution',
        line=dict(color='red', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f"Daily Returns Distribution<br><sub>Mean: {mean:.2f}% | Std: {std:.2f}%</sub>",
        xaxis_title="Daily Return (%)",
        yaxis_title="Frequency",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        showlegend=True,
        height=500
    )
    
    return fig

def create_chart_5_correlation_heatmap(correlation_matrix):
    """
    Chart 5: Asset Correlation Heatmap
    """
    fig = go.Figure(data=go.Heatmap(
        z=correlation_matrix.values,
        x=correlation_matrix.columns,
        y=correlation_matrix.index,
        colorscale='RdBu',
        zmid=0,
        text=correlation_matrix.values,
        texttemplate='%{text:.2f}',
        textfont=dict(size=10),
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Asset Correlation Matrix",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=600,
        width=700
    )
    
    return fig

def create_chart_6_rolling_volatility(portfolio_returns, window=252):
    """
    Chart 6: Rolling Volatility (Annualized)
    """
    rolling_vol = portfolio_returns.rolling(window=window).std() * np.sqrt(252) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rolling_vol.index,
        y=rolling_vol.values,
        mode='lines',
        fill='tozeroy',
        name='Rolling Volatility',
        line=dict(color=CHART_COLORS['primary'][2], width=2),
        fillcolor='rgba(58, 71, 250, 0.3)'
    ))
    
    # Add mean line
    mean_vol = rolling_vol.mean()
    fig.add_hline(y=mean_vol, line_dash="dash", line_color="yellow",
                  annotation_text=f"Mean: {mean_vol:.2f}%")
    
    fig.update_layout(
        title=f"Rolling Volatility (Annualized)<br><sub>Window: {window} days</sub>",
        xaxis_title="Date",
        yaxis_title="Volatility (%)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        hovermode='x',
        height=500
    )
    
    return fig

# ===================== MONTE CARLO CHARTS (7-12) =====================

def create_chart_7_mc_price_paths(simulations, capital, n_display=1000):
    """
    Chart 7: Monte Carlo Price Projections
    
    Args:
        simulations (np.ndarray): Shape (steps+1, paths)
        capital (float): Starting capital
        n_display (int): Number of paths to display
    """
    steps, paths = simulations.shape
    
    # Sample paths to display
    display_indices = np.random.choice(paths, min(n_display, paths), replace=False)
    
    fig = go.Figure()
    
    # Plot sample paths
    for idx in display_indices:
        fig.add_trace(go.Scatter(
            x=list(range(steps)),
            y=simulations[:, idx],
            mode='lines',
            line=dict(width=0.5, color='rgba(100, 150, 255, 0.1)'),
            showlegend=False,
            hoverinfo='skip'
        ))
    
    # Statistical paths
    median_path = np.median(simulations, axis=1)
    p10_path = np.percentile(simulations, 10, axis=1)
    p90_path = np.percentile(simulations, 90, axis=1)
    
    fig.add_trace(go.Scatter(
        x=list(range(steps)),
        y=median_path,
        mode='lines',
        name='Median (50th %ile)',
        line=dict(color='white', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(steps)),
        y=p10_path,
        mode='lines',
        name='10th Percentile',
        line=dict(color='orange', width=2, dash='dash')
    ))
    
    fig.add_trace(go.Scatter(
        x=list(range(steps)),
        y=p90_path,
        mode='lines',
        name='90th Percentile',
        line=dict(color='green', width=2, dash='dash')
    ))
    
    # Initial capital line
    fig.add_hline(y=capital, line_dash="dash", line_color="gray",
                  annotation_text=f"Initial: ${capital:,.0f}")
    
    fig.update_layout(
        title=f"Monte Carlo Simulation - Price Projections<br><sub>{paths:,} paths | {n_display:,} displayed</sub>",
        xaxis_title="Time (Months)",
        yaxis_title="Portfolio Value ($)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=600,
        yaxis=dict(tickformat="$,.0f")
    )
    
    return fig

def create_chart_8_mc_returns_distribution(simulations):
    """
    Chart 8: Monte Carlo Returns Distribution
    """
    final_returns = (simulations[-1, :] / simulations[0, :] - 1) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=final_returns,
        nbinsx=50,
        marker=dict(color=CHART_COLORS['primary'][3], line=dict(color='white', width=1)),
        opacity=0.8
    ))
    
    # Add mean and median lines
    mean_return = final_returns.mean()
    median_return = np.median(final_returns)
    
    fig.add_vline(x=mean_return, line_dash="dash", line_color="yellow",
                  annotation_text=f"Mean: {mean_return:.1f}%")
    fig.add_vline(x=median_return, line_dash="dash", line_color="green",
                  annotation_text=f"Median: {median_return:.1f}%")
    
    fig.update_layout(
        title="Monte Carlo Final Returns Distribution",
        xaxis_title="Final Return (%)",
        yaxis_title="Frequency",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_chart_9_var_analysis(simulations, confidence_levels=[0.95, 0.99]):
    """
    Chart 9: Value at Risk Analysis
    """
    from app.calculations import calculate_var
    
    final_returns = (simulations[-1, :] / simulations[0, :] - 1)
    
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=final_returns * 100,
        nbinsx=50,
        name='Returns Distribution',
        marker=dict(color='blue', opacity=0.7)
    ))
    
    # VaR lines
    colors = ['red', 'darkred']
    for i, conf in enumerate(confidence_levels):
        var = calculate_var(final_returns, conf) * 100
        fig.add_vline(x=var, line_dash="dash", line_color=colors[i],
                      annotation_text=f"VaR {conf*100:.0f}%: {var:.1f}%",
                      annotation_position="top")
    
    fig.update_layout(
        title="Value at Risk (VaR) Analysis",
        xaxis_title="Return (%)",
        yaxis_title="Frequency",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_chart_10_confidence_intervals(simulations):
    """
    Chart 10: Confidence Intervals Over Time
    """
    steps = simulations.shape[0]
    
    # Calculate percentiles over time
    p5 = np.percentile(simulations, 5, axis=1)
    p25 = np.percentile(simulations, 25, axis=1)
    p50 = np.percentile(simulations, 50, axis=1)
    p75 = np.percentile(simulations, 75, axis=1)
    p95 = np.percentile(simulations, 95, axis=1)
    
    fig = go.Figure()
    
    # Fill between percentiles
    x = list(range(steps))
    
    fig.add_trace(go.Scatter(
        x=x + x[::-1],
        y=list(p95) + list(p5[::-1]),
        fill='toself',
        fillcolor='rgba(100, 150, 255, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=True,
        name='5th-95th %ile (90% CI)'
    ))
    
    fig.add_trace(go.Scatter(
        x=x + x[::-1],
        y=list(p75) + list(p25[::-1]),
        fill='toself',
        fillcolor='rgba(100, 150, 255, 0.4)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=True,
        name='25th-75th %ile (50% CI)'
    ))
    
    fig.add_trace(go.Scatter(
        x=x,
        y=p50,
        mode='lines',
        name='Median',
        line=dict(color='white', width=2)
    ))
    
    fig.update_layout(
        title="Confidence Intervals Over Time",
        xaxis_title="Time (Months)",
        yaxis_title="Portfolio Value ($)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500,
        yaxis=dict(tickformat="$,.0f")
    )
    
    return fig

def create_chart_11_risk_adjusted_performance(simulations, risk_free_rate=0.02):
    """
    Chart 11: Risk-Adjusted Performance Metrics
    """
    from app.calculations import calculate_sharpe_ratio
    
    # Calculate final returns for each path
    final_returns = (simulations[-1, :] / simulations[0, :] - 1)
    
    # Calculate metrics
    mean_return = final_returns.mean()
    volatility = final_returns.std()
    sharpe = calculate_sharpe_ratio(final_returns, risk_free_rate)
    
    # Create metrics display
    fig = go.Figure()
    
    fig.add_trace(go.Indicator(
        mode="number+delta",
        value=mean_return * 100,
        title={'text': "Mean Return (%)"},
        domain={'row': 0, 'column': 0}
    ))
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=volatility * 100,
        title={'text': "Volatility (%)"},
        domain={'row': 0, 'column': 1}
    ))
    
    fig.add_trace(go.Indicator(
        mode="number",
        value=sharpe,
        title={'text': "Sharpe Ratio"},
        domain={'row': 0, 'column': 2}
    ))
    
    fig.update_layout(
        title="Risk-Adjusted Performance Metrics",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        grid={'rows': 1, 'columns': 3},
        font=dict(color='white', size=14),
        height=300
    )
    
    return fig

def create_chart_12_scenario_analysis(simulations, capital):
    """
    Chart 12: Scenario Analysis (Best/Expected/Worst)
    """
    final_values = simulations[-1, :]
    
    # Calculate scenarios
    best_case = np.percentile(final_values, 95)
    expected = np.median(final_values)
    worst_case = np.percentile(final_values, 5)
    
    scenarios = {
        'Best Case (95th)': best_case,
        'Expected (Median)': expected,
        'Worst Case (5th)': worst_case
    }
    
    fig = go.Figure(data=[go.Bar(
        x=list(scenarios.keys()),
        y=list(scenarios.values()),
        text=[f"${v:,.0f}" for v in scenarios.values()],
        textposition='auto',
        marker=dict(color=['green', 'blue', 'red'])
    )])
    
    fig.add_hline(y=capital, line_dash="dash", line_color="yellow",
                  annotation_text=f"Initial: ${capital:,.0f}")
    
    fig.update_layout(
        title="Scenario Analysis - Final Portfolio Values",
        xaxis_title="Scenario",
        yaxis_title="Portfolio Value ($)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(tickformat="$,.0f"),
        height=500
    )
    
    return fig

# ===================== RISK METRICS CHARTS (13-18) =====================

def create_chart_13_sharpe_evolution(portfolio_returns, window=252, risk_free_rate=0.02):
    """
    Chart 13: Sharpe Ratio Evolution (Rolling)
    """
    from app.calculations import calculate_rolling_sharpe
    
    rolling_sharpe = calculate_rolling_sharpe(portfolio_returns, window, risk_free_rate)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rolling_sharpe.index,
        y=rolling_sharpe.values,
        mode='lines',
        fill='tozeroy',
        name='Rolling Sharpe Ratio',
        line=dict(color=CHART_COLORS['primary'][4], width=2)
    ))
    
    # Add mean line
    mean_sharpe = rolling_sharpe.mean()
    fig.add_hline(y=mean_sharpe, line_dash="dash", line_color="yellow",
                  annotation_text=f"Mean: {mean_sharpe:.2f}")
    
    fig.update_layout(
        title=f"Sharpe Ratio Evolution<br><sub>Window: {window} days | Risk-Free Rate: {risk_free_rate*100}%</sub>",
        xaxis_title="Date",
        yaxis_title="Sharpe Ratio",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_chart_14_max_drawdown(portfolio_returns):
    """
    Chart 14: Maximum Drawdown Analysis
    """
    from app.calculations import calculate_max_drawdown
    
    # Calculate cumulative returns
    cumulative = (1 + portfolio_returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max * 100
    
    max_dd = calculate_max_drawdown(cumulative.values) * 100
    
    fig = make_subplots(rows=2, cols=1, subplot_titles=('Portfolio Value', 'Drawdown (%)'),
                        vertical_spacing=0.15)
    
    # Portfolio value
    fig.add_trace(go.Scatter(
        x=cumulative.index,
        y=cumulative.values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='blue', width=2)
    ), row=1, col=1)
    
    fig.add_trace(go.Scatter(
        x=running_max.index,
        y=running_max.values,
        mode='lines',
        name='Peak',
        line=dict(color='green', width=1, dash='dash')
    ), row=1, col=1)
    
    # Drawdown
    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown.values,
        mode='lines',
        fill='tozeroy',
        name='Drawdown',
        line=dict(color='red', width=2),
        fillcolor='rgba(255, 0, 0, 0.3)'
    ), row=2, col=1)
    
    fig.add_hline(y=max_dd, line_dash="dash", line_color="darkred",
                  annotation_text=f"Max DD: {max_dd:.2f}%", row=2, col=1)
    
    fig.update_layout(
        title=f"Maximum Drawdown Analysis<br><sub>Max DD: {max_dd:.2f}%</sub>",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=600,
        showlegend=True
    )
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Value", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    
    return fig

def create_chart_15_risk_return_scatter(portfolio_metrics, benchmark_metrics=None):
    """
    Chart 15: Risk-Return Scatter Plot
    """
    fig = go.Figure()
    
    # Portfolio point
    fig.add_trace(go.Scatter(
        x=[portfolio_metrics['vol_a'] * 100],
        y=[portfolio_metrics['mu_a'][0] * 100] if isinstance(portfolio_metrics['mu_a'], np.ndarray) else [portfolio_metrics['port_ret_d'].mean() * 252 * 100],
        mode='markers',
        name='Portfolio',
        marker=dict(size=15, color='red', symbol='star')
    ))
    
    # Individual assets
    if 'cols' in portfolio_metrics:
        for i, col in enumerate(portfolio_metrics['cols']):
            ret = portfolio_metrics['mu_a'][i] * 100 if isinstance(portfolio_metrics['mu_a'], np.ndarray) else 0
            vol = np.sqrt(portfolio_metrics['cov_a'][i, i]) * 100 if isinstance(portfolio_metrics['cov_a'], np.ndarray) else 0
            
            fig.add_trace(go.Scatter(
                x=[vol],
                y=[ret],
                mode='markers+text',
                name=col,
                text=[col],
                textposition="top center",
                marker=dict(size=10)
            ))
    
    fig.update_layout(
        title="Risk-Return Profile",
        xaxis_title="Risk (Volatility %)",
        yaxis_title="Expected Return (%)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500,
        showlegend=True
    )
    
    return fig

def create_chart_16_beta_analysis(portfolio_returns, benchmark_returns):
    """
    Chart 16: Beta Analysis vs Benchmark
    """
    # Calculate beta
    covariance = np.cov(portfolio_returns, benchmark_returns)[0, 1]
    benchmark_variance = np.var(benchmark_returns)
    beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
    
    # Create scatter plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=benchmark_returns * 100,
        y=portfolio_returns * 100,
        mode='markers',
        marker=dict(size=5, color='blue', opacity=0.5),
        name='Daily Returns'
    ))
    
    # Add regression line
    z = np.polyfit(benchmark_returns, portfolio_returns, 1)
    p = np.poly1d(z)
    x_line = np.linspace(benchmark_returns.min(), benchmark_returns.max(), 100)
    
    fig.add_trace(go.Scatter(
        x=x_line * 100,
        y=p(x_line) * 100,
        mode='lines',
        name=f'Regression Line (β={beta:.2f})',
        line=dict(color='red', width=2)
    ))
    
    fig.update_layout(
        title=f"Beta Analysis<br><sub>β = {beta:.2f}</sub>",
        xaxis_title="Benchmark Return (%)",
        yaxis_title="Portfolio Return (%)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_chart_17_var_history(portfolio_returns, window=252, confidence=0.95):
    """
    Chart 17: Rolling Value at Risk History
    """
    from app.calculations import calculate_var
    
    # Calculate rolling VaR
    rolling_var = portfolio_returns.rolling(window=window).apply(
        lambda x: calculate_var(x.values, confidence) * 100
    )
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rolling_var.index,
        y=rolling_var.values,
        mode='lines',
        fill='tozeroy',
        name=f'VaR {confidence*100:.0f}%',
        line=dict(color='red', width=2),
        fillcolor='rgba(255, 0, 0, 0.3)'
    ))
    
    mean_var = rolling_var.mean()
    fig.add_hline(y=mean_var, line_dash="dash", line_color="yellow",
                  annotation_text=f"Mean VaR: {mean_var:.2f}%")
    
    fig.update_layout(
        title=f"Rolling Value at Risk ({confidence*100:.0f}% Confidence)<br><sub>Window: {window} days</sub>",
        xaxis_title="Date",
        yaxis_title="VaR (%)",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_chart_18_conditional_var(portfolio_returns, confidence=0.95):
    """
    Chart 18: Conditional VaR (Expected Shortfall)
    """
    from app.calculations import calculate_var, calculate_expected_shortfall
    
    returns = portfolio_returns.dropna() * 100
    var = calculate_var(returns.values, confidence)
    cvar = calculate_expected_shortfall(returns.values, confidence)
    
    fig = go.Figure()
    
    # Histogram
    fig.add_trace(go.Histogram(
        x=returns,
        nbinsx=50,
        marker=dict(color='blue', opacity=0.7),
        name='Returns Distribution'
    ))
    
    # VaR line
    fig.add_vline(x=var, line_dash="dash", line_color="red",
                  annotation_text=f"VaR {confidence*100:.0f}%: {var:.2f}%")
    
    # CVaR line
    fig.add_vline(x=cvar, line_dash="dash", line_color="darkred",
                  annotation_text=f"CVaR: {cvar:.2f}%")
    
    fig.update_layout(
        title=f"Conditional VaR (Expected Shortfall)<br><sub>VaR: {var:.2f}% | CVaR: {cvar:.2f}%</sub>",
        xaxis_title="Return (%)",
        yaxis_title="Frequency",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

# ===================== MARKET ANALYSIS CHARTS (19-24) =====================

def create_chart_19_benchmark_comparison(portfolio_cumulative, benchmark_cumulative, benchmark_name="S&P 500"):
    """
    Chart 19: Benchmark Comparison
    """
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=portfolio_cumulative.index,
        y=portfolio_cumulative.values,
        mode='lines',
        name='Portfolio',
        line=dict(color='blue', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=benchmark_cumulative.index,
        y=benchmark_cumulative.values,
        mode='lines',
        name=benchmark_name,
        line=dict(color='green', width=2, dash='dot')
    ))
    
    fig.update_layout(
        title=f"Performance vs {benchmark_name}",
        xaxis_title="Date",
        yaxis_title="Cumulative Return",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500,
        hovermode='x unified'
    )
    
    return fig

def create_chart_20_relative_performance(portfolio_returns, benchmark_returns, benchmark_name="S&P 500"):
    """
    Chart 20: Relative Performance (Active Return)
    """
    active_returns = portfolio_returns - benchmark_returns
    cumulative_active = (1 + active_returns).cumprod()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=cumulative_active.index,
        y=cumulative_active.values,
        mode='lines',
        fill='tozeroy',
        name='Active Return',
        line=dict(color='purple', width=2)
    ))
    
    fig.add_hline(y=1.0, line_dash="dash", line_color="gray",
                  annotation_text="Neutral (No outperformance)")
    
    fig.update_layout(
        title=f"Relative Performance vs {benchmark_name}",
        xaxis_title="Date",
        yaxis_title="Cumulative Active Return",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_chart_21_sector_allocation(weights_series, sector_mapping):
    """
    Chart 21: Sector Allocation
    
    Args:
        weights_series (pd.Series): Asset weights
        sector_mapping (dict): {ticker: sector}
    """
    # Aggregate by sector
    sector_weights = {}
    for ticker, weight in weights_series.items():
        sector = sector_mapping.get(ticker, 'Other')
        sector_weights[sector] = sector_weights.get(sector, 0) + weight
    
    fig = go.Figure(data=[go.Pie(
        labels=list(sector_weights.keys()),
        values=list(sector_weights.values()),
        hole=0.4,
        marker=dict(colors=CHART_COLORS['primary']),
        textinfo='label+percent'
    )])
    
    fig.update_layout(
        title="Portfolio Allocation by Sector",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_chart_22_geographic_exposure(weights_series, country_mapping):
    """
    Chart 22: Geographic Exposure
    
    Args:
        weights_series (pd.Series): Asset weights
        country_mapping (dict): {ticker: country}
    """
    # Aggregate by country
    country_weights = {}
    for ticker, weight in weights_series.items():
        country = country_mapping.get(ticker, 'Other')
        country_weights[country] = country_weights.get(country, 0) + weight
    
    fig = go.Figure(data=[go.Bar(
        x=list(country_weights.keys()),
        y=list(country_weights.values()),
        marker=dict(color=CHART_COLORS['primary']),
        text=[f"{v*100:.1f}%" for v in country_weights.values()],
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Geographic Exposure",
        xaxis_title="Country/Region",
        yaxis_title="Weight",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(tickformat=".0%"),
        height=500
    )
    
    return fig

def create_chart_23_market_regime(portfolio_returns, window=60):
    """
    Chart 23: Market Regime Analysis (Bull/Bear/Neutral)
    """
    # Simple regime detection based on rolling returns
    rolling_returns = portfolio_returns.rolling(window=window).mean() * 252
    
    # Define regimes
    regimes = []
    for ret in rolling_returns:
        if pd.isna(ret):
            regimes.append('Neutral')
        elif ret > 0.05:
            regimes.append('Bull')
        elif ret < -0.05:
            regimes.append('Bear')
        else:
            regimes.append('Neutral')
    
    regime_series = pd.Series(regimes, index=portfolio_returns.index)
    
    # Create color map
    color_map = {'Bull': 'green', 'Bear': 'red', 'Neutral': 'gray'}
    colors = [color_map[r] for r in regimes]
    
    fig = go.Figure()
    
    # Plot cumulative returns colored by regime
    cumulative = (1 + portfolio_returns).cumprod()
    
    fig.add_trace(go.Scatter(
        x=cumulative.index,
        y=cumulative.values,
        mode='lines',
        line=dict(color='white', width=2),
        name='Portfolio'
    ))
    
    # Add colored background regions
    for regime in ['Bull', 'Bear', 'Neutral']:
        mask = regime_series == regime
        if mask.any():
            fig.add_trace(go.Scatter(
                x=cumulative[mask].index,
                y=cumulative[mask].values,
                mode='markers',
                marker=dict(size=3, color=color_map[regime]),
                name=f'{regime} Market',
                showlegend=True
            ))
    
    fig.update_layout(
        title=f"Market Regime Analysis<br><sub>Window: {window} days</sub>",
        xaxis_title="Date",
        yaxis_title="Portfolio Value",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    return fig

def create_chart_24_correlation_with_markets(portfolio_returns, market_indices):
    """
    Chart 24: Correlation with Major Markets
    
    Args:
        portfolio_returns (pd.Series): Portfolio returns
        market_indices (dict): {name: returns_series}
    """
    correlations = {}
    for name, returns in market_indices.items():
        # Align indices
        common_idx = portfolio_returns.index.intersection(returns.index)
        if len(common_idx) > 30:
            corr = portfolio_returns[common_idx].corr(returns[common_idx])
            correlations[name] = corr
    
    fig = go.Figure(data=[go.Bar(
        x=list(correlations.keys()),
        y=list(correlations.values()),
        marker=dict(
            color=list(correlations.values()),
            colorscale='RdBu',
            cmin=-1,
            cmax=1,
            colorbar=dict(title="Correlation")
        ),
        text=[f"{v:.2f}" for v in correlations.values()],
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Correlation with Major Market Indices",
        xaxis_title="Market Index",
        yaxis_title="Correlation Coefficient",
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        yaxis=dict(range=[-1, 1]),
        height=500
    )
    
    return fig

# ===================== CHART MAPPING =====================

CHART_FUNCTIONS = {
    1: create_chart_1_allocation,
    2: create_chart_2_value_distribution,
    3: create_chart_3_cumulative_returns,
    4: create_chart_4_returns_distribution,
    5: create_chart_5_correlation_heatmap,
    6: create_chart_6_rolling_volatility,
    7: create_chart_7_mc_price_paths,
    8: create_chart_8_mc_returns_distribution,
    9: create_chart_9_var_analysis,
    10: create_chart_10_confidence_intervals,
    11: create_chart_11_risk_adjusted_performance,
    12: create_chart_12_scenario_analysis,
    13: create_chart_13_sharpe_evolution,
    14: create_chart_14_max_drawdown,
    15: create_chart_15_risk_return_scatter,
    16: create_chart_16_beta_analysis,
    17: create_chart_17_var_history,
    18: create_chart_18_conditional_var,
    19: create_chart_19_benchmark_comparison,
    20: create_chart_20_relative_performance,
    21: create_chart_21_sector_allocation,
    22: create_chart_22_geographic_exposure,
    23: create_chart_23_market_regime,
    24: create_chart_24_correlation_with_markets,
}

def get_chart_function(chart_number):
    """Get chart function by number"""
    return CHART_FUNCTIONS.get(chart_number)

