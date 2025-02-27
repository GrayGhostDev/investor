import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List
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
    """
    Render a dashboard with key metrics and visualizations for investor data
    
    Args:
        df: DataFrame containing investor data
    """
    st.header("Investor Dashboard")
    
    if df.empty:
        st.warning("No investor data available to display")
        return
    
    # Add description
    st.markdown("""
    This dashboard provides an overview of the investor landscape based on your search results.
    Explore key metrics and visualizations to gain insights into investor distribution and trends.
    """)
    
    # Calculate key metrics
    total_investors = len(df)
    total_investments = df['investments'].sum() if 'investments' in df.columns else 0
    avg_investments = round(df['investments'].mean()) if 'investments' in df.columns else 0
    
    # Display metrics in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Total Investors",
            value=f"{total_investors:,}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="Total Investments",
            value=f"{total_investments:,}",
            delta=None
        )
    
    with col3:
        st.metric(
            label="Avg. Investments per Investor",
            value=f"{avg_investments:,}",
            delta=None
        )
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Investor Distribution", "Investment Analysis", "Geographic Insights"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Investor type distribution
            if 'type' in df.columns:
                type_counts = df['type'].value_counts().reset_index()
                type_counts.columns = ['Investor Type', 'Count']
                
                fig = px.pie(
                    type_counts,
                    values='Count',
                    names='Investor Type',
                    title='Investor Type Distribution',
                    color_discrete_sequence=px.colors.qualitative.Plotly
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Investment stage focus
            if 'investment_stages' in df.columns:
                # Flatten the list of investment stages
                all_stages = []
                for stages in df['investment_stages']:
                    if isinstance(stages, list):
                        all_stages.extend(stages)
                
                stage_counts = pd.Series(all_stages).value_counts().reset_index()
                stage_counts.columns = ['Investment Stage', 'Count']
                
                fig = px.bar(
                    stage_counts,
                    x='Investment Stage',
                    y='Count',
                    title='Investment Stage Focus',
                    color='Count',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="",
                    yaxis_title="Number of Investors"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top investors by investment count
            if 'investments' in df.columns and 'name' in df.columns:
                top_investors = df.sort_values('investments', ascending=False).head(10)
                
                fig = px.bar(
                    top_investors,
                    x='investments',
                    y='name',
                    title='Top 10 Investors by Investment Count',
                    orientation='h',
                    color='investments',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(
                    height=500,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Number of Investments",
                    yaxis_title="",
                    yaxis=dict(autorange="reversed")
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Investment distribution
            if 'investments' in df.columns:
                fig = px.histogram(
                    df,
                    x='investments',
                    nbins=20,
                    title='Investment Count Distribution',
                    color_discrete_sequence=['#2563EB']
                )
                fig.update_layout(
                    height=500,
                    margin=dict(l=20, r=20, t=40, b=20),
                    xaxis_title="Number of Investments",
                    yaxis_title="Number of Investors"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Geographic distribution
        if 'location' in df.columns:
            # Extract country/region from location
            df['country'] = df['location'].apply(lambda x: x.split(',')[-1].strip() if ',' in x else x)
            country_counts = df['country'].value_counts().reset_index()
            country_counts.columns = ['Country/Region', 'Count']
            
            fig = px.bar(
                country_counts.head(10),
                x='Country/Region',
                y='Count',
                title='Top 10 Investor Locations',
                color='Count',
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis_title="",
                yaxis_title="Number of Investors"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Map view if coordinates are available
        if 'latitude' in df.columns and 'longitude' in df.columns:
            st.subheader("Investor Locations Map")
            
            # Create a dataframe for the map
            map_data = pd.DataFrame({
                'lat': df['latitude'],
                'lon': df['longitude'],
                'name': df['name'] if 'name' in df.columns else '',
                'size': df['investments'] if 'investments' in df.columns else 10
            })
            
            st.map(map_data)
    
    # Add data table with key information
    st.subheader("Investor Data Table")
    
    # Select columns to display
    display_cols = ['name', 'type', 'location', 'investments']
    display_cols = [col for col in display_cols if col in df.columns]
    
    if display_cols:
        st.dataframe(df[display_cols], use_container_width=True)
    else:
        st.warning("No data columns available to display")