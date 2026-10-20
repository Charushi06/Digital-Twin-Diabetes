"""Probability calibration (isotonic if >= 300 positives, else Platt)."""

from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


class Calibrator:
    def __init__(self) -> None:
        self.kind = "identity"
        self._m = None

    def fit(self, scores: np.ndarray, y: np.ndarray) -> Calibrator:
        scores = np.asarray(scores, float)
        y = np.asarray(y, int)
        if y.sum() == 0 or y.sum() == len(y):
            self.kind = "identity"
            return self
        if y.sum() >= 300:
            self.kind = "isotonic"
            self._m = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(scores, y)
        else:
            self.kind = "platt"
            self._m = LogisticRegression(C=1e6).fit(_logit(scores).reshape(-1, 1), y)
        return self

    def transform(self, scores: np.ndarray) -> np.ndarray:
        scores = np.asarray(scores, float)
        if self.kind == "isotonic":
            return self._m.predict(scores)
        if self.kind == "platt":
            return self._m.predict_proba(_logit(scores).reshape(-1, 1))[:, 1]
        return scores


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-6, 1 - 1e-6)
    return np.log(p / (1 - p))
