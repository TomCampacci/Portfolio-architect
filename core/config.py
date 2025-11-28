# config.py - Portfolio Analysis Configuration
import os
import numpy as np

# Data directories
DATA_DIR = "C:/Users/CAMPACCI/Desktop/Portefeuille"
BENCH_DIR = "C:/Users/CAMPACCI/Desktop/Portefeuille/Benchmarks"
RESULTS_DIR = "./results"

# Portfolio configuration
WEIGHTS_RAW = {
    "ANXU": 0.20, "NVDA": 0.07, "PLTR": 0.07, "IUS2": 0.06, "BNK": 0.13,
    "CS1": 0.07, "MIB": 0.07, "CNKY": 0.07, "GLDA": 0.13, "CG1": 0.13
}

# Benchmark definitions
BENCH_DEF = [
    ("US (NASDAQ)", "NQ1!"),
    ("EU (DAX)", "FDAX1!"),
    ("Spain (IBEX)", "IBEX35"),
    ("Italy (MIB)", "FTSEMIB"),
    ("Japan (Nikkei)", "NIY1!"),
    ("Gold", "GC1!"),
]

# Sector mapping
SECTOR_MAPPING = {
    "ANXU": "US / Technology", "NVDA": "US / Technology", "PLTR": "US / Technology",
    "IUS2": "Broad Market", "BNK": "Financials", "CS1": "Europe",
    "MIB": "Europe", "CNKY": "Asia Pacific", "GLDA": "Commodities", "CG1": "Europe"
}

# Sector colors
SECTOR_COLORS = {
    "US / Technology": "#FF6B6B", "Broad Market": "#4ECDC4", "Financials": "#45B7D1",
    "Europe": "#96CEB4", "Asia Pacific": "#FFEAA7", "Commodities": "#DDA0DD"
}

# Analysis parameters
START_CAPITAL = 10000
ESTIMATION_YEARS = 0  # 0 = full history (no slicing); set to N to limit to last N years
MC_PATHS = 50000
MC_STEPS = 36
RANDOMNESS_FACTOR = 0.30
FORWARD_YEARS = 3
ANNUALIZATION = 252
MONTH_FACTOR = 12
PLOT_ALL_PATHS = False
SHOW_PLOTS = True
SEED = 42

# Initialize results directory and random seed
os.makedirs(RESULTS_DIR, exist_ok=True)
np.random.seed(SEED)

