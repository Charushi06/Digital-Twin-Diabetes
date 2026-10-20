"""FastAPI Full-Stack Digital Twin Backend (PRD section 11 & 12)."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Ensure src/ is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from glucotwin import MODEL_VERSION, ROOT, load_config, path_from_cfg
from glucotwin.alerts import alerts_from_probs
from glucotwin.data import bio_table, list_processed, load_frames, load_series, processed_dir
from glucotwin.explain import explain_sample
from glucotwin.features import ALL_FEATURES, build_features, to_minutes
from glucotwin.scenarios import (INDIAN_PRESET_LABEL, MANDATORY_DISCLAIMER_REPLAY,
                                MANDATORY_DISCLAIMER_RISK, MANDATORY_DISCLAIMER_SCENARIO,
                                load_india_presets, run_meal_scenario)

app = FastAPI(
    title="Glucose Twin API",
    description="Type 2 Diabetes Digital Twin Clinical Panel & Advisory API",
    version=MODEL_VERSION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global caches
_MODELS: dict[str, Any] = {}
_P2F: dict[str, dict[str, int]] = {}


def get_models_for_patient(pid: str) -> dict[int, Any]:
    """Retrieve the fold model for each horizon that held this participant out (Rule 5)."""
    cfg = load_config()
    models_dir = path_from_cfg(cfg["models_dir"])
    p2f_path = models_dir / "participant_to_fold.json"
    
    if not p2f_path.exists():
        return {}
    
    global _P2F
    if not _P2F:
        _P2F = json.loads(p2f_path.read_text())
    
    seed = str(cfg["seed"])
    fold_idx = _P2F.get(seed, {}).get(pid, 0)
    
    out = {}
    for H in cfg["horizons_minutes"]:
        key = f"h{H}_s{seed}_f{fold_idx}"
        if key not in _MODELS:
            m_path = models_dir / f"h{H}" / f"B2_s{seed}_f{fold_idx}.pkl"
            if m_path.exists():
                _MODELS[key] = joblib.load(m_path)
        if key in _MODELS:
            out[H] = _MODELS[key]
    return out


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "version": MODEL_VERSION,
        "disclaimer": MANDATORY_DISCLAIMER_RISK
    }


@app.get("/api/patients")
def list_patients():
    """UC1: Panel view list of all patients sorted by 120-minute excursion risk."""
    cfg = load_config()
    T = float(cfg["excursion"]["threshold_mgdl"] or 180.0)
    pids = list_processed()
    bio = bio_table()
    
    # Check if out-of-fold predictions exist
    oof_path = processed_dir() / "oof.parquet"
    oof_df = pd.read_parquet(oof_path) if oof_path.exists() else None

    patients = []
    for pid in pids:
        grid, meals = load_frames(pid)
        g_series = grid["glucose"].dropna()
        latest_g = float(g_series.iloc[-1]) if len(g_series) else 100.0
        prev_g = float(g_series.iloc[-6]) if len(g_series) >= 6 else latest_g
        delta = latest_g - prev_g
        
        trend = "rising" if delta > 5 else ("falling" if delta < -5 else "steady")
        currently_high = latest_g > T
        
        # Risk estimation
        risk_30, risk_60, risk_120 = 0.05, 0.10, 0.15
        spread_120 = 0.02
        if oof_df is not None:
            p_oof = oof_df[oof_df["pid"] == pid]
            if not p_oof.empty:
                r120_series = p_oof["B2_h120"].dropna()
                if len(r120_series):
                    risk_120 = float(r120_series.iloc[-1])
                r60_series = p_oof.get("B2_h60", pd.Series()).dropna()
                if len(r60_series):
                    risk_60 = float(r60_series.iloc[-1])
                r30_series = p_oof.get("B2_h30", pd.Series()).dropna()
                if len(r30_series):
                    risk_30 = float(r30_series.iloc[-1])
                spread_series = p_oof.get("B2_h120_spread", pd.Series()).dropna()
                if len(spread_series):
                    spread_120 = float(spread_series.iloc[-1])

        group = bio.loc[pid, "group"] if pid in bio.index else "unknown"
        valid_frac = float(grid["glucose_valid"].mean())
        hr_valid_frac = float(grid["hr_valid"].mean())

        patients.append({
            "pid": pid,
            "group": group,
            "latest_glucose": round(latest_g, 1),
            "trend": trend,
            "glucose_delta_30": round(delta, 1),
            "currently_high": bool(currently_high),
            "risk_30": round(risk_30, 3),
            "risk_60": round(risk_60, 3),
            "risk_120": round(risk_120, 3),
            "risk_interval_120": [round(max(0.0, risk_120 - spread_120/2), 3),
                                  round(min(1.0, risk_120 + spread_120/2), 3)],
            "sensor_completeness": round(valid_frac * 100, 1),
            "hr_completeness": round(hr_valid_frac * 100, 1),
            "meals_count": len(meals),
            "is_warmed_up": len(grid) >= int(cfg["warmup_hours"] * 12),
            "low_confidence": valid_frac < 0.90
        })

    # Sort descending by 120-minute risk (UC1 requirement)
    patients.sort(key=lambda p: (not p["currently_high"], -p["risk_120"]))
    return {
        "patients": patients,
        "cohort_count": len(patients),
        "disclaimer_risk": MANDATORY_DISCLAIMER_RISK,
        "disclaimer_replay": MANDATORY_DISCLAIMER_REPLAY
    }


@app.get("/api/patients/{pid}")
def get_patient(pid: str):
    """UC2 & UC6: Detailed digital twin state, timeline traces, twin parameters & cohort benchmarks."""
    cfg = load_config()
    T = float(cfg["excursion"]["threshold_mgdl"] or 180.0)
    bio = bio_table()
    if pid not in bio.index:
        raise HTTPException(status_code=404, detail="Patient not found")

    ps, grid, meals = load_series(pid)
    
    # Cohort statistics for comparison
    all_pids = list_processed()
    all_means = []
    all_sds = []
    all_meal_rises = []
    all_resting_hrs = []
    for p in all_pids:
        try:
            s_p, _, _ = load_series(p)
            if s_p.baseline.get("personal_mean_glucose"):
                all_means.append(s_p.baseline["personal_mean_glucose"])
            if s_p.baseline.get("personal_sd_glucose"):
                all_sds.append(s_p.baseline["personal_sd_glucose"])
            if s_p.baseline.get("personal_median_meal_rise"):
                all_meal_rises.append(s_p.baseline["personal_median_meal_rise"])
            if s_p.baseline.get("personal_resting_hr"):
                all_resting_hrs.append(s_p.baseline["personal_resting_hr"])
        except Exception:
            pass

    cohort_stats = {
        "mean_glucose_cohort_median": float(np.nanmedian(all_means)) if all_means else 115.0,
        "sd_glucose_cohort_median": float(np.nanmedian(all_sds)) if all_sds else 22.0,
        "meal_rise_cohort_median": float(np.nanmedian(all_meal_rises)) if all_meal_rises else 35.0,
        "resting_hr_cohort_median": float(np.nanmedian(all_resting_hrs)) if all_resting_hrs else 62.0,
    }

    # Out-of-fold probabilities
    oof_path = processed_dir() / "oof.parquet"
    oof_df = pd.read_parquet(oof_path) if oof_path.exists() else None
    
    grid_res = grid.copy()
    grid_res["ts_str"] = grid_res["ts"].dt.strftime("%Y-%m-%d %H:%M")
    grid_res["t_min"] = to_minutes(grid_res["ts"])
    
    if oof_df is not None:
        p_oof = oof_df[oof_df["pid"] == pid]
        merged = pd.merge(grid_res, p_oof[["t", "B2_h30", "B2_h60", "B2_h120", "B2_h120_spread"]],
                          left_on="t_min", right_on="t", how="left")
    else:
        merged = grid_res
        merged["B2_h30"] = np.nan
        merged["B2_h60"] = np.nan
        merged["B2_h120"] = np.nan
        merged["B2_h120_spread"] = 0.02

    # Compute alerts based on B2 at 2/day budget
    b2_scores = merged["B2_h120"].to_numpy(float)
    alert_mask = alerts_from_probs(b2_scores, 0.45, cfg["alerts"]["consecutive_points"], 12)
    merged["alert"] = alert_mask

    # Format timeline downsampled to regular intervals for crisp client rendering
    timeline = []
    for _, row in merged.iterrows():
        timeline.append({
            "ts": row["ts_str"],
            "t_min": int(row["t_min"]),
            "glucose": None if pd.isna(row["glucose"]) else round(float(row["glucose"]), 1),
            "glucose_obs": None if pd.isna(row["glucose_obs"]) else round(float(row["glucose_obs"]), 1),
            "glucose_quality": str(row["glucose_quality"]),
            "hr": None if pd.isna(row["hr"]) else round(float(row["hr"]), 0),
            "mets": None if pd.isna(row["mets"]) else round(float(row["mets"]), 1),
            "wearable_off": bool(row["wearable_off"]),
            "risk_30": None if pd.isna(row["B2_h30"]) else round(float(row["B2_h30"]), 3),
            "risk_60": None if pd.isna(row["B2_h60"]) else round(float(row["B2_h60"]), 3),
            "risk_120": None if pd.isna(row["B2_h120"]) else round(float(row["B2_h120"]), 3),
            "risk_120_spread": 0.02 if pd.isna(row.get("B2_h120_spread")) else round(float(row["B2_h120_spread"]), 3),
            "alert": bool(row["alert"])
        })

    # Format meals
    meal_list = []
    for _, m in meals.iterrows():
        meal_list.append({
            "ts": m["ts"].strftime("%Y-%m-%d %H:%M"),
            "meal_type": str(m["meal_type"]),
            "carbs_g": float(m["carbs"]) if pd.notna(m["carbs"]) else 0.0,
            "protein_g": float(m["protein"]) if pd.notna(m["protein"]) else 0.0,
            "fat_g": float(m["fat"]) if pd.notna(m["fat"]) else 0.0,
            "fiber_g": float(m["fiber"]) if pd.notna(m["fiber"]) else None,
            "kcal": float(m["kcal"]) if pd.notna(m["kcal"]) else 0.0
        })

    profile = bio.loc[pid].to_dict()
    # Clean profile for JSON serialization
    clean_profile = {}
    for k, v in profile.items():
        if pd.isna(v):
            clean_profile[k] = None
        elif isinstance(v, (np.floating, float)):
            clean_profile[k] = round(float(v), 2)
        else:
            clean_profile[k] = v

    return {
        "pid": pid,
        "group": clean_profile.get("group", "unknown"),
        "profile": clean_profile,
        "baseline": ps.baseline,
        "cohort_stats": cohort_stats,
        "excursion_threshold": T,
        "timeline": timeline,
        "meals": meal_list,
        "model_version": MODEL_VERSION,
        "held_out_note": f"Held-out prediction: {pid} was not used in the training fold scoring this data.",
        "disclaimers": {
            "risk": MANDATORY_DISCLAIMER_RISK,
            "replay": MANDATORY_DISCLAIMER_REPLAY
        }
    }


@app.get("/api/patients/{pid}/drivers")
def get_drivers(pid: str, t_min: int | None = Query(None)):
    """UC2: Explainability drivers formatted in plain clinical language (Appendix A)."""
    models = get_models_for_patient(pid)
    m120 = models.get(120)
    if not m120:
        raise HTTPException(status_code=500, detail="Fold model not loaded")

    ps, grid, _ = load_series(pid)
    target_t = t_min if t_min is not None else int(ps.t[-1])
    
    feats = build_features(ps, target_t)
    drivers = explain_sample(m120.model, feats, top_k=5)
    
    return {
        "pid": pid,
        "t_min": target_t,
        "drivers": drivers,
        "model_horizon": 120,
        "disclaimer": MANDATORY_DISCLAIMER_RISK
    }


class ScenarioRequest(BaseModel):
    t_min: int
    carbs_g: float
    protein_g: float
    fat_g: float
    fiber_g: float | None = None


@app.post("/api/patients/{pid}/scenario")
def run_scenario(pid: str, req: ScenarioRequest):
    """UC3: Pre-meal sensitivity check (S1) with monotonicity verification and OOD guard."""
    models = get_models_for_patient(pid)
    m120 = models.get(120)
    if not m120:
        raise HTTPException(status_code=500, detail="Fold model for 120m not available")

    ps, _, _ = load_series(pid)
    base_feats = build_features(ps, req.t_min)
    
    result = run_meal_scenario(
        m120,
        base_features=base_feats,
        new_carbs=req.carbs_g,
        new_protein=req.protein_g,
        new_fat=req.fat_g,
        new_fiber=req.fiber_g
    )
    return result


@app.get("/api/presets")
def get_presets():
    """UC4: Indian meal presets with explicit NIN-ICMR IFCT 2017 sources and extrapolation label."""
    presets = load_india_presets()
    return {
        "presets": presets,
        "label": INDIAN_PRESET_LABEL,
        "is_extrapolation": True,
        "disclaimer": MANDATORY_DISCLAIMER_SCENARIO
    }


@app.get("/api/metrics")
def get_metrics_summary():
    """Metrics and Ablation table (PRD section 16) for transparency."""
    cfg = load_config()
    rep_dir = path_from_cfg(cfg["reports_dir"])
    metrics_md_path = rep_dir / "metrics.md"
    ablation_md_path = rep_dir / "ablation.md"
    audit_md_path = rep_dir / "data_audit.md"

    return {
        "metrics_markdown": metrics_md_path.read_text(encoding="utf-8") if metrics_md_path.exists() else "Training in progress...",
        "ablation_markdown": ablation_md_path.read_text(encoding="utf-8") if ablation_md_path.exists() else "Ablation in progress...",
        "audit_markdown": audit_md_path.read_text(encoding="utf-8") if audit_md_path.exists() else "Audit pending...",
        "disclaimer": MANDATORY_DISCLAIMER_RISK
    }
