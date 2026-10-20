"""Plain-language explanations for model predictions (PRD section 10.1 & Appendix A)."""

from __future__ import annotations

import numpy as np
import shap


def format_driver(feat_name: str, feat_val: float, shap_val: float) -> str:
    """Translate feature and value into an audited plain-language sentence."""
    if feat_val is None or np.isnan(feat_val):
        return f"{feat_name}: data not available."

    v = float(feat_val)

    if feat_name == "glucose_delta_30":
        return f"Glucose has changed by {v:+.0f} mg/dL in the last 30 minutes."
    elif feat_name == "glucose_now":
        return f"Glucose is currently {v:.0f} mg/dL."
    elif feat_name == "glucose_minus_personal_mean":
        return f"Glucose is {v:+.0f} mg/dL compared with this patient's usual level."
    elif feat_name == "last_meal_carbs":
        return f"The last meal contained {v:.0f} g of carbohydrate."
    elif feat_name == "min_since_last_meal":
        return f"The last meal was {v:.0f} minutes ago."
    elif feat_name == "glucose_rise_since_meal":
        return f"Glucose has risen {v:.0f} mg/dL since the last meal started."
    elif feat_name == "carbs_last_4h":
        return f"{v:.0f} g of carbohydrate in the last 4 hours."
    elif feat_name == "personal_median_meal_rise":
        return f"This patient's meals typically raise glucose by {v:.0f} mg/dL."
    elif feat_name == "hr_minus_resting":
        return f"Heart rate is {v:+.0f} bpm above this patient's resting rate."
    elif feat_name in ("mets_mean_30", "act_kcal_mean_30"):
        direction = "higher" if v > 15 else "lower"
        return f"Recent activity is {direction} than this patient's usual."
    elif feat_name == "hba1c":
        return f"HbA1c is {v:.1f}%."
    elif feat_name in ("hour_sin", "hour_cos"):
        return "Time of day is currently contributing to excursion risk for this patient."
    elif feat_name == "glucose_slope_30":
        return f"Glucose rate of change is {v*5:+.1f} mg/dL every 5 minutes."
    elif feat_name == "fasting_glucose":
        return f"Clinical baseline fasting glucose is {v:.0f} mg/dL."
    elif feat_name == "bmi":
        return f"Body Mass Index (BMI) is {v:.1f} kg/m²."
    elif feat_name == "homa_ir":
        return f"Calculated insulin resistance (HOMA-IR) is {v:.2f}."
    else:
        direction = "elevating" if shap_val > 0 else "moderating"
        return f"{feat_name.replace('_', ' ').capitalize()} is {v:.1f}, {direction} estimated risk."


def explain_sample(tree_model, X_sample: dict[str, float], top_k: int = 4) -> list[dict]:
    """Compute SHAP contributions and generate formatted plain-language sentences."""
    import pandas as pd
    df_sample = pd.DataFrame([X_sample])
    explainer = shap.TreeExplainer(tree_model)
    shap_vals = explainer.shap_values(df_sample)
    
    # LightGBM binary classifier might return a list of 2 arrays or 1 array
    if isinstance(shap_vals, list) and len(shap_vals) == 2:
        sv = shap_vals[1][0]
    elif isinstance(shap_vals, np.ndarray) and shap_vals.ndim == 2:
        sv = shap_vals[0]
    else:
        sv = np.asarray(shap_vals).ravel()

    features = list(df_sample.columns)
    # Sort features by absolute contribution to positive risk
    ranked_idx = np.argsort(-np.abs(sv))
    
    drivers = []
    for idx in ranked_idx[:top_k]:
        fn = features[idx]
        val = df_sample.iloc[0, idx]
        s_val = float(sv[idx])
        drivers.append({
            "feature": fn,
            "value": None if np.isnan(val) else float(val),
            "shap_value": s_val,
            "sentence": format_driver(fn, val, s_val),
            "direction": "risk_increasing" if s_val > 0 else "risk_decreasing"
        })
    return drivers
