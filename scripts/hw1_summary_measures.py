"""Homework 1 - Numerical summary measures of monthly CO2 at Baring Head.

Computes Type I (power) means, median, trimmed mean, skewness of x^r and
histograms. Run from the repository root:

    python scripts/hw1_summary_measures.py
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

df = cs.load_data()
x = df["co2_ppm"].to_numpy()
n = len(x)

# ------------------------------------------------------------ Part a: Type I means
means = pd.DataFrame({
    "r": [-1, 0, 1, 2],
    "name": ["Harmonic", "Geometric", "Arithmetic", "Quadratic"],
    "M_r_ppm": [cs.power_mean(x, r) for r in (-1, 0, 1, 2)],
})

# ------------------------------------------------------------ Part b: skewness of x^r
rows = []
for r in (-1, 0, 1, 2):
    y = np.log(x) if r == 0 else x ** r
    rows.append({"r": r, **cs.skewness_measures(y)})
skew = pd.DataFrame(rows)
best_r = int(skew.loc[skew["S"].abs().idxmin(), "r"])

# ------------------------------------------------------------ Part c/d: median, trimmed mean
other = pd.DataFrame({
    "measure": ["n", "median q0.5", "10% trimmed mean", "std (divisor n)", "C_vx"],
    "value": [n, cs.quantile(x, 0.5), cs.trimmed_mean(x, 0.10),
              x.std(ddof=0), x.std(ddof=0) / x.mean()],
})

means.round(4).to_csv(RES / "hw1_type1_means.csv", index=False)
skew.round(4).to_csv(RES / "hw1_skewness.csv", index=False)
other.round(4).to_csv(RES / "hw1_other_measures.csv", index=False)

print(f"n = {n}, period {df.date.min():%Y-%m} to {df.date.max():%Y-%m}\n")
print("Type I means (ppm):\n", means.round(4).to_string(index=False), "\n")
print("Skewness of y = x^r:\n", skew.round(3).to_string(index=False), "\n")
print(other.round(4).to_string(index=False), "\n")
print(f"Best Type I mean (min |S|): r = {best_r}, "
      f"M = {cs.power_mean(x, best_r):.4f} ppm")

# ------------------------------------------------------------ Figures
k = round(1 + 3.3 * np.log10(n))  # Sturges-type rule from the lecture


def histogram(ax, data, title, xlabel):
    counts, edges, _ = ax.hist(data, bins=np.linspace(data.min(), data.max(), k + 1),
                               color=ps.BLUE, edgecolor=ps.SURFACE, linewidth=2)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Frequency (months)")
    ax.grid(axis="x", visible=False)
    return counts


fig, axes = plt.subplots(1, 2, figsize=(11, 4))
c1 = histogram(axes[0], x, "Original data, x", "CO₂ (ppm)")
c2 = histogram(axes[1], 1e3 / x, "Transformed data, y = x⁻¹", "x⁻¹ (×10⁻³ ppm⁻¹)")
fig.suptitle(f"Histograms of monthly CO₂ at Baring Head (n = {n}, k = {k} classes)",
             x=0.01, y=1.04, ha="left", fontweight="bold")
fig.savefig(FIG / "hw1_histograms.png")
print("\nClass frequencies x:   ", c1.astype(int).tolist())
print("Class frequencies 1/x: ", c2.astype(int).tolist())

# Time series with linear trend - context figure for the README
t = df.year + (df.month - 0.5) / 12
slope, intercept = np.polyfit(t, x, 1)
fig, ax = plt.subplots(figsize=(10, 4))
# reindex to a full monthly calendar so the 29 missing months show as gaps
full = df.set_index("date")["co2_ppm"].resample("MS").mean()
ax.plot(full.index + pd.Timedelta(days=14), full.values, color=ps.BLUE,
        label="Monthly mean (gaps = missing months)")
ax.plot(df.date, slope * t + intercept, color=ps.ORANGE, linewidth=1.5,
        linestyle="--", label=f"Linear trend ({slope:.2f} ppm/yr)")
ax.set_title("Atmospheric CO₂ at Baring Head, New Zealand")
ax.set_ylabel("CO₂ (ppm)")
ax.legend(loc="upper left")
ax.annotate(f"{x[-1]:.1f} ppm", (df.date.iloc[-1], x[-1]), xytext=(6, 0),
            textcoords="offset points", va="center", color=ps.INK2)
fig.text(0.01, -0.02, "Data: NOAA Global Monitoring Laboratory, flask network (BHD)",
         color=ps.MUTED, fontsize=8)
fig.savefig(FIG / "co2_timeseries.png")
print(f"Linear trend: {slope:.3f} ppm/year")
