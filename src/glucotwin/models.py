"""Model ladder (PRD 9.1): B0a, B0b rules; B1 logistic regression; B2 monotone LightGBM."""

from __future__ import annotations

from dataclasses import dataclass, field

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .calibrate import Calibrator


def b0a_score(df: pd.DataFrame, horizon: int) -> np.ndarray:
    """Trend-arrow rule: projected glucose = now + slope_30 * H (mg/dL)."""
    return (df["glucose_now"] + df["glucose_slope_30"].fillna(0) * horizon).fillna(0).to_numpy(float)


def b0b_score(df: pd.DataFrame) -> np.ndarray:
    """Meal rule: carbs of a meal that started within the last grid step, else 0."""
    at_start = df["min_since_last_meal"].fillna(1e9) < 5
    return np.where(at_start, df["last_meal_carbs"].fillna(0), 0.0)


def make_lgbm(features: list[str], monotone: list[str], seed: int) -> lgb.LGBMClassifier:
    mono = [1 if f in monotone else 0 for f in features]
    return lgb.LGBMClassifier(
        n_estimators=300, learning_rate=0.05, num_leaves=31, min_child_samples=50,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0,
        class_weight="balanced", monotone_constraints=mono, monotone_constraints_method="advanced",
        random_state=seed, n_jobs=-1, verbose=-1, deterministic=True, force_col_wise=True,
    )


def make_lr(seed: int):
    return make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(),
                         LogisticRegression(class_weight="balanced", max_iter=3000, C=0.1, random_state=seed))


@dataclass
class FoldModel:
    kind: str                 # "B1" or "B2"
    horizon: int
    seed: int
    fold: int
    features: list[str]
    model: object
    calibrator: Calibrator
    train_pids: list[str]     # participants used to fit the model
    cal_pids: list[str]       # participants used to fit calibrator and theta
    test_pids: list[str]
    thetas: dict[float, float] = field(default_factory=dict)   # alert budget -> theta
    meal_ranges: dict[str, tuple[float, float]] = field(default_factory=dict)  # 5th-95th pct
    model_version: str = ""

    def raw(self, X: pd.DataFrame) -> np.ndarray:
        return self.model.predict_proba(X[self.features])[:, 1]

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return self.calibrator.transform(self.raw(X))
