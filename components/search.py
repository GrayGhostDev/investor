import streamlit as st
import pandas as pd
from typing import List, Dict
from InvestorSearchTool import InvestorSearchTool
from components.web_scraper import render_web_scraper_section

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
            
        # Always use real APIs
        st.info("Using real APIs for accurate location data and investor information based on your search terms.")

    return {
        "investment_range": investment_range,
        "investment_stages": investment_stages,
        "sectors": sectors,
        "continents": continents,
        "investment_size": investment_size,
        "years_active": years_active,
        "use_real_api": True  # Always use real API
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
                        "investment_stages": filters["investment_stages"],
                        "sectors": filters["sectors"],
                        "continents": filters["continents"]
                    },
                    sort_by=sort_by,
                    sort_order=sort_order.lower(),
                    use_real_api=filters.get("use_real_api", True)
                )

                if not results.empty:
                    st.session_state.search_results = results
                    st.success(f"Found {len(results)} investors matching your criteria")
                    
                    # Show a message that real APIs were used
                    st.info("Results include data from real APIs for enhanced accuracy and up-to-date information.")
                    
                    # Display a more detailed results view
                    st.write("### Investor Results")
                    
                    # Create tabs for different views
                    tab1, tab2 = st.tabs(["List View", "Map View"])
                    
                    with tab1:
                        # Enhanced list view with more details
                        for i, row in results.iterrows():
                            with st.expander(f"{row['name']} - {row['type']}"):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.write(f"**Location:** {row['location']}")
                                    st.write(f"**Investments:** {row['investments']}")
                                    st.write(f"**Investment Stages:** {', '.join(row['investment_stages'])}")
                                    if 'profile_url' in row and row['profile_url']:
                                        st.write(f"**Website:** [{row['profile_url']}]({row['profile_url']})")
                                
                                with col2:
                                    # Display a small map for the investor location
                                    if 'latitude' in row and 'longitude' in row and row['latitude'] and row['longitude']:
                                        st.write("**Location Map:**")
                                        location_df = pd.DataFrame({
                                            'lat': [row['latitude']],
                                            'lon': [row['longitude']],
                                            'name': [row['name']]
                                        })
                                        st.map(location_df, zoom=4)
                    
                    with tab2:
                        # Map view of all investors
                        if 'latitude' in results.columns and 'longitude' in results.columns:
                            map_data = pd.DataFrame({
                                'lat': results['latitude'],
                                'lon': results['longitude'],
                                'name': results['name']
                            })
                            st.map(map_data)
                        else:
                            st.warning("Location data not available for map view")
                    
                    # Remove the button to go to the matching algorithm tab since they're now in the same tab
                    st.markdown("---")
                    st.markdown("""
                    ### Find Your Perfect Investor Match
                    Use our matching algorithm on the right to find the investors that best match your startup's profile.
                    Enter your startup details and get personalized investor recommendations.
                    """)
                    
                    # Add a separator before web scraper section
                    st.markdown("---")
                    
                    # Add web scraper section to find additional investors from the web
                    render_web_scraper_section(search_terms, filters.get("location"))
                else:
                    st.warning("No investors found matching your criteria")
                    
                    # Even if no API results, try web scraping
                    st.markdown("---")
                    st.markdown("### Searching the web for alternatives...")
                    render_web_scraper_section(search_terms, filters.get("location"))

            except Exception as e:
                st.session_state.error = f"Error during search: {str(e)}"