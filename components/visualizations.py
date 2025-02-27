import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from typing import List, Dict, Any

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
    """
    Render advanced data visualizations for investor analysis
    
    Args:
        df: DataFrame containing investor data
    """
    st.header("Investor Data Analysis")
    
    if df.empty:
        st.warning("No investor data available to visualize")
        return
    
    # Add description
    st.markdown("""
    Explore advanced visualizations to gain deeper insights into investor patterns and trends.
    These visualizations help you understand the investment landscape and identify potential opportunities.
    """)
    
    # Create tabs for different visualization categories
    tab1, tab2, tab3, tab4 = st.tabs([
        "Investment Patterns", 
        "Geographic Analysis", 
        "Investor Comparisons",
        "Custom Analysis"
    ])
    
    with tab1:
        st.subheader("Investment Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Investment stage heatmap
            if 'investment_stages' in df.columns and 'type' in df.columns:
                st.write("#### Investment Stages by Investor Type")
                
                # Create a matrix of investor types vs investment stages
                investor_types = df['type'].unique()
                
                # Get all unique investment stages
                all_stages = set()
                for stages in df['investment_stages']:
                    if isinstance(stages, list):
                        all_stages.update(stages)
                all_stages = sorted(list(all_stages))
                
                # Create the heatmap data
                heatmap_data = []
                for inv_type in investor_types:
                    type_df = df[df['type'] == inv_type]
                    
                    for stage in all_stages:
                        # Count investors of this type that invest in this stage
                        count = sum(1 for stages in type_df['investment_stages'] if stage in stages)
                        
                        heatmap_data.append({
                            'Investor Type': inv_type,
                            'Investment Stage': stage,
                            'Count': count
                        })
                
                heatmap_df = pd.DataFrame(heatmap_data)
                
                # Create pivot table for heatmap
                pivot_df = heatmap_df.pivot(
                    index='Investor Type', 
                    columns='Investment Stage', 
                    values='Count'
                ).fillna(0)
                
                # Create heatmap
                fig = px.imshow(
                    pivot_df,
                    labels=dict(x="Investment Stage", y="Investor Type", color="Count"),
                    x=pivot_df.columns,
                    y=pivot_df.index,
                    color_continuous_scale='Blues',
                    aspect="auto"
                )
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=20, b=20),
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.caption("This heatmap shows the distribution of investment stages across different investor types.")
        
        with col2:
            # Investment count by type - box plot
            if 'investments' in df.columns and 'type' in df.columns:
                st.write("#### Investment Count Distribution by Type")
                
                fig = px.box(
                    df,
                    x='type',
                    y='investments',
                    color='type',
                    title='Investment Count Distribution by Investor Type',
                    labels={'type': 'Investor Type', 'investments': 'Number of Investments'}
                )
                fig.update_layout(
                    height=400,
                    margin=dict(l=20, r=20, t=40, b=20),
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.caption("This box plot shows the distribution of investment counts across different investor types.")
    
    with tab2:
        st.subheader("Geographic Analysis")
        
        # Check if we have location data
        if 'location' in df.columns:
            # Create a world map of investor locations
            if 'latitude' in df.columns and 'longitude' in df.columns:
                st.write("#### Global Investor Distribution")
                
                # Create a scatter map
                fig = px.scatter_geo(
                    df,
                    lat='latitude',
                    lon='longitude',
                    color='type' if 'type' in df.columns else None,
                    hover_name='name' if 'name' in df.columns else None,
                    size='investments' if 'investments' in df.columns else None,
                    projection='natural earth',
                    title='Global Investor Distribution'
                )
                fig.update_layout(
                    height=500,
                    margin=dict(l=0, r=0, t=40, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Location-based analysis
            st.write("#### Investment Activity by Region")
            
            # Extract regions from location
            df['region'] = df['location'].apply(lambda x: x.split(',')[-1].strip() if ',' in x else x)
            
            # Group by region and calculate metrics
            region_data = df.groupby('region').agg({
                'investments': ['sum', 'mean', 'count']
            }).reset_index()
            
            region_data.columns = ['Region', 'Total Investments', 'Average Investments', 'Investor Count']
            
            # Sort by total investments
            region_data = region_data.sort_values('Total Investments', ascending=False)
            
            # Create a bar chart
            fig = px.bar(
                region_data.head(10),
                x='Region',
                y='Total Investments',
                color='Investor Count',
                text='Investor Count',
                title='Top 10 Regions by Investment Activity',
                labels={'Region': 'Region', 'Total Investments': 'Total Investments'},
                color_continuous_scale='Blues'
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Investor Comparisons")
        
        # Allow user to select investors to compare
        if 'name' in df.columns:
            selected_investors = st.multiselect(
                "Select investors to compare",
                options=df['name'].tolist(),
                default=df['name'].head(3).tolist() if len(df) >= 3 else df['name'].tolist()
            )
            
            if selected_investors:
                # Filter data for selected investors
                selected_df = df[df['name'].isin(selected_investors)]
                
                # Create radar chart for comparison
                if not selected_df.empty:
                    st.write("#### Investor Comparison - Radar Chart")
                    
                    # Define metrics for comparison
                    metrics = []
                    
                    if 'investments' in selected_df.columns:
                        metrics.append('investments')
                        # Normalize investments for radar chart
                        max_investments = selected_df['investments'].max()
                        selected_df['investments_normalized'] = selected_df['investments'] / max_investments
                    
                    # Add more metrics if available
                    # For example, we could add metrics like:
                    # - Number of investment stages
                    # - Geographic diversity
                    # - Sector diversity
                    
                    if 'investment_stages' in selected_df.columns:
                        # Add number of investment stages as a metric
                        selected_df['num_stages'] = selected_df['investment_stages'].apply(len)
                        max_stages = selected_df['num_stages'].max()
                        selected_df['stages_normalized'] = selected_df['num_stages'] / max_stages if max_stages > 0 else 0
                        metrics.append('stages_normalized')
                    
                    # Create radar chart if we have metrics
                    if metrics:
                        # Create figure
                        fig = go.Figure()
                        
                        # Add a trace for each investor
                        for _, row in selected_df.iterrows():
                            values = [row[metric] for metric in metrics]
                            # Add the first value again to close the loop
                            values.append(values[0])
                            
                            # Define categories
                            categories = [metric.replace('_normalized', '').title() for metric in metrics]
                            categories.append(categories[0])  # Close the loop
                            
                            fig.add_trace(go.Scatterpolar(
                                r=values,
                                theta=categories,
                                fill='toself',
                                name=row['name']
                            ))
                        
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 1]
                                )
                            ),
                            showlegend=True,
                            height=500,
                            margin=dict(l=80, r=80, t=20, b=20),
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Create a comparison table
                    st.write("#### Detailed Comparison")
                    
                    # Select columns for comparison
                    compare_cols = ['name', 'type', 'location', 'investments']
                    if 'investment_stages' in selected_df.columns:
                        # Convert investment stages list to string for display
                        selected_df['stages_display'] = selected_df['investment_stages'].apply(
                            lambda x: ', '.join(x) if isinstance(x, list) else str(x)
                        )
                        compare_cols.append('stages_display')
                    
                    # Filter columns that exist
                    compare_cols = [col for col in compare_cols if col in selected_df.columns]
                    
                    if compare_cols:
                        st.dataframe(selected_df[compare_cols], use_container_width=True)
    
    with tab4:
        st.subheader("Custom Analysis")
        
        st.markdown("""
        Create your own custom visualization by selecting variables to plot.
        This allows you to explore relationships between different investor attributes.
        """)
        
        # Get available numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        # Get available categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Remove any list-type columns from categorical
        categorical_cols = [col for col in categorical_cols if not isinstance(df[col].iloc[0], list)]
        
        # Create form for custom visualization
        with st.form("custom_viz_form"):
            viz_type = st.selectbox(
                "Visualization Type",
                options=["Scatter Plot", "Bar Chart", "Box Plot", "Histogram"]
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if viz_type in ["Scatter Plot", "Bar Chart", "Box Plot"]:
                    x_axis = st.selectbox(
                        "X-Axis",
                        options=categorical_cols + numeric_cols
                    )
                else:  # Histogram
                    x_axis = st.selectbox(
                        "Variable",
                        options=numeric_cols
                    )
            
            with col2:
                if viz_type == "Scatter Plot":
                    y_axis = st.selectbox(
                        "Y-Axis",
                        options=numeric_cols
                    )
                elif viz_type in ["Bar Chart", "Box Plot"]:
                    y_axis = st.selectbox(
                        "Y-Axis",
                        options=numeric_cols
                    )
                else:  # Histogram
                    bins = st.slider(
                        "Number of Bins",
                        min_value=5,
                        max_value=50,
                        value=20
                    )
            
            # Color option
            color_var = st.selectbox(
                "Color By",
                options=["None"] + categorical_cols
            )
            
            # Submit button
            submitted = st.form_submit_button("Generate Visualization")
        
        # Generate visualization if form is submitted
        if submitted:
            st.write(f"#### Custom {viz_type}")
            
            try:
                if viz_type == "Scatter Plot":
                    fig = px.scatter(
                        df,
                        x=x_axis,
                        y=y_axis,
                        color=None if color_var == "None" else color_var,
                        title=f"{y_axis} vs {x_axis}",
                        labels={x_axis: x_axis.title(), y_axis: y_axis.title()}
                    )
                
                elif viz_type == "Bar Chart":
                    if x_axis in categorical_cols:
                        # Group by categorical variable and calculate mean of numeric variable
                        grouped_df = df.groupby(x_axis)[y_axis].mean().reset_index()
                        
                        fig = px.bar(
                            grouped_df,
                            x=x_axis,
                            y=y_axis,
                            color=None if color_var == "None" else (color_var if color_var in grouped_df.columns else None),
                            title=f"Average {y_axis} by {x_axis}",
                            labels={x_axis: x_axis.title(), y_axis: f"Average {y_axis.title()}"}
                        )
                    else:
                        st.warning(f"Bar chart requires a categorical variable for the X-axis. {x_axis} is numeric.")
                        fig = None
                
                elif viz_type == "Box Plot":
                    fig = px.box(
                        df,
                        x=x_axis,
                        y=y_axis,
                        color=None if color_var == "None" else color_var,
                        title=f"Distribution of {y_axis} by {x_axis}",
                        labels={x_axis: x_axis.title(), y_axis: y_axis.title()}
                    )
                
                elif viz_type == "Histogram":
                    fig = px.histogram(
                        df,
                        x=x_axis,
                        color=None if color_var == "None" else color_var,
                        nbins=bins,
                        title=f"Distribution of {x_axis}",
                        labels={x_axis: x_axis.title()}
                    )
                
                # Display the figure if it was created
                if fig:
                    fig.update_layout(
                        height=500,
                        margin=dict(l=20, r=20, t=40, b=20),
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            except Exception as e:
                st.error(f"Error generating visualization: {str(e)}")
                st.info("Try selecting different variables or a different visualization type.")