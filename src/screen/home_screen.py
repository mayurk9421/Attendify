import streamlit as st

from src.components.header import header_home
from src.components.footer import footer_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():
    style_background_home()
    style_base_layout()

    # Center the main content
    st.markdown("""
        <style>
        /* Main block container centering */
        [data-testid="stAppViewContainer"] .block-container {
            max-width: 1100px;
            margin: 0 auto;
            padding-top: 2rem !important;
            padding-bottom: 1rem !important;
        }

        .portal-title {
            text-align: center;
        }

        /* Target the horizontal block containing the two columns */
        [data-testid="stHorizontalBlock"] {
            display: flex;
            justify-content: center;
            align-items: center;
            max-width: 700px;
            margin: 0 auto;
        }

        /* Style individual columns for internal centering */
        div[data-testid="stColumn"] {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }

        div[data-testid="stColumn"] h2 {
            text-align: center;
        }

        div[data-testid="stColumn"] img {
            display: block;
            margin: 0 auto;
        }

        div[data-testid="stColumn"] button {
            display: block;
            margin: 0 auto;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header: logo + Attendify
    header_home()
    
    # Center the two portal cards
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.header("I'm Student")
        st.image(
            "https://i.ibb.co/844D9Lrt/mascot-student.png",
            width=110
        )

        if st.button(
            "Student Portal",
            type="primary",
            icon=":material/arrow_outward:",
            icon_position="right"
        ):
            st.session_state["login_type"] = "student"
            st.rerun()

    with col2:
        st.header("I'm Teacher")
        st.image(
            "https://i.ibb.co/CsmQQV6X/mascot-prof.png",
            width=120
        )

        if st.button(
            "Teacher Portal",
            type="primary",
            icon=":material/arrow_outward:",
            icon_position="right"
        ):
            st.session_state["login_type"] = "teacher"
            st.rerun()

    # Footer
    footer_home()