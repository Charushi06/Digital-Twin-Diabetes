"""Window-level metrics with participant-level bootstrap CIs (PRD 9.2/9.3)."""

from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def safe_auc(y: np.ndarray, s: np.ndarray) -> float:
    return float(roc_auc_score(y, s)) if 0 < y.sum() < len(y) else float("nan")


def safe_ap(y: np.ndarray, s: np.ndarray) -> float:
    return float(average_precision_score(y, s)) if y.sum() > 0 else float("nan")


def participant_bootstrap(y: np.ndarray, s: np.ndarray, pid: np.ndarray, fn, n_boot: int, seed: int
                          ) -> tuple[float, float, float]:
    """Point estimate and 95% CI by resampling participants with replacement."""
    point = fn(y, s)
    rng = np.random.default_rng(seed)
    ups = np.unique(pid)
    idx_by = {p: np.where(pid == p)[0] for p in ups}
    vals = []
    for _ in range(n_boot):
        pick = rng.choice(ups, size=len(ups), replace=True)
        ix = np.concatenate([idx_by[p] for p in pick])
        v = fn(y[ix], s[ix])
        if not np.isnan(v):
            vals.append(v)
    if not vals:
        return point, float("nan"), float("nan")
    return point, float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))


def brier(y: np.ndarray, p: np.ndarray) -> float:
    return float(brier_score_loss(y, np.clip(p, 0, 1)))


def ece(y: np.ndarray, p: np.ndarray, n_bins: int = 10) -> float:
    bins = np.linspace(0, 1, n_bins + 1)
    ix = np.clip(np.digitize(p, bins) - 1, 0, n_bins - 1)
    e = 0.0
    for b in range(n_bins):
        m = ix == b
        if m.any():
            e += m.mean() * abs(p[m].mean() - y[m].mean())
    return float(e)


def per_participant_auc(y: np.ndarray, s: np.ndarray, pid: np.ndarray) -> dict[str, float]:
    return {p: safe_auc(y[pid == p], s[pid == p]) for p in np.unique(pid)}


def fmt_ci(t: tuple[float, float, float]) -> str:
    a, lo, hi = t
    if np.isnan(a):
        return "n/a"
    return f"{a:.3f} [{lo:.3f}, {hi:.3f}]"
