# charts/__init__.py - Charts Module
"""
Chart generation modules for Portfolio Analysis.

Contains all chart generators:
- Portfolio charts
- Sector charts
- Benchmark charts
- Monte Carlo charts
- Risk metrics charts
- Regime analysis charts
- Sector projection charts
"""

# Import chart modules (imported on demand to avoid circular imports)
__all__ = [
    'chart_portfolio',
    'chart_sector',
    'chart_benchmarks',
    'chart_monte_carlo',
    'chart_risk_metrics',
    'chart_regime',
    'chart_sector_projection'
]


