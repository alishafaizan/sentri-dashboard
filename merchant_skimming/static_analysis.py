# --- file: skimming_detection/static_analysis.py
import math, re, statistics
from typing import Dict, List, Tuple
from .collectors import extract_scripts, domain_of, sha256_text
from bs4 import BeautifulSoup
import logging

SUSPICIOUS_PATTERNS = {
    "eval_usage": re.compile(r"\beval\s*\("),
    "func_ctor": re.compile(r"new\s+Function\s*\("),
    "fromcharcode_loop": re.compile(r"fromCharCode\s*\(", re.I),
    "btoa_atob": re.compile(r"\b(btoa|atob)\s*\("),
    "document_write": re.compile(r"document\.write\s*\("),
    "keylog_handlers": re.compile(r"on(keypress|keyup|keydown)\s*=", re.I),
    "addEventListener_keys": re.compile(r"addEventListener\s*\(\s*keypress|keyup|keydown['\"]", re.I),
    "form_intercept": re.compile(r"addEventListener\s*\(\s*['\"]submit['\"]", re.I),
    "beacon": re.compile(r"navigator\.sendBeacon\s*\("),
    "img_exfil": re.compile(r"new\s+Image\s*\(\)\s*\.src\s*=", re.I),
    "xhr_fetch": re.compile(r"(XMLHttpRequest|fetch)\s*\(", re.I),
    "local_storage": re.compile(r"localStorage\.(getItem|setItem)", re.I),
    "cc_fields": re.compile(r"(card(number|no)|cvv|cvc|expiry|expdate|pan|track_?1|track_?2)", re.I),
    "packer1": re.compile(r"eval\(function\(p,a,c,k,e,d\)", re.I),
}

SUSPICIOUS_TLDS = (".top", ".xyz", ".tk", ".ga", ".gq", ".ml")

def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    from collections import Counter
    counts = Counter(s)
    total = len(s)
    return -sum((c/total) * math.log2(c/total) for c in counts.values())

def static_features(html: str, base_url: str, allow_domains: List[str], baseline_script_hashes: List[str]) -> Tuple[Dict[str,float], List[str], List[str]]:
    scripts = extract_scripts(html, base_url)
    inline_contents = [s["content"] for s in scripts if s["type"]=="inline"]
    external_urls = [s["url"] for s in scripts if s["type"]=="external"]
    iframe_urls = [s["url"] for s in scripts if s["type"]=="iframe"]

    # Inline metrics
    inline_len = [len(c or "") for c in inline_contents]
    inline_entropy = [_shannon_entropy(c or "") for c in inline_contents]

    # Pattern hits
    hits = {name:0 for name in SUSPICIOUS_PATTERNS}
    explanations = []
    for c in inline_contents:
        for name, rx in SUSPICIOUS_PATTERNS.items():
            if rx.search(c or ""):
                hits[name] += 1
    for name, cnt in hits.items():
        if cnt>0:
            explanations.append(f"{name}:{cnt}")

    # External domains & allowlist drift
    external_domains = [domain_of(u) for u in external_urls if u]
    unknown_domains = [d for d in external_domains if d and d not in ("", None)]
    evidence_domains = []
    allowlist_miss = 0
    for d in unknown_domains:
        if allow_domains and not any(d==a or d.endswith("."+a) for a in [a.strip() for a in allow_domains if a.strip()]):
            allowlist_miss += 1
            evidence_domains.append(d)
    # Suspicious TLDs
    tld_hits = sum(1 for d in unknown_domains if any(d.endswith(t) for t in SUSPICIOUS_TLDS))


    if allowlist_miss > 0:
        logging.warning(f"Allowlist miss detected for domains: {evidence_domains}")
    if tld_hits > 0:
        logging.warning(f"Suspicious TLDs detected: {tld_hits}")


    # Baseline drift (hashes of inline)
    in_hashes = [sha256_text(c or "") for c in inline_contents]
    baseline_miss = 0
    if baseline_script_hashes:
        baseline_set = set([h.strip() for h in baseline_script_hashes if h.strip()])
        baseline_miss = sum(1 for h in in_hashes if h not in baseline_set)

    feats = dict(
        inline_script_count = float(len(inline_contents)),
        inline_mean_len = float(statistics.mean(inline_len) if inline_len else 0.0),
        inline_max_len = float(max(inline_len) if inline_len else 0.0),
        inline_mean_entropy = float(statistics.mean(inline_entropy) if inline_entropy else 0.0),
        pattern_eval = float(hits["eval_usage"]),
        pattern_func_ctor = float(hits["func_ctor"]),
        pattern_fromcharcode = float(hits["fromcharcode_loop"]),
        pattern_packer1 = float(hits["packer1"]),
        pattern_beacon = float(hits["beacon"]),
        pattern_img_exfil = float(hits["img_exfil"]),
        pattern_xhr_fetch = float(hits["xhr_fetch"]),
        pattern_form_intercept = float(hits["form_intercept"]),
        pattern_keylog = float(hits["keylog_handlers"] + hits["addEventListener_keys"]),
        pattern_local_storage = float(hits["local_storage"]),
        pattern_cc_terms = float(hits["cc_fields"]),
        external_script_count = float(len(external_urls)),
        iframe_count = float(len(iframe_urls)),
        allowlist_miss = float(allowlist_miss),
        suspicious_tld_refs = float(tld_hits),
        baseline_hash_miss = float(baseline_miss),
    )
    return feats, explanations, list(sorted(set(evidence_domains)))