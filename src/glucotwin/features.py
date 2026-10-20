"""The ONE shared feature function (PRD section 8).

`build_features(series, t)` is used by both the batch pipeline and the online twin. It only reads
data with timestamp <= t, and dynamic data only from (t - 240 min, t], so a twin holding a 4-hour
buffer computes identical features to the batch pipeline (test T-03).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

GRID = 5
MEAL_TYPE_CODE = {"breakfast": 1, "lunch": 2, "dinner": 3, "snacks": 4, "snack": 4}

GLUCOSE_FEATURES = [
    "glucose_now", "glucose_delta_5", "glucose_delta_15", "glucose_delta_30", "glucose_delta_60",
    "glucose_slope_30", "glucose_min_60", "glucose_max_60", "glucose_std_60", "glucose_min_120",
    "glucose_max_120", "glucose_std_120", "glucose_valid_frac_120",
]
PERSONAL_RELATIVE = ["glucose_minus_personal_mean", "glucose_z_personal", "hr_minus_resting"]
MEAL_FEATURES = [
    "min_since_last_meal", "last_meal_carbs", "last_meal_protein", "last_meal_fat", "last_meal_fiber",
    "last_meal_kcal", "carbs_last_4h", "meals_today", "last_meal_type", "glucose_at_last_meal",
    "glucose_rise_since_meal",
]
WEARABLE_FEATURES = ["hr_mean_30", "hr_max_30", "mets_mean_30", "mets_mean_120", "act_kcal_mean_30",
                     "act_kcal_mean_120", "wearable_off"]
CIRCADIAN = ["hour_sin", "hour_cos"]
STATIC_BASE = ["age", "sex_male", "bmi", "hba1c", "fasting_glucose", "homa_ir", "triglycerides", "hdl", "ldl"]
STATIC_FEATURES = STATIC_BASE + [f"{s}_missing" for s in STATIC_BASE]
BASELINE_FEATURES = ["personal_mean_glucose", "personal_sd_glucose", "personal_median_meal_rise",
                     "personal_resting_hr"]

ALL_FEATURES = (GLUCOSE_FEATURES + MEAL_FEATURES + WEARABLE_FEATURES + CIRCADIAN + STATIC_FEATURES
                + BASELINE_FEATURES + PERSONAL_RELATIVE)

# Ablation variants (PRD section 16). Circadian goes with A0 (documented in ASSUMPTIONS.md).
ABLATIONS: dict[str, list[str]] = {
    "A0 glucose only": GLUCOSE_FEATURES + CIRCADIAN,
    "A1 +meals": GLUCOSE_FEATURES + CIRCADIAN + MEAL_FEATURES,
    "A2 +wearable": GLUCOSE_FEATURES + CIRCADIAN + MEAL_FEATURES + WEARABLE_FEATURES,
    "A3 +static": GLUCOSE_FEATURES + CIRCADIAN + MEAL_FEATURES + WEARABLE_FEATURES + STATIC_FEATURES,
    "A4 +personal (full twin)": ALL_FEATURES,
    "Static only": STATIC_FEATURES + BASELINE_FEATURES,
    "Dynamic only": GLUCOSE_FEATURES + CIRCADIAN + MEAL_FEATURES + WEARABLE_FEATURES,
}

LOOKBACK_BUFFER_MIN = 240


@dataclass
class PatientSeries:
    """Container of grid + meal arrays. Times are integer minutes on the time-shifted clock."""

    pid: str
    t: np.ndarray            # int64 minutes, regular 5-min grid, sorted
    glucose: np.ndarray      # float, NaN where not valid
    hr: np.ndarray           # float, NaN where invalid
    wearable_off: np.ndarray  # bool
    mets: np.ndarray         # float (METs x 10); NaN in files that only have 'Intensity'
    act_kcal: np.ndarray     # Fitbit activity calories per minute
    meal_t: np.ndarray       # int64 minutes (exact minute)
    meal_carbs: np.ndarray
    meal_protein: np.ndarray
    meal_fat: np.ndarray
    meal_fiber: np.ndarray
    meal_kcal: np.ndarray
    meal_type: np.ndarray    # int codes
    static: dict = field(default_factory=dict)
    baseline: dict = field(default_factory=dict)


def to_minutes(ts) -> np.ndarray:
    return (pd.to_datetime(pd.Series(ts)).astype("datetime64[ns]").astype("int64") // 60_000_000_000
            ).to_numpy(np.int64)


def from_minutes(m: int) -> pd.Timestamp:
    return pd.Timestamp(int(m) * 60_000_000_000)


def series_from_frames(pid: str, grid: pd.DataFrame, meals: pd.DataFrame, static: dict) -> PatientSeries:
    g = grid["glucose_obs"].to_numpy(float)
    mt = (meals["meal_type"].astype(str).str.lower().str.extract(r"([a-z]+)")[0]
          .map(MEAL_TYPE_CODE).fillna(5).to_numpy(int))
    s = PatientSeries(
        pid=pid, t=to_minutes(grid["ts"]), glucose=g, hr=grid["hr"].to_numpy(float),
        wearable_off=grid["wearable_off"].to_numpy(bool), mets=grid["mets"].to_numpy(float),
        act_kcal=grid["act_kcal"].to_numpy(float),
        meal_t=to_minutes(meals["ts"]) if len(meals) else np.array([], np.int64),
        meal_carbs=np.nan_to_num(meals["carbs"].to_numpy(float)),
        meal_protein=np.nan_to_num(meals["protein"].to_numpy(float)),
        meal_fat=np.nan_to_num(meals["fat"].to_numpy(float)),
        meal_fiber=meals["fiber"].to_numpy(float), meal_kcal=np.nan_to_num(meals["kcal"].to_numpy(float)),
        meal_type=mt, static=dict(static),
    )
    return s


def _nanstat(fn, x: np.ndarray) -> float:
    x = x[~np.isnan(x)]
    return float(fn(x)) if x.size else float("nan")


def _at(s: PatientSeries, arr: np.ndarray, tm: int) -> float:
    i = np.searchsorted(s.t, tm)
    if i < len(s.t) and s.t[i] == tm:
        return float(arr[i])
    return float("nan")


def compute_baseline(s: PatientSeries, warm_end: int) -> dict:
    """Personal parameters from warm-up data only (t <= warm_end)."""
    e = np.searchsorted(s.t, warm_end, side="right")
    g = s.glucose[:e]
    out = {
        "personal_mean_glucose": _nanstat(np.mean, g),
        "personal_sd_glucose": _nanstat(np.std, g),
        "personal_resting_hr": _nanstat(lambda x: np.percentile(x, 10), s.hr[:e]),
    }
    rises = []
    for mt in s.meal_t:
        if mt + 120 > warm_end:
            continue
        g0 = _at(s, s.glucose, int(np.ceil(mt / GRID) * GRID))
        a, b = np.searchsorted(s.t, mt, side="right"), np.searchsorted(s.t, mt + 120, side="right")
        mx = _nanstat(np.max, s.glucose[a:b])
        if not np.isnan(g0) and not np.isnan(mx):
            rises.append(mx - g0)
    out["personal_median_meal_rise"] = float(np.median(rises)) if len(rises) >= 4 else float("nan")
    return out


def build_features(s: PatientSeries, t: int) -> dict[str, float]:
    """Feature vector at time t (int minutes). Uses only data with timestamp <= t."""
    f: dict[str, float] = {}
    e = int(np.searchsorted(s.t, t, side="right"))
    def win(arr: np.ndarray, minutes: int) -> np.ndarray:
        a = int(np.searchsorted(s.t, t - minutes, side="right"))
        return arr[a:e]

    g_now = _at(s, s.glucose, t)
    f["glucose_now"] = g_now
    for k in (5, 15, 30, 60):
        f[f"glucose_delta_{k}"] = g_now - _at(s, s.glucose, t - k)
    tw, gw = win(s.t, 30), win(s.glucose, 30)
    m = ~np.isnan(gw)
    f["glucose_slope_30"] = float(np.polyfit(tw[m] - t, gw[m], 1)[0]) if m.sum() >= 3 else float("nan")
    for L in (60, 120):
        x = win(s.glucose, L)
        f[f"glucose_min_{L}"] = _nanstat(np.min, x)
        f[f"glucose_max_{L}"] = _nanstat(np.max, x)
        f[f"glucose_std_{L}"] = _nanstat(np.std, x)
    f["glucose_valid_frac_120"] = float((~np.isnan(win(s.glucose, 120))).sum()) / (120 / GRID)

    # meals (exact minute; counted only from logged start time)
    j = int(np.searchsorted(s.meal_t, t, side="right"))
    if j > 0:
        i = j - 1
        mt = int(s.meal_t[i])
        f["min_since_last_meal"] = float(t - mt)
        f["last_meal_carbs"] = float(s.meal_carbs[i])
        f["last_meal_protein"] = float(s.meal_protein[i])
        f["last_meal_fat"] = float(s.meal_fat[i])
        f["last_meal_fiber"] = float(s.meal_fiber[i])
        f["last_meal_kcal"] = float(s.meal_kcal[i])
        f["last_meal_type"] = float(s.meal_type[i])
        g0 = _at(s, s.glucose, int(np.ceil(mt / GRID) * GRID)) if t - mt <= LOOKBACK_BUFFER_MIN else float("nan")
        f["glucose_at_last_meal"] = g0
        f["glucose_rise_since_meal"] = g_now - g0
    else:
        for k in ["min_since_last_meal", "last_meal_carbs", "last_meal_protein", "last_meal_fat",
                  "last_meal_fiber", "last_meal_kcal", "glucose_at_last_meal", "glucose_rise_since_meal"]:
            f[k] = float("nan")
        f["last_meal_type"] = 0.0
    a4 = int(np.searchsorted(s.meal_t, t - 240, side="right"))
    f["carbs_last_4h"] = float(s.meal_carbs[a4:j].sum())
    day0 = (t // 1440) * 1440
    f["meals_today"] = float(j - int(np.searchsorted(s.meal_t, day0, side="left")))

    # wearable
    hr30 = win(s.hr, 30)
    f["hr_mean_30"] = _nanstat(np.mean, hr30)
    f["hr_max_30"] = _nanstat(np.max, hr30)
    f["mets_mean_30"] = _nanstat(np.mean, win(s.mets, 30))
    f["mets_mean_120"] = _nanstat(np.mean, win(s.mets, 120))
    f["act_kcal_mean_30"] = _nanstat(np.mean, win(s.act_kcal, 30))
    f["act_kcal_mean_120"] = _nanstat(np.mean, win(s.act_kcal, 120))
    wo = _at(s, s.wearable_off.astype(float), t)
    f["wearable_off"] = 1.0 if np.isnan(wo) else wo

    hour = (t % 1440) / 60.0
    f["hour_sin"] = float(np.sin(2 * np.pi * hour / 24))
    f["hour_cos"] = float(np.cos(2 * np.pi * hour / 24))

    for k in STATIC_BASE:
        v = s.static.get(k, float("nan"))
        v = float("nan") if v is None else float(v)
        f[k] = v
        f[f"{k}_missing"] = float(np.isnan(v))

    for k in BASELINE_FEATURES:
        f[k] = float(s.baseline.get(k, float("nan")))
    pm, ps = f["personal_mean_glucose"], f["personal_sd_glucose"]
    f["glucose_minus_personal_mean"] = g_now - pm
    f["glucose_z_personal"] = (g_now - pm) / ps if ps and not np.isnan(ps) and ps > 0 else float("nan")
    f["hr_minus_resting"] = f["hr_mean_30"] - f["personal_resting_hr"]
    return f


def batch_features(s: PatientSeries, times: np.ndarray) -> pd.DataFrame:
    rows = [build_features(s, int(t)) for t in times]
    return pd.DataFrame(rows, columns=ALL_FEATURES)
