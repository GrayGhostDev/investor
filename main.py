import streamlit as st
import pandas as pd
from components.search import render_search_section
from components.dashboard import render_dashboard
from components.visualizations import render_visualizations
from components.pitch_deck import render_pitch_deck_generator
from components.comparison import render_comparison_section
from components.sentiment import render_sentiment_tracker
from components.translator import render_translator_section
from components.matching_algorithm import render_matching_algorithm_section
from components.email_alerts import render_email_alerts_section
from utils.styling import load_css, set_page_config

def main():
    # Set page configuration
    set_page_config()

    # Load custom CSS
    load_css()

    # Page header
    st.title("Investor Search Platform")

    # Initialize session state
    if 'search_results' not in st.session_state:
        st.session_state.search_results = None
    if 'selected_investors' not in st.session_state:
        st.session_state.selected_investors = []
    if 'error' not in st.session_state:
        st.session_state.error = None
    if 'startup_profile' not in st.session_state:
        st.session_state.startup_profile = None

    # Create tabs for different sections - combining Search and Matching Algorithm
    tabs = st.tabs(["Search & Match", "Dashboard", "Analysis", "Pitch Deck", "Compare", "Market Sentiment", "Translator", "Email Alerts"])

    with tabs[0]:
        # Create columns for search and matching algorithm
        search_col, match_col = st.columns([1, 1])
        
        with search_col:
            render_search_section()
        
        with match_col:
            render_matching_algorithm_section(st.session_state.search_results if st.session_state.search_results is not None else None)

    with tabs[1]:
        if st.session_state.search_results is not None:
            render_dashboard(st.session_state.search_results)
        else:
            st.info("Use the search tab to find investors first")

    with tabs[2]:
        if st.session_state.search_results is not None:
            render_visualizations(st.session_state.search_results)
        else:
            st.info("Use the search tab to find investors first")

    with tabs[3]:
        if st.session_state.search_results is not None:
            render_pitch_deck_generator(st.session_state.search_results)
        else:
            st.info("Use the search tab to find investors first")

    with tabs[4]:
        if st.session_state.search_results is not None:
            render_comparison_section(st.session_state.search_results)
        else:
            st.info("Use the search tab to find investors first")

    with tabs[5]:
        render_sentiment_tracker()

    with tabs[6]:
        render_translator_section()
        
    with tabs[7]:
        render_email_alerts_section(st.session_state.search_results if st.session_state.search_results is not None else None)

    # Error handling
    if st.session_state.error:
        st.error(st.session_state.error)
        st.session_state.error = None

if __name__ == "__main__":
    main()