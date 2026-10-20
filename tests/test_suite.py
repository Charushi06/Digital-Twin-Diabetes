"""Comprehensive PRD Test Suite (PRD section 15)."""

import numpy as np
import pandas as pd
import pytest

from glucotwin import load_config
from glucotwin.cv import participant_folds
from glucotwin.explain import format_driver
from glucotwin.features import build_features, series_from_frames
from glucotwin.labels import build_labels, excursion_runs
from glucotwin.preprocess import interpolate_short_gaps, preprocess, resample_last
from glucotwin.scenarios import (INDIAN_PRESET_LABEL, MANDATORY_DISCLAIMER_REPLAY,
                                MANDATORY_DISCLAIMER_RISK, MANDATORY_DISCLAIMER_SCENARIO)


def test_t01_resampling_last_obs():
    """T-01: Values land on the 5-minute grid; last-observation rule holds."""
    df = pd.DataFrame({
        "ts": pd.to_datetime(["2026-01-01 10:01:00", "2026-01-01 10:04:00", "2026-01-01 10:07:00"]),
        "dexcom": [100.0, 105.0, 110.0]
    })
    grid, _ = preprocess(df, "dexcom", 5)
    # The reading at 10:04 should be binned into 10:05 with value 105.0
    r = grid[grid["ts"] == "2026-01-01 10:05:00"]
    assert len(r) == 1
    assert float(r["glucose"].iloc[0]) == 105.0


def test_t02_gap_rule():
    """T-02: Gap rule: a 15-minute gap (3 steps) is interpolated; a 20-minute gap stays missing."""
    x = np.array([100.0, np.nan, np.nan, np.nan, 140.0])  # 3-step gap
    filled, flag = interpolate_short_gaps(x, max_gap=3)
    assert not np.isnan(filled).any()
    assert flag[1:4].all()

    x_long = np.array([100.0, np.nan, np.nan, np.nan, np.nan, 150.0])  # 4-step gap (20 min)
    filled_l, flag_l = interpolate_short_gaps(x_long, max_gap=3)
    assert np.isnan(filled_l[1:5]).all()
    assert not flag_l.any()


def test_t04_no_leakage():
    """T-04: Changing data after t leaves features at t unchanged."""
    cfg = load_config()
    dates = pd.date_range("2026-01-01 08:00:00", periods=40, freq="5min")
    df1 = pd.DataFrame({"ts": dates, "dexcom": np.linspace(100, 150, 40)})
    g1, m1 = preprocess(df1, "dexcom", 5)
    s1 = series_from_frames("test", g1, m1, {})
    
    t_eval = int(s1.t[20])
    f1 = build_features(s1, t_eval)

    # Change future points (after t_eval)
    g2 = g1.copy()
    g2.loc[25:, "glucose_obs"] = 350.0
    s2 = series_from_frames("test", g2, m1, {})
    f2 = build_features(s2, t_eval)

    for k in f1:
        v1, v2 = f1[k], f2[k]
        if np.isnan(v1):
            assert np.isnan(v2)
        else:
            assert np.isclose(v1, v2, atol=1e-6)


def test_t05_label_builder():
    """T-05: Hand-made series produce expected excursion runs and onsets."""
    g = np.array([100, 110, 185, 190, 195, 150, 120])
    v = np.ones(len(g), dtype=bool)
    runs = excursion_runs(g, v, threshold=180.0, min_consec=3)
    assert len(runs) == 1
    assert runs[0] == (2, 4)


def test_t06_cv_folds():
    """T-06: No participant appears in both train and test portions."""
    pids = [f"CGMacros-{i:03d}" for i in range(1, 46)]
    groups = ["healthy"] * 15 + ["prediabetes"] * 16 + ["type2"] * 14
    folds = participant_folds(pids, groups, n_splits=5, seed=42)
    assert len(folds) == 5
    for tr, te in folds:
        assert len(set(tr).intersection(set(te))) == 0


def test_t10_explanation_templates():
    """T-10: Every driver sentence contains a real feature value, no unfilled placeholders."""
    s1 = format_driver("glucose_delta_30", 35.0, 0.42)
    assert "35 mg/dL" in s1
    assert "{" not in s1

    s2 = format_driver("last_meal_carbs", 80.0, 0.55)
    assert "80 g" in s2
    assert "{" not in s2


def test_t12_mandatory_disclaimers():
    """T-12: PRD mandatory disclaimer strings are present in source."""
    assert "Sensitivity analysis on model inputs" in MANDATORY_DISCLAIMER_SCENARIO
    assert "Advisory forecast from a research prototype" in MANDATORY_DISCLAIMER_RISK
    assert "Replay of recorded data" in MANDATORY_DISCLAIMER_REPLAY
    assert "Indian meal presets are an extrapolation" in INDIAN_PRESET_LABEL
