# --- file: skimming_detection/collectors.py
import requests, hashlib, tldextract, re
from bs4 import BeautifulSoup
from typing import Tuple, List, Dict

import logging

def fetch_html(url: str, user_agent: str, timeout: int, max_bytes: int) -> Tuple[str, str]:
    if not url.lower().startswith("https://"):
        logging.error(f"Insecure URL detected: {url}. Only HTTPS URLs are allowed for compliance.")
        raise ValueError(f"Insecure URL detected: {url}. Only HTTPS URLs are allowed.")
    logging.info(f"Fetching HTML for merchant URL: {url}")
    headers = {"User-Agent": user_agent}
    try:
        r = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True, stream=True)
        r.raise_for_status()
        content = r.raw.read(max_bytes, decode_content=True)
        logging.info(f"Successfully fetched content from {url}")
        return content.decode(r.encoding or "utf-8", errors="ignore"), r.url
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        raise

def _abs_url(base: str, maybe_rel: str) -> str:
    if not maybe_rel:
        return ""
    if maybe_rel.startswith("http://") or maybe_rel.startswith("https://"):
        return maybe_rel
    if maybe_rel.startswith("//"):
        return "https:" + maybe_rel
    # Simple resolver
    if maybe_rel.startswith("/"):
        m = re.match(r"^(https?://[^/]+)", base)
        return (m.group(1) if m else base.rstrip("/")) + maybe_rel
    return base.rstrip("/") + "/" + maybe_rel.lstrip("./")

def extract_scripts(html: str, base_url: str) -> List[Dict]:
    soup = BeautifulSoup(html, "lxml")
    scripts = []
    for tag in soup.find_all("script"):
        src = tag.get("src")
        if src:
            url = _abs_url(base_url, src)
            scripts.append({"type":"external", "url": url, "content": None})
        else:
            content = tag.string or tag.text or ""
            scripts.append({"type":"inline", "url": None, "content": content})
    # Detect iframes that host third-party checkout widgets
    iframes = [ _abs_url(base_url, i.get("src")) for i in soup.find_all("iframe") if i.get("src") ]
    return scripts + [{"type":"iframe","url":u,"content":None} for u in iframes]

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def domain_of(url: str) -> str:
    ext = tldextract.extract(url)
    return ".".join([p for p in [ext.domain, ext.suffix] if p])

def is_domain_allowed(domain: str, allowlist: List[str]) -> bool:
    d = domain.lower()
    allow = [a.lower().strip() for a in allowlist if a.strip()]
    return any(d==a or d.endswith("."+a) for a in allow)