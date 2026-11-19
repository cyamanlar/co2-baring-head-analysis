"""Small statistics toolkit used in the CO2 Baring Head analysis.

All functions follow the definitions in the MTO 311E lecture notes
(Numerical and Graphical Summary Measures).
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "co2_bhd_monthly.csv"


def load_data(path=DATA_FILE):
    """Read the monthly CO2 series and add a datetime column."""
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(dict(year=df.year, month=df.month, day=15))
    return df


# ---------------------------------------------------------------- quantiles
def quantile(y, p):
    """Inclusive quantile: position p(n-1)+1 with linear interpolation
    (same as Excel QUARTILE.INC / numpy 'linear')."""
    return float(np.quantile(np.asarray(y, dtype=float), p, method="linear"))


def five_number_summary(y):
    y = np.asarray(y, dtype=float)
    q1, q2, q3 = (quantile(y, p) for p in (0.25, 0.5, 0.75))
    return {"min": y.min(), "q25": q1, "median": q2, "q75": q3,
            "max": y.max(), "mean": y.mean(), "iqr": q3 - q1}


# ---------------------------------------------------------------- means
def power_mean(x, r):
    """Type I (power) mean M_r. r = 0 gives the geometric mean."""
    x = np.asarray(x, dtype=float)
    if r == 0:
        return float(np.exp(np.log(x).mean()))
    return float(np.mean(x ** r) ** (1.0 / r))


def trimmed_mean(x, alpha):
    """Trimmed mean, k = floor(alpha * n) values removed from each end."""
    x = np.sort(np.asarray(x, dtype=float))
    k = int(np.floor(alpha * len(x)))
    return float(x[k:len(x) - k].mean())


# ---------------------------------------------------------------- skewness
def skewness_measures(y):
    """Pearson S, Yule-Kendall index and moment coefficient C_sx
    (population standard deviation, divisor n)."""
    y = np.asarray(y, dtype=float)
    mu, sd = y.mean(), y.std(ddof=0)
    q1, q2, q3 = (quantile(y, p) for p in (0.25, 0.5, 0.75))
    return {
        "S": 3 * (mu - q2) / sd,
        "gamma_YK": (q1 - 2 * q2 + q3) / (q3 - q1),
        "C_sx": np.mean((y - mu) ** 3) / sd ** 3,
    }


# ---------------------------------------------------------------- reexpression
def power_transform(x, lam):
    """Order-preserving power transformation T1(x)."""
    x = np.asarray(x, dtype=float)
    if lam > 0:
        return x ** lam
    if lam == 0:
        return np.log(x)
    return -(x ** lam)


def d_lambda(x, lam):
    """d_lambda = |mean - median| / IQR of the transformed data."""
    y = power_transform(x, lam)
    s = five_number_summary(y)
    return abs(s["mean"] - s["median"]) / s["iqr"]


def fences(y):
    s = five_number_summary(y)
    iqr = s["iqr"]
    return {"lower_outer": s["q25"] - 3 * iqr, "lower_inner": s["q25"] - 1.5 * iqr,
            "upper_inner": s["q75"] + 1.5 * iqr, "upper_outer": s["q75"] + 3 * iqr}
