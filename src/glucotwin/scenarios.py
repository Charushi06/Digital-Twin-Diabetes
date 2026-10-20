"""Scenario analysis: pre-meal sensitivity (S1) and Indian meal presets (PRD section 10)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

from . import ROOT

MANDATORY_DISCLAIMER_SCENARIO = (
    "Sensitivity analysis on model inputs. Not a treatment simulation, not proof of causation, not medical advice."
)
MANDATORY_DISCLAIMER_RISK = "Advisory forecast from a research prototype. Not a diagnosis."
MANDATORY_DISCLAIMER_REPLAY = "Replay of recorded data. Not a live patient."
INDIAN_PRESET_LABEL = "Model trained on US meals. Indian meal presets are an extrapolation and illustrative only."


def load_india_presets() -> list[dict[str, Any]]:
    path = ROOT / "data" / "india_meals.yaml"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    presets = data.get("presets", [])
    # PRD rule: presets shown ONLY if every preset has a non-empty source
    for p in presets:
        if not p.get("source") or str(p.get("source")).strip() == "":
            return []
    return presets


def check_ood(macros: dict[str, float], ranges: dict[str, tuple[float, float]]) -> list[str]:
    """Flag if requested meal macros fall outside the 5th-95th percentiles of training meals."""
    warnings = []
    mapping = {
        "carbs_g": "last_meal_carbs",
        "protein_g": "last_meal_protein",
        "fat_g": "last_meal_fat",
        "fiber_g": "last_meal_fiber"
    }
    for field_name, range_key in mapping.items():
        val = macros.get(field_name)
        if val is not None and range_key in ranges:
            low, high = ranges[range_key]
            if val < low or val > high:
                warnings.append(
                    f"{field_name.replace('_g', '')} ({val:.1f}g) is outside the training range "
                    f"[{low:.1f}g - {high:.1f}g] seen by the model."
                )
    return warnings


def run_meal_scenario(
    fold_model,
    base_features: dict[str, float],
    new_carbs: float,
    new_protein: float,
    new_fat: float,
    new_fiber: float | None = None
) -> dict[str, Any]:
    """Compute risk difference when editing an upcoming meal at meal start time."""
    feat_baseline = dict(base_features)
    feat_scenario = dict(base_features)

    # Update meal features for scenario
    feat_scenario["last_meal_carbs"] = float(new_carbs)
    feat_scenario["last_meal_protein"] = float(new_protein)
    feat_scenario["last_meal_fat"] = float(new_fat)
    feat_scenario["last_meal_fiber"] = float(new_fiber) if new_fiber is not None else 0.0
    feat_scenario["min_since_last_meal"] = 0.0
    feat_scenario["glucose_rise_since_meal"] = 0.0

    # Re-evaluate cumulative carbs in last 4 hours
    old_meal_carbs = base_features.get("last_meal_carbs", 0.0)
    if np.isnan(old_meal_carbs):
        old_meal_carbs = 0.0
    prev_carbs_4h = base_features.get("carbs_last_4h", 0.0)
    feat_scenario["carbs_last_4h"] = max(0.0, prev_carbs_4h - old_meal_carbs + new_carbs)

    df_base = pd.DataFrame([feat_baseline])
    df_scen = pd.DataFrame([feat_scenario])

    p_base = float(fold_model.predict(df_base)[0])
    p_scen = float(fold_model.predict(df_scen)[0])

    # Monotonicity test: increasing carbs cannot decrease risk
    # (Enforced by LightGBM monotone constraints)
    is_monotonic = True
    if new_carbs > old_meal_carbs and p_scen < (p_base - 1e-5):
        is_monotonic = False

    macros = {
        "carbs_g": new_carbs,
        "protein_g": new_protein,
        "fat_g": new_fat,
        "fiber_g": new_fiber or 0.0
    }
    ood_warnings = check_ood(macros, fold_model.meal_ranges)

    return {
        "baseline_prob": p_base,
        "scenario_prob": p_scen,
        "delta_prob": p_scen - p_base,
        "is_monotonic": is_monotonic,
        "ood_warnings": ood_warnings,
        "is_ood": len(ood_warnings) > 0,
        "disclaimer": MANDATORY_DISCLAIMER_SCENARIO
    }
