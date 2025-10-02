import streamlit as st
from streamlit_option_menu import option_menu
import home, account, Feature1, ReportFraud, AccountBalance

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="Sentri Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------ Session State for Authentication ------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = None


# ------------------ Sidebar Menu ------------------
def show_sidebar():
    with st.sidebar:
        app = option_menu(
            menu_title="ABC BANK",
            options=["Home", "Add Beneficiary", "Account Balance", "Report Fraud" ,"Sign Out"],
            icons=["house-fill", "person-fill","cash-coin", "incognito", "box-arrow-right",],
            menu_icon="chat-text-fill",
            default_index=0,
            styles={
                "container": {"padding": "5!important", "background-color": "#2c4068"},
                "icon": {"color": "white", "font-size": "22px"},
                "nav-link": {"color": "white", "font-size": "18px", "text-align": "left", "margin": "2px"},
                "nav-link-selected": {"background-color": "#02ab21"},
            },   
        )
        # Add footer at the bottom of sidebar
        #from utils import add_sidebar_footer
        #add_sidebar_footer(logo_path="MCLogo.png", powered_by="Powered by Mastercard")

        return app


# ------------------ Main App Flow ------------------
if not st.session_state.authenticated:
    # Only show Account page until user logs in
    account.app()
else:
    # Show sidebar with Home + Feature1 + Logout
    selected = show_sidebar()

    if selected == "Home":
        home.app()
    elif selected == "Add Beneficiary":
        Feature1.app()
    elif selected == "Account Balance":
        AccountBalance.app()
    elif selected == "Report Fraud":
        ReportFraud.app()
    elif selected == "Sign Out":
        st.session_state.authenticated = False
        st.session_state.username = None
        st.success("✅ You have been logged out.")
        st.rerun()
