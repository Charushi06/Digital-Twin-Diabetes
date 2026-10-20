"""Loading processed participants into PatientSeries (shared by batch, twin, replay, dashboard)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd

from . import load_config, path_from_cfg
from .features import PatientSeries, compute_baseline, series_from_frames, to_minutes
from .io import load_bio


def processed_dir(synthetic: bool = False) -> Path:
    return path_from_cfg(load_config()["data"]["processed_dir"]) / ("synthetic" if synthetic else "real")


def list_processed(synthetic: bool = False) -> list[str]:
    return sorted(p.name.replace("_grid.parquet", "") for p in processed_dir(synthetic).glob("*_grid.parquet"))


@lru_cache(maxsize=4)
def bio_table(synthetic: bool = False) -> pd.DataFrame:
    return load_bio(synthetic)


def load_frames(pid: str, synthetic: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = processed_dir(synthetic)
    return pd.read_parquet(d / f"{pid}_grid.parquet"), pd.read_parquet(d / f"{pid}_meals.parquet")


def static_for(pid: str, synthetic: bool = False) -> dict:
    b = bio_table(synthetic)
    return b.loc[pid].to_dict() if pid in b.index else {}


def warm_end_minute(t0: int) -> int:
    cfg = load_config()
    return int(t0 + cfg["warmup_hours"] * 60 - cfg["grid_minutes"])


def load_series(pid: str, synthetic: bool = False) -> tuple[PatientSeries, pd.DataFrame, pd.DataFrame]:
    grid, meals = load_frames(pid, synthetic)
    s = series_from_frames(pid, grid, meals, static_for(pid, synthetic))
    s.baseline = compute_baseline(s, warm_end_minute(int(s.t[0])))
    return s, grid, meals


def grid_minutes_of(grid: pd.DataFrame):
    return to_minutes(grid["ts"])
