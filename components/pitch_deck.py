import streamlit as st
import pandas as pd
import openai
import os
from typing import List, Dict
import json
from datetime import datetime

class PitchDeckGenerator:
    """Generate AI-powered pitch deck content and suggestions"""
    
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = self.openai_api_key

    def generate_content_suggestions(self, investor_data: pd.DataFrame, focus_areas: List[str]) -> Dict:
        """Generate content suggestions based on investor data"""
        try:
            # Prepare context for AI
            investor_summary = {
                'types': investor_data['type'].value_counts().to_dict(),
                'locations': investor_data['location'].value_counts().head(5).to_dict(),
                'stages': list(set([stage for stages in investor_data['investment_stages'] for stage in stages])),
                'focus_areas': focus_areas
            }

            # Create prompt for OpenAI
            prompt = f"""
            Generate pitch deck content suggestions based on this investor data:
            {json.dumps(investor_summary, indent=2)}

            Please provide:
            1. Executive Summary (2-3 sentences)
            2. Key Value Propositions (3 points)
            3. Market Opportunity (2-3 points)
            4. Competitive Advantages (2-3 points)
            5. Investment Ask (1-2 sentences)

            Format as JSON with these keys: 
            executive_summary, value_props, market_opportunity, competitive_advantages, investment_ask
            """

            # Get AI suggestions
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert pitch deck consultant."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse and return suggestions
            suggestions = json.loads(response.choices[0].message.content)
            return suggestions

        except Exception as e:
            st.error(f"Error generating content suggestions: {str(e)}")
            return None

    def generate_design_suggestions(self, content: Dict) -> Dict:
        """Generate design suggestions for the pitch deck"""
        try:
            prompt = f"""
            Based on this pitch deck content:
            {json.dumps(content, indent=2)}

            Provide design suggestions for:
            1. Color scheme (3 colors)
            2. Layout recommendations
            3. Visual elements
            4. Typography pairing

            Format as JSON with these keys:
            colors, layout, visuals, typography
            """

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert presentation designer."},
                    {"role": "user", "content": prompt}
                ]
            )

            design_suggestions = json.loads(response.choices[0].message.content)
            return design_suggestions

        except Exception as e:
            st.error(f"Error generating design suggestions: {str(e)}")
            return None

def render_pitch_deck_generator(df: pd.DataFrame):
    """Render the pitch deck generator interface"""
    st.header("AI-Powered Pitch Deck Generator")
    
    # Initialize generator
    generator = PitchDeckGenerator()

    # Add description
    st.markdown("""
    Generate a customized investor pitch deck with AI-powered content and design suggestions.
    The suggestions are based on your selected investors and focus areas.
    """)

    # Get user inputs
    with st.form("pitch_deck_form"):
        # Focus areas selection
        focus_areas = st.multiselect(
            "Select Your Focus Areas",
            ["B2B SaaS", "Enterprise Software", "Consumer Tech", "AI/ML", 
             "Healthcare Tech", "FinTech", "E-commerce", "Mobile Apps",
             "Clean Tech", "Hardware", "Marketplace", "Developer Tools"],
            max_selections=3,
            help="Choose up to 3 main focus areas for your startup"
        )

        # Funding stage
        funding_stage = st.selectbox(
            "Current Funding Stage",
            ["Pre-seed", "Seed", "Series A", "Series B", "Series C+"]
        )

        # Investment amount
        investment_amount = st.number_input(
            "Investment Amount ($)",
            min_value=100000,
            max_value=100000000,
            value=1000000,
            step=100000,
            format="%d",
            help="Enter the amount you're looking to raise"
        )

        # Generate button
        generate_button = st.form_submit_button("Generate Pitch Deck", type="primary")

    if generate_button and focus_areas:
        with st.spinner("Generating pitch deck content..."):
            # Generate content suggestions
            content = generator.generate_content_suggestions(df, focus_areas)
            
            if content:
                # Generate design suggestions
                design = generator.generate_design_suggestions(content)
                
                if design:
                    # Display suggestions
                    st.success("✨ Pitch deck suggestions generated successfully!")
                    
                    # Content suggestions
                    st.subheader("Content Suggestions")
                    
                    st.write("##### Executive Summary")
                    st.write(content["executive_summary"])
                    
                    st.write("##### Key Value Propositions")
                    for prop in content["value_props"]:
                        st.markdown(f"• {prop}")
                    
                    st.write("##### Market Opportunity")
                    for point in content["market_opportunity"]:
                        st.markdown(f"• {point}")
                    
                    st.write("##### Competitive Advantages")
                    for adv in content["competitive_advantages"]:
                        st.markdown(f"• {adv}")
                    
                    st.write("##### Investment Ask")
                    st.write(content["investment_ask"])
                    
                    # Design suggestions
                    st.subheader("Design Suggestions")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("##### Color Scheme")
                        for color in design["colors"]:
                            st.markdown(f"• {color}")
                        
                        st.write("##### Typography")
                        st.write(design["typography"])
                    
                    with col2:
                        st.write("##### Layout Recommendations")
                        st.write(design["layout"])
                        
                        st.write("##### Visual Elements")
                        st.write(design["visuals"])
                    
                    # Export options
                    st.subheader("Export Options")
                    st.info("""
                    💡 These suggestions can be used to create your pitch deck in:
                    - PowerPoint
                    - Keynote
                    - Google Slides
                    
                    Copy the content and follow the design suggestions in your preferred tool.
                    """)
    else:
        if generate_button:
            st.warning("Please select at least one focus area.")
