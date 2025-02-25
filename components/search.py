import streamlit as st
import pandas as pd
from typing import List, Dict
from InvestorSearchTool import InvestorSearchTool

def initialize_search_tool():
    """Initialize the investor search tool"""
    try:
        return InvestorSearchTool()
    except Exception as e:
        st.error(f"Error initializing search tool: {str(e)}")
        return None

def render_search_filters():
    """Render search filter inputs"""
    col1, col2 = st.columns(2)
    
    with col1:
        investor_type = st.multiselect(
            "Investor Type",
            ["Venture Capital", "Angel Investor", "Private Equity", "Accelerator", "Incubator"],
            default=["Venture Capital"]
        )
        
        investment_stage = st.multiselect(
            "Investment Stage",
            ["Pre-Seed", "Seed", "Series A", "Series B", "Growth", "Late Stage"],
            default=["Seed", "Series A"]
        )
    
    with col2:
        location = st.text_input("Location", placeholder="e.g., San Francisco, US")
        
        sectors = st.multiselect(
            "Investment Sectors",
            ["Technology", "Healthcare", "Finance", "Consumer", "Enterprise", "AI/ML"],
            default=["Technology"]
        )
    
    return {
        "investor_type": investor_type,
        "investment_stage": investment_stage,
        "location": location,
        "sectors": sectors
    }

def render_search_section():
    """Render the complete search section"""
    st.header("Search Investors")
    
    # Initialize search tool
    search_tool = initialize_search_tool()
    if not search_tool:
        return
    
    # Render filters
    filters = render_search_filters()
    
    # Search button
    if st.button("Search Investors", type="primary"):
        with st.spinner("Searching for investors..."):
            try:
                # Combine filters into search terms
                search_terms = [
                    *filters["investor_type"],
                    *filters["investment_stage"],
                    filters["location"],
                    *filters["sectors"]
                ]
                
                # Get investor data
                results = search_tool.get_investor_data(search_terms)
                
                if not results.empty:
                    st.session_state.search_results = results
                    st.success(f"Found {len(results)} investors matching your criteria")
                else:
                    st.warning("No investors found matching your criteria")
                    
            except Exception as e:
                st.session_state.error = f"Error during search: {str(e)}"
