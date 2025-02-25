import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict
import json

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
    """Render the investor comparison section"""
    st.header("Investor Comparison Tool")
    
    # Add description
    st.markdown("""
    Compare selected investors side by side to analyze their:
    - Investment patterns
    - Investment stages
    - Geographic presence
    - Key metrics
    """)
    
    # Investor selection
    selected_investors = st.multiselect(
        "Select Investors to Compare (2-4 recommended)",
        options=df['name'].unique(),
        max_selections=4
    )
    
    if len(selected_investors) < 2:
        st.warning("Please select at least 2 investors to compare")
        return
    
    # Create metrics comparison
    metrics = create_comparison_metrics(df, selected_investors)
    
    # Display metrics in columns
    st.subheader("Key Metrics Comparison")
    cols = st.columns(len(selected_investors))
    
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(f"### {metric['name']}")
            st.metric("Type", metric['type'])
            st.metric("Location", metric['location'])
            st.metric("Total Investments", metric['investments'])
            st.metric("Investment Stages", metric['stages'])
            
            # Display investment stages
            st.write("Investment Stages:")
            for stage in metric['investment_stages']:
                st.markdown(f"- {stage}")
    
    # Add spacing
    st.markdown("---")
    
    # Create and display radar chart
    st.subheader("Investment Profile Comparison")
    st.plotly_chart(
        create_radar_chart(df, selected_investors),
        use_container_width=True
    )
    
    # Create and display stages comparison
    st.subheader("Investment Stages Analysis")
    st.plotly_chart(
        create_stages_comparison(df, selected_investors),
        use_container_width=True
    )
    
    # Add visual comparison guide
    st.markdown("""
    ### Understanding the Comparison
    
    #### Radar Chart
    - **Investments**: Total number of investments made
    - **Stages**: Number of investment stages covered
    - **Geographic Reach**: Geographic coverage of investments
    
    #### Stages Heatmap
    - Dark blue indicates the investor is active in that stage
    - White indicates no activity in that stage
    """)
