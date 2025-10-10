# --- file: skimming_detection/schemas.py
from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass
class Merchant:
    merchant_id: str
    homepage_url: str
    allow_domains: List[str]
    baseline_script_hashes: List[str]
    country: Optional[str] = None

@dataclass
class ScanConfig:
    # user_agent: str = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "\
    #                   "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36"
    timeout_sec: int = 20
    max_html_bytes: int = 2000000
    dynamic_enabled: bool = True
    har_dir: Optional[str] = None
    rum_path: Optional[str] = None

@dataclass
class FeatureVector:
    merchant_id: str
    feats: Dict[str, float]
    evidence_domains: List[str]
    explanations: List[str]