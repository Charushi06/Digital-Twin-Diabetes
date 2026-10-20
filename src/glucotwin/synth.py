"""Small synthetic generator for 3 fake patients in the CGMacros schema (PRD section 5.5)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import ROOT


def generate_synthetic_data(out_dir: Path | None = None) -> None:
    if out_dir is None:
        out_dir = ROOT / "data" / "synthetic"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Synthetic bio.csv
    bio_rows = [
        {"subject": 101, "Age": 45, "Gender": "M", "BMI": 26.5, "Body weight ": 175.0, "Height ": 68.0,
         "Self-identify ": "White", "A1c PDL (Lab)": 5.4, "Fasting GLU - PDL (Lab)": 92.0, "Insulin ": 6.5,
         "Triglycerides": 98.0, "Cholesterol": 180.0, "HDL": 55.0, "Non HDL ": 125.0, "LDL (Cal)": 105.0},
        {"subject": 102, "Age": 56, "Gender": "F", "BMI": 29.8, "Body weight ": 165.0, "Height ": 63.0,
         "Self-identify ": "Hispanic/Latino", "A1c PDL (Lab)": 6.1, "Fasting GLU - PDL (Lab)": 112.0, "Insulin ": 14.2,
         "Triglycerides": 160.0, "Cholesterol": 210.0, "HDL": 42.0, "Non HDL ": 168.0, "LDL (Cal)": 136.0},
        {"subject": 103, "Age": 62, "Gender": "M", "BMI": 33.2, "Body weight ": 210.0, "Height ": 67.0,
         "Self-identify ": "African American", "A1c PDL (Lab)": 7.8, "Fasting GLU - PDL (Lab)": 145.0, "Insulin ": 22.0,
         "Triglycerides": 220.0, "Cholesterol": 240.0, "HDL": 36.0, "Non HDL ": 204.0, "LDL (Cal)": 160.0},
    ]
    pd.DataFrame(bio_rows).to_csv(out_dir / "bio.csv", index=False)

    rng = np.random.default_rng(42)
    start_date = pd.Timestamp("2026-01-01 08:00:00")
    total_minutes = 7 * 24 * 60  # 7 days of 1-minute rows

    for sub_id in [101, 102, 103]:
        p_folder = out_dir / f"CGMacros-{sub_id:03d}"
        p_folder.mkdir(parents=True, exist_ok=True)
        ts_range = pd.date_range(start_date, periods=total_minutes, freq="1min")
        
        # Base glucose with diurnal cycle and random walk
        hour = ts_range.hour + ts_range.minute / 60.0
        base_g = 90.0 + (sub_id - 100) * 20.0 + 15.0 * np.sin(2 * np.pi * (hour - 6) / 24)
        noise = np.cumsum(rng.normal(0, 0.4, size=total_minutes))
        glucose = np.clip(base_g + noise, 60, 280)
        
        # Heart rate
        hr = np.clip(68.0 + 12.0 * np.sin(2 * np.pi * (hour - 8) / 24) + rng.normal(0, 3, size=total_minutes), 45, 150)
        mets = np.clip(12.0 + rng.exponential(5, size=total_minutes), 10, 100)

        meal_types = [None] * total_minutes
        carbs = [np.nan] * total_minutes
        protein = [np.nan] * total_minutes
        fat = [np.nan] * total_minutes
        fiber = [np.nan] * total_minutes
        kcal = [np.nan] * total_minutes

        # Add 3 meals a day
        for day in range(7):
            day_offset = day * 1440
            for m_time, m_name, m_carbs in [(8*60, "Breakfast", 45.0), (13*60, "Lunch", 65.0), (19*60, "Dinner", 75.0)]:
                idx = day_offset + m_time + rng.integers(-20, 20)
                if 0 <= idx < total_minutes:
                    meal_types[idx] = m_name
                    carbs[idx] = m_carbs + rng.uniform(-10, 20)
                    protein[idx] = 20.0 + rng.uniform(0, 15)
                    fat[idx] = 15.0 + rng.uniform(0, 10)
                    fiber[idx] = 5.0 + rng.uniform(0, 5)
                    kcal[idx] = carbs[idx] * 4 + protein[idx] * 4 + fat[idx] * 9
                    
                    # Add glucose excursion bump after meal
                    bump_len = min(180, total_minutes - idx)
                    bump = (carbs[idx] * 0.8) * np.sin(np.linspace(0, np.pi, bump_len))
                    glucose[idx:idx+bump_len] += bump

        df_p = pd.DataFrame({
            "Timestamp": ts_range.strftime("%Y-%m-%d %H:%M:%S"),
            "Libre GL": np.round(glucose + rng.normal(0, 2, size=total_minutes), 1),
            "Dexcom GL": np.round(glucose, 1),
            "HR": np.round(hr, 0),
            "Calories (Activity)": np.round(mets * 0.1, 2),
            "METs": np.round(mets, 0),
            "Meal Type": meal_types,
            "Calories": kcal,
            "Carbs": carbs,
            "Protein": protein,
            "Fat": fat,
            "Fiber": fiber,
            "Amount Consumed": [100.0 if mt else np.nan for mt in meal_types]
        })
        df_p.to_csv(p_folder / f"CGMacros-{sub_id:03d}.csv", index=False)


if __name__ == "__main__":
    generate_synthetic_data()
    print("Synthetic dataset generated.")
