# --- file: skimming_detection/model.py
import os, math, json
from typing import List, Tuple
import numpy as np

XGB_AVAILABLE = False
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except Exception:
    XGB_AVAILABLE = False

FEATURE_ORDER = []  # will be inferred from first vector if model absent

def _vectorize(feats: dict, feature_order: List[str]) -> np.ndarray:
    return np.array([feats.get(k, 0.0) for k in feature_order], dtype=np.float32)

def _rule_score(feats: dict) -> Tuple[float, List[str]]:
    """
    Deterministic risk score in [0,1] with simple weighting.
    """
    signals = []
    w = {
        "pattern_form_intercept": 0.20,
        "pattern_keylog":         0.20,
        "pattern_xhr_fetch":      0.10,
        "pattern_img_exfil":      0.10,
        "pattern_beacon":         0.05,
        "allowlist_miss":         0.10,
        "suspicious_tld_refs":    0.05,
        "baseline_hash_miss":     0.05,
        "inline_mean_entropy":    0.05,
        "har_exfil_posts":        0.10,
        "har_cross_domain_posts": 0.05,
        "rum_exfil_posts":        0.10,
    }
    # Sum weighted indicators
    score = 0.0
    for k, wt in w.items():
        val = feats.get(k, 0.0)
        # squash non-binary metrics
        contrib = wt * (1.0 - math.exp(-val))
        if val > 0:
            signals.append(f"{k}={val:.2f} (+{contrib:.2f})")
        score += contrib
    # Clamp to [0,1]
    return min(1.0, score), signals

class SkimRiskModel:
    def __init__(self, model_path: str = "models/skimming_xgb.json"):
        self.model_path = model_path
        self.booster = None
        self.feature_order: List[str] = []

        if XGB_AVAILABLE and os.path.exists(model_path):
            self.booster = xgb.Booster()
            self.booster.load_model(model_path)
            self.feature_order = self.booster.feature_names
        else:
            self.booster = None

    def predict_score01(self, feats: dict) -> Tuple[float, List[str]]:
        if self.booster:
            train_features = best_model.get_booster().feature_names
            X_test_aligned = X_test.reindex(columns=train_features, fill_value=0)
            order = self.feature_order or sorted(feats.keys())
            vec = _vectorize(feats, order).reshape(1, -1)
            d = xgb.DMatrix(vec, feature_names=order)
            prob = float(self.booster.predict(d)[0])
            return max(0.0, min(1.0, prob)), ["xgb_prob"]
        else:
            return _rule_score(feats)