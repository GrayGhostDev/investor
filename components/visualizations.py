import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_investment_distribution(df: pd.DataFrame):
    """Create investment distribution chart"""
    fig = px.pie(
        df,
        names='type',
        title='Distribution of Investor Types',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_location_map(df: pd.DataFrame):
    """Create location-based visualization"""
    # First, group by location and count
    location_counts = df.groupby(['location', 'latitude', 'longitude']).size().reset_index(name='count')

    fig = px.scatter_mapbox(
        location_counts,
        lat='latitude',
        lon='longitude',
        size='count',
        hover_name='location',
        zoom=1,
        title='Investor Locations'
    )
    fig.update_layout(mapbox_style="carto-positron")
    return fig

def create_investment_stages(df: pd.DataFrame):
    """Create investment stages visualization"""
    stages_data = df['investment_stages'].explode().value_counts()

    fig = px.bar(
        stages_data,
        title='Investment Stages Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_layout(
        xaxis_title="Investment Stage",
        yaxis_title="Number of Investors"
    )
    return fig

def render_visualizations(df: pd.DataFrame):
    """Render all visualizations"""
    st.header("Investment Analysis")

    # Distribution chart
    st.plotly_chart(
        create_investment_distribution(df),
        use_container_width=True
    )

    # Location map
    st.plotly_chart(
        create_location_map(df),
        use_container_width=True
    )

    # Investment stages
    st.plotly_chart(
        create_investment_stages(df),
        use_container_width=True
    )