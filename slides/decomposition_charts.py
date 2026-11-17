"""
decomposition_charts.py - two monochrome figures for the "decomposition"
slides, built from results/decomposition_results.json (run scripts/decomposition.py first).
"""
import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "decomposition_results.json"
ASSETS = ROOT / "slides" / "assets"

plt.rcParams.update({
    "font.family": "serif",
    "mathtext.fontset": "cm",
    "text.color": "black", "axes.edgecolor": "black", "axes.labelcolor": "black",
    "xtick.color": "black", "ytick.color": "black",
    "axes.facecolor": "white", "figure.facecolor": "white",
    "axes.grid": True, "grid.color": "#dddddd", "grid.linewidth": 0.6,
    "axes.spines.top": False, "axes.spines.right": False,
    "font.size": 12,
})
BLACK = "black"
DPI = 220

with open(RESULTS, encoding="utf-8") as f:
    d = json.load(f)


def savefig(fig, name, pad=0.15):
    fig.savefig(ASSETS / f"{name}.png", dpi=DPI, bbox_inches="tight", pad_inches=pad, facecolor="white")
    plt.close(fig)


# 1 --------------------------------------------------- sequential R^2 (waterfall)
seq = d["sequential_r2"]
labels = [s["block"] for s in seq]
marg = [s["r2_marginal"] * 100 for s in seq]
cum = [s["r2_cumulative"] * 100 for s in seq]

fig, ax = plt.subplots(figsize=(9.5, 5.0))
bottoms = [c - m for c, m in zip(cum, marg)]
ax.bar(labels, marg, bottom=bottoms, color="white", edgecolor=BLACK, linewidth=1.2, width=0.55)
for i, (c, m) in enumerate(zip(cum, marg)):
    ax.text(i, c + 1.2, f"R²={c:.0f}%\n(+{m:.0f})", ha="center", fontsize=10.5)
ax.set_ylabel(r"Cumulative $R^2$ (%)")
ax.set_title("Where the model's explanatory power comes from")
ax.set_ylim(0, max(cum) + 12)
ax.yaxis.set_major_formatter(mticker.FormatStrFormatter("%d%%"))
fig.autofmt_xdate(rotation=12)
fig.tight_layout()
savefig(fig, "seq_r2")

# 2 --------------------------------------------------- raw vs adjusted city gap
cg = d["city_gap_decomposition"]
cities = [r["city"] for r in cg]
raw = [r["raw_pct"] for r in cg]
adj = [r["adjusted_pct"] for r in cg]

y = np.arange(len(cities))
h = 0.35
fig, ax = plt.subplots(figsize=(8.5, 5.0))
ax.barh(y + h / 2, raw, height=h, color="white", edgecolor=BLACK, linewidth=1.2)
ax.barh(y - h / 2, adj, height=h, color=BLACK, edgecolor=BLACK, linewidth=1.2)
ax.axvline(0, color=BLACK, linewidth=1)
ax.set_yticks(y); ax.set_yticklabels(cities)
ax.set_xlabel("% rent gap vs. Kaunas")
ax.set_title("City rent gaps: raw vs. holding size, age, heating fixed")
ax.xaxis.set_major_formatter(mticker.FormatStrFormatter("%+.0f%%"))
handles = [
    Patch(facecolor="white", edgecolor=BLACK, linewidth=1.2, label="Raw gap (unconditional)"),
    Patch(facecolor=BLACK, edgecolor=BLACK, linewidth=1.2, label="Adjusted gap (regression)"),
]
fig.legend(handles=handles, loc="lower center", ncol=2, frameon=False, fontsize=9.5,
           bbox_to_anchor=(0.5, -0.02))
fig.tight_layout(rect=(0, 0.07, 1, 1))
savefig(fig, "city_gap_decomp")

print("decomposition charts written")
