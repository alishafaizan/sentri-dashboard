import streamlit as st
from firebase_config import db  # Firestore connection

def app():
    from utils import add_header_logo
    add_header_logo()
    st.title("Account Balance")
    user_id = st.session_state.username
    balance_ref = db.collection("users").document(user_id).collection("account").document("balance")
    balance_doc = balance_ref.get()
    balances = balance_doc.to_dict()
    checking = balances.get("checking", 0)
    savings = balances.get("savings", 0)
    credit_card = balances.get("credit_card", 0)
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Checking Account", f"${checking:,.2f}")
    col2.metric("Savings Account", f"${savings:,.2f}")
    col3.metric("Credit Card Balance", f"${credit_card:,.2f}")
    
    