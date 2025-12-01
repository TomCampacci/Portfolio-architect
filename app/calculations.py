"""
Module de calculs financiers pour Portfolio Architect
Porté depuis utils_math.py (version Tkinter)

Contient tous les calculs sophistiqués :
- Métriques de portfolio (rendements, volatilité, corrélations)
- Métriques de risque (VaR, CVaR, Max Drawdown, Sharpe, Sortino, Calmar)
- Simulations Monte Carlo (gaussien normal et avec randomness)
- Calculs de beta vs benchmark
"""

import numpy as np
import pandas as pd
import streamlit as st

# ===================== COVARIANCE ESTIMATION =====================

def ledoit_cov(X: np.ndarray):
    """
    Estimation de covariance avec shrinkage Ledoit-Wolf
    
    Plus robuste que la covariance empirique, particulièrement pour
    les petits échantillons ou matrices mal conditionnées.
    
    Args:
        X (np.ndarray): Matrice des retours (observations x assets)
    
    Returns:
        np.ndarray: Matrice de covariance estimée
    """
    try:
        from sklearn.covariance import LedoitWolf
        return LedoitWolf().fit(X).covariance_
    except ImportError:
        # Fallback to standard covariance if sklearn not available
        st.warning("sklearn non disponible, utilisation de la covariance standard")
        return np.cov(X, rowvar=False, ddof=1)
    except Exception:
        return np.cov(X, rowvar=False, ddof=1)

# ===================== PORTFOLIO METRICS =====================

def compute_portfolio_metrics(prices: pd.DataFrame, weights_raw: dict, 
                              cov_method="ledoit", annualization=252):
    """
    Calcule toutes les métriques du portfolio à partir des prix et poids
    
    Args:
        prices (pd.DataFrame): Prix historiques (index=dates, columns=tickers)
        weights_raw (dict): Dictionnaire {ticker: weight}
        cov_method (str): Méthode de covariance ("ledoit" ou "standard")
        annualization (int): Facteur d'annualisation (252 pour daily, 12 pour monthly)
    
    Returns:
        dict: Contient:
            - cols: Liste des tickers disponibles
            - w: Array des poids normalisés
            - w_series: Series des poids
            - rets_d: DataFrame des retours journaliers
            - mu_a: Retours annualisés moyens
            - cov_a: Matrice de covariance annualisée
            - port_ret_d: Series des retours du portfolio
            - corr: Matrice de corrélation
            - cr_pct: Contributions au risque (%)
            - vol_a: Volatilité annualisée du portfolio
    """
    # Filtrer uniquement les assets présents dans les prix
    available = [c for c in weights_raw if c in prices.columns]
    missing = [c for c in weights_raw if c not in prices.columns]
    
    if missing:
        st.warning(f"Tickers ignorés (données introuvables): {', '.join(missing)}")
    
    if not available:
        raise RuntimeError("Aucun ticker valide trouvé dans les données de prix")
    
    # Normaliser les poids (somme = 1)
    w = np.array([weights_raw[c] for c in available], dtype=float)
    w = w / w.sum()
    w_series = pd.Series(w, index=available)
    
    # Calculer les retours logarithmiques
    rets = np.log(prices[available] / prices[available].shift(1)).dropna()
    
    if rets.empty or len(rets) < 2:
        raise RuntimeError("Pas assez de données pour calculer les métriques (minimum 2 périodes)")
    
    # Calcul de la covariance et des moyennes
    if cov_method == "ledoit":
        cov_d = ledoit_cov(rets.values)
    else:
        cov_d = rets.cov().values
    
    mu_d = rets.mean().values
    
    # Annualisation
    mu_a = mu_d * annualization
    cov_a = cov_d * annualization
    
    # Retours du portfolio
    port_ret_d = pd.Series(rets.values @ w, index=rets.index, name="Portfolio")
    
    # Contributions au risque (Risk Contributions)
    vol_a = float(np.sqrt(w @ cov_a @ w))
    mcr = (cov_a @ w) / max(vol_a, 1e-12)  # Marginal Contribution to Risk
    cr = w * mcr  # Risk Contribution
    cr_pct = cr / max(cr.sum(), 1e-12)  # Contribution en %
    
    return {
        "cols": available,
        "w": w,
        "w_series": w_series,
        "rets_d": rets,
        "mu_a": mu_a,
        "cov_a": cov_a,
        "port_ret_d": port_ret_d,
        "corr": rets.corr(),
        "cr_pct": cr_pct,
        "vol_a": vol_a
    }

# ===================== BENCHMARK METRICS =====================

def compute_benchmark_params(bench_prices: pd.DataFrame, bench_def: list, 
                            annualization=252):
    """
    Calcule les paramètres des benchmarks
    
    Args:
        bench_prices (pd.DataFrame): Prix des benchmarks
        bench_def (list): Liste de tuples (label, ticker)
        annualization (int): Facteur d'annualisation
    
    Returns:
        dict: {label: {'mu_ann': float, 'vol_ann': float}}
    """
    out = {}
    for label, tick in bench_def:
        if tick in bench_prices.columns:
            r = np.log(bench_prices[tick] / bench_prices[tick].shift(1)).dropna()
            if len(r) >= 30:  # Minimum 30 observations
                out[label] = {
                    "mu_ann": float(r.mean() * annualization),
                    "vol_ann": float(r.std(ddof=1) * np.sqrt(annualization))
                }
    return out

# ===================== RISK MEASURES =====================

def calculate_var(rets, confidence_level=0.95):
    """
    Calcule la Value at Risk (VaR) au niveau de confiance spécifié
    
    La VaR représente la perte maximale attendue sur une période donnée
    avec un niveau de confiance donné (ex: 95% = perte dépassée dans 5% des cas)
    
    Args:
        rets (array-like): Array des retours
        confidence_level (float): Niveau de confiance (0.95 = 95%)
    
    Returns:
        float: Valeur de la VaR (négatif = perte)
    """
    return np.percentile(rets, (1 - confidence_level) * 100)

def calculate_expected_shortfall(rets, confidence_level=0.95):
    """
    Calcule l'Expected Shortfall (ES) / Conditional VaR (CVaR)
    
    L'ES est la perte moyenne attendue dans les scénarios où
    la perte dépasse la VaR. Plus conservateur que la VaR.
    
    Args:
        rets (array-like): Array des retours
        confidence_level (float): Niveau de confiance (0.95 = 95%)
    
    Returns:
        float: Valeur de l'ES (négatif = perte moyenne conditionnelle)
    """
    var = calculate_var(rets, confidence_level)
    return rets[rets <= var].mean()

def calculate_max_drawdown_duration(values):
    """
    Calcule la durée maximale du drawdown en nombre de périodes
    
    Mesure combien de temps le portfolio reste "sous l'eau"
    (en dessous de son précédent sommet).
    
    Args:
        values (array-like): Série de valeurs du portfolio
    
    Returns:
        int: Durée maximale du drawdown en périodes
    """
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
    """
    Calcule le ratio de Calmar : Rendement annuel / Maximum Drawdown
    
    Mesure le rendement ajusté pour le risque de drawdown.
    Plus le ratio est élevé, meilleur est le profil risque/rendement.
    
    Args:
        annual_return (float): Rendement annuel
        max_drawdown (float): Maximum drawdown (positif)
    
    Returns:
        float: Ratio de Calmar
    """
    if max_drawdown == 0:
        return np.inf if annual_return > 0 else 0
    return annual_return / abs(max_drawdown)

def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """
    Calcule le ratio de Sharpe : (Rendement moyen - Taux sans risque) / Écart-type
    
    Mesure le rendement excédentaire par unité de risque total.
    
    Args:
        returns (array-like): Array des retours (annualisés)
        risk_free_rate (float): Taux sans risque annuel (défaut 2%)
    
    Returns:
        float: Ratio de Sharpe
    """
    mean_return = np.mean(returns)
    std_return = np.std(returns, ddof=1)
    
    if std_return == 0:
        return 0
    
    sharpe = (mean_return - risk_free_rate) / std_return
    return sharpe

def calculate_sortino_ratio(returns, risk_free_rate=0.02, target_return=0):
    """
    Calcule le ratio de Sortino : (Rendement moyen - Cible) / Downside deviation
    
    Similaire au Sharpe mais pénalise uniquement la volatilité négative (downside).
    
    Args:
        returns (array-like): Array des retours
        risk_free_rate (float): Taux sans risque annuel
        target_return (float): Rendement cible (défaut 0)
    
    Returns:
        float: Ratio de Sortino
    """
    mean_return = np.mean(returns)
    downside_returns = returns[returns < target_return]
    
    if len(downside_returns) == 0:
        return np.inf if mean_return > risk_free_rate else 0
    
    downside_deviation = np.std(downside_returns, ddof=1)
    
    if downside_deviation == 0:
        return 0
    
    sortino = (mean_return - risk_free_rate) / downside_deviation
    return sortino

# ===================== MONTE CARLO SIMULATIONS =====================

def mc_gaussian(mu_a, cov_a, w, start_value, steps, paths, month_factor=12):
    """
    Simulation Monte Carlo multi-assets gaussienne (sans randomness supplémentaire)
    
    Simule l'évolution du portfolio avec distribution normale multivariée.
    Préserve la structure de covariance entre les actifs.
    
    Args:
        mu_a (np.ndarray): Rendements annuels moyens par asset
        cov_a (np.ndarray): Matrice de covariance annualisée
        w (np.ndarray): Poids du portfolio
        start_value (float): Valeur initiale
        steps (int): Nombre de pas temporels (mois)
        paths (int): Nombre de simulations
        month_factor (int): Facteur de conversion annuel vers mensuel (12)
    
    Returns:
        np.ndarray: Matrice (steps+1, paths) des valeurs simulées
    """
    w = w.reshape(-1, 1)
    mu_m = (mu_a / month_factor).reshape(-1, 1)
    cov_m = cov_a / month_factor
    
    # Décomposition de Cholesky avec régularisation si nécessaire
    try:
        L = np.linalg.cholesky(cov_m + 1e-12 * np.eye(cov_m.shape[0]))
    except np.linalg.LinAlgError:
        # Matrice mal conditionnée, augmenter la régularisation
        L = np.linalg.cholesky(cov_m + 1e-6 * np.eye(cov_m.shape[0]))
    
    out = np.empty((steps + 1, paths))
    out[0] = start_value
    
    for t in range(1, steps + 1):
        Z = np.random.randn(cov_m.shape[0], paths)
        r = mu_m + L @ Z  # Retours multivariés corrélés
        pr = (w.T @ r).ravel()  # Retour du portfolio
        out[t] = out[t - 1] * (1 + pr)
    
    return out

def mc_gaussian_with_randomness(mu_a, cov_a, w, start_value, steps, paths, 
                                randomness_factor=0.30, month_factor=12):
    """
    Simulation Monte Carlo avec sauts aléatoires et volatilité stochastique
    
    Modèle plus réaliste incluant :
    - Sauts soudains (jump process) - 5% de probabilité par mois
    - Volatilité stochastique (varie dans le temps)
    - Limitation des retours extrêmes
    
    Args:
        mu_a (np.ndarray): Rendements annuels moyens
        cov_a (np.ndarray): Matrice de covariance annualisée
        w (np.ndarray): Poids du portfolio
        start_value (float): Valeur initiale
        steps (int): Nombre de pas (mois)
        paths (int): Nombre de simulations
        randomness_factor (float): Facteur de randomness (0.3 = 30%)
        month_factor (int): Conversion annuel → mensuel
    
    Returns:
        np.ndarray: Matrice (steps+1, paths) des valeurs simulées
    """
    w = w.reshape(-1, 1)
    mu_m = (mu_a / month_factor).reshape(-1, 1)
    cov_m = cov_a / month_factor
    
    # Cholesky avec régularisation
    try:
        L = np.linalg.cholesky(cov_m + 1e-12 * np.eye(cov_m.shape[0]))
    except np.linalg.LinAlgError:
        L = np.linalg.cholesky(cov_m + 1e-6 * np.eye(cov_m.shape[0]))
    
    out = np.empty((steps + 1, paths))
    out[0] = start_value
    
    for t in range(1, steps + 1):
        # Simulation normale de base
        Z = np.random.randn(cov_m.shape[0], paths)
        r_normal = mu_m + L @ Z
        
        # Sauts aléatoires (jump process)
        jump_prob = 0.05  # 5% de chance de saut par mois
        jump_size = np.random.normal(0, randomness_factor, (cov_m.shape[0], paths))
        jump_mask = np.random.random((cov_m.shape[0], paths)) < jump_prob
        
        # Volatilité stochastique (varie dans le temps)
        vol_multiplier = 1 + np.random.normal(0, randomness_factor / 2, (cov_m.shape[0], paths))
        vol_multiplier = np.clip(vol_multiplier, 0.5, 2.0)  # Entre 0.5x et 2x
        
        # Application des effets
        r_jumps = jump_size * jump_mask
        r_stochastic = r_normal * vol_multiplier
        
        # Retour final avec randomness
        r_final = r_stochastic + r_jumps
        pr = (w.T @ r_final).ravel()
        
        # Limitation des retours extrêmes (éviter explosion/implosion)
        pr = np.clip(pr, -0.5, 1.0)  # Entre -50% et +100% par mois
        
        out[t] = out[t - 1] * (1 + pr)
    
    return out

def mc_single_asset(mu_ann, vol_ann, start_value, steps, paths, month_factor=12):
    """
    Simulation Monte Carlo pour un actif unique (benchmark)
    
    Args:
        mu_ann (float): Rendement annuel moyen
        vol_ann (float): Volatilité annuelle
        start_value (float): Valeur initiale
        steps (int): Nombre de pas (mois)
        paths (int): Nombre de simulations
        month_factor (int): Conversion annuel → mensuel
    
    Returns:
        np.ndarray: Matrice (steps+1, paths) des valeurs simulées
    """
    mu_m = mu_ann / month_factor
    sig_m = vol_ann / np.sqrt(month_factor)
    
    out = np.empty((steps + 1, paths))
    out[0] = start_value
    
    for t in range(1, steps + 1):
        r = np.random.randn(paths) * sig_m + mu_m
        out[t] = out[t - 1] * (1 + r)
    
    return out

# ===================== MONTE CARLO ANALYSIS =====================

def compute_median_monthly_returns(paths):
    """
    Calcule la médiane des retours mensuels depuis les chemins simulés
    
    Args:
        paths (np.ndarray): Matrice (steps+1, paths) des valeurs simulées
    
    Returns:
        np.ndarray: Array 1D des retours mensuels médians
    """
    monthly = paths[1:, :] / paths[:-1, :] - 1.0
    return np.median(monthly, axis=1)

def estimate_beta_vs_benchmark(portfolio_paths, bench_paths):
    """
    Estime le beta du portfolio vs benchmark depuis les simulations
    
    Beta = Cov(portfolio, benchmark) / Var(benchmark)
    
    Args:
        portfolio_paths (np.ndarray): Chemins simulés du portfolio
        bench_paths (np.ndarray): Chemins simulés du benchmark
    
    Returns:
        float: Beta estimé
    """
    pr = portfolio_paths[1:, :] / portfolio_paths[:-1, :] - 1.0
    br = bench_paths[1:, :] / bench_paths[:-1, :] - 1.0
    
    # Utiliser les médianes pour obtenir une série temporelle par asset
    pr_m = np.median(pr, axis=1)
    br_m = np.median(br, axis=1)
    
    cov = np.cov(pr_m, br_m)
    
    if cov[1, 1] == 0:
        return 0.0
    
    return cov[0, 1] / cov[1, 1]

# ===================== ADDITIONAL METRICS =====================

def calculate_max_drawdown(values):
    """
    Calcule le maximum drawdown (MDD) d'une série de valeurs
    
    Args:
        values (array-like): Série de valeurs du portfolio
    
    Returns:
        float: Maximum drawdown en pourcentage (négatif)
    """
    peak = np.maximum.accumulate(values)
    drawdown = (values - peak) / peak
    return np.min(drawdown)

def calculate_rolling_sharpe(returns, window=252, risk_free_rate=0.02):
    """
    Calcule le ratio de Sharpe rolling sur une fenêtre mobile
    
    Args:
        returns (pd.Series): Série des retours
        window (int): Taille de la fenêtre (252 = 1 an de trading)
        risk_free_rate (float): Taux sans risque annuel
    
    Returns:
        pd.Series: Sharpe ratios rolling
    """
    rolling_mean = returns.rolling(window=window).mean() * 252
    rolling_std = returns.rolling(window=window).std() * np.sqrt(252)
    
    sharpe_rolling = (rolling_mean - risk_free_rate) / rolling_std
    return sharpe_rolling

def calculate_rolling_volatility(returns, window=252):
    """
    Calcule la volatilité rolling annualisée
    
    Args:
        returns (pd.Series): Série des retours
        window (int): Taille de la fenêtre
    
    Returns:
        pd.Series: Volatilité rolling annualisée
    """
    return returns.rolling(window=window).std() * np.sqrt(252)

