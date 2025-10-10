# --- file: skimming_detection/pipeline.py
from typing import List, Tuple
from .schemas import Merchant, FeatureVector, ScanConfig
from .collectors import fetch_html
from .static_analysis import static_features
from .dynamic_analysis import features_from_har, features_from_rum
from .feature_union import union_features
from .model import SkimRiskModel
import logging

def process_merchant(m: Merchant, cfg: ScanConfig, model: SkimRiskModel) -> Tuple[str, int, str, str]:
    # Fetch & analyze statically
    logging.info(f"Processing merchant: {m.merchant_id}")
    try:
        html, final_url = fetch_html(m.homepage_url, cfg.user_agent, cfg.timeout_sec, cfg.max_html_bytes)
    except Exception as e:
        logging.warning(f"Fetch error for merchant {m.merchant_id}: {e}")
        # If fetch fails, emit minimal info with neutral/low risk
        return m.merchant_id, 1, "fetch_error", ""

    s_feats, s_expl, s_domains = static_features(html, final_url, m.allow_domains, m.baseline_script_hashes)

    # Dynamic (optional)
    d_feats, d_expl, d_domains = {}, [], []
    if cfg.dynamic_enabled and cfg.har_dir:
        d_feats, d_expl, d_domains = features_from_har(f"{cfg.har_dir}/{m.merchant_id}.har")
    r_feats, r_expl, r_domains = {}, [], []
    if cfg.dynamic_enabled and cfg.rum_path:
        r_feats, r_expl, r_domains = features_from_rum(cfg.rum_path)

    fv: FeatureVector = union_features(m.merchant_id, s_feats, s_expl, s_domains, d_feats, d_expl, d_domains, r_feats, r_expl, r_domains)

    # Predict
    prob01, expl_model = model.predict_score01(fv.feats)
    risk_0_9 = int(round(9.0 * prob01))
    top_signals = ";".join((fv.explanations + expl_model)[:6])
    ev_domains = ";".join(fv.evidence_domains[:6])
    logging.info(f"Risk score for merchant {m.merchant_id}: {risk_0_9}")
    return m.merchant_id, risk_0_9, top_signals, ev_domains

def run_pipeline(merchants: List[Merchant], cfg: ScanConfig, with_explanations: bool) -> List[Tuple[str,int,str,str]]:
    model = SkimRiskModel()
    rows = []
    for m in merchants:
        mid, score, top, doms = process_merchant(m, cfg, model)
        rows.append((mid, score, top, doms) if with_explanations else (mid, score))
    return rows