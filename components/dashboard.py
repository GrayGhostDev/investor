import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict
from io import BytesIO
import json

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

def export_data(df: pd.DataFrame, file_format: str) -> BytesIO:
    """Export data in the specified format"""
    buffer = BytesIO()

    if file_format == "CSV":
        df.to_csv(buffer, index=False)
    elif file_format == "Excel":
        df.to_excel(buffer, index=False, engine='openpyxl')
    elif file_format == "JSON":
        # Handle nested data like investment_stages
        export_df = df.copy()
        if 'investment_stages' in export_df.columns:
            export_df['investment_stages'] = export_df['investment_stages'].apply(json.dumps)
        export_df.to_json(buffer, orient='records')

    buffer.seek(0)
    return buffer

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

    # Add export functionality
    if not filtered_df.empty:
        st.write("### Export Data")
        export_col1, export_col2 = st.columns([2, 1])

        with export_col1:
            export_format = st.selectbox(
                "Select Export Format",
                ["CSV", "Excel", "JSON"],
                help="Choose the format for exporting the filtered data"
            )

        with export_col2:
            if st.button("Export Data", type="primary"):
                # Create the export buffer
                buffer = export_data(filtered_df, export_format)

                # Generate filename
                timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                filename = f"investor_data_{timestamp}.{export_format.lower()}"
                if export_format == "Excel":
                    filename = f"investor_data_{timestamp}.xlsx"

                # Offer the file for download
                st.download_button(
                    label=f"Download {export_format}",
                    data=buffer,
                    file_name=filename,
                    mime={
                        "CSV": "text/csv",
                        "Excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        "JSON": "application/json"
                    }[export_format]
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