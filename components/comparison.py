import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any

def create_comparison_metrics(investors_data: pd.DataFrame, selected_investors: List[str]):
    """Create comparison metrics for selected investors"""
    filtered_data = investors_data[investors_data['name'].isin(selected_investors)]
    
    # Create metrics comparison
    metrics = []
    for _, investor in filtered_data.iterrows():
        metrics.append({
            'name': investor['name'],
            'type': investor['type'],
            'location': investor['location'],
            'investments': investor['investments'],
            'stages': len(investor['investment_stages']),
            'investment_stages': investor['investment_stages']
        })
    
    return metrics

def create_radar_chart(investors_data: pd.DataFrame, selected_investors: List[str]):
    """Create radar chart comparing investor attributes"""
    filtered_data = investors_data[investors_data['name'].isin(selected_investors)]
    
    # Prepare data for radar chart
    fig = go.Figure()
    
    # Define dimensions for comparison
    dimensions = ['investments', 'stages', 'geographic_reach']
    
    for _, investor in filtered_data.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[
                investor['investments'],
                len(investor['investment_stages']),
                1  # Placeholder for geographic reach
            ],
            theta=dimensions,
            name=investor['name']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(filtered_data['investments'].max(), 
                            filtered_data['investment_stages'].apply(len).max())]
            )
        ),
        title="Investor Comparison Radar"
    )
    
    return fig

def create_stages_comparison(investors_data: pd.DataFrame, selected_investors: List[str]):
    """Create investment stages comparison chart"""
    filtered_data = investors_data[investors_data['name'].isin(selected_investors)]
    
    # Prepare data for stages comparison
    all_stages = []
    for stages in filtered_data['investment_stages']:
        all_stages.extend(stages)
    unique_stages = sorted(list(set(all_stages)))
    
    # Create stage presence matrix
    stage_data = []
    for _, investor in filtered_data.iterrows():
        investor_stages = investor['investment_stages']
        stage_data.append({
            'Investor': investor['name'],
            **{stage: 1 if stage in investor_stages else 0 for stage in unique_stages}
        })
    
    stage_df = pd.DataFrame(stage_data)
    
    # Create heatmap
    fig = px.imshow(
        stage_df.set_index('Investor')[unique_stages],
        labels=dict(x="Investment Stage", y="Investor", color="Present"),
        title="Investment Stages Comparison",
        color_continuous_scale=["white", "#0066cc"]
    )
    
    return fig

def render_comparison_section(df: pd.DataFrame):
    """
    Render a section for comparing multiple investors
    
    Args:
        df: DataFrame containing investor data
    """
    st.header("Investor Comparison Tool")
    
    if df.empty:
        st.warning("No investor data available for comparison")
        return
    
    # Add description
    st.markdown("""
    Compare multiple investors side by side to identify the best matches for your startup.
    Select investors from your search results to see detailed comparisons of their investment focus,
    portfolio, and other key metrics.
    """)
    
    # Allow user to select investors to compare
    selected_investors = st.multiselect(
        "Select investors to compare (2-5 recommended)",
        options=df['name'].tolist(),
        default=df['name'].head(3).tolist() if len(df) >= 3 else df['name'].tolist(),
        max_selections=5
    )
    
    if not selected_investors or len(selected_investors) < 2:
        st.info("Please select at least 2 investors to compare")
        return
    
    # Filter data for selected investors
    comparison_df = df[df['name'].isin(selected_investors)].copy()
    
    # Create tabs for different comparison views
    tab1, tab2, tab3 = st.tabs(["Overview", "Detailed Comparison", "Side-by-Side Analysis"])
    
    with tab1:
        st.subheader("Comparison Overview")
        
        # Create a summary table
        st.write("#### Key Metrics")
        
        # Prepare data for display
        display_data = []
        
        for _, investor in comparison_df.iterrows():
            investor_data = {
                "Investor": investor['name'],
                "Type": investor['type'] if 'type' in investor else "N/A",
                "Location": investor['location'] if 'location' in investor else "N/A",
                "Investments": investor['investments'] if 'investments' in investor else "N/A"
            }
            
            # Add investment stages if available
            if 'investment_stages' in investor and isinstance(investor['investment_stages'], list):
                investor_data["Investment Stages"] = ", ".join(investor['investment_stages'])
            else:
                investor_data["Investment Stages"] = "N/A"
            
            display_data.append(investor_data)
        
        # Create DataFrame for display
        display_df = pd.DataFrame(display_data)
        st.dataframe(display_df, use_container_width=True)
        
        # Create a radar chart for visual comparison
        st.write("#### Visual Comparison")
        
        # Define metrics for comparison
        metrics = []
        
        if 'investments' in comparison_df.columns:
            # Normalize investments for radar chart
            max_investments = comparison_df['investments'].max()
            comparison_df['investments_normalized'] = comparison_df['investments'] / max_investments if max_investments > 0 else 0
            metrics.append('investments_normalized')
        
        if 'investment_stages' in comparison_df.columns:
            # Add number of investment stages as a metric
            comparison_df['num_stages'] = comparison_df['investment_stages'].apply(
                lambda x: len(x) if isinstance(x, list) else 0
            )
            max_stages = comparison_df['num_stages'].max()
            comparison_df['stages_normalized'] = comparison_df['num_stages'] / max_stages if max_stages > 0 else 0
            metrics.append('stages_normalized')
        
        # Create radar chart if we have metrics
        if metrics:
            # Create figure
            fig = go.Figure()
            
            # Add a trace for each investor
            for _, row in comparison_df.iterrows():
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
    
    with tab2:
        st.subheader("Detailed Comparison")
        
        # Create a detailed comparison table
        comparison_data = []
        
        # Define comparison categories
        categories = [
            "Type",
            "Location",
            "Investment Count",
            "Investment Stages",
            "Website"
        ]
        
        # Create a row for each category
        for category in categories:
            row_data = {"Category": category}
            
            for _, investor in comparison_df.iterrows():
                if category == "Type":
                    value = investor.get('type', "N/A")
                elif category == "Location":
                    value = investor.get('location', "N/A")
                elif category == "Investment Count":
                    value = investor.get('investments', "N/A")
                elif category == "Investment Stages":
                    stages = investor.get('investment_stages', [])
                    value = ", ".join(stages) if isinstance(stages, list) else "N/A"
                elif category == "Website":
                    value = investor.get('profile_url', "N/A")
                else:
                    value = "N/A"
                
                row_data[investor['name']] = value
            
            comparison_data.append(row_data)
        
        # Create DataFrame for display
        comparison_table = pd.DataFrame(comparison_data)
        st.dataframe(comparison_table, use_container_width=True)
        
        # Create bar chart comparing investment counts
        if 'investments' in comparison_df.columns:
            st.write("#### Investment Count Comparison")
            
            fig = px.bar(
                comparison_df,
                x='name',
                y='investments',
                color='name',
                title='Investment Count by Investor',
                labels={'name': 'Investor', 'investments': 'Number of Investments'}
            )
            fig.update_layout(
                height=400,
                margin=dict(l=20, r=20, t=40, b=20),
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Side-by-Side Analysis")
        
        # Create columns for side-by-side comparison
        columns = st.columns(len(selected_investors))
        
        for i, investor_name in enumerate(selected_investors):
            investor_data = comparison_df[comparison_df['name'] == investor_name].iloc[0]
            
            with columns[i]:
                st.write(f"#### {investor_data['name']}")
                
                # Create a card-like display
                st.markdown(f"""
                **Type:** {investor_data.get('type', 'N/A')}  
                **Location:** {investor_data.get('location', 'N/A')}  
                **Investments:** {investor_data.get('investments', 'N/A')}  
                """)
                
                # Show investment stages if available
                if 'investment_stages' in investor_data and isinstance(investor_data['investment_stages'], list):
                    st.write("**Investment Stages:**")
                    for stage in investor_data['investment_stages']:
                        st.markdown(f"- {stage}")
                
                # Show website if available
                if 'profile_url' in investor_data and investor_data['profile_url']:
                    st.markdown(f"**Website:** [{investor_data['profile_url']}]({investor_data['profile_url']})")
                
                # Add a visual indicator of investment activity
                if 'investments' in investor_data:
                    st.write("**Investment Activity:**")
                    
                    # Create a gauge chart
                    max_investments = comparison_df['investments'].max()
                    normalized_value = investor_data['investments'] / max_investments if max_investments > 0 else 0
                    
                    # Use a progress bar as a simple gauge
                    st.progress(normalized_value)
                    
                    # Add a label
                    if normalized_value < 0.33:
                        st.caption("Low relative to comparison group")
                    elif normalized_value < 0.67:
                        st.caption("Medium relative to comparison group")
                    else:
                        st.caption("High relative to comparison group")
    
    # Add a section for recommendations
    st.subheader("Comparison Insights")
    
    # Generate some simple insights
    insights = []
    
    if 'investments' in comparison_df.columns:
        max_investor = comparison_df.loc[comparison_df['investments'].idxmax()]
        insights.append(f"- **{max_investor['name']}** has the highest number of investments ({max_investor['investments']}).")
    
    if 'investment_stages' in comparison_df.columns:
        # Find common investment stages
        common_stages = set()
        first = True
        
        for _, investor in comparison_df.iterrows():
            stages = investor.get('investment_stages', [])
            if isinstance(stages, list):
                if first:
                    common_stages = set(stages)
                    first = False
                else:
                    common_stages = common_stages.intersection(set(stages))
        
        if common_stages:
            insights.append(f"- All selected investors focus on the following stages: {', '.join(common_stages)}.")
        else:
            insights.append("- The selected investors have no common investment stages.")
    
    if 'location' in comparison_df.columns:
        locations = comparison_df['location'].unique()
        if len(locations) == 1:
            insights.append(f"- All selected investors are located in {locations[0]}.")
        else:
            insights.append(f"- The selected investors are spread across {len(locations)} different locations.")
    
    # Display insights
    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("Not enough data to generate insights for the selected investors.")
