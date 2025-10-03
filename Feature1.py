import streamlit as st
from firebase_config import db  # import Firestore connection
import random
import time

def app():
    from utils import add_header_logo
    add_header_logo()
    st.title("Add Beneficiary")

    # Input fields
    name = st.text_input("Beneficiary Name *")
    iban = st.text_input("IBAN Number *")

    if st.button("Add Beneficiary"):
        if name and iban:
            try:
                # Generate random rating from 1 to 5
                rating = random.randint(1, 5)
                
                # Create a placeholder for animation
                placeholder = st.empty()
                
                # Show "Analyzing..." message
                with placeholder.container():
                    st.info("🔍 Analyzing beneficiary trust score...")
                
                time.sleep(1)
                
                # Display star rating with color
                with placeholder.container():
                    stars = "⭐" * rating
                    if rating >= 4:
                        st.success(f"### Trust Score: {stars} ({rating}/5)")
                    elif rating >= 3:
                        st.warning(f"### Trust Score: {stars} ({rating}/5)")
                    else:
                        st.error(f"### Trust Score: {stars} ({rating}/5)")
                
                time.sleep(0.5)
                # Use the logged-in username/email as the user document ID
                user_id = st.session_state.username  

                # Store beneficiary inside user's subcollection
                db.collection("users").document(user_id).collection("beneficiaries").document(name).set({
                    "name": name,
                    "iban": iban,
                    "trust_score": rating
                })

                st.success(f"✅ Beneficiary '{name}' added under user {user_id}!")

            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.warning("Please enter both name and IBAN.")
