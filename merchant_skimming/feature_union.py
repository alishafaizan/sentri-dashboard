# --- file: skimming_detection/feature_union.py
from typing import Dict, List, Tuple
from .schemas import FeatureVector

def union_features(merchant_id: str,
                   static_feats, static_expl, static_domains,
                   dyn_feats, dyn_expl, dyn_domains,
                   rum_feats, rum_expl, rum_domains) -> FeatureVector:
    feats = {}
    for d in (static_feats or {}, dyn_feats or {}, rum_feats or {}):
        feats.update(d)
    explanations = (static_expl or []) + (dyn_expl or []) + (rum_expl or [])
    domains = list(sorted(set((static_domains or []) + (dyn_domains or []) + (rum_domains or []))))
    return FeatureVector(merchant_id=merchant_id, feats=feats, evidence_domains=domains, explanations=explanations)