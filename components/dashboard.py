import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict

def render_metrics(df: pd.DataFrame):
    """Render key metrics about the investor data"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Investors", len(df))
    with col2:
        st.metric("Avg Investments", int(df['investments'].mean()))
    with col3:
        st.metric("Active Locations", df['location'].nunique())
    with col4:
        st.metric("Investment Types", df['type'].nunique())

def render_data_table(df: pd.DataFrame):
    """Render interactive data table with investor information"""
    st.subheader("Investor Details")
    
    # Add column filters
    col1, col2 = st.columns(2)
    with col1:
        type_filter = st.multiselect(
            "Filter by Type",
            options=df['type'].unique(),
            default=df['type'].unique()
        )
    with col2:
        location_filter = st.multiselect(
            "Filter by Location",
            options=df['location'].unique(),
            default=df['location'].unique()
        )
    
    # Apply filters
    filtered_df = df[
        (df['type'].isin(type_filter)) &
        (df['location'].isin(location_filter))
    ]
    
    # Display table with custom formatting
    st.dataframe(
        filtered_df,
        column_config={
            "name": "Investor Name",
            "type": "Type",
            "location": "Location",
            "investments": st.column_config.NumberColumn(
                "Investment Count",
                help="Number of investments made"
            ),
            "profile_url": st.column_config.LinkColumn("Profile")
        },
        hide_index=True
    )

def render_dashboard(df: pd.DataFrame):
    """Render the main dashboard view"""
    st.header("Investor Dashboard")
    
    # Render metrics
    render_metrics(df)
    
    # Add spacing
    st.markdown("---")
    
    # Render data table
    render_data_table(df)
