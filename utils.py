import streamlit as st
from PIL import Image

def add_header_logo(logo_path="MCLogo.png", powered_by="Powered by Mastercard"):
    """Add logo and text at top-right of the webpage"""
    # Create columns with the right one for logo
    col1, col2 = st.columns([5, 1])
    
    with col2:
        try:
            logo = Image.open(logo_path)
            logo_col, text_col = st.columns([1, 2])
            with logo_col:
                st.image(logo, width=40)
            with text_col:
                st.markdown(f"<p style='font-size:11px; color:gray; margin-top:10px;'>{powered_by}</p>", 
                           unsafe_allow_html=True)
        except:
            st.markdown(f"<p style='text-align:center; font-size:10px; color:gray;'>{powered_by}</p>", 
                       unsafe_allow_html=True)

def add_footer(logo_path="MCLogo.png", powered_by="Powered by Mastercard"):
    # Using st.markdown with HTML/CSS for bottom-right placement
    footer_html = f"""
    <div style="
        position: fixed;
        bottom: 10px;
        right: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
        z-index: 1000;
    ">
        <img src="{logo_path}" width="40" height="40">
        <span style="font-size:12px; color:gray;">{powered_by}</span>
    </div>
    """
    st.markdown(footer_html, unsafe_allow_html=True)

import streamlit as st

def add_sidebar_footer(logo_path="MCLogo.png", powered_by="Powered by Mastercard"):
    # Add some empty lines to push footer to the bottom
    for _ in range(23):  # adjust number to push footer down
        st.sidebar.write("")

        # Load the logo image
    try:
        logo = Image.open(logo_path)
        
    except Exception as e:
        st.sidebar.write("Logo not found!")
        logo= None
    
    # Create two columns: one for logo, one for text
    col1, col2 = st.sidebar.columns([1, 4])  # adjust ratio if needed

    if logo:
        col1.image(logo, width=30)  # logo in first column

    col2.markdown(f"<span style='font-size:12px; color:gray;'>{powered_by}</span>",
    unsafe_allow_html=True)
    

