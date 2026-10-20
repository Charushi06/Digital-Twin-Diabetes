"""Unified event schema (PRD section 7.2)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

Quality = Literal["ok", "interpolated", "out_of_range", "invalid", "missing"]


class MealPayload(BaseModel):
    carbs_g: float
    protein_g: float
    fat_g: float
    fiber_g: float | None = None
    kcal: float
    meal_type: str


class Event(BaseModel):
    patient_id: str
    ts: datetime  # timezone-naive, time-shifted dataset time
    kind: Literal["cgm", "hr", "mets", "meal"]
    value: float | None  # glucose mg/dL, bpm, or METs*10; None for meal
    meal: MealPayload | None = None
    quality: Quality
    source: str  # e.g. "cgmacros:dexcom", "synthetic"
