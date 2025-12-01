# 🗄️ Archive - Application Tkinter (Desktop)

## 📅 Date d'archivage : Décembre 2024

Cette archive contient l'**ancienne version desktop** de l'application Portfolio Architect, développée avec Tkinter.

## ❓ Pourquoi archivé ?

L'application a été **migrée vers Streamlit** pour permettre :
- ✅ Un déploiement web accessible partout
- ✅ Une interface moderne et responsive
- ✅ Un partage facile via URL
- ✅ Pas d'installation nécessaire pour les utilisateurs

## 📂 Contenu de l'archive

```
_archive_tkinter/
├── app.py                    # Point d'entrée Tkinter
├── ui/                       # Interface utilisateur (4 versions)
│   ├── menu_principal.py
│   ├── menu_principal_v2.py
│   ├── menu_principal_v3.py
│   └── menu_principal_v4.py  # Dernière version utilisée
├── core/                     # Logique métier
│   ├── analysis_runner.py    # Orchestrateur d'analyse
│   ├── config.py             # Configuration
│   └── main.py
├── charts/                   # Génération des 24 graphiques
│   ├── chart_portfolio.py
│   ├── chart_benchmarks.py
│   ├── chart_monte_carlo.py
│   ├── chart_risk_metrics.py
│   ├── chart_sector.py
│   ├── chart_sector_projection.py
│   └── chart_regime.py
├── utils/                    # Utilitaires
│   ├── utils_data.py         # Chargement données
│   ├── utils_math.py         # Calculs financiers
│   └── utils_plot.py         # Helpers graphiques
├── managers/                 # Gestionnaires
│   ├── portfolio_manager.py
│   ├── currency_manager.py
│   ├── market_data_manager.py
│   └── symbol_handler.py
└── tests/                    # Tests unitaires
    └── test_refactoring.py
```

## 🔧 Comment utiliser cette archive ?

### Si tu veux lancer l'ancienne version desktop :

```bash
cd _archive_tkinter
python app.py
```

### Dépendances nécessaires :
```bash
pip install pandas numpy yfinance matplotlib tkinter
```

## 📚 Documentation technique

Cette archive sert de **référence** pour :
- Les formules de calcul financier (VaR, Sharpe, etc.)
- La logique des 24 types de graphiques
- L'architecture multi-modules
- Les patterns de gestion de données

## ⚠️ Note importante

**Cette version n'est plus maintenue.** Toutes les nouvelles fonctionnalités sont développées dans **streamlit_app.py**.

Pour contribuer au projet, utilise la version Streamlit :
```bash
streamlit run streamlit_app.py
```

---

## 🚀 Version actuelle : Streamlit (Web)

L'application actuelle est **streamlit_app.py** et est déployée sur **Streamlit Cloud**.

✅ Accessible via navigateur  
✅ Déploiement automatique via GitHub  
✅ Interface moderne et responsive  
✅ Pas d'installation nécessaire  

---

*Archive créée le 1er décembre 2024*

