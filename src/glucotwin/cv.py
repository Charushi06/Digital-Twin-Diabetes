"""Participant-grouped cross-validation (PRD section 9.2)."""

from __future__ import annotations

import numpy as np
from sklearn.model_selection import StratifiedKFold, train_test_split


def participant_folds(pids: list[str], groups: list[str], n_splits: int, seed: int
                      ) -> list[tuple[list[str], list[str]]]:
    """Stratified group K-fold at participant level (each participant is its own group).

    Equivalent to StratifiedGroupKFold when every group is one participant; done at the
    participant table level so that no row-level split is ever possible.
    """
    pids_a = np.array(pids)
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)
    out = []
    for tr, te in skf.split(pids_a, np.array(groups)):
        out.append((pids_a[tr].tolist(), pids_a[te].tolist()))
    return out


def calibration_split(train_pids: list[str], groups: dict[str, str], frac: float, seed: int
                      ) -> tuple[list[str], list[str]]:
    """Hold out `frac` of training *participants* (stratified) as the calibration set."""
    strat = [groups[p] for p in train_pids]
    try:
        fit, cal = train_test_split(train_pids, test_size=frac, random_state=seed, stratify=strat)
    except ValueError:
        fit, cal = train_test_split(train_pids, test_size=frac, random_state=seed)
    return list(fit), list(cal)
