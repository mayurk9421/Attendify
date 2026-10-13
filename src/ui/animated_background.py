
import streamlit as st


def render_aurora_background():
    st.markdown(
        """
        <style>
        /* Full-page animated background */
        [data-testid="stAppViewContainer"] {
            background: #f3eaff !important;
            position: relative;
            isolation: isolate;
        }

        [data-testid="stAppViewContainer"]::before {
            content: "";
            position: fixed;
            inset: -30%;
            z-index: -1;
            pointer-events: none;

            background:
                radial-gradient(
                    ellipse at 20% 30%,
                    rgba(128, 83, 255, 0.20) 0%,
                    transparent 45%
                ),
                radial-gradient(
                    ellipse at 80% 35%,
                    rgba(255, 70, 175, 0.16) 0%,
                    transparent 42%
                ),
                radial-gradient(
                    ellipse at 50% 80%,
                    rgba(92, 105, 255, 0.15) 0%,
                    transparent 48%
                );

            background-size: 150% 150%;
            animation: attendifyFullAurora 28s ease-in-out infinite alternate;
            will-change: transform;
        }

        /* Keep Streamlit's content above the background */
        [data-testid="stHeader"],
        [data-testid="stMain"],
        [data-testid="stBottom"] {
            background: transparent !important;
        }

        @keyframes attendifyFullAurora {
            0% {
                transform: translate3d(-3%, -2%, 0) scale(1);
            }
            50% {
                transform: translate3d(2%, 3%, 0) scale(1.04);
            }
            100% {
                transform: translate3d(-1%, 1%, 0) scale(1.02);
            }
        }

        @media (prefers-reduced-motion: reduce) {
            [data-testid="stAppViewContainer"]::before {
                animation: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
