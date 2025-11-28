# 🎨 Nouveau Layout du Menu Principal

## ✅ Modifications Apportées

### 1. Split Vertical (55% / 45%)
```
┌─────────────────────────────────────────────────────────────────────┐
│  Portfolio Analysis Studio    Capital: [10,000] [USD ▼] ● Ready    │
├──────────────────────────┬──────────────────────────────────────────┤
│                          │                                          │
│  GAUCHE (55%)            │  DROITE (45%)                           │
│  Configuration           │  Sélection Charts                        │
│                          │                                          │
│ ┌─ 💱 Market Data ─────┐ │ ┌─ 📊 Analysis Charts ──────────────┐  │
│ │ [Refresh]            │ │ │                    [All] [None]   │  │
│ ├───────────┬──────────┤ │ ├────────────────────────────────────┤  │
│ │ Forex     │ Indexes  │ │ │                                    │  │
│ │ EUR: 1.09 │ S&P: 5K  │ │ │ ▼ Core Portfolio Analysis          │  │
│ │ GBP: 1.27 │ Dow: 40K │ │ │ ☑ 📊 Portfolio Performance         │  │
│ │ JPY: 149  │ Nas: 16K │ │ │    Cumulative returns vs benchmarks│  │
│ │ CHF: 0.88 │ FTS: 8K  │ │ │ ☑ ⚠️ Risk Metrics Dashboard        │  │
│ └───────────┴──────────┘ │ │    Volatility, VaR, Sharpe...      │  │
│                          │ │ ☑ 📈 Benchmark Comparison          │  │
│ ┌─ 📊 Portfolio ───────┐ │ │    Performance vs selected indexes │  │
│ │  [Equal][Norm][Clear]│ │ │                                    │  │
│ ├──────────────────────┤ │ │ ▼ Sector Analysis                  │  │
│ │ Ticker  Wgt%  Amount │ │ │ ☑ 🏢 Sector Allocation             │  │
│ │ [    ]  [  ]  [    ] │ │ │    Current sector breakdown        │  │
│ │ (10 lignes)          │ │ │ ☑ 🎯 Sector Projections            │  │
│ ├──────────────────────┤ │ │    Monte Carlo by sector           │  │
│ │ Total: 0%            │ │ │                                    │  │
│ └──────────────────────┘ │ │ ▼ Advanced Analytics               │  │
│                          │ │ ☑ 🎲 Monte Carlo Simulation        │  │
│ ┌─ 📈 Benchmarks ──────┐ │ │    Probabilistic projections       │  │
│ │ [^GSPC]              │ │ │ ☑ 🌊 Market Regime Analysis        │  │
│ │ [^NDX ]              │ │ │    Performance in regimes          │  │
│ │ (5 lignes)           │ │ │                                    │  │
│ └──────────────────────┘ │ └────────────────────────────────────┘  │
│                          │                                          │
├──────────────────────────┴──────────────────────────────────────────┤
│                  [📊 Run Portfolio Analysis]                        │
└─────────────────────────────────────────────────────────────────────┘
```

## 🎯 Changements Clés

### ✅ Ajouté
1. **Section Market Data en haut à gauche** :
   - Forex Rates (EUR, GBP, JPY, CHF) vs USD
   - Major Indexes (S&P 500, Dow Jones, Nasdaq, FTSE 100)
   - Bouton Refresh intégré
   - Données en temps réel avec couleurs (vert/rouge)

2. **Sélection de charts intégrée à droite** :
   - Visible en permanence (pas de dialogue)
   - 3 catégories : Core, Sector, Advanced
   - Icônes visuelles : 📊 ⚠️ 📈 🏢 🎯 🎲 🌊
   - Descriptions claires pour chaque chart
   - Boutons All/None pour sélection rapide

3. **Toolbar moderne en haut** :
   - Capital et devise
   - Status indicator (● Ready)

### ❌ Supprimé
1. **Section Analysis Period** :
   - Plus nécessaire car le backtest prend automatiquement la date la plus ancienne disponible

## 📊 Avantages

### Efficacité
- ✅ **Tout visible d'un coup** : Plus besoin d'ouvrir de dialogue
- ✅ **Market data toujours affichée** : Contexte de marché disponible en permanence
- ✅ **Workflow optimisé** : Configuration à gauche, sélection à droite

### Visuel
- ✅ **Interface professionnelle** : Design épuré et moderne
- ✅ **Icônes significatives** : Identification rapide des charts
- ✅ **Couleurs dynamiques** : Vert/rouge pour les variations d'indexes

### UX
- ✅ **Moins de clics** : Tout est accessible directement
- ✅ **Contexte clair** : Market data aide à comprendre l'environnement
- ✅ **Sélection intuitive** : Charts organisés logiquement

## 🚀 Test

```bash
# Lancer le nouveau menu
cd Portfolio
python ui/menu_principal_v2.py

# Ou via app.py (après mise à jour)
python app.py
```

## 📝 Détails Techniques

### Structure des Panels

**Panel Gauche (55%)** :
1. Market Data (fixe en haut)
   - Forex rates + Major indexes en 2 colonnes
2. Portfolio (scrollable)
   - 10 lignes de tickers
   - Actions : Equal, Normalize, Clear
3. Benchmarks (scrollable)
   - 5 lignes de benchmarks

**Panel Droite (45%)** :
- Sélection de charts par catégorie
- Scrollable pour plus de charts si nécessaire
- Checkboxes avec icônes et descriptions

### Fonctionnalités

**Market Data** :
- ✅ Rafraîchissement en temps réel (background thread)
- ✅ Bouton refresh manuel
- ✅ Couleurs dynamiques pour les variations
- ✅ Format adapté (4 décimales forex, 0 décimales indexes)

**Charts** :
- ✅ 7 charts définis par défaut
- ✅ Sélection/désélection facile
- ✅ Boutons All/None
- ✅ Descriptions explicatives

## 💡 Pourquoi Ces Changements ?

### Market Data en Haut
- **Contexte** : Voir immédiatement l'état du marché
- **Pertinence** : Aide à comprendre la performance du portfolio
- **Professionnel** : Comme sur Bloomberg/Reuters

### Pas de Analysis Period
- **Automatique** : Le backtest prend la date la plus ancienne
- **Simplicité** : Moins de configuration manuelle
- **Focus** : Sur ce qui compte vraiment (les actifs)

### Split Vertical
- **Visibilité** : Tout est visible simultanément
- **Logique** : Configuration à gauche, actions à droite
- **Efficacité** : Workflow naturel de gauche à droite

## 🎨 Prochaines Étapes

1. ✅ Tester le menu (en cours)
2. ⏳ Connecter toute la logique métier
3. ⏳ Remplacer l'ancien menu
4. ⏳ Ajouter validation des tickers
5. ⏳ Implémenter run_analysis complet

---

**C'est exactement ce que vous vouliez ?** 🎯

