"""Preprocessing per PRD section 5.6."""

from __future__ import annotations

import numpy as np
import pandas as pd


def resample_last(df: pd.DataFrame, cols: list[str], grid_minutes: int = 5) -> pd.DataFrame:
    """Clock-aligned bins (t-5min, t] labelled by their right edge t, so the value at grid time t
    never contains a reading taken after t (no future information); last non-null observation
    within each bin; full regular grid."""
    d = df.copy()
    d["bin"] = d["ts"].dt.ceil(f"{grid_minutes}min")
    g = d.groupby("bin")[cols].last()
    full = pd.date_range(g.index.min(), g.index.max(), freq=f"{grid_minutes}min")
    g = g.reindex(full)
    g.index.name = "ts"
    return g


def interpolate_short_gaps(x: np.ndarray, max_gap: int = 3) -> tuple[np.ndarray, np.ndarray]:
    """Linearly fill NaN runs of length <= max_gap bounded on both sides. Returns (values, interp_flag)."""
    x = x.astype(float).copy()
    flag = np.zeros(len(x), dtype=bool)
    isn = np.isnan(x)
    i, n = 0, len(x)
    while i < n:
        if isn[i]:
            j = i
            while j + 1 < n and isn[j + 1]:
                j += 1
            L = j - i + 1
            if i > 0 and j < n - 1 and L <= max_gap:
                a, b = x[i - 1], x[j + 1]
                for k in range(L):
                    x[i + k] = a + (b - a) * (k + 1) / (L + 1)
                flag[i:j + 1] = True
            i = j + 1
        else:
            i += 1
    return x, flag


def run_lengths_true(mask: np.ndarray) -> np.ndarray:
    """For each position, the length of the run of True values it belongs to (0 if False)."""
    out = np.zeros(len(mask), dtype=int)
    i, n = 0, len(mask)
    while i < n:
        if mask[i]:
            j = i
            while j + 1 < n and mask[j + 1]:
                j += 1
            out[i:j + 1] = j - i + 1
            i = j + 1
        else:
            i += 1
    return out


def trailing_run(mask: np.ndarray) -> np.ndarray:
    """Number of consecutive True values ending at each position (causal)."""
    out = np.zeros(len(mask), dtype=int)
    c = 0
    for i, m in enumerate(mask):
        c = c + 1 if m else 0
        out[i] = c
    return out


def preprocess(raw: pd.DataFrame, glucose_source: str = "dexcom", grid_minutes: int = 5
               ) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (grid, meals).

    grid columns: glucose, glucose_valid, glucose_quality, hr, hr_valid, wearable_off, mets
    meals columns: ts, meal_type, carbs, protein, fat, fiber, kcal
    """
    gcol = glucose_source if glucose_source in raw.columns else "libre"
    cols = [c for c in [gcol, "hr", "mets", "act_kcal"] if c in raw.columns]
    sub = raw[["ts"] + cols].copy()
    if gcol in sub:
        sub = sub.rename(columns={gcol: "glucose"})
    grid = resample_last(sub.rename(columns={}), [c if c != gcol else "glucose" for c in cols],
                         grid_minutes)
    g = grid["glucose"].to_numpy(float)
    oor = ~np.isnan(g) & ((g < 40) | (g > 400))
    g_clip = np.where(oor, np.clip(g, 40, 400), g)
    g_fill, interp = interpolate_short_gaps(g_clip, max_gap=int(15 / grid_minutes))
    quality = np.where(np.isnan(g_fill), "missing", np.where(interp, "interpolated",
                                                             np.where(oor, "out_of_range", "ok")))
    grid["glucose"] = g_fill
    grid["glucose_valid"] = ~np.isnan(g_fill)
    grid["glucose_quality"] = quality
    hr = grid["hr"].to_numpy(float) if "hr" in grid else np.full(len(grid), np.nan)
    hr_valid = ~np.isnan(hr) & (hr >= 30) & (hr <= 220)
    grid["hr"] = np.where(hr_valid, hr, np.nan)
    grid["hr_valid"] = hr_valid
    off_steps = int(np.ceil(10 / grid_minutes))
    grid["wearable_off"] = trailing_run(~hr_valid) >= off_steps
    # Observed glucose (excludes interpolated points, whose value depends on the next reading).
    # Features use this; labels and plots use the interpolated `glucose`.
    grid["glucose_obs"] = np.where(grid["glucose_valid"] & (grid["glucose_quality"] != "interpolated"),
                                   grid["glucose"], np.nan)
    for c in ("mets", "act_kcal"):
        if c not in grid:
            grid[c] = np.nan
    grid = grid.reset_index()

    if "meal_type" in raw.columns:
        m = raw[raw["meal_type"].notna()].copy()
    else:
        m = raw.iloc[0:0].copy()
    meals = pd.DataFrame({
        "ts": m["ts"].to_numpy(),
        "meal_type": m["meal_type"].astype(str).to_numpy() if len(m) else np.array([], dtype=str),
        "carbs": m["carbs"].to_numpy(float) if "carbs" in m else np.nan,
        "protein": m["protein"].to_numpy(float) if "protein" in m else np.nan,
        "fat": m["fat"].to_numpy(float) if "fat" in m else np.nan,
        "fiber": m["fiber"].to_numpy(float) if "fiber" in m else np.nan,
        "kcal": m["kcal"].to_numpy(float) if "kcal" in m else np.nan,
    })
    meals = meals.sort_values("ts").reset_index(drop=True)
    return grid, meals
