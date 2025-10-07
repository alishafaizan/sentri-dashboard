import streamlit as st
from firebase_config import auth_client  # Use auth from firebase_config

from firebase_config import db

import random

def generate_iban():
    """Generate random IBAN starting with AE followed by 8 digits"""
    random_digits = ''.join([str(random.randint(0, 9)) for _ in range(8)])
    return f"AE{random_digits}"

def app():
    st.title("🔐 Account Login / Sign Up")

    choice = st.selectbox("Choose Action", ["Login", "Sign Up"])

    if choice == "Login":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                user = auth_client.get_user_by_email(email)
                # Login successful
                st.session_state.authenticated = True
                st.session_state.username = user.uid
                st.success(f"Welcome back, {st.session_state.username}!")
                st.rerun()
            except Exception as e:
                st.error(f"Login failed: {e}")

    elif choice == "Sign Up":
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        username = st.text_input('Enter your unique username')
        if st.button("Sign Up"):
            try:
                user = auth_client.create_user(email=emai