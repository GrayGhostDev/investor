import streamlit as st

def set_page_config():
    """Set the page configuration for the Streamlit app"""
    st.set_page_config(
        page_title="Investor Search Platform",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def load_css():
    """Load custom CSS styling for the application"""
    st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        color: #1E3A8A;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    h3 {
        color: #2563EB;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }
    
    /* Button styling */
    .stButton > button {
        font-weight: 600;
        border-radius: 0.375rem;
    }
    
    /* Primary button */
    .stButton > button[data-baseweb="button"] {
        background-color: #2563EB;
        color: white;
    }
    
    /* Card styling for investor results */
    div[data-testid="stExpander"] {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #E0E7FF;
        color: #1E3A8A;
        font-weight: 600;
    }
    
    /* Form styling */
    div[data-testid="stForm"] {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    
    /* Metric styling */
    div[data-testid="stMetric"] {
        background-color: #F3F4F6;
        border-radius: 0.5rem;
        padding: 1rem;
    }
    
    div[data-testid="stMetricLabel"] {
        font-size: 1rem;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1E3A8A;
    }
    
    /* Dataframe styling */
    div[data-testid="stDataFrame"] {
        border: 1px solid #E5E7EB;
        border-radius: 0.5rem;
        padding: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
