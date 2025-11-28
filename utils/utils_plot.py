# utils_plot.py - Common plotting utilities and formatters
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from datetime import datetime

# --------- GLOBAL STYLE - ULTRA HIGH DEFINITION (Optimized for ThinkPad P14 Gen5) ---------
plt.rcParams.update({
    "figure.dpi": 200,          # Display DPI - balanced for performance and quality
    "savefig.dpi": 600,         # Save DPI - ultra high quality for exports
    "font.size": 11,
    "axes.titlesize": 15,
    "axes.labelsize": 12,
    "legend.fontsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.linewidth": 1.2,      # Thicker axes for better visibility on HiDPI
    "lines.linewidth": 2.0,     # Thicker lines
    "lines.markersize": 6,      # Larger markers
    "axes.grid": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "none",
    "figure.autolayout": True,
    "font.family": "sans-serif",
    "font.sans-serif": ["Segoe UI", "Arial", "DejaVu Sans"],
    "figure.figsize": (12, 7),  # Larger default figure size
    "savefig.format": "png",
    "savefig.transparent": False,
})

# ---------- FORMATTERS ----------
eur_fmt  = FuncFormatter(lambda x, _: f"€{x:,.0f}")
pct_fmt  = FuncFormatter(lambda x, _: f"{x*100:.0f}%")
pct1_fmt = FuncFormatter(lambda x, _: f"{x*100:.1f}%")

# ---------- UTILITIES ----------
def add_bar_labels(ax, fmt="{:.1f}%"):
    """Add labels on top of bars in bar charts."""
    for cont in ax.containers:
        try:
            labels = [fmt.format(v) for v in cont.datavalues]
            ax.bar_label(cont, labels=labels, padding=3, fontsize=8)
        except Exception:
            pass
    ax.margins(y=0.15)

def save_and_show(fig, name, results_dir="./results", show_plots=True):
    """Save figure and optionally show it."""
    os.makedirs(results_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(results_dir, f"{ts}_{name}")
    fig.savefig(path, bbox_inches="tight", pad_inches=0.25)
    print("Saved:", path)
    if show_plots:
        try: plt.show()
        except Exception: pass

def placeholder_figure(title: str, subtitle: str = ""):
    """Create a placeholder figure when data is not available."""
    fig, ax = plt.subplots(figsize=(10,4))
    ax.axis("off")
    ax.text(0.5, 0.6, title, ha="center", va="center", fontsize=12, weight="bold")
    if subtitle:
        ax.text(0.5, 0.35, subtitle, ha="center", va="center", fontsize=10)
    return fig

def apply_chart_style(ax, title=None, xlabel=None, ylabel=None, grid=True):
    """Apply common styling to charts."""
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold', pad=16)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12)
    if grid:
        ax.grid(True, alpha=0.3)
    fig.tight_layout()