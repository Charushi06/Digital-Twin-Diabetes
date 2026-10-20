"""Glucose Twin: a research-prototype digital twin for type 2 diabetes (CGMacros)."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
MODEL_VERSION = "glucotwin-0.1.0"


@lru_cache(maxsize=1)
def load_config() -> dict[str, Any]:
    path = Path(os.environ.get("GLUCOTWIN_CONFIG", ROOT / "config.yaml"))
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def path_from_cfg(rel: str) -> Path:
    p = Path(rel)
    return p if p.is_absolute() else ROOT / p
