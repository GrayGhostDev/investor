import streamlit as st
import pandas as pd
from components.search import render_search_section
from components.dashboard import render_dashboard
from components.visualizations import render_visualizations
from components.pitch_deck import render_pitch_deck_generator
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

    # Create tabs for different sections
    tabs = st.tabs(["Search", "Dashboard", "Analysis", "Pitch Deck"])

    with tabs[0]:
        render_search_section()

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

    # Error handling
    if st.session_state.error:
        st.error(st.session_state.error)
        st.session_state.error = None

if __name__ == "__main__":
    main()