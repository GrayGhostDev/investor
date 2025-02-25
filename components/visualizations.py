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

def create_investment_trend_heatmap(df: pd.DataFrame):
    """Create interactive investment trend heatmap"""
    # Extract and process investment stages and sectors
    stages = df['investment_stages'].explode().unique()
    sectors = df['type'].unique()

    # Create matrix of investment counts
    heatmap_data = pd.DataFrame(0, index=sectors, columns=stages)

    # Calculate investment counts for each sector-stage combination
    for idx, row in df.iterrows():
        sector = row['type']
        for stage in row['investment_stages']:
            heatmap_data.loc[sector, stage] += 1

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        hoverongaps=False
    ))

    # Update layout
    fig.update_layout(
        title='Investment Trends Heatmap',
        xaxis_title="Investment Stage",
        yaxis_title="Investor Type",
        height=500,
        xaxis={'side': 'bottom'}
    )

    # Add hover template
    fig.update_traces(
        hovertemplate="Investor Type: %{y}<br>Stage: %{x}<br>Count: %{z}<extra></extra>"
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

    # Investment trend heatmap
    st.subheader("Investment Trend Analysis")
    st.markdown("""
    This heatmap shows the distribution of investments across different stages and investor types.
    Hover over the cells to see detailed information.
    """)
    st.plotly_chart(
        create_investment_trend_heatmap(df),
        use_container_width=True
    )