import streamlit as st
import pandas as pd
import numpy as np
import time
from utils import add_footer 
from firebase_config import db  # Firestore connection


def dashboard():
    st.title("📊 Dashboard")

    st.markdown("---")  # Divider

    # Sample account summary
    st.subheader("💰 Account Summary")
    col1, col2, col3 = st.columns(3)

    col1.metric("Checking Account", "$5,240.50", "+2.5%")
    col2.metric("Savings Account", "$12,430.75", "+1.8%")
    col3.metric("Credit Card Balance", "$1,230.00", "-0.5%")

    st.markdown("---")

    # Quick actions
    st.subheader("⚡ Quick Actions")
    action_col1, action_col2, action_col3, action_col4 = st.columns(4)

    if action_col1.button("Transfer Money"):
        st.info("Navigate to 'Add Beneficiary' to transfer money.")
    if action_col2.button("Pay Bills"):
        st.info("Bill payment feature coming soon.")
    if action_col3.button("View Statements"):
        st.info("Statement feature coming soon.")
    if action_col4.button("Report Fraud"):
        st.info("Navigate to 'Report Fraud' to report an issue.")

    st.markdown("---")

    # Optional: recent transactions (dummy table)
    st.subheader("📜 Recent Transactions")
    transactions = {
        "Date": ["2025-09-28", "2025-09-27", "2025-09-25"],
        "Description": ["Amazon Purchase", "Salary Credit", "Utility Bill"],
        "Amount": ["- $120.50", "+ $3,000.00", "- $150.00"],
        "Balance": ["$5,120.00", "$8,120.50", "$8,270.50"]
    }
    st.table(transactions)
    st.markdown("---")

    # Fetch beneficiaries for this user
    try:
        user_id = st.session_state.username 
        beneficiaries_ref = db.collection("users").document(user_id).collection("beneficiaries")
        docs = beneficiaries_ref.stream()

        beneficiaries = []
        for doc in docs:
            beneficiaries.append(doc.to_dict())

        if beneficiaries:
            st.subheader("💳 Your Beneficiaries:")
            # Convert list of dicts to DataFrame
            df = pd.DataFrame(beneficiaries)
            
            # Reset index to start from 1
            df.index = df.index + 1
            df.index.name = "No."  # optional: name the index column
            
            st.table(df)
            #st.table(beneficiaries)   # or use st.dataframe for more functionality
        else:
            st.info("You have not added any beneficiaries yet.")
    
    except Exception as e:
        st.error(f"Error fetching beneficiaries: {e}")

def app():
    
    # Check if username exists in session_state
    if "username" in st.session_state and st.session_state.username:
        st.title(f"Welcome back, {st.session_state.username}!")
    else:
        st.info("Welcome! Please log in to access all features.")
    dashboard()
    

