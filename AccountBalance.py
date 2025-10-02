import streamlit as st

def app():
    from utils import add_header_logo
    add_header_logo()
    st.title("Account Balance")