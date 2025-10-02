import os
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Determine if running on Streamlit Cloud
if "STREAMLIT_SERVER_PORT" in os.environ:
    # Load Firebase credentials from Streamlit secrets
    cred_dict = {
        "type": "service_account",
        "project_id": st.secrets["firebase"]["project_id"],
        "private_key_id": st.secrets["firebase"]["private_key_id"],
        "private_key": st.secrets["firebase"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["firebase"]["client_email"],
        "client_id": st.secrets["firebase"]["client_id"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": st.secrets["firebase"]["client_x509_cert_url"]
    }
    cred = credentials.Certificate(cred_dict)
else:
    # Local environment: load JSON from local file
    cred_path = os.path.join(os.path.dirname(__file__), "sentri-c2304-firebase-adminsdk-fbsvc-fea4203cfc.json")
    cred = credentials.Certificate(cred_path)

# Initialize Firebase app only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# Firestore client and auth
db = firestore.client()
auth_client = auth
