import streamlit as st
import base64

def get_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def footer_home():
    logo = get_base64("assets/logo.png")

    st.markdown(f"""
    <div style="margin-top:2rem; display:flex; gap:6px; justify-content:center; align-items:center;">
        <p style="font-weight:bold">Created with ❤️ by</p>
        <img src="data:image/png;base64,{logo}" style="height:40px;display:block;" />
    </div>
""", unsafe_allow_html=True)