import streamlit as st
import pandas as pd
import openai
import os
from typing import List, Dict
import json
from datetime import datetime
import random

class PitchDeckGenerator:
    """Generate AI-powered pitch deck content and suggestions"""

    def __init__(self):
        """Initialize the pitch deck generator with OpenAI API key"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.api_available = False
        
        if self.openai_api_key:
            try:
                self.client = openai.OpenAI(api_key=self.openai_api_key)
                self.api_available = True
            except Exception as e:
                st.warning(f"Error initializing OpenAI client: {str(e)}")
                st.warning("Using mock pitch deck generator instead.")
        else:
            st.warning("OpenAI API key not set. Pitch deck generator will use mock data.")

    def _generate_mock_content(self, focus_areas: List[str]) -> Dict:
        """Generate mock content when API is not available"""
        # Sample executive summaries for different focus areas
        exec_summaries = {
            "B2B SaaS": "Our B2B SaaS platform streamlines operations for enterprise clients, reducing costs by 35% and improving efficiency. We're targeting the $50B enterprise software market with our innovative solution.",
            "AI/ML": "Our AI-powered platform automates complex decision processes, saving companies 20+ hours per week. With proprietary algorithms and a growing dataset, we're positioned to disrupt the $30B business intelligence market.",
            "FinTech": "Our fintech solution democratizes access to financial services for underserved markets. With 10,000+ early users and growing transaction volume, we're ready to scale across new markets.",
            "Healthcare Tech": "Our healthcare platform connects patients with specialists, reducing wait times by 60%. With HIPAA compliance and partnerships with major providers, we're positioned for rapid growth.",
            "E-commerce": "Our e-commerce platform enables small businesses to compete with major retailers through AI-powered inventory and marketing tools. We've grown 200% YoY with minimal marketing spend."
        }
        
        # Default summary for any focus area not in our predefined list
        default_summary = "Our innovative platform addresses key pain points in the market, with early traction showing strong product-market fit. We're positioned to disrupt a growing market with our unique approach and technology."
        
        # Select a relevant summary or use default
        if focus_areas and any(area in exec_summaries for area in focus_areas):
            for area in focus_areas:
                if area in exec_summaries:
                    executive_summary = exec_summaries[area]
                    break
        else:
            executive_summary = default_summary
            
        return {
            "executive_summary": executive_summary,
            "value_props": [
                "Reduces operational costs by 30-40% through automation and AI-powered optimization",
                "Increases team productivity by eliminating manual processes and streamlining workflows",
                "Provides actionable insights through comprehensive analytics and reporting features"
            ],
            "market_opportunity": [
                f"The global {'/'.join(focus_areas[:2] if focus_areas else ['SaaS', 'Tech'])} market is projected to reach $200B by 2025, growing at 15% annually",
                "Enterprise clients are increasingly seeking integrated solutions that reduce vendor complexity",
                "Regulatory changes are creating new opportunities for compliant, secure solutions"
            ],
            "competitive_advantages": [
                "Proprietary technology that delivers 2x the performance of leading competitors",
                "Strategic partnerships with key industry players providing access to enterprise clients",
                "Experienced founding team with previous successful exits in the industry"
            ],
            "investment_ask": f"We're raising ${random.randint(1, 5)}M to accelerate product development, expand our sales team, and enter new markets in the next 18 months."
        }

    def _generate_mock_design(self) -> Dict:
        """Generate mock design suggestions when API is not available"""
        color_schemes = [
            ["#2C3E50 (Deep Blue), #E74C3C (Coral Red), #ECF0F1 (Light Gray)"],
            ["#27AE60 (Emerald Green), #3498DB (Bright Blue), #F1C40F (Sunflower Yellow)"],
            ["#8E44AD (Purple), #2ECC71 (Green), #F39C12 (Orange)"],
            ["#1A5276 (Navy Blue), #D35400 (Burnt Orange), #F4F6F7 (Off-White)"],
            ["#34495E (Charcoal), #16A085 (Teal), #F5B041 (Golden)"]
        ]
        
        typography_options = [
            "Heading: Montserrat Bold, Body: Open Sans Regular - Clean and modern combination",
            "Heading: Playfair Display, Body: Roboto - Professional contrast between serif and sans-serif",
            "Heading: Poppins Bold, Body: Lato - Contemporary and highly readable",
            "Heading: Oswald, Body: Source Sans Pro - Strong visual hierarchy with excellent readability",
            "Heading: Raleway, Body: Merriweather - Elegant combination with excellent contrast"
        ]
        
        layout_options = [
            "Use a consistent grid layout with clear section dividers. Maintain ample white space and align all elements to a 12-column grid for professional appearance.",
            "Implement a modular slide structure with consistent positioning of titles and content. Use the top-left rule for important information placement.",
            "Create visual consistency with a fixed position for headers and footers. Use the rule of thirds for placing key visual elements and text blocks.",
            "Utilize a Z-pattern layout for slides with multiple elements, guiding the viewer's eye naturally through the content in order of importance.",
            "Employ a minimalist approach with asymmetrical balance. Limit each slide to one main point with supporting visuals aligned to a consistent baseline."
        ]
        
        visual_options = [
            "Use simple data visualizations (bar charts, line graphs) to illustrate market trends. Include product screenshots with annotations highlighting key features.",
            "Incorporate custom icons for key concepts and value propositions. Use high-quality stock photography with a consistent filter applied for brand cohesion.",
            "Create infographics to visualize complex processes and workflows. Use subtle animations to reveal information progressively during presentation.",
            "Implement before/after comparisons to demonstrate value. Use isometric illustrations for product features and architecture diagrams.",
            "Utilize customer logos and testimonial highlights. Create custom diagrams showing market positioning relative to competitors."
        ]
        
        return {
            "colors": random.choice(color_schemes),
            "typography": random.choice(typography_options),
            "layout": random.choice(layout_options),
            "visuals": random.choice(visual_options)
        }

    def generate_content_suggestions(self, investor_data: pd.DataFrame, focus_areas: List[str]) -> Dict:
        """Generate content suggestions based on investor data"""
        try:
            # Use mock data if API is not available
            if not self.api_available:
                return self._generate_mock_content(focus_areas)
                
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

            # Get AI suggestions using the new API format
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert pitch deck consultant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            # Parse and return suggestions
            try:
                suggestions = json.loads(response.choices[0].message.content)
                return suggestions
            except (json.JSONDecodeError, AttributeError, IndexError) as e:
                st.error(f"Error parsing content suggestions: {str(e)}")
                return self._generate_mock_content(focus_areas)

        except Exception as e:
            st.error(f"Error generating content suggestions: {str(e)}")
            return self._generate_mock_content(focus_areas)

    def generate_design_suggestions(self, content: Dict) -> Dict:
        """Generate design suggestions for the pitch deck"""
        try:
            # Use mock data if API is not available
            if not self.api_available:
                return self._generate_mock_design()
                
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

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert presentation designer."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            try:
                design_suggestions = json.loads(response.choices[0].message.content)
                return design_suggestions
            except (json.JSONDecodeError, AttributeError, IndexError) as e:
                st.error(f"Error parsing design suggestions: {str(e)}")
                return self._generate_mock_design()

        except Exception as e:
            st.error(f"Error generating design suggestions: {str(e)}")
            return self._generate_mock_design()

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