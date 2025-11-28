# utils_math.py - Mathematical calculations (MC, risk metrics)
import numpy as np
import pandas as pd

def ledoit_cov(X: np.ndarray):
    """Ledoit-Wolf shrinkage covariance estimation."""
    try:
        from sklearn.covariance import LedoitWolf
        return LedoitWolf().fit(X).covariance_
    except Exception:
        return np.cov(X, rowvar=False, ddof=1)

def compute_portfolio_metrics(prices: pd.DataFrame, weights_raw: dict, cov_method="ledoit", annualization=252):
    """Compute portfolio metrics from price data and weights."""
    # Utiliser uniquement les ETF présents + renormaliser les poids
    available = [c for c in weights_raw if c in prices.columns]
    missing   = [c for c in weights_raw if c not in prices.columns]
    if missing:
        print("Poids ignorés (ETF introuvables):", missing)

    w = np.array([weights_raw[c] for c in available], dtype=float)
    w = w / w.sum()
    w_series = pd.Series(w, index=available)

    rets = np.log(prices[available] / prices[available].shift(1)).dropna()
    if rets.empty:
        raise RuntimeError("Pas assez de retours pour calculer les métriques.")

    # mu, cov (journalier -> annualisé)
    cov_d = ledoit_cov(rets.values) if cov_method=="ledoit" else rets.cov().values
    mu_d  = rets.mean().values
    mu_a  = mu_d * annualization
    cov_a = cov_d * annualization

    # Retour portefeuille comme Series alignée
    port_ret_d = pd.Series(rets.values @ w, index=rets.index, name="Portfolio")

    # Contributions au risque (marginales * poids)
    vol_a = float(np.sqrt(w @ cov_a @ w))
    mcr   = (cov_a @ w) / max(vol_a, 1e-12)
    cr    = w * mcr
    cr_pct = cr / max(cr.sum(), 1e-12)

    return {
        "cols": available, "w": w, "w_series": w_series,
        "rets_d": rets, "mu_a": mu_a, "cov_a": cov_a,
        "port_ret_d": port_ret_d,
        "corr": rets.corr(),
        "cr_pct": cr_pct, "vol_a": vol_a
    }

def compute_benchmark_params(bench_prices: pd.DataFrame, bench_def: list, annualization=252):
    """Compute benchmark parameters from price data."""
    out = {}
    for label, tick in bench_def:
        if tick in bench_prices.columns:
            r = np.log(bench_prices[tick] / bench_prices[tick].shift(1)).dropna()
            if len(r) >= 30:
                out[label] = {
                    "mu_ann":  float(r.mean()*annualization),
                    "vol_ann": float(r.std(ddof=1)*np.sqrt(annualization))
                }
    return out

# ---------- RISK MEASURES ----------
def calculate_var(rets, confidence_level=0.95):
    """Calculate Value at Risk (VaR) at specified confidence level."""
    return np.percentile(rets, (1 - confidence_level) * 100)

def calculate_expected_shortfall(rets, confidence_level=0.95):
    """Calculate Expected Shortfall (CVaR) at specified confidence level."""
    var = calculate_var(rets, confidence_level)
    return rets[rets <= var].mean()

def calculate_max_drawdown_duration(values):
    """Calculate maximum drawdown duration in periods."""
    peak = np.maximum.accumulate(values)
    drawdown = (values - peak) / peak
    underwater = drawdown < 0
    
    durations = []
    current_duration = 0
    
    for is_underwater in underwater:
        if is_underwater:
            current_duration += 1
        else:
            if current_duration > 0:
                durations.append(current_duration)
            current_duration = 0
    
    if current_duration > 0:
        durations.append(current_duration)
    
    return max(durations) if durations else 0

def calculate_calmar_ratio(annual_return, max_drawdown):
    """Calculate Calmar Ratio: Annual Return / Maximum Drawdown."""
    if max_drawdown == 0:
        return np.inf if annual_return > 0 else 0
    return annual_return / abs(max_drawdown)

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe Ratio: (Mean Return - Risk Free Rate) / Std Deviation.
    
    Args:
        returns: Array of returns (annualized)
        risk_free_rate: Annual risk-free rate (default 2%)
    
    Returns:
        Sharpe Ratio value
    """
    mean_return = np.mean(returns)
    std_return = np.std(returns)
    
    if std_return == 0:
        return 0
    
    sharpe = (mean_return - risk_free_rate) / std_return
    return sharpe

# ---------- MONTE CARLO ----------
def mc_gaussian(mu_a, cov_a, w, start_value, steps, paths, month_factor=12):
    """MC multi-actifs mensuel (Normal, covariance préservée) - SANS randomness."""
    w = w.reshape(-1,1)
    mu_m  = (mu_a / month_factor).reshape(-1,1)
    cov_m =  cov_a / month_factor
    # Cholesky avec petite régularisation si nécessaire
    try:
        L = np.linalg.cholesky(cov_m + 1e-12*np.eye(cov_m.shape[0]))
    except np.linalg.LinAlgError:
        L = np.linalg.cholesky(cov_m + 1e-6*np.eye(cov_m.shape[0]))
    out = np.empty((steps+1, paths)); out[0] = start_value
    for t in range(1, steps+1):
        Z = np.random.randn(cov_m.shape[0], paths)
        r = mu_m + L @ Z
        pr = (w.T @ r).ravel()            # retour mensuel du portefeuille
        out[t] = out[t-1]*(1+pr)
    return out

def mc_gaussian_with_randomness(mu_a, cov_a, w, start_value, steps, paths, randomness_factor=0.30, month_factor=12):
    """MC multi-actifs avec sauts aléatoires et volatilité stochastique."""
    w = w.reshape(-1,1)
    mu_m  = (mu_a / month_factor).reshape(-1,1)
    cov_m =  cov_a / month_factor
    
    # Cholesky avec petite régularisation si nécessaire
    try:
        L = np.linalg.cholesky(cov_m + 1e-12*np.eye(cov_m.shape[0]))
    except np.linalg.LinAlgError:
        L = np.linalg.cholesky(cov_m + 1e-6*np.eye(cov_m.shape[0]))
    
    out = np.empty((steps+1, paths)); out[0] = start_value
    
    for t in range(1, steps+1):
        # Simulation normale
        Z = np.random.randn(cov_m.shape[0], paths)
        r_normal = mu_m + L @ Z
        
        # Ajout de randomness avec sauts aléatoires
        jump_prob = 0.05  # 5% de chance de saut par mois
        jump_size = np.random.normal(0, randomness_factor, (cov_m.shape[0], paths))
        jump_mask = np.random.random((cov_m.shape[0], paths)) < jump_prob
        
        # Volatilité stochastique (varie dans le temps)
        vol_multiplier = 1 + np.random.normal(0, randomness_factor/2, (cov_m.shape[0], paths))
        vol_multiplier = np.clip(vol_multiplier, 0.5, 2.0)  # Limite entre 0.5x et 2x
        
        # Application des effets
        r_jumps = jump_size * jump_mask
        r_stochastic = r_normal * vol_multiplier
        
        # Retour final avec randomness
        r_final = r_stochastic + r_jumps
        pr = (w.T @ r_final).ravel()  # retour mensuel du portefeuille
        
        # Limitation des retours extrêmes
        pr = np.clip(pr, -0.5, 1.0)  # Entre -50% et +100%
        
        out[t] = out[t-1]*(1+pr)
    
    return out

def mc_single_asset(mu_ann, vol_ann, start_value, steps, paths, month_factor=12):
    """MC mono-actif mensuel."""
    mu_m  = mu_ann / month_factor
    sig_m = vol_ann / np.sqrt(month_factor)
    out = np.empty((steps+1, paths)); out[0] = start_value
    for t in range(1, steps+1):
        r = np.random.randn(paths)*sig_m + mu_m
        out[t] = out[t-1]*(1+r)
    return out

def compute_median_monthly_returns(paths):
    """Return a 1D series of median monthly returns from simulated paths."""
    monthly = paths[1:, :] / paths[:-1, :] - 1.0
    return np.median(monthly, axis=1)

def estimate_beta_vs_benchmark(portfolio_paths, bench_paths):
    """Estimate beta using simulated monthly returns (median regression proxy)."""
    pr = portfolio_paths[1:, :] / portfolio_paths[:-1, :] - 1.0
    br = bench_paths[1:, :] / bench_paths[:-1, :] - 1.0
    # Use medians across paths to get a single time series per asset
    pr_m = np.median(pr, axis=1)
    br_m = np.median(br, axis=1)
    cov = np.cov(pr_m, br_m)
    if cov[1,1] == 0:
        return 0.0
    return cov[0,1] / cov[1,1]