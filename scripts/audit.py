"""M0: preprocess every participant, audit the real data, choose and freeze threshold T.

Usage: python scripts/audit.py [--synthetic]
Writes: data/processed/*.parquet, reports/data_audit.md, config.yaml (threshold_mgdl)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from glucotwin import ROOT, load_config, path_from_cfg  # noqa: E402
from glucotwin.io import list_participants, load_bio, load_raw  # noqa: E402
from glucotwin.labels import build_labels, episode_onsets  # noqa: E402
from glucotwin.preprocess import preprocess  # noqa: E402


def cadence(ts: pd.Series, vals: pd.Series) -> str:
    """Median minutes between *changes* in a sensor value (reveals filled/interpolated rows)."""
    v = vals.dropna()
    if len(v) < 3:
        return "n/a"
    t = ts.loc[v.index]
    nn = t.diff().dt.total_seconds().div(60).median()
    ch = v.diff().fillna(1) != 0
    ct = t[ch].diff().dt.total_seconds().div(60).median()
    return f"rows every {nn:.0f} min; value changes every {ct:.0f} min (median)"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--synthetic", action="store_true")
    args = ap.parse_args()
    cfg = load_config()
    gm = cfg["grid_minutes"]
    proc = path_from_cfg(cfg["data"]["processed_dir"]) / ("synthetic" if args.synthetic else "real")
    proc.mkdir(parents=True, exist_ok=True)
    parts = list_participants(args.synthetic)
    bio = load_bio(args.synthetic)
    lines = ["# Data audit (M0)", "", f"Source: {'SYNTHETIC' if args.synthetic else 'CGMacros 1.0.0'}", ""]
    rows, col_sets, notes = [], {}, []
    grids = {}
    for pid, path in parts.items():
        raw = load_raw(path)
        col_sets[pid] = tuple(pd.read_csv(path, nrows=0).columns)
        grid, meals = preprocess(raw, cfg["glucose_source"], gm)
        grid.to_parquet(proc / f"{pid}_grid.parquet", index=False)
        meals.to_parquet(proc / f"{pid}_meals.parquet", index=False)
        grids[pid] = grid
        dex_frac = raw["dexcom"].notna().mean() if "dexcom" in raw else 0.0
        rows.append({
            "pid": pid, "group": bio.loc[pid, "group"] if pid in bio.index else "missing-bio",
            "rows": len(raw), "days": (raw["ts"].max() - raw["ts"].min()).total_seconds() / 86400,
            "dexcom_nonnull": round(dex_frac, 3),
            "grid_valid": round(grid["glucose_valid"].mean(), 3),
            "interp": int((grid["glucose_quality"] == "interpolated").sum()),
            "oor": int((grid["glucose_quality"] == "out_of_range").sum()),
            "hr_valid": round(grid["hr_valid"].mean(), 3),
            "meals": len(meals),
            "meal_types": ",".join(sorted(meals["meal_type"].unique())),
            "dexcom_cadence": cadence(raw["ts"], raw["dexcom"]) if "dexcom" in raw else "absent",
            "libre_cadence": cadence(raw["ts"], raw["libre"]) if "libre" in raw else "absent",
        })
        if dex_frac == 0:
            notes.append(f"{pid}: no Dexcom values; preprocess fell back to Libre.")
    df = pd.DataFrame(rows)
    missing_bio = [p for p in parts if p not in bio.index]
    no_file = [p for p in bio.index if p not in parts]

    lines += ["## Files", f"- Participant files found: **{len(parts)}** (PRD says 45)",
              f"- bio.csv rows: {len(bio)}", f"- Participants without bio row: {missing_bio or 'none'}",
              f"- bio rows without file: {no_file or 'none'}", ""]
    uniq = {}
    for p, c in col_sets.items():
        uniq.setdefault(c, []).append(p)
    lines += ["## Column sets (raw headers)"]
    for c, ps in uniq.items():
        lines.append(f"- {len(ps)} files: `{list(c)}`")
    lines += ["", "## Counts per diagnosis group (derived from HbA1c)",
              df.groupby("group").size().to_frame("participants").to_markdown(), ""]
    lines += ["## Sensor cadence (first 5 participants)"]
    for r in rows[:5]:
        lines.append(f"- {r['pid']}: Dexcom {r['dexcom_cadence']}; Libre {r['libre_cadence']}")
    lines += ["", "## Per-participant summary", df.drop(columns=["dexcom_cadence", "libre_cadence"])
              .to_markdown(index=False), ""]

    # Threshold selection rule (PRD section 6)
    exc = cfg["excursion"]
    lines += ["## Threshold selection rule", "",
              f"Rule: first T in {exc['candidate_thresholds']} with >= {exc['rule_min_participants']} "
              f"participants having >= {exc['rule_min_episodes']} post-warm-up episodes AND >= "
              f"{exc['rule_min_positive_fraction']:.0%} positive eligible windows (120 min horizon).", "",
              "| T | participants with >=5 episodes | total episodes | eligible windows | positive % | passes |",
              "|---|---|---|---|---|---|"]
    chosen = None
    H = cfg["primary_horizon_minutes"]
    for T in exc["candidate_thresholds"]:
        n_ok, tot_ep, n_el, n_pos = 0, 0, 0, 0
        for pid, grid in grids.items():
            ons = episode_onsets(grid, T, cfg, gm)
            tot_ep += len(ons)
            n_ok += int(len(ons) >= exc["rule_min_episodes"])
            lab = build_labels(grid, T, [H], cfg, gm)
            n_el += int(lab[f"eligible_{H}"].sum())
            n_pos += int(lab[f"y_{H}"].sum())
        frac = n_pos / n_el if n_el else 0
        ok = n_ok >= exc["rule_min_participants"] and frac >= exc["rule_min_positive_fraction"]
        lines.append(f"| {T} | {n_ok} | {tot_ep} | {n_el} | {frac:.2%} | {'yes' if ok else 'no'} |")
        if ok and chosen is None:
            chosen = T
    if chosen is None:
        chosen = exc["candidate_thresholds"][-1]
        notes.append(f"No threshold passed the rule; using {chosen} (state in README).")
    lines += ["", f"**Chosen T = {chosen} mg/dL** (frozen in config.yaml).", ""]
    if notes:
        lines += ["## Notes"] + [f"- {n}" for n in notes]

    reports = path_from_cfg(cfg["reports_dir"])
    reports.mkdir(exist_ok=True)
    name = "data_audit_synthetic.md" if args.synthetic else "data_audit.md"
    (reports / name).write_text("\n".join(lines), encoding="utf-8")
    if not args.synthetic:
        cp = ROOT / "config.yaml"
        txt = cp.read_text(encoding="utf-8")
        txt = re.sub(r"threshold_mgdl: \S+", f"threshold_mgdl: {chosen}", txt, count=1)
        cp.write_text(txt, encoding="utf-8")
    print("\n".join(lines[:40]))
    print(f"chosen T={chosen}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
