This repo contains the transaction risk dashboard (Python). The tree includes Streamlit-style app files (e.g., home.py, main.py, requirements.txt), utilities for ingesting behavioral scores, and the trained XGBoost model (xgboost_model_sentri.json).

Overview
Sentri Dashboard fuses:

Behavioral Risk (scores from the iOS app / API),

Transaction features (entered in the UI or uploaded),

Threat/merchant intelligence (files/APIs),
to produce an overall risk score for beneficiary add / P2P transactions and visualize alerts.

What’s inside
main.py, home.py – app entry/views (Streamlit-style layout)

requirements.txt – Python deps (Streamlit, XGBoost, etc.)

xgboost_model_sentri.json – trained model artifact

behavioral_io.py, utils.py – feature wiring & I/O helpers

Example XML/CSV files (sample data) for demo runs GitHub

Quickstart (local)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# If this is a Streamlit app (recommended structure)
export SUPABASE_URL="https://<project>.supabase.co"
export SUPABASE_ANON_KEY="<anon>"
export BEHAVIORAL_TABLE="behavioral_events"

# run
streamlit run home.py    # or: streamlit run main.py
Config (env)
SUPABASE_URL, SUPABASE_ANON_KEY – to fetch recent behavioral scores

BEHAVIORAL_TABLE – table name (default behavioral_events)

(Optional) API keys for threat intel feeds

Typical Flow
Behavioral scores flow into behavioral_events (Supabase or your REST).

User enters transaction details (UI form or file upload).

App builds the feature vector (see utils.py, behavioral_io.py).

XGBoost (xgboost_model_sentri.json) scores risk; dashboard renders explanation (shapley/feature bars) and a decision recommendation.

Deploy
Streamlit Community Cloud: push repo, set env vars.

Docker: FROM python:3.11-slim → install reqs → streamlit run.

Supabase SQL (once) to store behavioral events:

create table if not exists public.behavioral_events (
  id bigserial primary key,
  device_id_hash text not null,
  event_ts timestamptz not null default now(),
  p_scam real not null check (p_scam>=0 and p_scam<=1),
  source text not null default 'voice'
  -- add 'transcript text' ONLY if you want to store it
);
alter table public.behavioral_events enable row level security;
create policy "allow inserts from anon"
on public.behavioral_events for insert to anon with check (true);
Notes & Limits
The dashboard ships with a pre-trained xgboost_model_sentri.json; retrain by replacing the artifact and keeping feature order consistent.

Storing transcripts is optional; privacy-preserving mode uses scores only.
