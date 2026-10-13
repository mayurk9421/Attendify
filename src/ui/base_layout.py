import streamlit as st




def style_background_home():
    st.markdown("""
        <style>
                .stApp {
                background: #5865F2 !important;
                }
                .stApp div[data-testid="stColumn"]{
                background-color:#E0E3FF !important;
                padding:2.5rem !important;
                border-radius: 5rem !important;
                width: fit-content !important;
                min-width: 100px !important;
                max-width: 300px !important;
                }

              

        </style>
                
                """
                ,unsafe_allow_html=True)
    
    



def style_background_dashboard():
    st.markdown("""
        <style>
        /* Base colour for the whole Attendify app */
        .stApp {
            background: #EDE3FF !important;
            position: relative;
        }

        /* Animated purple-pink aurora layer */
        [data-testid="stAppViewContainer"] {
            background: transparent !important;
            position: relative;
            isolation: isolate;
        }

        
        [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: -35%;
        z-index: -1;
        pointer-events: none;

        background:
                radial-gradient(
                ellipse at 20% 30%,
                rgba(115, 65, 255, 0.38) 0%,
                transparent 45%
                ),
                radial-gradient(
                ellipse at 75% 35%,
                rgba(255, 55, 175, 0.30) 0%,
                transparent 45%
                ),
                radial-gradient(
                ellipse at 50% 80%,
                rgba(70, 115, 255, 0.32) 0%,
                transparent 48%
                );

        filter: blur(55px);
        background-size: 180% 180%;
        animation: attendifyAurora 18s ease-in-out infinite alternate;
        will-change: transform, background-position;
        }

        @keyframes attendifyAurora {
        0% {
                transform: translate3d(-4%, -3%, 0) scale(1);
                background-position: 0% 50%;
        }

        25% {
                transform: translate3d(3%, 2%, 0) scale(1.04);
                background-position: 50% 0%;
        }

        50% {
                transform: translate3d(4%, -2%, 0) scale(1.08);
                background-position: 100% 50%;
        }

        75% {
                transform: translate3d(-2%, 4%, 0) scale(1.04);
                background-position: 50% 100%;
        }

        100% {
                transform: translate3d(-4%, -3%, 0) scale(1);
                background-position: 0% 50%;
        }
        }

        @media (prefers-reduced-motion: reduce) {
        [data-testid="stAppViewContainer"]::before {
                animation: none;
        }
        }

        </style>
    """, unsafe_allow_html=True)

def style_base_layout():
    st.markdown("""
        <style>
                @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&display=swap');
                @import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&family=Climate+Crisis:YEAR@1979&family=Google+Sans:ital,opsz,wght@0,17..18,400..700;1,17..18,400..700&family=Outfit:wght@100..900&family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap');

        /*Hide top bar of streamlit */
                #MainMenu, Footer, Header {
                visibility: Hidden;
                }
                .block-container {
                padding-Top:1.5rem !important;}


                h1 {
                font-family: 'climate Crisis', sans-serif !important;
                font-size: 3.5rem !important;
                line-height:1.1 !important;
                margin-bottom:0rem !important;
                 }
                
                h2 {
                font-family: 'climate Crisis', sans-serif !important;
                font-size: 2rem !important;
                line-height:1.1 !important;
                margin-bottom:0rem !important;
                 }
                
                h3,h4,p, span{
                font-family: 'outfit',sans-serif;
                }

                button{
                background-color: #5865F2 !important;
                color:white !important;
                padding:10px 20px !important; 
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }


                button[kind='secondary']{
                background-color: #EB459E !important;
                color:white !important;
                padding:10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

                button[kind='tertiary']{
                background-color: black !important;
                color:white !important;
                padding:10px 20px !important;
                border: none !important;
                transition: transform 0.25s ease-in-out !important;
                }

                button:hover{
                transform :scale(1.05)
                }

                
                     </style>
                """
                ,unsafe_allow_html=True)
    
