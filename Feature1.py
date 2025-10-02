import streamlit as st
from firebase_config import db  # import Firestore connection

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
                # Use the logged-in username/email as the user document ID
                user_id = st.session_state.username  

                # Store beneficiary inside user's subcollection
                db.collection("users").document(user_id).collection("beneficiaries").add({
                    "name": name,
                    "iban": iban
                })

                st.success(f"✅ Beneficiary '{name}' added under user {user_id}!")

            except Exception as e:
                st.error(f"Error: {e}")
        else: