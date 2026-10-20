"""Replay engine for streaming participant events (PRD section 7.4)."""

from __future__ import annotations

import time
from typing import Generator

import numpy as np
import pandas as pd

from .data import load_frames, static_for
from .schema import Event, MealPayload
from .twin import TwinState


def generate_events(pid: str, synthetic: bool = False) -> Generator[Event, None, None]:
    """Convert preprocessed grid and meal tables into a chronological Event stream."""
    grid, meals = load_frames(pid, synthetic)
    
    events: list[Event] = []
    
    # CGM, HR, METs events
    for _, row in grid.iterrows():
        ts = row["ts"]
        if row["glucose_valid"]:
            events.append(Event(
                patient_id=pid,
                ts=ts,
                kind="cgm",
                value=float(row["glucose"]),
                quality=row["glucose_quality"],
                source="cgmacros:dexcom"
            ))
        if row["hr_valid"]:
            events.append(Event(
                patient_id=pid,
                ts=ts,
                kind="hr",
                value=float(row["hr"]),
                quality="ok",
                source="cgmacros:fitbit"
            ))
        if pd.notna(row.get("mets")):
            events.append(Event(
                patient_id=pid,
                ts=ts,
                kind="mets",
                value=float(row["mets"]),
                quality="ok",
                source="cgmacros:fitbit"
            ))

    # Meal events
    for _, m in meals.iterrows():
        events.append(Event(
            patient_id=pid,
            ts=m["ts"],
            kind="meal",
            value=None,
            meal=MealPayload(
                carbs_g=float(m["carbs"]) if pd.notna(m["carbs"]) else 0.0,
                protein_g=float(m["protein"]) if pd.notna(m["protein"]) else 0.0,
                fat_g=float(m["fat"]) if pd.notna(m["fat"]) else 0.0,
                fiber_g=float(m["fiber"]) if pd.notna(m["fiber"]) else None,
                kcal=float(m["kcal"]) if pd.notna(m["kcal"]) else 0.0,
                meal_type=str(m["meal_type"])
            ),
            quality="ok",
            source="cgmacros:meal_log"
        ))

    # Sort strictly by timestamp
    events.sort(key=lambda e: e.ts)
    for ev in events:
        yield ev


def run_replay(pid: str, fold_models: dict[int, any], synthetic: bool = False) -> list[dict]:
    """Replay a participant and record scores at every 5-minute grid point."""
    static = static_for(pid, synthetic)
    twin = TwinState(pid, static)
    
    scores_history = []
    last_scored_min = -1

    for event in generate_events(pid, synthetic):
        twin.update(event)
        cur_min = int(event.ts.timestamp() // 60)
        # Score on 5-minute boundaries
        if cur_min % 5 == 0 and cur_min != last_scored_min:
            scores = twin.score(cur_min, fold_models)
            if scores:
                scores_history.append({
                    "ts": event.ts.isoformat(),
                    "t_min": cur_min,
                    "scores": scores
                })
            last_scored_min = cur_min

    return scores_history
