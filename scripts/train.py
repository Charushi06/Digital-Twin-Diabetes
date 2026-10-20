"""M3 + M7: grouped CV training, calibration, alerts, metrics, ablations, figures.

Usage: python scripts/train.py [--skip-ablation] [--boot N]
Writes models/, reports/metrics.md, reports/ablation.md, reports/figures/*.png,
data/processed/real/oof.parquet
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from sklearn.calibration import calibration_curve  # noqa: E402
from sklearn.metrics import precision_recall_curve  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from glucotwin import MODEL_VERSION, load_config, path_from_cfg  # noqa: E402
from glucotwin.alerts import alerts_from_probs, choose_theta, event_metrics  # noqa: E402
from glucotwin.calibrate import Calibrator  # noqa: E402
from glucotwin.cv import calibration_split, participant_folds  # noqa: E402
from glucotwin.data import bio_table, processed_dir  # noqa: E402
from glucotwin.features import ABLATIONS, ALL_FEATURES  # noqa: E402
from glucotwin.metrics import (brier, ece, fmt_ci, participant_bootstrap, per_participant_auc,  # noqa: E402
                               safe_ap, safe_auc)
from glucotwin.models import FoldModel, b0a_score, b0b_score, make_lgbm, make_lr  # noqa: E402

MEAL_MACROS = ["last_meal_carbs", "last_meal_protein", "last_meal_fat", "last_meal_fiber"]


class Ctx:
    def __init__(self, df: pd.DataFrame, cfg: dict):
        self.df, self.cfg = df, cfg
        self.pid = df["pid"].to_numpy()
        self.pids = sorted(df["pid"].unique())
        bio = bio_table()
        self.gmap = bio["group"].to_dict()
        self.groups = [self.gmap[p] for p in self.pids]
        self.rows = {p: np.where(self.pid == p)[0] for p in self.pids}
        self.days = {p: df.loc[self.rows[p], "glucose_valid"].sum() * cfg["grid_minutes"] / 1440 for p in self.pids}
        ac = cfg["alerts"]
        self.consec = ac["consecutive_points"]
        self.cool = int(ac["cooldown_minutes"] / cfg["grid_minutes"])
        self.budgets = ac["report_budgets"]

    def per_pid(self, prob: np.ndarray, elig: np.ndarray, pids) -> dict[str, np.ndarray]:
        return {p: np.where(elig[self.rows[p]], prob[self.rows[p]], np.nan) for p in pids}


def meal_ranges(df: pd.DataFrame, pids: list[str]) -> dict[str, tuple[float, float]]:
    m = df[df["pid"].isin(pids) & (df["min_since_last_meal"] < 5)]
    return {c: (float(np.nanpercentile(m[c], 5)), float(np.nanpercentile(m[c], 95))) for c in MEAL_MACROS
            if m[c].notna().any()}


def train_horizon(ctx: Ctx, H: int, models_dir: Path) -> dict[str, dict]:
    cfg, df = ctx.cfg, ctx.df
    seeds = cfg["cv"]["seeds"]
    el = df[f"eligible_{H}"].to_numpy(bool)
    y = df[f"y_{H}"].to_numpy(int)
    n = len(df)
    oof = {k: np.full((len(seeds), n), np.nan) for k in ("B1", "B2")}
    th = {k: np.full((len(seeds), n, len(ctx.budgets)), np.nan) for k in ("B1", "B2", "B0b")}
    p2f: dict[str, dict[str, int]] = {}
    b0b = b0b_score(df)
    for si, seed in enumerate(seeds):
        folds = participant_folds(ctx.pids, ctx.groups, cfg["cv"]["n_splits"], seed)
        p2f[str(seed)] = {}
        for k, (tr, te) in enumerate(folds):
            assert not set(tr) & set(te)
            for p in te:
                p2f[str(seed)][p] = k
            fit_p, cal_p = calibration_split(tr, ctx.gmap, cfg["cv"]["calibration_participant_fraction"], seed)
            fit_m = np.isin(ctx.pid, fit_p) & el
            cal_m = np.isin(ctx.pid, cal_p)
            te_m = np.isin(ctx.pid, te)
            tr_probs = ctx.per_pid(b0b, el, tr)
            for bi, b in enumerate(ctx.budgets):
                th["B0b"][si, te_m, bi] = choose_theta(tr_probs, {p: ctx.days[p] for p in tr}, b, ctx.consec, ctx.cool)
            for kind in ("B1", "B2"):
                model = make_lr(seed) if kind == "B1" else make_lgbm(ALL_FEATURES, cfg["monotone_features"], seed)
                model.fit(df.loc[fit_m, ALL_FEATURES], y[fit_m])
                raw_cal = model.predict_proba(df.loc[cal_m, ALL_FEATURES])[:, 1]
                calib = Calibrator().fit(raw_cal[el[cal_m]], y[cal_m & el])
                p_cal = np.full(n, np.nan)
                p_cal[cal_m] = calib.transform(raw_cal)
                cal_probs = ctx.per_pid(p_cal, el, cal_p)
                thetas = {b: choose_theta(cal_probs, {p: ctx.days[p] for p in cal_p}, b, ctx.consec, ctx.cool)
                          for b in ctx.budgets}
                p_te = calib.transform(model.predict_proba(df.loc[te_m, ALL_FEATURES])[:, 1])
                oof[kind][si, te_m] = p_te
                for bi, b in enumerate(ctx.budgets):
                    th[kind][si, te_m, bi] = thetas[b]
                if kind == "B2":
                    fm = FoldModel(kind, H, seed, k, list(ALL_FEATURES), model, calib, list(fit_p), list(cal_p),
                                   list(te), thetas, meal_ranges(df, list(fit_p)), MODEL_VERSION)
                    joblib.dump(fm, models_dir / f"h{H}" / f"B2_s{seed}_f{k}.pkl")
            print(f"  H={H} seed={seed} fold={k} done", flush=True)
    (models_dir / "participant_to_fold.json").write_text(json.dumps(p2f, indent=1))
    return {
        "B0a": {"score": b0a_score(df, H), "fixed": float(cfg["excursion"]["threshold_mgdl"])},
        "B0b": {"score": b0b, "theta": np.nanmean(th["B0b"], axis=0)},
        "B1": {"score": np.nanmean(oof["B1"], axis=0), "theta": np.nanmean(th["B1"], axis=0), "prob": True},
        "B2": {"score": np.nanmean(oof["B2"], axis=0), "theta": np.nanmean(th["B2"], axis=0), "prob": True,
               "spread": np.nanmax(oof["B2"], axis=0) - np.nanmin(oof["B2"], axis=0)},
    }


def event_eval(ctx: Ctx, H: int, score: np.ndarray, theta_rows: np.ndarray | float, el: np.ndarray):
    steps = int(H / ctx.cfg["grid_minutes"])
    det = tot = n_al = 0
    leads: list[float] = []
    for p in ctx.pids:
        r = ctx.rows[p]
        prob = np.where(el[r], score[r], np.nan)
        thv = float(theta_rows) if np.isscalar(theta_rows) else float(np.nanmean(theta_rows[r]))
        al = alerts_from_probs(prob, thv, ctx.consec, ctx.cool)
        ons = np.where(ctx.df["episode_onset"].to_numpy()[r])[0]
        d, t_, lt = event_metrics(al, ons, steps, ctx.cfg["grid_minutes"])
        det, tot, n_al = det + d, tot + t_, n_al + int(al.sum())
        leads += lt
    days = sum(ctx.days.values())
    return {"sens": det / tot if tot else float("nan"), "events": tot,
            "lead": float(np.median(leads)) if leads else float("nan"), "apd": n_al / days}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-ablation", action="store_true")
    ap.add_argument("--boot", type=int, default=None)
    args = ap.parse_args()
    cfg = load_config()
    t_start = time.time()
    df = pd.read_parquet(processed_dir() / "dataset.parquet").sort_values(["pid", "t"]).reset_index(drop=True)
    ctx = Ctx(df, cfg)
    models_dir = path_from_cfg(cfg["models_dir"])
    rep = path_from_cfg(cfg["reports_dir"])
    figs = rep / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    nb = args.boot or cfg["cv"]["bootstrap_resamples"]
    seed = cfg["seed"]
    bio = bio_table()
    T = cfg["excursion"]["threshold_mgdl"]

    lines = ["# Metrics (held-out participants, grouped 5-fold CV x 3 seeds)", "",
             f"Threshold T = {T} mg/dL. 95% CIs from a participant-level bootstrap ({nb} resamples).",
             f"Participants: {len(ctx.pids)}. Patient-days scored: {sum(ctx.days.values()):.1f}.",
             "Targets in the PRD are guidelines, not claims.", ""]
    oof_out = df[["pid", "t"]].copy()
    fig_cal, ax_cal = plt.subplots(figsize=(5, 5))
    for H in cfg["horizons_minutes"]:
        (models_dir / f"h{H}").mkdir(parents=True, exist_ok=True)
        print(f"Training H={H}", flush=True)
        res = train_horizon(ctx, H, models_dir)
        el = df[f"eligible_{H}"].to_numpy(bool)
        y = df[f"y_{H}"].to_numpy(int)
        pid_el = ctx.pid[el]
        lines += [f"## Horizon {H} min", "",
                  f"Eligible windows: {int(el.sum())}; positive: {int(y[el].sum())} ({y[el].mean():.2%}).", "",
                  "| Model | AUROC | PR-AUC | Brier | ECE* | per-participant AUROC median (range) |"
                  " event sensitivity @2/day | median lead (min) | alerts / patient-day |",
                  "|---|---|---|---|---|---|---|---|---|"]
        fig_pr, ax_pr = plt.subplots(figsize=(5, 5))
        for name, r in res.items():
            s = r["score"]
            oof_out[f"{name}_h{H}"] = s
            auc = participant_bootstrap(y[el], s[el], pid_el, safe_auc, nb, seed)
            apr = participant_bootstrap(y[el], s[el], pid_el, safe_ap, nb, seed)
            pp = np.array([v for v in per_participant_auc(y[el], s[el], pid_el).values() if not np.isnan(v)])
            if r.get("prob"):
                br, ec = f"{brier(y[el], s[el]):.3f}", f"{ece(y[el], s[el]):.3f}"
            else:
                br = ec = "n/a"
            ev = event_eval(ctx, H, s, r.get("theta", r.get("fixed")), el)
            lines.append(f"| {name} | {fmt_ci(auc)} | {fmt_ci(apr)} | {br} | {ec} | {np.median(pp):.3f} "
                         f"({pp.min():.3f} to {pp.max():.3f}) | {ev['sens']:.1%} of {ev['events']} | "
                         f"{ev['lead']:.0f} | {ev['apd']:.2f} |")
            pr, rc, _ = precision_recall_curve(y[el], s[el])
            ax_pr.plot(rc, pr, label=f"{name} (AP {apr[0]:.2f})")
            if name == "B2":
                oof_out[f"B2_h{H}_spread"] = r["spread"]
                fp, mp = calibration_curve(y[el], np.clip(s[el], 0, 1), n_bins=10, strategy="quantile")
                ax_cal.plot(mp, fp, marker="o", label=f"B2 {H} min")
                b2 = r
        lines += ["", "*ECE bins are sparse at high probabilities; read with caution.", ""]
        # alert budgets for B2
        lines += ["Alert budget sweep (B2):", "", "| budget/day | event sensitivity | median lead | alerts/patient-day |",
                  "|---|---|---|---|"]
        for bi, b in enumerate(ctx.budgets):
            ev = event_eval(ctx, H, b2["score"], b2["theta"][:, bi], el)
            lines.append(f"| {b} | {ev['sens']:.1%} | {ev['lead']:.0f} | {ev['apd']:.2f} |")
        # subgroups for B2
        lines += ["", "Subgroups (B2):", "", "| subgroup | participants | AUROC | PR-AUC |", "|---|---|---|---|"]
        sub = {f"group={g}": df["pid"].map(bio["group"]) == g for g in ["healthy", "prediabetes", "type2"]}
        sub["sex=female"] = df["pid"].map(bio["sex_male"]) == 0
        sub["sex=male"] = df["pid"].map(bio["sex_male"]) == 1
        if (bio["age"] >= 65).sum() >= 5:
            sub["age>=65"] = df["pid"].map(bio["age"]) >= 65
        for nm, m in sub.items():
            mm = m.to_numpy() & el
            a = participant_bootstrap(y[mm], b2["score"][mm], ctx.pid[mm], safe_auc, min(nb, 200), seed)
            pa = participant_bootstrap(y[mm], b2["score"][mm], ctx.pid[mm], safe_ap, min(nb, 200), seed)
            lines.append(f"| {nm} | {len(np.unique(ctx.pid[mm]))} | {fmt_ci(a)} | {fmt_ci(pa)} |")
        if (bio["age"] >= 65).sum() < 5:
            lines.append(f"| age>=65 | {(bio['age'] >= 65).sum()} | too few participants to report | |")
        lines.append("")
        ax_pr.set_xlabel("Recall")
        ax_pr.set_ylabel("Precision")
        ax_pr.set_title(f"Precision-recall, {H} min (held-out)")
        ax_pr.legend()
        fig_pr.tight_layout()
        fig_pr.savefig(figs / f"pr_{H}.png", dpi=110)
        plt.close(fig_pr)
    ax_cal.plot([0, 1], [0, 1], "k--", lw=1)
    ax_cal.set_xlabel("Predicted probability")
    ax_cal.set_ylabel("Observed frequency")
    ax_cal.set_title("Reliability (B2, held-out)")
    ax_cal.legend()
    fig_cal.tight_layout()
    fig_cal.savefig(figs / "calibration.png", dpi=110)
    plt.close(fig_cal)
    oof_out.to_parquet(processed_dir() / "oof.parquet", index=False)
    lines += ["Figures: `figures/pr_*.png`, `figures/calibration.png`.",
              f"Shipped model: B2 (LightGBM, monotone on {cfg['monotone_features']}). M1 fusion network not built (P1)."]
    (rep / "metrics.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"metrics written ({time.time() - t_start:.0f}s)", flush=True)

    if not args.skip_ablation:
        run_ablation(ctx, rep)
    print(f"done in {time.time() - t_start:.0f}s")
    return 0


def run_ablation(ctx: Ctx, rep: Path) -> None:
    cfg, df = ctx.cfg, ctx.df
    seed = cfg["seed"]
    nb = cfg["cv"]["ablation_bootstrap_resamples"]
    folds = participant_folds(ctx.pids, ctx.groups, cfg["cv"]["n_splits"], seed)
    lines = ["# Ablation: what each stream adds (B2 LightGBM, seed 42, grouped 5-fold)", "",
             f"Window-level PR-AUC and AUROC on held-out participants; participant bootstrap ({nb}) 95% CIs.",
             "If a stream adds nothing, that is reported as a finding.", ""]
    for H in cfg["horizons_minutes"]:
        el = df[f"eligible_{H}"].to_numpy(bool)
        y = df[f"y_{H}"].to_numpy(int)
        lines += [f"## Horizon {H} min", "", "| Variant | n features | PR-AUC | AUROC |", "|---|---|---|---|"]
        for name, feats in ABLATIONS.items():
            s = np.full(len(df), np.nan)
            for tr, te in folds:
                m = np.isin(ctx.pid, tr) & el
                mdl = make_lgbm(feats, cfg["monotone_features"], seed).fit(df.loc[m, feats], y[m])
                te_m = np.isin(ctx.pid, te)
                s[te_m] = mdl.predict_proba(df.loc[te_m, feats])[:, 1]
            pa = participant_bootstrap(y[el], s[el], ctx.pid[el], safe_ap, nb, seed)
            au = participant_bootstrap(y[el], s[el], ctx.pid[el], safe_auc, nb, seed)
            lines.append(f"| {name} | {len(feats)} | {fmt_ci(pa)} | {fmt_ci(au)} |")
            print(f"  ablation H={H} {name}: AP={pa[0]:.3f}", flush=True)
        lines.append("")
    (rep / "ablation.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
