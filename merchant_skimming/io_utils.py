# --- file: skimming_detection/io_utils.py
import csv, json, os, yaml
import xml.etree.ElementTree as ET
from typing import List, Tuple
from .schemas import Merchant, ScanConfig


def read_catalog_xml(path: str) -> List[Merchant]:
    merchants = []
    tree = ET.parse(path)
    root = tree.getroot()
    # Example: assuming ISO 20022 structure with <Merchant> elements
    for m_elem in root.findall('.//Merchant'):
        merchants.append(Merchant(
            merchant_id=m_elem.findtext('MerchantId'),
            homepage_url=m_elem.findtext('HomepageUrl'),
            allow_domains=m_elem.findtext('AllowDomains', '').split(';'),
            baseline_script_hashes=m_elem.findtext('BaselineScriptHashes', '').split('\n'),
            country=m_elem.findtext('Country')
        ))
    return merchants


def read_catalog(path: str) -> List[Merchant]:
    merchants = []

    if path.lower().endswith('.xml'):
        return read_catalog_xml(path)

    elif path.lower().endswith(".jsonl"):
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                o = json.loads(line)
                merchants.append(Merchant(
                    merchant_id=o["merchant_id"],
                    homepage_url=o["homepage_url"],
                    allow_domains=(o.get("allow_domains","") or "").split(";") if o.get("allow_domains") else [],
                    baseline_script_hashes=(o.get("baseline_script_hashes","") or "").split("|") if o.get("baseline_script_hashes") else [],
                    country=o.get("country")
                ))
    else:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                merchants.append(Merchant(
                    merchant_id=r["merchant_id"],
                    homepage_url=r["homepage_url"],
                    allow_domains=(r.get("allow_domains","") or "").split(";") if r.get("allow_domains") else [],
                    baseline_script_hashes=(r.get("baseline_script_hashes","") or "").split("|") if r.get("baseline_script_hashes") else [],
                    country=r.get("country")
                ))
    return merchants

def read_config(path: str) -> ScanConfig:
    if not path or not os.path.exists(path):
        return ScanConfig()
    with open(path, "r", encoding="utf-8") as f:
        y = yaml.safe_load(f) or {}
    return ScanConfig(
        user_agent=y.get("user_agent", ScanConfig.user_agent),
        timeout_sec=y.get("timeout_sec", ScanConfig.timeout_sec),
        max_html_bytes=y.get("max_html_bytes", ScanConfig.max_html_bytes),
        dynamic_enabled=y.get("feature_flags",{}).get("dynamic_enabled", True),
        har_dir=y.get("dynamic",{}).get("har_dir"),
        rum_path=y.get("dynamic",{}).get("rum_path"),
    )

import xml.etree.ElementTree as ET

def safe_join_domains(domains):
    if isinstance(domains, str):
        return domains
    elif isinstance(domains, list):
        return ';'.join(map(str, domains))
    else:
        return str(domains)


def write_catalog_xml(out_path: str, merchants: List[Merchant]):
    root = ET.Element('Merchants')
    for merchant in merchants:
        m_elem = ET.SubElement(root, 'Merchant')
        ET.SubElement(m_elem, 'MerchantId').text = str(merchant.merchant_id)
        ET.SubElement(m_elem, 'HomepageUrl').text = str(merchant.homepage_url)
        ET.SubElement(m_elem, 'AllowDomains').text = safe_join_domains(merchant.allow_domains)
        ET.SubElement(m_elem, 'BaselineScriptHashes').text = '\n'.join(map(str, merchant.baseline_script_hashes))
        ET.SubElement(m_elem, 'Country').text = str(merchant.country) if merchant.country else ''
    tree = ET.ElementTree(root)
    tree.write(out_path, encoding='utf-8', xml_declaration=True)

def write_lookup(out_path: str, rows):
    # rows: list[(merchant_id, risk_score, top_signals?, evidence_domains?)]
    
    if out_path.lower().endswith('.xml'):
        # Convert rows to Merchant objects if needed
        write_catalog_xml(out_path, [Merchant(*r) for r in rows])
    else:
        headers = ["merchant_id", "risk_score"] + \
                (["top_signals", "evidence_domains"] if len(rows[0])==4 else [])
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            for r in rows:
                w.writerow(r)