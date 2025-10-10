# --- file: skimming_detection/dynamic_analysis.py
import json, os, re, tldextract
from typing import Dict, List, Tuple
import logging

EXFIL_HINTS = re.compile(r"/(collect|capture|grab|send|exfil|leak|log|track)/?", re.I)
CARD_HINTS = re.compile(r"(cc|card|pan|cvv|cvc|expiry|exp|billing)", re.I)
BEACON_TYPES = ("application/json", "text/plain")

def _domain(u: str) -> str:
    ext = tldextract.extract(u)
    return ".".join([p for p in [ext.domain, ext.suffix] if p])

def features_from_har(har_path: str) -> Tuple[Dict[str,float], List[str], List[str]]:
    """
    Extract dynamic egress indicators from a HAR file.
    """
    if not os.path.exists(har_path):
        logging.warning(f"HAR file not found: {har_path}")
        return {}, [], []
    try:
        with open(har_path, "r", encoding="utf-8") as f:
            har = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load HAR file {har_path}: {e}")
        return {}, [], []
    entries = har.get("log",{}).get("entries",[])
    suspicious_domains, explanations = [], []
    exfil_posts, beacon_posts, json_posts, cross_domain_posts = 0,0,0,0
    hosts = set()
    first_host = None

    for e in entries:
        req = e.get("request",{})
        res = e.get("response",{})
        url = req.get("url","")
        method = req.get("method","GET")
        host = _domain(url)
        if not first_host:
            first_host = host
        if host != first_host:
            cross_domain_posts += 1 if method=="POST" else 0
        hosts.add(host)
        # Heuristics
        if method=="POST" and (EXFIL_HINTS.search(url) or any(h.get("name","").lower()=="referer" and "checkout" in h.get("value","").lower() for h in req.get("headers",[]))):
            exfil_posts += 1
            suspicious_domains.append(host)
        if method in ("POST","PUT") and any(h.get("name","").lower()=="content-type" and any(t in h.get("value","").lower() for t in BEACON_TYPES) for h in req.get("headers",[])):
            json_posts += 1
        if any(h.get("name","").lower()=="x-beacon" for h in req.get("headers",[])):
            beacon_posts += 1

    if exfil_posts > 0:
        logging.warning(f"Exfiltration detected in HAR for {har_path}: {exfil_posts} posts")
    if cross_domain_posts > 0:
        logging.info(f"Cross-domain POSTs detected in HAR for {har_path}: {cross_domain_posts}")

    feats = dict(
        har_total_entries=float(len(entries)),
        har_unique_hosts=float(len(hosts)),
        har_cross_domain_posts=float(cross_domain_posts),
        har_exfil_posts=float(exfil_posts),
        har_beacon_posts=float(beacon_posts),
        har_json_posts=float(json_posts),
    )
    explanations = [f"har_exfil_posts:{exfil_posts}", f"har_cross_domain_posts:{cross_domain_posts}"] if (exfil_posts or cross_domain_posts) else []
    return feats, explanations, list(sorted(set(suspicious_domains)))

def features_from_rum(rum_path: str) -> Tuple[Dict[str,float], List[str], List[str]]:
    if not rum_path or not os.path.exists(rum_path):
        logging.warning(f"RUM file not found: {rum_path}")
        return {}, [], []
    exfil, cross_posts, uniq_hosts = 0,0,set()
    susp = []
    with open(rum_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                e = json.loads(line)
            except Exception:
                continue
            host = _domain(e.get("url","") or e.get("request_host",""))
            if host: uniq_hosts.add(host)
            if e.get("method")=="POST" and (EXFIL_HINTS.search(e.get("url","")) or CARD_HINTS.search(e.get("url",""))):
                exfil += 1
                susp.append(host)
                logging.warning(f"Exfiltration POST detected to {host} in RUM file {rum_path}")
            if e.get("direction")=="outbound" and e.get("method")=="POST":
                cross_posts += 1
    
    if exfil > 0:
        logging.warning(f"Total exfiltration POSTs in RUM for {rum_path}: {exfil}")

    feats = dict(
        rum_unique_hosts=float(len(uniq_hosts)),
        rum_exfil_posts=float(exfil),
        rum_cross_domain_posts=float(cross_posts),
    )
    expl = [f"rum_exfil_posts:{exfil}"] if exfil else []
    return feats, expl, list(sorted(set(susp)))