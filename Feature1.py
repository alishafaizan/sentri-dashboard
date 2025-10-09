import streamlit as st
from firebase_config import db  # import Firestore connection
import random
import time
from scoring_script01 import score_transaction
import pandas as pd
import random
from datetime import datetime

#Add function to get card, merchant, mcc
def get_m():
    df = pd.read_excel("SampleDataset02.xlsx")  # replace with your actual CSV file name

    # Pick a random row
    random_row = df.sample(n=1).iloc[0]

    # Extract Card, Merchant Name and MCC
    random_card = random_row['Card']
    random_merchant = random_row['Merchant ID']
    random_mcc = random_row['MCC']

    return random_card, random_merchant, random_mcc

#Get current hour
def get_current_hour():
    """Returns the current hour of the day (0–23)."""
    current_time = datetime.now()
    return current_time.hour

# Add your function here at the top
def analyze_beneficiary(username, beneficiary_name, iban):
    """
    Analyzes beneficiary and returns trust score and explanation.
    Replace random logic with actual model later.
    """
    # Placeholder logic - replace with your actual model
    rating = random.randint(1, 5)
    explanation = "Model Output"
    
    return rating, explanation

def app():
    st.title("Add Beneficiary")
    from utils import add_header_logo
    add_header_logo()
    # Input fields
    name = st.text_input("Beneficiary Name *")
    iban = st.text_input("IBAN Number *")

    # Initialize session state for rating flow
    if 'show_confirmation' not in st.session_state:
        st.session_state.show_confirmation = False
    if 'current_rating' not in st.session_state:
        st.session_state.current_rating = None
    if 'current_explanation' not in st.session_state:
        st.session_state.current_explanation = None
    if 'current_name' not in st.session_state:
        st.session_state.current_name = None
    if 'current_iban' not in st.session_state:
        st.session_state.current_iban = None

    # If showing confirmation screen
    if st.session_state.show_confirmation:
        rating = st.session_state.current_rating
        explanation = st.session_state.current_explanation
        stars = "⭐" * rating
        
        if rating >= 4:
            st.success(f"### Trust Score: {stars} ({rating}/5)")
        elif rating >= 3:
            st.warning(f"### Trust Score: {stars} ({rating}/5)")
        else:
            st.error(f"### Trust Score: {stars} ({rating}/5)")
        
        st.info(explanation)

        st.warning("⚠️ Are you sure you want to add this beneficiary?")
            
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Yes, Add Beneficiary", use_container_width=True):
                try:
                    user_id = st.session_state.username
                    
                    # Store beneficiary using NAME as the document ID
                    db.collection("users").document(user_id).collection("beneficiaries").document(st.session_state.current_name).set({
                        "name": st.session_state.current_name,
                        "iban": st.session_state.current_iban
                    })
                    
                    st.success(f"✅ Beneficiary '{st.session_state.current_name}' added successfully!")
                    
                    # Reset state
                    st.session_state.show_confirmation = False
                    st.session_state.current_rating = None
                    st.session_state.current_explanation = None
                    st.session_state.current_name = None
                    st.session_state.current_iban = None
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")
        
        with col2:
            if st.button("❌ No, Go Back", use_container_width=True):
                # Reset state and go back
                st.session_state.show_confirmation = False
                st.session_state.current_rating = None
                st.session_state.current_explanation = None
                st.session_state.current_name = None
                st.session_state.current_iban = None
                st.rerun()
    else:
        if st.button("Add Beneficiary"):
            if name and iban:
                # Create a placeholder for animation
                placeholder = st.empty()
                
                # Show "Analyzing..." message
                with placeholder.container():
                    st.info("🔍 Calculating Sentri Score...")
                time.sleep(1)

                # Generate random rating from 1 to 5
                user_id = st.session_state.username
                #rating, explanation = analyze_beneficiary(user_id, name, iban)
                card, merchant, mcc = get_m()
                hour = get_current_hour()
                amount = random.randint(1, 1000)
                rating, explanation = score_transaction(card,merchant,amount,mcc,hour)
                #rating, explanation = score_transaction(0,7945328079774550000,50,5411,12)

                #rating = random.randint(1, 5)
                
                # Store in session state
                st.session_state.current_rating = rating
                st.session_state.current_explanation = explanation
                st.session_state.current_name = name
                st.session_state.current_iban = iban
                
                
                # Set flag to show confirmation screen
                st.session_state.show_confirmation = True
                st.rerun()
                
            else:
                st.warning("Please enter both name and IBAN.")