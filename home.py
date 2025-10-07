import streamlit as st
import pandas as pd
import numpy as np
import time
from utils import add_header_logo
from firebase_config import db

def dashboard(user_id):
    
    # Fetch REAL account summary
    try:
        balance_ref = db.collection("users").document(user_id).collection("account").document("balance")
        balance_doc = balance_ref.get()
        
        if balance_doc.exists:
            balances = balance_doc.to_dict()
            checking = balances.get("checking", 0)
            savings = balances.get("savings", 0)
            credit_card = balances.get("credit_card", 0)
            user_iban = balances.get("iban", "N/A")
        else:
            # Initialize if not exists
            import random
            user_iban = f"AE{''.join([str(random.randint(0, 9)) for _ in range(8)])}"
            checking, savings, credit_card = 5000.00, 12430.75, 1230.00
            db.collection("users").document(user_id).collection("account").document("balance").set({
                "checking": checking,
                "savings": savings,
                "credit_card": credit_card,
                "iban": user_iban
            })
    except Exception as e:
        st.error(f"Error fetching balance: {e}")
        checking, savings, credit_card = 0, 0, 0
        user_iban = "N/A"
    
    st.subheader("💰 Account Summary")
    
    # Display IBAN
    st.info(f"🏦 Your IBAN: **{user_iban}**")
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Checking Account", f"${checking:,.2f}")
    col2.metric("Savings Account", f"${savings:,.2f}")
    col3.metric("Credit Card Balance", f"${credit_card:,.2f}")
    
    st.markdown("---")
    
    
    # Fetch REAL transactions
    st.subheader("📜 Recent Transactions")
    try:
        transactions_ref = db.collection("users").document(user_id).collection("transactions")
        docs = transactions_ref.order_by("date", direction="DESCENDING").limit(10).stream()
        
        transactions = []
        for doc in docs:
            data = doc.to_dict()
            transactions.append({
                "Date": data['date'].strftime("%Y-%m-%d %H:%M"),
                "Description": data['description'],
                "Type": "Sent ⬆️" if data['type'] == "sent" else "Received ⬇️",
                "Amount": f"- ${data['amount']:,.2f}" if data['type'] == "sent" else f"+ ${data['amount']:,.2f}",
                "Balance": f"${data['balance_after']:,.2f}"
            })
        
        if transactions:
            df = pd.DataFrame(transactions)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No transactions yet. Start by sending money to a beneficiary!")
            
    except Exception as e:
        st.error(f"Error fetching transactions: {e}")
    
    st.markdown("---")
    
    # Fetch beneficiaries
    try:
        beneficiaries_ref = db.collection("users").document(user_id).collection("beneficiaries")
        docs = beneficiaries_ref.stream()
        
        beneficiaries = []
        for doc in docs:
            beneficiaries.append(doc.to_dict())
        
        if beneficiaries:
            st.subheader("💳 Your Beneficiaries:")
            df = pd.DataFrame(beneficiaries)
            df.index = df.index + 1
            df.index.name = "No."
            st.table(df)
        else:
            st.info("You have not added any beneficiaries yet.")
    
    except Exception as e:
        st.error(f"Error fetching beneficiaries: {e}")

def app():
    add_header_logo()
    
    if "username" in st.session_state and st.session_state.username:
        st.title(f"Welcome back, {st.session_state.username}!")
        user_id = st.session_state.username
    else:
        st.info("Welcome! Please log in to access all features.")
        return
    
    dashboard(user_id)