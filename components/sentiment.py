import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import trafilatura
import openai
import os
import json
from typing import List, Dict
import time

class MarketSentimentTracker:
    """Track and analyze real-time market sentiment"""

    def __init__(self):
        """Initialize the sentiment tracker"""
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.sentiment_cache = {}
        self.last_update = None

    def fetch_market_news(self, sources: List[str]) -> List[Dict]:
        """Fetch recent market news from specified sources"""
        news_items = []

        # Example sources with venture capital and startup news
        news_sources = {
            "techcrunch": "https://techcrunch.com/venture/",
            "venturebeat": "https://venturebeat.com/venture/",
            "reuters_vc": "https://www.reuters.com/markets/venture-capital/"
        }

        for source_name, url in news_sources.items():
            if source_name in sources:
                try:
                    downloaded = trafilatura.fetch_url(url)
                    if downloaded:
                        text = trafilatura.extract(downloaded)
                        if text:
                            news_items.append({
                                "source": source_name,
                                "content": text,
                                "url": url,
                                "timestamp": datetime.now()
                            })
                except Exception as e:
                    st.error(f"Error fetching news from {source_name}: {str(e)}")

        return news_items

    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using OpenAI API"""
        try:
            prompt = f"""
            Analyze the market sentiment in this text, focusing on venture capital and startup investment trends:
            {text[:1000]}...

            Provide a JSON response with:
            1. Sentiment score (-1 to 1)
            2. Key trends identified
            3. Market confidence level (0-100)
            4. Primary sectors mentioned
            5. Notable concerns or opportunities

            Format as JSON with these keys:
            sentiment_score, trends, confidence_level, sectors, insights
            """

            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a market sentiment analysis expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )

            return json.loads(response.choices[0].message.content)

        except Exception as e:
            st.error(f"Error analyzing sentiment: {str(e)}")
            return None

    def create_sentiment_timeline(self, sentiment_data: List[Dict]) -> go.Figure:
        """Create sentiment timeline visualization"""
        dates = []
        scores = []
        confidence = []

        for data in sentiment_data:
            dates.append(data.get('timestamp'))
            scores.append(data.get('sentiment_score'))
            confidence.append(data.get('confidence_level'))

        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add sentiment score line
        fig.add_trace(
            go.Scatter(x=dates, y=scores, name="Sentiment Score",
                      line=dict(color="#1f77b4")),
            secondary_y=False
        )

        # Add confidence level line
        fig.add_trace(
            go.Scatter(x=dates, y=confidence, name="Confidence Level",
                      line=dict(color="#ff7f0e")),
            secondary_y=True
        )

        # Update layout
        fig.update_layout(
            title="Market Sentiment Timeline",
            xaxis_title="Time",
            yaxis_title="Sentiment Score (-1 to 1)",
            yaxis2_title="Confidence Level (0-100)",
            height=400,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        return fig

    def create_sector_sentiment(self, sentiment_data: List[Dict]) -> go.Figure:
        """Create sector-wise sentiment visualization"""
        sectors = {}
        for data in sentiment_data:
            for sector in data.get('sectors', []):
                if sector not in sectors:
                    sectors[sector] = []
                sectors[sector].append(data.get('sentiment_score', 0))

        sector_avg = {
            sector: sum(scores) / len(scores)
            for sector, scores in sectors.items()
        }

        fig = go.Figure(data=go.Bar(
            x=list(sector_avg.keys()),
            y=list(sector_avg.values()),
            marker_color=px.colors.qualitative.Set3
        ))

        fig.update_layout(
            title="Sector-wise Sentiment Analysis",
            xaxis_title="Sectors",
            yaxis_title="Average Sentiment Score",
            yaxis=dict(range=[-1, 1]),
            height=400
        )

        return fig

def render_sentiment_tracker():
    """Render the sentiment tracking interface"""
    st.header("Real-time Market Sentiment Tracker")

    # Initialize tracker
    tracker = MarketSentimentTracker()

    # Add description
    st.markdown("""
    Track real-time market sentiment across venture capital and startup ecosystems.
    Data is sourced from major financial news outlets and analyzed using AI.
    """)

    # Source selection
    selected_sources = st.multiselect(
        "Select News Sources",
        ["techcrunch", "venturebeat", "reuters_vc"],
        default=["techcrunch"],
        help="Choose news sources to track"
    )

    # Update frequency
    update_frequency = st.select_slider(
        "Update Frequency",
        options=[1, 5, 10, 15, 30, 60],
        value=5,
        help="Select how often to update sentiment analysis (in minutes)"
    )

    # Initialize or get session state
    if 'sentiment_data' not in st.session_state:
        st.session_state.sentiment_data = []
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None

    # Check if update is needed
    current_time = datetime.now()
    should_update = (
        st.session_state.last_update is None or
        (current_time - st.session_state.last_update).total_seconds() > update_frequency * 60
    )

    if should_update and selected_sources:
        with st.spinner("Fetching and analyzing market sentiment..."):
            # Fetch and analyze news
            news_items = tracker.fetch_market_news(selected_sources)

            for item in news_items:
                sentiment = tracker.analyze_sentiment(item.get('content', ''))
                if sentiment:
                    sentiment['timestamp'] = item.get('timestamp')
                    st.session_state.sentiment_data.append(sentiment)

            st.session_state.last_update = current_time

    # Display sentiment visualizations
    if st.session_state.sentiment_data:
        # Current sentiment metrics
        latest = st.session_state.sentiment_data[-1]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Current Sentiment",
                f"{latest.get('sentiment_score', 0):.2f}",
                delta=f"{latest.get('sentiment_score', 0) - st.session_state.sentiment_data[-2].get('sentiment_score', 0):.2f}" 
                if len(st.session_state.sentiment_data) > 1 else None
            )
        with col2:
            st.metric("Market Confidence", f"{latest.get('confidence_level', 0)}%")
        with col3:
            st.metric("Active Sectors", len(latest.get('sectors', [])))

        # Show sentiment timeline
        st.plotly_chart(
            tracker.create_sentiment_timeline(st.session_state.sentiment_data),
            use_container_width=True
        )

        # Show sector sentiment
        st.plotly_chart(
            tracker.create_sector_sentiment(st.session_state.sentiment_data),
            use_container_width=True
        )

        # Display key insights
        st.subheader("Current Market Insights")
        for insight in latest.get('insights', []):
            st.markdown(f"• {insight}")

        # Show trending topics
        st.subheader("Key Market Trends")
        for trend in latest.get('trends', []):
            st.markdown(f"• {trend}")

    else:
        st.info("Waiting for sentiment data... Please allow a few minutes for initial analysis.")

    # Add auto-refresh
    if st.checkbox("Enable Auto-refresh", value=True):
        time.sleep(1)  # Prevent too frequent refreshes
        st.experimental_rerun()