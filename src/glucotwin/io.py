"""Raw CGMacros readers. Column names verified against the real files in M0 (see ASSUMPTIONS.md)."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from . import load_config, path_from_cfg

STATIC_FIELDS = ["age", "sex_male", "bmi", "hba1c", "fasting_glucose", "fasting_insulin",
                 "triglycerides", "hdl", "ldl"]

_BIO_MAP = {
    "Age": "age", "BMI": "bmi", "A1c PDL (Lab)": "hba1c", "Fasting GLU - PDL (Lab)": "fasting_glucose",
    "Insulin": "fasting_insulin", "Triglycerides": "triglycerides", "HDL": "hdl", "LDL (Cal)": "ldl",
}


def raw_dir(synthetic: bool = False) -> Path:
    cfg = load_config()
    return path_from_cfg(cfg["data"]["synthetic_dir"] if synthetic else cfg["data"]["raw_dir"])


def list_participants(synthetic: bool = False) -> dict[str, Path]:
    files = sorted(raw_dir(synthetic).rglob("CGMacros-*.csv"))
    return {f.stem: f for f in files}


def _find_col(cols: list[str], *names: str) -> str | None:
    norm = {re.sub(r"\s+", " ", c.strip().lower()): c for c in cols}
    for n in names:
        if n.lower() in norm:
            return norm[n.lower()]
    return None


def load_raw(path: Path) -> pd.DataFrame:
    """Load one participant file and normalise column names."""
    df = pd.read_csv(path, low_memory=False)
    cols = list(df.columns)
    rename = {}
    for std, cands in {
        "ts": ("Timestamp",), "libre": ("Libre GL",), "dexcom": ("Dexcom GL",), "hr": ("HR",),
        "act_kcal": ("Calories (Activity)",), "mets": ("METs", "Mets"), "meal_type": ("Meal Type",),
        "kcal": ("Calories",), "carbs": ("Carbs",), "protein": ("Protein",), "fat": ("Fat",),
        "fiber": ("Fiber", "Fibre"), "amount": ("Amount Consumed",),
    }.items():
        c = _find_col(cols, *cands)
        if c is not None:
            rename[c] = std
    df = df.rename(columns=rename)
    keep = [c for c in ["ts", "libre", "dexcom", "hr", "act_kcal", "mets", "meal_type", "kcal", "carbs",
                        "protein", "fat", "fiber", "amount"] if c in df.columns]
    df = df[keep].copy()
    df["ts"] = pd.to_datetime(df["ts"])
    for c in keep:
        if c not in ("ts", "meal_type"):
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "meal_type" in df.columns:
        df["meal_type"] = df["meal_type"].astype("string").str.strip().replace({"": pd.NA})
    return df.sort_values("ts").reset_index(drop=True)


def diagnosis_group(hba1c: float) -> str:
    if hba1c is None or np.isnan(hba1c):
        return "unknown"
    if hba1c < 5.7:
        return "healthy"
    if hba1c <= 6.4:
        return "prediabetes"
    return "type2"


def load_bio(synthetic: bool = False) -> pd.DataFrame:
    """Static profile per participant (index = participant id like 'CGMacros-001')."""
    path = next(raw_dir(synthetic).rglob("bio.csv"))
    b = pd.read_csv(path)
    b.columns = [re.sub(r"\s+", " ", c.strip()) for c in b.columns]
    out = pd.DataFrame(index=[f"CGMacros-{int(s):03d}" for s in b["subject"]])
    for src, dst in _BIO_MAP.items():
        out[dst] = pd.to_numeric(b[src], errors="coerce").to_numpy() if src in b.columns else np.nan
    out["sex_male"] = (b["Gender"].astype(str).str.strip().str.upper() == "M").astype(float).to_numpy()
    # Data dictionary: LDL 800 and VLDL 400 are calculation errors.
    out.loc[out["ldl"] >= 800, "ldl"] = np.nan
    out["homa_ir"] = out["fasting_insulin"] * out["fasting_glucose"] / 405.0
    out["group"] = [diagnosis_group(v) for v in out["hba1c"]]
    return out
