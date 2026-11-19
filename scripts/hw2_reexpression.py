"""Homework 2 - Schematic plot, power transformation and the d_lambda statistic.

Run from the repository root:

    python scripts/hw2_reexpression.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import co2stats as cs  # noqa: E402
import plotstyle as ps  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

FIG, RES = ROOT / "figures", ROOT / "results"
FIG.mkdir(exist_ok=True)
RES.mkdir(exist_ok=True)
ps.apply()

x = cs.load_data()["co2_ppm"].to_numpy()
LAMBDAS = [2, 1, 0.5, 0, -0.5, -1, -2, -3, -4]

# ------------------------------------------------------------ Part a: schematic plot of x
s = cs.five_number_summary(x)
f = cs.fences(x)
n_outside = int(((x < f["lower_inner"]) | (x > f["upper_inner"])).sum())
print("Five-number summary (ppm):", {k: round(v, 4) for k, v in s.items()})
print("Fences (ppm):", {k: round(v, 2) for k, v in f.items()})
print("Points outside inner fences:", n_outside, "\n")

# ------------------------------------------------------------ Part b/c: d_lambda table
rows = []
for lam in LAMBDAS:
    y = cs.power_transform(x, lam)
    t = cs.five_number_summary(y)
    rows.append({
        "lambda": lam,
        "d_lambda": abs(t["mean"] - t["median"]) / t["iqr"],
        "mean_minus_median_sign": "+" if t["mean"] > t["median"] else "-",
        "box_ratio": (t["q75"] - t["median"]) / (t["median"] - t["q25"]),
        "whisker_ratio": (t["max"] - t["q75"]) / (t["q25"] - t["min"]),
    })
table = pd.DataFrame(rows)
table.round(4).to_csv(RES / "hw2_d_lambda.csv", index=False)
print(table.round(4).to_string(index=False), "\n")

grid = np.round(np.arange(-6, 3.0001, 0.05), 2)
d_grid = np.array([cs.d_lambda(x, lam) for lam in grid])
lam_best = grid[d_grid.argmin()]
best_trial = table.loc[table.d_lambda.idxmin(), "lambda"]
print(f"Optimum among trial values: lambda = {best_trial}")
print(f"Fine grid minimum: lambda = {lam_best:.2f}, d = {d_grid.min():.5f}")

# ------------------------------------------------------------ Figure: schematic plots
fig, ax = plt.subplots(figsize=(11, 4.5))
data = [(cs.power_transform(x, l) - cs.quantile(cs.power_transform(x, l), .5))
        / cs.five_number_summary(cs.power_transform(x, l))["iqr"] for l in LAMBDAS]
bp = ax.boxplot(data, whis=1.5, widths=0.55, patch_artist=True, showmeans=True,
                meanprops=dict(marker="+", markeredgecolor=ps.INK, markersize=9),
                medianprops=dict(color=ps.INK, linewidth=1.5),
                whiskerprops=dict(color=ps.INK2), capprops=dict(color=ps.INK2))
for lam, box in zip(LAMBDAS, bp["boxes"]):
    box.set(facecolor=ps.ORANGE if lam == best_trial else ps.BLUE,
            alpha=0.85, edgecolor=ps.SURFACE, linewidth=2)
ax.set_xticks(range(1, len(LAMBDAS) + 1),
              [f"λ = {l:g}\nd = {d:.4f}" for l, d in zip(LAMBDAS, table.d_lambda)])
ax.set_ylabel("(T₁(x) − median) / IQR")
ax.set_title("Schematic plots of the power-transformed CO₂ data "
             f"(optimum λ = {best_trial:g} highlighted, + = mean)")
ax.grid(axis="x", visible=False)
fig.savefig(FIG / "hw2_schematic_plots.png")

# ------------------------------------------------------------ Figure: d_lambda curve
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(grid, d_grid, color=ps.BLUE)
ax.scatter(table["lambda"], table["d_lambda"], s=40, facecolor=ps.SURFACE,
           edgecolor=ps.BLUE, linewidth=1.5, zorder=3, label="Trial values")
ax.scatter([lam_best], [d_grid.min()], s=60, color=ps.ORANGE, zorder=4,
           label=f"Minimum (λ ≈ {lam_best:.2f})")
ax.axvline(1, color=ps.MUTED, linewidth=0.8, linestyle=":")
ax.text(0.95, ax.get_ylim()[1] * 0.92, "original data (λ = 1)", color=ps.MUTED,
        fontsize=8, ha="right")
ax.set_xlabel("λ")
ax.set_ylabel("d_λ = |mean − median| / IQR")
ax.set_title("Choosing the symmetry-producing power transformation")
ax.legend(loc="upper left")
fig.savefig(FIG / "hw2_d_lambda_curve.png")
