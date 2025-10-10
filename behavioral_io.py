# behavioral_io.py
import os, requests, pandas as pd
from datetime import datetime, timedelta

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def fetch_behavioral(hours=3, limit=200):
    url = f"{SUPABASE_URL}/rest/v1/behavioral_events"
    hdr = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Accept": "application/json",
    }
    params = {
        "select": "*",
        "order": "event_ts.desc",
        "limit": str(limit),
    }
    r = requests.get(url, headers=hdr, params=params, timeout=30)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    if not df.empty:
        df["event_ts"] = pd.to_datetime(df["event_ts"], utc=True)
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        df = df[df["event_ts"] >= pd.Timestamp(cutoff, tz="UTC")]
    return df