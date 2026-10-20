"""Excursion labels and eligible-window builder (PRD section 6)."""

from __future__ import annotations

import numpy as np
import pandas as pd


def excursion_runs(glucose: np.ndarray, valid: np.ndarray, threshold: float, min_consec: int = 3
                   ) -> list[tuple[int, int]]:
    """Return (start_idx, end_idx_inclusive) of runs of >= min_consec consecutive valid samples > T."""
    above = valid & (np.nan_to_num(glucose, nan=-1.0) > threshold)
    runs: list[tuple[int, int]] = []
    i, n = 0, len(above)
    while i < n:
        if above[i]:
            j = i
            while j + 1 < n and above[j + 1]:
                j += 1
            if j - i + 1 >= min_consec:
                runs.append((i, j))
            i = j + 1
        else:
            i += 1
    return runs


def episodes_from_runs(runs: list[tuple[int, int]], gap_steps: int) -> list[tuple[int, int]]:
    """Merge runs: a new episode needs >= gap_steps grid steps since the previous run ended."""
    eps: list[tuple[int, int]] = []
    for s, e in runs:
        if eps and s - eps[-1][1] - 1 < gap_steps:
            eps[-1] = (eps[-1][0], e)
        else:
            eps.append((s, e))
    return eps


def build_labels(grid: pd.DataFrame, threshold: float, horizons: list[int], cfg: dict,
                 grid_minutes: int = 5) -> pd.DataFrame:
    """For each grid index, compute eligibility and labels per horizon.

    grid must contain columns: glucose (float), glucose_valid (bool), sorted on a regular grid.
    Returns DataFrame indexed like grid with columns eligible_{H}, y_{H}, currently_high, post_warmup.
    """
    g = grid["glucose"].to_numpy(float)
    v = grid["glucose_valid"].to_numpy(bool)
    n = len(g)
    exc = cfg["excursion"]
    runs = excursion_runs(g, v, threshold, exc["min_consecutive_samples"])
    onset = np.zeros(n, dtype=bool)
    for s, _ in runs:
        onset[s] = True
    warm_steps = int(cfg["warmup_hours"] * 60 / grid_minutes)
    lb = int(cfg["lookback_minutes"] / grid_minutes)
    min_lb = int(np.ceil(cfg["eligibility"]["min_valid_fraction_lookback"] * lb - 1e-9))
    vc = np.concatenate([[0], np.cumsum(v.astype(int))])
    oc = np.concatenate([[0], np.cumsum(onset.astype(int))])
    idx = np.arange(n)
    # lookback window (t-120, t] -> indices idx-lb+1 .. idx
    lo = np.clip(idx - lb + 1, 0, None)
    lb_valid = vc[idx + 1] - vc[lo]
    lb_full = (idx - lb + 1) >= 0
    gnow_ok = v & (np.nan_to_num(g, nan=np.inf) <= threshold)
    post_warm = idx >= warm_steps
    out = pd.DataFrame(index=grid.index)
    out["post_warmup"] = post_warm
    out["currently_high"] = v & (np.nan_to_num(g, nan=-1) > threshold)
    out["lookback_ok"] = lb_full & (lb_valid >= min_lb)
    min_h = cfg["eligibility"]["min_valid_fraction_horizon"]
    for H in horizons:
        hs = int(H / grid_minutes)
        hi = np.clip(idx + hs, None, n - 1)
        # horizon (t, t+H] -> idx+1 .. idx+hs
        n_on = oc[hi + 1] - oc[idx + 1]
        y = n_on > 0
        h_valid = vc[hi + 1] - vc[idx + 1]
        extends = (idx + hs) <= n - 1
        observable = y | (extends & (h_valid >= np.ceil(min_h * hs - 1e-9)))
        elig = post_warm & gnow_ok & out["lookback_ok"].to_numpy() & observable
        out[f"eligible_{H}"] = elig
        out[f"y_{H}"] = (y & elig).astype(int)
    return out


def episode_onsets(grid: pd.DataFrame, threshold: float, cfg: dict, grid_minutes: int = 5) -> np.ndarray:
    """Indices of episode onsets (after warm-up) used for event-level metrics."""
    exc = cfg["excursion"]
    runs = excursion_runs(grid["glucose"].to_numpy(float), grid["glucose_valid"].to_numpy(bool),
                          threshold, exc["min_consecutive_samples"])
    eps = episodes_from_runs(runs, int(exc["episode_gap_minutes"] / grid_minutes))
    warm = int(cfg["warmup_hours"] * 60 / grid_minutes)
    return np.array([s for s, _ in eps if s >= warm], dtype=int)
