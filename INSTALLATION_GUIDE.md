# 🚀 Guide d'Installation - Portfolio Analysis

Ce guide vous aide à configurer le projet sur un **nouvel ordinateur Windows**.

---

## 📋 Prérequis

### 1. Installer Python (si absent)

1. Téléchargez Python depuis [python.org](https://www.python.org/downloads/)
   - **Version recommandée** : Python 3.11 ou 3.12
   - Choisissez "Windows installer (64-bit)"

2. **IMPORTANT** : Lors de l'installation
   - ✅ **Cochez "Add Python to PATH"** (case en bas de l'installeur)
   - Cliquez sur "Install Now"

3. Vérifiez l'installation :
   ```powershell
   python --version
   ```
   Vous devriez voir : `Python 3.11.x` ou similaire

---

## 📦 Installation du Projet

### Étape 1 : Ouvrir PowerShell dans le dossier du projet

1. Naviguez vers le dossier du projet dans l'Explorateur Windows :
   ```
   C:\Users\tomca\Desktop\Sript Python\Sript Python\Portfolio
   ```

2. Dans la barre d'adresse de l'Explorateur, tapez `powershell` puis appuyez sur **Entrée**
   - Une fenêtre PowerShell s'ouvrira directement dans le bon dossier

### Étape 2 : Créer un environnement virtuel (recommandé)

```powershell
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
.\venv\Scripts\Activate.ps1
```

**Note** : Si vous obtenez une erreur de sécurité PowerShell, exécutez :
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Étape 3 : Installer les dépendances

```powershell
# Installer toutes les dépendances depuis requirements.txt
pip install -r requirements.txt
```

Cette commande installera :
- `pandas` - Traitement de données
- `numpy` - Calculs numériques
- `matplotlib` & `seaborn` - Graphiques
- `yfinance` - Données financières Yahoo
- `requests` - API HTTP
- `scipy` - Statistiques avancées

### Étape 4 : Configuration optionnelle (FRED API)

Pour obtenir les taux sans risque (SOFR) depuis la Fed :

1. Obtenez votre clé API gratuite : [fred.stlouisfed.org](https://fred.stlouisfed.org/docs/api/api_key.html)

2. Configurez la clé (choisissez une méthode) :

**Option A - Session actuelle uniquement :**
```powershell
$env:FRED_API_KEY="votre_cle_api_ici"
```

**Option B - Permanent pour votre compte :**
```powershell
[System.Environment]::SetEnvironmentVariable('FRED_API_KEY', 'votre_cle_api_ici', 'User')
```

**Note** : Si vous ne configurez pas la clé FRED, l'application utilisera automatiquement le taux du Trésor américain (^IRX) depuis Yahoo Finance.

---

## ▶️ Lancer l'Application

### Méthode 1 : Depuis PowerShell

```powershell
# Assurez-vous d'être dans le dossier Portfolio
cd "C:\Users\tomca\Desktop\Sript Python\Sript Python\Portfolio"

# Si environnement virtuel activé :
python app.py

# OU sans environnement virtuel :
python app.py
```

### Méthode 2 : Double-clic (Créer un raccourci)

1. Clic droit sur `app.py` → "Ouvrir avec" → "Python"

OU créez un fichier `Lancer_Portfolio.bat` avec ce contenu :
```batch
@echo off
cd /d "%~dp0"
python app.py
pause
```

---

## ✅ Vérifier que tout fonctionne

### Test rapide :
```powershell
# Test des imports
python -c "import pandas, numpy, yfinance, matplotlib, seaborn, scipy; print('✅ Toutes les dépendances sont installées!')"

# Test de Yahoo Finance
python -c "import yfinance as yf; ticker = yf.Ticker('AAPL'); print('✅ Yahoo Finance OK:', ticker.info.get('symbol'))"
```

### Test complet (génération de graphiques) :
```powershell
python test_generate_charts.py
```

---

## 🆘 Dépannage

### Problème : "Python n'est pas reconnu"
**Solution** : Python n'est pas dans votre PATH
1. Réinstallez Python en cochant "Add Python to PATH"
2. OU ajoutez manuellement Python au PATH :
   - Ouvrez "Modifier les variables d'environnement système"
   - Variables d'environnement → Path → Modifier
   - Ajoutez : `C:\Users\tomca\AppData\Local\Programs\Python\Python311`

### Problème : "pip n'est pas reconnu"
**Solution** :
```powershell
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Problème : "cannot import name '...' from pandas"
**Solution** : Version incompatible
```powershell
pip install --upgrade pandas numpy matplotlib
```

### Problème : Erreur lors du lancement (tkinter manquant)
**Cause** : Tkinter n'est pas installé avec Python
**Solution** : Réinstallez Python en cochant "tcl/tk and IDLE"

### Problème : Les graphiques ne s'affichent pas
**Solution** :
```powershell
pip install --upgrade matplotlib pillow
```

---

## 📁 Structure du Projet

```
Portfolio/
├── app.py                      # 🚀 POINT D'ENTRÉE - Lancez ce fichier
├── requirements.txt            # 📦 Dépendances Python
├── INSTALLATION_GUIDE.md       # 📖 Ce guide
├── FRED_API_SETUP.md          # Configuration API FRED (optionnel)
│
├── core/                      # Logique centrale
│   ├── config.py             # Configuration
│   ├── main.py               # Orchestration
│   └── analysis_runner.py    # Exécution des analyses
│
├── ui/                       # Interface graphique
│   ├── menu_principal_v3.py  # Interface principale (latest)
│   ├── theme_colors.py       # Thème visuel
│   └── ui_builder.py         # Composants UI
│
├── managers/                 # Gestionnaires de données
│   ├── portfolio_manager.py
│   ├── market_data_manager.py
│   ├── currency_manager.py
│   └── symbol_handler.py
│
├── charts/                   # Génération des graphiques
│   ├── chart_portfolio.py
│   ├── chart_monte_carlo.py
│   ├── chart_benchmarks.py
│   ├── chart_risk_metrics.py
│   └── chart_sector.py
│
├── utils/                    # Utilitaires
│   ├── utils_data.py         # Chargement données (Yahoo Finance)
│   ├── utils_math.py         # Calculs financiers
│   └── utils_plot.py         # Helpers graphiques
│
├── data/                     # Données et caches
│   ├── weights.csv
│   ├── benchmarks.csv
│   └── *.json               # Caches (secteurs, forex, etc.)
│
└── results/                  # 📊 Graphiques générés (PNG)
```

---

## 🎯 Prochaines Étapes

1. ✅ Installez Python et les dépendances (étapes ci-dessus)
2. ✅ Lancez l'application : `python app.py`
3. ✅ Ajoutez vos positions dans l'interface
4. ✅ Sélectionnez les graphiques à générer
5. ✅ Cliquez sur "Run Portfolio Analysis"
6. ✅ Les graphiques seront sauvegardés dans `results/`

---

## 💡 Astuces

- **Performance** : Utilisez un environnement virtuel (`venv`) pour isoler les dépendances
- **Mises à jour** : Exécutez `pip install --upgrade -r requirements.txt` régulièrement
- **Données** : Les données sont mises en cache pour accélérer les analyses futures
- **FRED API** : Optionnel mais recommandé pour des taux sans risque précis

---

## 📞 Support

En cas de problème :
1. Vérifiez que Python 3.8+ est installé : `python --version`
2. Vérifiez que les dépendances sont installées : `pip list`
3. Consultez les logs dans la console PowerShell
4. Vérifiez `_docs/README.md` pour plus de détails

---

**Bon courage avec votre analyse de portfolio ! 📈💼**






