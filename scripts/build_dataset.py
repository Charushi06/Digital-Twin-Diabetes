"""M1/M2: build labelled feature table for every participant (batch pipeline).

Usage: python scripts/build_dataset.py [--synthetic]
Writes data/processed/<real|synthetic>/dataset.parquet and reports/windows.md
"""

from __future__ import annotations

import argparse
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from glucotwin import load_config, path_from_cfg  # noqa: E402
from glucotwin.data import bio_table, list_processed, load_series, processed_dir  # noqa: E402
from glucotwin.features import batch_features  # noqa: E402
from glucotwin.labels import build_labels, episode_onsets  # noqa: E402


def one(args: tuple[str, bool]) -> pd.DataFrame:
    pid, synthetic = args
    cfg = load_config()
    T = cfg["excursion"]["threshold_mgdl"]
    H = cfg["horizons_minutes"]
    s, grid, _ = load_series(pid, synthetic)
    lab = build_labels(grid, T, H, cfg, cfg["grid_minutes"])
    onset = np.zeros(len(grid), dtype=bool)
    onset[episode_onsets(grid, T, cfg, cfg["grid_minutes"])] = True
    keep = lab["post_warmup"].to_numpy()
    feats = batch_features(s, s.t[keep])
    out = pd.concat([pd.DataFrame({"pid": pid, "t": s.t[keep], "episode_onset": onset[keep],
                                   "glucose_valid": grid["glucose_valid"].to_numpy()[keep]}),
                     lab.loc[keep].reset_index(drop=True), feats], axis=1)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    pids = list_processed(args.synthetic)
    t0 = time.time()
    with ProcessPoolExecutor() as ex:
        parts = list(ex.map(one, [(p, args.synthetic) for p in pids]))
    df = pd.concat(parts, ignore_index=True)
    bio = bio_table(args.synthetic)
    df["group"] = df["pid"].map(bio["group"])
    df.to_parquet(processed_dir(args.synthetic) / "dataset.parquet", index=False)
    lines = ["# Windows and positives", "", f"Threshold T = {cfg['excursion']['threshold_mgdl']} mg/dL", "",
             "| Horizon | eligible windows | positives | positive % | participants with positives |",
             "|---|---|---|---|---|"]
    for H in cfg["horizons_minutes"]:
        e = df[f"eligible_{H}"]
        y = df.loc[e, f"y_{H}"]
        npp = df.loc[e & (df[f"y_{H}"] == 1), "pid"].nunique()
        lines.append(f"| {H} | {int(e.sum())} | {int(y.sum())} | {y.mean():.2%} | {npp} |")
    lines += ["", f"Episodes after warm-up: {int(df['episode_onset'].sum())}",
              f"Currently-high (not scored) grid points: {int(df['currently_high'].sum())}"]
    rep = path_from_cfg(cfg["reports_dir"])
    rep.mkdir(exist_ok=True)
    (rep / ("windows_synthetic.md" if args.synthetic else "windows.md")).write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"rows={len(df)} in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
