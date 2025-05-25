import streamlit as st

def apply_custom_ui():
    st.set_page_config(layout="wide")

    st.markdown("""
        <style>
            .stTextArea textarea {
                font-size: 15px;
            }
            .block-container {
                padding-left: 2rem;
                padding-right: 2rem;
                max-width:900px;
            }
            
        </style>
    """, unsafe_allow_html=True)
