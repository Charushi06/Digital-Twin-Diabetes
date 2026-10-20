"""Persistent per-patient Digital Twin state (PRD section 7)."""

from __future__ import annotations

from collections import deque
from datetime import datetime, timedelta
from typing import Any

import numpy as np
import pandas as pd

from . import MODEL_VERSION, load_config
from .features import (ALL_FEATURES, LOOKBACK_BUFFER_MIN, PatientSeries,
                       build_features, compute_baseline)
from .schema import Event


class TwinState:
    """Virtual twin keeping rolling sensor buffers, warm-up baseline, and scoring capabilities."""

    def __init__(self, patient_id: str, static_profile: dict[str, Any] | None = None) -> None:
        self.patient_id = patient_id
        self.static_profile = static_profile or {}
        self.cfg = load_config()
        self.grid_minutes = self.cfg["grid_minutes"]
        self.warmup_hours = self.cfg["warmup_hours"]

        # Buffers: store (timestamp_minutes, value)
        self.glucose_buffer: deque[tuple[int, float]] = deque()
        self.hr_buffer: deque[tuple[int, float]] = deque()
        self.mets_buffer: deque[tuple[int, float]] = deque()
        self.act_kcal_buffer: deque[tuple[int, float]] = deque()
        self.meals: list[dict[str, Any]] = []

        self.first_ts_min: int | None = None
        self.warmup_end_min: int | None = None
        self.is_warmed_up = False
        self.baseline: dict[str, float] = {}

        self.last_update_ts: datetime | None = None
        self.last_update_min: int | None = None
        self.latest_scores: dict[int, dict[str, Any]] = {}
        self.model_version = MODEL_VERSION

    def update(self, event: Event) -> None:
        """Ingest a single Event (cgm, hr, mets, meal)."""
        ts_min = int(event.ts.timestamp() // 60)
        self.last_update_ts = event.ts
        self.last_update_min = ts_min

        if self.first_ts_min is None:
            self.first_ts_min = ts_min
            self.warmup_end_min = int(ts_min + self.warmup_hours * 60 - self.grid_minutes)

        if event.kind == "cgm":
            if event.quality != "missing" and event.value is not None:
                self.glucose_buffer.append((ts_min, float(event.value)))
        elif event.kind == "hr":
            if event.quality != "missing" and event.value is not None:
                self.hr_buffer.append((ts_min, float(event.value)))
        elif event.kind == "mets":
            if event.quality != "missing" and event.value is not None:
                self.mets_buffer.append((ts_min, float(event.value)))
        elif event.kind == "meal" and event.meal is not None:
            self.meals.append({
                "ts_min": ts_min,
                "carbs": float(event.meal.carbs_g),
                "protein": float(event.meal.protein_g),
                "fat": float(event.meal.fat_g),
                "fiber": float(event.meal.fiber_g) if event.meal.fiber_g is not None else 0.0,
                "kcal": float(event.meal.kcal),
                "meal_type": event.meal.meal_type
            })

        # Evict data older than 6 hours from rolling buffers to maintain bounded memory
        cutoff = ts_min - 360
        self._trim_buffer(self.glucose_buffer, cutoff)
        self._trim_buffer(self.hr_buffer, cutoff)
        self._trim_buffer(self.mets_buffer, cutoff)
        self._trim_buffer(self.act_kcal_buffer, cutoff)

        if not self.is_warmed_up and self.warmup_end_min is not None and ts_min >= self.warmup_end_min:
            self._finalize_warmup()

    def _trim_buffer(self, buf: deque[tuple[int, float]], cutoff: int) -> None:
        while buf and buf[0][0] < cutoff:
            buf.popleft()

    def _finalize_warmup(self) -> None:
        """Compute personal baseline from warm-up observations."""
        self.is_warmed_up = True
        # Construct PatientSeries for warm-up computation
        ps = self.to_patient_series(up_to_min=self.warmup_end_min)
        if ps is not None and self.warmup_end_min is not None:
            self.baseline = compute_baseline(ps, self.warmup_end_min)

    def to_patient_series(self, up_to_min: int | None = None) -> PatientSeries | None:
        """Create a PatientSeries representation strictly using data up to `up_to_min`."""
        if not self.glucose_buffer:
            return None
        t_max = up_to_min if up_to_min is not None else self.last_update_min
        if t_max is None:
            return None

        # Build regular 5-minute grid over the lookback horizon (4 hours)
        t_min = t_max - LOOKBACK_BUFFER_MIN
        grid_times = np.arange(t_min, t_max + 1, self.grid_minutes, dtype=np.int64)

        g_dict = dict(self.glucose_buffer)
        hr_dict = dict(self.hr_buffer)
        m_dict = dict(self.mets_buffer)
        ak_dict = dict(self.act_kcal_buffer)

        glucose_arr = np.array([g_dict.get(t, np.nan) for t in grid_times], dtype=float)
        hr_arr = np.array([hr_dict.get(t, np.nan) for t in grid_times], dtype=float)
        mets_arr = np.array([m_dict.get(t, np.nan) for t in grid_times], dtype=float)
        ak_arr = np.array([ak_dict.get(t, np.nan) for t in grid_times], dtype=float)

        # Causal wearable_off: >= 2 consecutive invalid HR samples (10 min)
        hr_invalid = np.isnan(hr_arr) | (hr_arr < 30) | (hr_arr > 220)
        wearable_off = np.zeros(len(grid_times), dtype=bool)
        streak = 0
        for i, inv in enumerate(hr_invalid):
            streak = streak + 1 if inv else 0
            if streak >= 2:
                wearable_off[i] = True

        relevant_meals = [m for m in self.meals if m["ts_min"] <= t_max]
        meal_t = np.array([m["ts_min"] for m in relevant_meals], dtype=np.int64)
        meal_carbs = np.array([m["carbs"] for m in relevant_meals], dtype=float)
        meal_protein = np.array([m["protein"] for m in relevant_meals], dtype=float)
        meal_fat = np.array([m["fat"] for m in relevant_meals], dtype=float)
        meal_fiber = np.array([m["fiber"] for m in relevant_meals], dtype=float)
        meal_kcal = np.array([m["kcal"] for m in relevant_meals], dtype=float)
        meal_type = np.array([1 for _ in relevant_meals], dtype=int)

        ps = PatientSeries(
            pid=self.patient_id,
            t=grid_times,
            glucose=glucose_arr,
            hr=hr_arr,
            wearable_off=wearable_off,
            mets=mets_arr,
            act_kcal=ak_arr,
            meal_t=meal_t,
            meal_carbs=meal_carbs,
            meal_protein=meal_protein,
            meal_fat=meal_fat,
            meal_fiber=meal_fiber,
            meal_kcal=meal_kcal,
            meal_type=meal_type,
            static=self.static_profile,
            baseline=self.baseline
        )
        return ps

    def score(self, t_min: int, fold_models: dict[int, Any]) -> dict[int, dict[str, Any]]:
        """Compute the shared feature vector and score all horizons (PRD section 7.4)."""
        ps = self.to_patient_series(up_to_min=t_min)
        if ps is None:
            return {}

        feats = build_features(ps, t_min)
        df_feat = pd.DataFrame([feats])

        scores = {}
        for H, model in fold_models.items():
            prob = float(model.predict(df_feat)[0])
            scores[H] = {
                "horizon": H,
                "probability": prob,
                "features": feats,
                "is_warmed_up": self.is_warmed_up,
                "quality_ok": feats.get("glucose_valid_frac_120", 0) >= 0.80
            }
        self.latest_scores = scores
        return scores
