# 🏗️ Guide d'Architecture - Portfolio Architect (Streamlit)

## 📂 Structure du Projet

```
Portfolio/
│
├── 📱 APPLICATION PRINCIPALE
│   ├── streamlit_app.py              # Point d'entrée (interface utilisateur)
│   └── app/                          # Modules organisés par fonction
│       ├── __init__.py
│       ├── config.py                 # ⚙️ Configuration & constantes
│       ├── data_fetcher.py           # 📊 Récupération données Yahoo Finance
│       ├── calculations.py           # 🧮 Calculs financiers (À CRÉER)
│       ├── charts.py                 # 📈 Génération graphiques (À CRÉER)
│       └── ui_components.py          # 🎨 Composants UI réutilisables (À CRÉER)
│
├── ⚙️ CONFIGURATION
│   ├── .streamlit/
│   │   └── config.toml               # 🎨 Personnalisation couleurs & thème
│   ├── requirements.txt              # 📦 Dépendances Python
│   └── .gitignore                    # 🚫 Fichiers ignorés par Git
│
├── 📚 DONNÉES & CACHE
│   └── data/
│       ├── benchmarks.csv
│       ├── weights.csv
│       └── *_cache.json
│
├── 🗄️ ARCHIVE
│   └── _archive_tkinter/             # Ancien code Tkinter (référence)
│       ├── app.py
│       ├── ui/
│       ├── core/
│       └── README_ARCHIVE.md
│
└── 📖 DOCUMENTATION
    ├── ARCHITECTURE_GUIDE.md         # Ce fichier
    ├── README.md
    └── _docs/                        # Documentation technique
```

---

## 🎯 Modules et Responsabilités

### **1. `streamlit_app.py`** - Point d'entrée principal
**Responsabilité :** Interface utilisateur et flux de l'application

**Contient :**
- Configuration de la page Streamlit
- Layout principal (sidebar, tabs)
- Orchestration des différentes sections
- Appels aux modules `app/*`

**Quand modifier :**
- Ajouter/supprimer des onglets
- Changer le layout général
- Modifier le flux utilisateur

---

### **2. `app/config.py`** - Configuration et constantes
**Responsabilité :** Toutes les constantes et configurations centralisées

**Contient :**
- `POPULAR_TICKERS`: Base de données tickers populaires
- `QUICK_SELECT_OPTIONS`: Options du selectbox rapide
- `CHART_DESCRIPTIONS`: Descriptions des 24 graphiques
- `CHART_COLORS`: Palette de couleurs pour graphiques
- `DEFAULT_*`: Valeurs par défaut (capital, devise, période)
- `API_SETTINGS`: Paramètres API (timeouts, limites)

**Quand modifier :**
- Ajouter des tickers populaires
- Changer les couleurs des graphiques
- Modifier les valeurs par défaut
- Ajouter de nouvelles constantes

**Exemple :**
```python
# Ajouter un nouveau ticker populaire
POPULAR_TICKERS["BNP.PA"] = {
    "name": "BNP Paribas",
    "exchange": "Euronext Paris"
}
```

---

### **3. `app/data_fetcher.py`** - Récupération de données
**Responsabilité :** Communication avec Yahoo Finance et validation

**Contient :**
- `validate_and_get_ticker_info()`: Validation ticker + infos
- `search_tickers()`: Recherche de tickers
- `fetch_historical_prices()`: Prix historiques
- `get_current_price()`: Prix actuel
- `fetch_market_data()`: Données de marché (forex, indices)

**Quand modifier :**
- Ajouter une nouvelle source de données
- Modifier la logique de cache
- Améliorer la recherche de tickers
- Ajouter de nouveaux types de données

**Exemple :**
```python
# Récupérer des données
from app.data_fetcher import fetch_historical_prices

prices = fetch_historical_prices(["AAPL", "NVDA"], period="1y")
```

---

### **4. `app/calculations.py`** - Calculs financiers (À CRÉER)
**Responsabilité :** Tous les calculs financiers et statistiques

**Devrait contenir :**
- `calculate_returns()`: Calcul des rendements
- `calculate_volatility()`: Calcul de volatilité
- `calculate_sharpe_ratio()`: Ratio de Sharpe
- `calculate_var()`: Value at Risk
- `calculate_correlation()`: Matrice de corrélation
- `run_monte_carlo()`: Simulations Monte Carlo
- `calculate_beta()`: Beta du portfolio

**Quand modifier :**
- Ajouter de nouveaux indicateurs financiers
- Modifier les formules de calcul
- Optimiser les performances de calcul

---

### **5. `app/charts.py`** - Génération de graphiques (À CRÉER)
**Responsabilité :** Création de tous les graphiques Plotly

**Devrait contenir :**
- `create_allocation_chart()`: Graphique de répartition
- `create_performance_chart()`: Graphique de performance
- `create_correlation_heatmap()`: Heatmap de corrélation
- `create_monte_carlo_chart()`: Graphiques Monte Carlo
- `create_risk_metrics_chart()`: Graphiques de risque
- ... (un pour chacun des 24 types)

**Quand modifier :**
- Changer le style des graphiques
- Ajouter de nouveaux types de visualisation
- Modifier les couleurs ou layouts

---

### **6. `app/ui_components.py`** - Composants UI (À CRÉER)
**Responsabilité :** Composants réutilisables de l'interface

**Devrait contenir :**
- `display_metric_card()`: Carte de métrique stylisée
- `portfolio_position_input()`: Input de position portfolio
- `ticker_search_widget()`: Widget de recherche ticker
- `chart_selector_panel()`: Panneau de sélection graphiques
- `export_buttons()`: Boutons d'export

**Quand modifier :**
- Créer de nouveaux composants réutilisables
- Standardiser l'apparence de l'UI
- Factoriser du code dupliqué

---

## 🎨 Personnalisation des Couleurs

### **Fichier : `.streamlit/config.toml`**

```toml
[theme]
primaryColor = "#e94560"           # Couleur principale (boutons, liens)
backgroundColor = "#0f0f23"        # Fond principal
secondaryBackgroundColor = "#1a1a2e"  # Fond secondaire (cards)
textColor = "#ffffff"              # Couleur du texte
font = "sans serif"                # Police
```

### **5 Thèmes prédéfinis disponibles :**

1. **Dark Modern** (actuel) - Rouge/Bleu foncé
2. **Professional Blue** - Bleu professionnel
3. **Finance Green** - Vert financier
4. **Purple Elegance** - Violet élégant
5. **Orange Dynamic** - Orange dynamique

**Pour changer de thème :** Décommente un bloc dans `config.toml`

---

## 📝 Comment Modifier une Section ?

### **Exemple 1 : Ajouter un ticker populaire**

**Fichier :** `app/config.py`  
**Section :** `POPULAR_TICKERS`

```python
# Ajouter dans POPULAR_TICKERS:
"BNP.PA": {"name": "BNP Paribas", "exchange": "Euronext Paris"},
```

---

### **Exemple 2 : Modifier les couleurs des graphiques**

**Fichier :** `app/config.py`  
**Section :** `CHART_COLORS`

```python
CHART_COLORS = {
    'primary': ['#NEW_COLOR_1', '#NEW_COLOR_2', ...],
    'positive': '#00ff00',  # Vert plus vif
    'negative': '#ff0000',  # Rouge plus vif
}
```

---

### **Exemple 3 : Changer la couleur de fond**

**Fichier :** `.streamlit/config.toml`

```toml
[theme]
backgroundColor = "#000000"  # Noir pur
```

---

## 🔄 Workflow de Développement

### **1. Modifier localement**
```bash
# Éditer les fichiers
code streamlit_app.py
code app/config.py

# Tester localement
streamlit run streamlit_app.py
```

### **2. Push vers GitHub**
```bash
git add .
git commit -m "Description des changements"
git push
```

### **3. Déploiement automatique**
Streamlit Cloud détecte le push et redéploie automatiquement (30-60 sec)

---

## 🚀 Prochaines Étapes

### **À créer :**
- [ ] `app/calculations.py` - Calculs financiers
- [ ] `app/charts.py` - Génération graphiques
- [ ] `app/ui_components.py` - Composants UI

### **À refactoriser :**
- [ ] Extraire les calculs de `streamlit_app.py` → `calculations.py`
- [ ] Extraire la génération de graphiques → `charts.py`
- [ ] Extraire les composants UI → `ui_components.py`

---

## 📞 Besoin d'Aide ?

### **Pour modifier :**
- **Couleurs** → `.streamlit/config.toml`
- **Tickers populaires** → `app/config.py`
- **Logique de recherche** → `app/data_fetcher.py`
- **Interface utilisateur** → `streamlit_app.py`

### **Structure de commit Git :**
```
feat: Ajouter nouvelle fonctionnalité
fix: Corriger un bug
style: Modifier les couleurs/CSS
refactor: Refactoriser le code
docs: Modifier la documentation
```

---

*Dernière mise à jour : Décembre 2024*

