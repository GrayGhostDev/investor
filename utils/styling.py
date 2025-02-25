import streamlit as st

def set_page_config():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title="Investor Search Platform",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def load_css():
    """Load custom CSS styles"""
    st.markdown("""
        <style>
            /* Custom styles from assets/styles.css */
            .stApp {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .stHeader {
                background-color: #ffffff;
                padding: 1rem 0;
            }
            
            .stMetric {
                background-color: #f8f9fa;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stPlotlyChart {
                background-color: #ffffff;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stDataFrame {
                background-color: #ffffff;
                padding: 1rem;
                border-radius: 0.5rem;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            /* Loading animation */
            .stSpinner {
                text-align: center;
                max-width: 50%;
                margin: 0 auto;
            }
            
            /* Button styling */
            .stButton>button {
                background-color: #0066cc;
                color: white;
                border-radius: 0.3rem;
                padding: 0.5rem 1rem;
                border: none;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            
            .stButton>button:hover {
                background-color: #0052a3;
                border: none;
            }
            
            /* Tab styling */
            .stTab {
                background-color: #ffffff;
                border-radius: 0.5rem 0.5rem 0 0;
            }
            
            /* Alert/Info styling */
            .stAlert {
                border-radius: 0.5rem;
                margin: 1rem 0;
            }
        </style>
    """, unsafe_allow_html=True)
