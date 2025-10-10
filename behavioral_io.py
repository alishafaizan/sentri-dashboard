# behavioral_io.py
import os, requests, pandas as pd
from datetime import datetime, timedelta
import streamlit as st
#SUPABASE_URL = os.environ.get("SUPABASE_URL")
#SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Supabase config
supabase_url = st.secrets["supabase"]["url"]
supabase_key = st.secrets["supabase"]["key"]

def fetch_behavioral(hours=24, limit=200):
    url = f"{supabase_url}/rest/v1/behavioral_events"
    hdr = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
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