"""Alert rule, alert-budget threshold selection and event-level metrics (PRD 9.3)."""

from __future__ import annotations

import numpy as np


def alerts_from_probs(prob: np.ndarray, theta: float, consecutive: int, cooldown_steps: int
                      ) -> np.ndarray:
    """prob: per grid point (NaN where not scored). Alert when prob >= theta at `consecutive`
    consecutive grid points, then a cool-down. Returns boolean alert array."""
    n = len(prob)
    hit = np.nan_to_num(prob, nan=-1.0) >= theta
    alerts = np.zeros(n, dtype=bool)
    streak, cool_until = 0, -1
    for i in range(n):
        streak = streak + 1 if hit[i] else 0
        if i <= cool_until:
            continue
        if streak >= consecutive:
            alerts[i] = True
            cool_until = i + cooldown_steps
            streak = 0
    return alerts


def alerts_per_day(alerts_by_pid: dict[str, np.ndarray], days_by_pid: dict[str, float]) -> float:
    tot = sum(int(a.sum()) for a in alerts_by_pid.values())
    days = sum(days_by_pid.values())
    return tot / days if days > 0 else float("nan")


def choose_theta(probs_by_pid: dict[str, np.ndarray], days_by_pid: dict[str, float], budget: float,
                 consecutive: int, cooldown_steps: int) -> float:
    """Lowest theta whose alert rate is <= budget alerts per patient-day (bisection on quantiles)."""
    allp = np.concatenate([p[~np.isnan(p)] for p in probs_by_pid.values()]) if probs_by_pid else np.array([])
    if allp.size == 0:
        return 1.0
    cands = np.unique(np.quantile(allp, np.linspace(0.5, 0.9999, 120)))
    lo, hi = 0, len(cands) - 1
    best = float(cands[-1])
    while lo <= hi:
        mid = (lo + hi) // 2
        th = float(cands[mid])
        rate = alerts_per_day({k: alerts_from_probs(p, th, consecutive, cooldown_steps)
                               for k, p in probs_by_pid.items()}, days_by_pid)
        if rate <= budget:
            best, hi = th, mid - 1
        else:
            lo = mid + 1
    return best


def event_metrics(alerts: np.ndarray, onsets: np.ndarray, horizon_steps: int, grid_minutes: int = 5
                  ) -> tuple[int, int, list[float]]:
    """Detected if any alert in [onset - H, onset - 1 step]. Returns (n_detected, n_events, lead_times_min)."""
    det, leads = 0, []
    for o in onsets:
        lo = max(0, o - horizon_steps)
        w = np.where(alerts[lo:o])[0]
        if w.size:
            det += 1
            leads.append(float((o - (lo + w[0])) * grid_minutes))
    return det, len(onsets), leads
