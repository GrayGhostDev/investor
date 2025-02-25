import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def create_investment_distribution(df: pd.DataFrame):
    """Create enhanced investment distribution chart"""
    # Add chart type selector
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Pie Chart", "Treemap", "Bar Chart"],
        key="distribution_chart_type"
    )

    if chart_type == "Pie Chart":
        fig = px.pie(
            df,
            names='type',
            title='Distribution of Investor Types',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
    elif chart_type == "Treemap":
        fig = px.treemap(
            df,
            path=['type'],
            values='investments',
            title='Investment Distribution by Type',
            color='investments',
            color_continuous_scale='Viridis'
        )
    else:  # Bar Chart
        fig = px.bar(
            df.groupby('type')['investments'].sum().reset_index(),
            x='type',
            y='investments',
            title='Investment Distribution by Type',
            color='type',
            color_discrete_sequence=px.colors.qualitative.Set3
        )

    return fig

def create_location_map(df: pd.DataFrame):
    """Create enhanced location-based visualization"""
    # Add map style selector
    map_style = st.selectbox(
        "Select Map Style",
        ["carto-positron", "open-street-map", "carto-darkmatter"],
        key="map_style"
    )

    # Filter by minimum investments
    min_investments = st.slider(
        "Minimum Investment Count",
        min_value=0,
        max_value=int(df['investments'].max()),
        value=0,
        key="map_min_investments"
    )

    # Filter data
    filtered_df = df[df['investments'] >= min_investments]
    location_counts = filtered_df.groupby(['location', 'latitude', 'longitude']).size().reset_index(name='count')

    fig = px.scatter_mapbox(
        location_counts,
        lat='latitude',
        lon='longitude',
        size='count',
        hover_name='location',
        zoom=1,
        title='Investor Locations'
    )
    fig.update_layout(mapbox_style=map_style)
    return fig

def create_investment_stages(df: pd.DataFrame):
    """Create enhanced investment stages visualization"""
    # Add chart orientation option
    orientation = st.radio(
        "Chart Orientation",
        ["Vertical", "Horizontal"],
        horizontal=True,
        key="stages_orientation"
    )

    stages_data = df['investment_stages'].explode().value_counts()

    fig = px.bar(
        stages_data,
        orientation='v' if orientation == "Vertical" else 'h',
        title='Investment Stages Distribution',
        color_discrete_sequence=px.colors.qualitative.Set3
    )

    fig.update_layout(
        xaxis_title="Investment Stage" if orientation == "Vertical" else "Count",
        yaxis_title="Count" if orientation == "Vertical" else "Investment Stage"
    )
    return fig

def create_investment_trend_heatmap(df: pd.DataFrame):
    """Create enhanced interactive investment trend heatmap"""
    # Add colorscale selector
    colorscale = st.selectbox(
        "Select Color Scale",
        ["Viridis", "Plasma", "Inferno", "Magma", "RdBu"],
        key="heatmap_colorscale"
    )

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
        colorscale=colorscale,
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

def create_bubble_chart(df: pd.DataFrame):
    """Create bubble chart for investment analysis"""
    # Group data by type and calculate metrics
    grouped_data = df.groupby('type').agg({
        'investments': ['sum', 'mean', 'count']
    }).reset_index()
    grouped_data.columns = ['type', 'total_investments', 'avg_investments', 'investor_count']

    fig = px.scatter(
        grouped_data,
        x='total_investments',
        y='avg_investments',
        size='investor_count',
        color='type',
        hover_name='type',
        title='Investment Analysis Bubble Chart',
        labels={
            'total_investments': 'Total Investments',
            'avg_investments': 'Average Investments per Investor',
            'investor_count': 'Number of Investors'
        }
    )

    return fig

def create_investment_summary(df: pd.DataFrame):
    """Create investment summary subplot"""
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('Investment Distribution', 'Top Locations'),
        specs=[[{"type": "pie"}, {"type": "bar"}]]
    )

    # Add investment type distribution
    type_dist = df['type'].value_counts()
    fig.add_trace(
        go.Pie(labels=type_dist.index, values=type_dist.values),
        row=1, col=1
    )

    # Add top locations bar chart
    top_locations = df['location'].value_counts().head(5)
    fig.add_trace(
        go.Bar(x=top_locations.index, y=top_locations.values),
        row=1, col=2
    )

    fig.update_layout(height=400, title_text="Investment Summary")
    return fig

def render_visualizations(df: pd.DataFrame):
    """Render all visualizations"""
    st.header("Investment Analysis")

    # Add visualization selector
    st.sidebar.header("Visualization Controls")
    show_summary = st.sidebar.checkbox("Show Summary Dashboard", value=True)
    show_distribution = st.sidebar.checkbox("Show Type Distribution", value=True)
    show_map = st.sidebar.checkbox("Show Location Map", value=True)
    show_stages = st.sidebar.checkbox("Show Investment Stages", value=True)
    show_heatmap = st.sidebar.checkbox("Show Trend Heatmap", value=True)
    show_bubble = st.sidebar.checkbox("Show Bubble Chart", value=True)

    # Summary dashboard
    if show_summary:
        st.subheader("Investment Summary Dashboard")
        st.plotly_chart(
            create_investment_summary(df),
            use_container_width=True
        )

    # Distribution chart
    if show_distribution:
        st.subheader("Investment Type Distribution")
        st.plotly_chart(
            create_investment_distribution(df),
            use_container_width=True
        )

    # Location map
    if show_map:
        st.subheader("Geographic Distribution")
        st.plotly_chart(
            create_location_map(df),
            use_container_width=True
        )

    # Investment stages
    if show_stages:
        st.subheader("Investment Stages Analysis")
        st.plotly_chart(
            create_investment_stages(df),
            use_container_width=True
        )

    # Investment trend heatmap
    if show_heatmap:
        st.subheader("Investment Trend Analysis")
        st.markdown("""
        This heatmap shows the distribution of investments across different stages and investor types.
        Hover over the cells to see detailed information.
        """)
        st.plotly_chart(
            create_investment_trend_heatmap(df),
            use_container_width=True
        )

    # Bubble chart
    if show_bubble:
        st.subheader("Investment Metrics Analysis")
        st.plotly_chart(
            create_bubble_chart(df),
            use_container_width=True
        )