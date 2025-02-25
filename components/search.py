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

def render_advanced_filters():
    """Render advanced search filter inputs"""
    with st.expander("Advanced Filters", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            investment_range = st.slider(
                "Investment Count Range",
                min_value=0,
                max_value=2000,
                value=(0, 2000),
                step=100
            )

            investment_stages = st.multiselect(
                "Investment Stages",
                ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Growth", "Late Stage"],
                default=[]
            )

            sectors = st.multiselect(
                "Investment Sectors",
                ["Technology", "Healthcare", "Finance", "Consumer", "Enterprise", "AI/ML", 
                 "Blockchain", "SaaS", "E-commerce", "Mobile", "IoT", "Clean Tech"],
                default=[]
            )

        with col2:
            continents = st.multiselect(
                "Regions",
                ["North America", "Europe", "Asia", "South America", "Africa", "Oceania"],
                default=[]
            )

            investment_size = st.select_slider(
                "Typical Investment Size",
                options=["< $100K", "$100K-$500K", "$500K-$1M", "$1M-$5M", "$5M-$10M", "> $10M"],
                value=("< $100K", "> $10M")
            )

            years_active = st.slider(
                "Years Active",
                min_value=0,
                max_value=50,
                value=(0, 50),
                step=5
            )

    return {
        "investment_range": investment_range,
        "investment_stages": investment_stages,
        "sectors": sectors,
        "continents": continents,
        "investment_size": investment_size,
        "years_active": years_active
    }

def render_search_filters():
    """Render main search filter inputs"""
    st.write("### Basic Search")

    col1, col2 = st.columns(2)

    with col1:
        investor_type = st.multiselect(
            "Investor Type",
            ["Venture Capital", "Angel Investor", "Private Equity", "Accelerator", "Incubator"],
            default=["Venture Capital"]
        )

        location = st.text_input(
            "Location",
            placeholder="e.g., San Francisco, US or Europe"
        )

    with col2:
        focus_area = st.multiselect(
            "Primary Focus",
            ["B2B", "B2C", "Hardware", "Software", "Deep Tech", "Consumer"],
            default=[]
        )

        keywords = st.text_input(
            "Keywords",
            placeholder="Enter keywords (comma-separated)"
        )

    # Get advanced filters
    advanced_filters = render_advanced_filters()

    return {
        "investor_type": investor_type,
        "location": location,
        "focus_area": focus_area,
        "keywords": keywords,
        **advanced_filters
    }

def render_search_section():
    """Render the complete search section"""
    st.header("Search Investors")

    # Initialize search tool
    search_tool = initialize_search_tool()
    if not search_tool:
        return

    # Add search description
    st.markdown("""
    Use the filters below to find investors matching your criteria. 
    Combine basic and advanced filters for more precise results.
    """)

    # Render filters
    filters = render_search_filters()

    # Add sorting options
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_by = st.selectbox(
            "Sort By",
            ["Investment Count", "Years Active", "Name", "Location"]
        )
    with sort_col2:
        sort_order = st.radio(
            "Order",
            ["Descending", "Ascending"],
            horizontal=True
        )

    # Search button
    if st.button("Search Investors", type="primary"):
        with st.spinner("Searching for investors..."):
            try:
                # Process search terms
                search_terms = []

                # Add basic filters
                if filters["investor_type"]:
                    search_terms.extend(filters["investor_type"])
                if filters["location"]:
                    search_terms.append(filters["location"])
                if filters["focus_area"]:
                    search_terms.extend(filters["focus_area"])
                if filters["keywords"]:
                    search_terms.extend([k.strip() for k in filters["keywords"].split(",")])

                # Add advanced filters
                if filters["investment_stages"]:
                    search_terms.extend(filters["investment_stages"])
                if filters["sectors"]:
                    search_terms.extend(filters["sectors"])
                if filters["continents"]:
                    search_terms.extend(filters["continents"])

                # Get investor data with filters
                results = search_tool.get_investor_data(
                    search_terms=search_terms,
                    filters={
                        "investment_range": filters["investment_range"],
                        "investment_size": filters["investment_size"],
                        "years_active": filters["years_active"]
                    },
                    sort_by=sort_by,
                    sort_order=sort_order.lower()
                )

                if not results.empty:
                    st.session_state.search_results = results
                    st.success(f"Found {len(results)} investors matching your criteria")
                else:
                    st.warning("No investors found matching your criteria")

            except Exception as e:
                st.session_state.error = f"Error during search: {str(e)}"