import logging
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

# Try to import scikit-learn components, but provide fallbacks if not available
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logging.warning("scikit-learn modules not available. Using simplified text matching.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MatchingAlgorithm")

class InvestorMatchingAlgorithm:
    """
    Algorithm to match startups with the most suitable investors based on various criteria
    """
    
    def __init__(self):
        """Initialize the investor matching algorithm"""
        self.logger = logging.getLogger("MatchingAlgorithm")
        
        # Initialize vectorizer if scikit-learn is available
        if SKLEARN_AVAILABLE:
            try:
                self.vectorizer = TfidfVectorizer(stop_words='english')
                self.logger.info("TF-IDF vectorizer initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize TF-IDF vectorizer: {str(e)}")
                self.vectorizer = None
        else:
            self.vectorizer = None
            self.logger.warning("TF-IDF vectorizer not available - using simplified text matching")
            
        self.logger.info("InvestorMatchingAlgorithm initialized")
        
    def match_investors(self, 
                        investors_df: pd.DataFrame, 
                        startup_profile: Dict[str, Any],
                        top_n: int = 10) -> pd.DataFrame:
        """
        Match a startup profile with the most suitable investors
        
        Args:
            investors_df: DataFrame containing investor data
            startup_profile: Dictionary containing startup information
            top_n: Number of top matches to return
            
        Returns:
            DataFrame with matched investors and match scores
        """
        if investors_df.empty:
            self.logger.warning("No investors provided for matching")
            return pd.DataFrame()
            
        try:
            # Calculate match scores for different criteria
            stage_scores = self._calculate_stage_match(investors_df, startup_profile)
            sector_scores = self._calculate_sector_match(investors_df, startup_profile)
            location_scores = self._calculate_location_match(investors_df, startup_profile)
            investment_size_scores = self._calculate_investment_size_match(investors_df, startup_profile)
            
            # Calculate overall match score (weighted average)
            weights = {
                'stage': 0.35,  # Investment stage is very important
                'sector': 0.30,  # Sector focus is important
                'location': 0.20,  # Location preference has medium importance
                'investment_size': 0.15  # Investment size has lower importance
            }
            
            # Combine scores with weights
            overall_scores = (
                stage_scores * weights['stage'] +
                sector_scores * weights['sector'] +
                location_scores * weights['location'] +
                investment_size_scores * weights['investment_size']
            )
            
            # Add match scores to the DataFrame
            result_df = investors_df.copy()
            result_df['match_score'] = overall_scores
            result_df['stage_match'] = stage_scores
            result_df['sector_match'] = sector_scores
            result_df['location_match'] = location_scores
            result_df['investment_size_match'] = investment_size_scores
            
            # Sort by match score and return top N
            result_df = result_df.sort_values('match_score', ascending=False).head(top_n)
            
            # Convert match scores to percentages for better readability
            result_df['match_percentage'] = (result_df['match_score'] * 100).round(1)
            result_df['stage_match_percentage'] = (result_df['stage_match'] * 100).round(1)
            result_df['sector_match_percentage'] = (result_df['sector_match'] * 100).round(1)
            result_df['location_match_percentage'] = (result_df['location_match'] * 100).round(1)
            result_df['investment_size_match_percentage'] = (result_df['investment_size_match'] * 100).round(1)
            
            return result_df
            
        except Exception as e:
            self.logger.error(f"Error in matching algorithm: {str(e)}")
            return pd.DataFrame()
    
    def _calculate_stage_match(self, investors_df: pd.DataFrame, startup_profile: Dict[str, Any]) -> np.ndarray:
        """Calculate match score based on investment stage"""
        startup_stage = startup_profile.get('stage', '')
        
        # Map startup stage to standardized stages
        stage_mapping = {
            'idea': ['Pre-Seed'],
            'prototype': ['Pre-Seed', 'Seed'],
            'mvp': ['Pre-Seed', 'Seed'],
            'pre-seed': ['Pre-Seed', 'Seed'],
            'seed': ['Seed', 'Pre-Seed'],
            'early revenue': ['Seed', 'Series A'],
            'series a': ['Series A', 'Seed'],
            'growth': ['Series A', 'Series B'],
            'series b': ['Series B', 'Series A', 'Series C'],
            'series c': ['Series C', 'Series B', 'Growth'],
            'expansion': ['Growth', 'Series C', 'Late Stage'],
            'late stage': ['Late Stage', 'Growth']
        }
        
        # Get standardized stages for the startup
        startup_standardized_stages = []
        for key, stages in stage_mapping.items():
            if key in startup_stage.lower():
                startup_standardized_stages.extend(stages)
                
        if not startup_standardized_stages:
            # Default to all stages if no match found
            startup_standardized_stages = ['Pre-Seed', 'Seed', 'Series A', 'Series B', 'Series C', 'Growth', 'Late Stage']
        
        # Calculate match scores
        scores = []
        for _, investor in investors_df.iterrows():
            investor_stages = investor.get('investment_stages', [])
            
            if not investor_stages:
                scores.append(0.5)  # Neutral score if no stages specified
                continue
                
            # Calculate overlap between startup stages and investor stages
            matches = sum(1 for stage in startup_standardized_stages if stage in investor_stages)
            total = len(startup_standardized_stages)
            
            # Calculate score based on overlap
            score = matches / total if total > 0 else 0.5
            scores.append(score)
            
        return np.array(scores)
    
    def _calculate_sector_match(self, investors_df: pd.DataFrame, startup_profile: Dict[str, Any]) -> np.ndarray:
        """Calculate match score based on sector/industry"""
        startup_sector = startup_profile.get('sector', '')
        startup_description = startup_profile.get('description', '')
        
        # Combine sector and description for better matching
        startup_text = f"{startup_sector} {startup_description}"
        
        # Extract key sectors from startup profile
        common_sectors = [
            "Technology", "Healthcare", "Finance", "Consumer", "Enterprise", "AI/ML", 
            "Blockchain", "SaaS", "E-commerce", "Mobile", "IoT", "Clean Tech",
            "B2B", "B2C", "Hardware", "Software", "Deep Tech"
        ]
        
        startup_sectors = []
        for sector in common_sectors:
            if sector.lower() in startup_text.lower():
                startup_sectors.append(sector)
                
        if not startup_sectors:
            # Extract words that might represent sectors
            words = set(w.lower() for w in startup_text.split() if len(w) > 3)
            startup_sectors = list(words)
        
        # Calculate match scores using text similarity
        scores = []
        for _, investor in investors_df.iterrows():
            # Get investor focus areas or sectors
            investor_sectors = []
            
            if 'focus_areas' in investor and investor['focus_areas']:
                investor_sectors.extend(investor['focus_areas'])
                
            # Convert to text for comparison
            investor_text = " ".join(investor_sectors)
            
            if not investor_text:
                scores.append(0.5)  # Neutral score if no sectors specified
                continue
            
            # Calculate text similarity
            try:
                if SKLEARN_AVAILABLE and self.vectorizer:
                    # Use scikit-learn for TF-IDF similarity
                    corpus = [" ".join(startup_sectors), investor_text]
                    tfidf_matrix = self.vectorizer.fit_transform(corpus)
                    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                else:
                    # Fallback to simple word overlap similarity
                    similarity = self._calculate_simple_text_similarity(startup_sectors, investor_text)
                    
                scores.append(max(0, min(1, similarity)))  # Ensure score is between 0 and 1
            except Exception as e:
                self.logger.warning(f"Error calculating sector similarity: {str(e)}")
                scores.append(0.5)  # Fallback to neutral score
        
        return np.array(scores)
    
    def _calculate_simple_text_similarity(self, startup_sectors: List[str], investor_text: str) -> float:
        """Calculate simple text similarity based on word overlap when scikit-learn is not available"""
        if not startup_sectors or not investor_text:
            return 0.5
            
        # Convert everything to lowercase
        startup_words = set(" ".join(startup_sectors).lower().split())
        investor_words = set(investor_text.lower().split())
        
        # Calculate Jaccard similarity (intersection over union)
        intersection = len(startup_words.intersection(investor_words))
        union = len(startup_words.union(investor_words))
        
        if union == 0:
            return 0.5
            
        return intersection / union
    
    def _calculate_location_match(self, investors_df: pd.DataFrame, startup_profile: Dict[str, Any]) -> np.ndarray:
        """Calculate match score based on location preference"""
        startup_location = startup_profile.get('location', '').lower()
        
        # Extract country and region information
        country_mapping = {
            'us': ['united states', 'usa', 'america'],
            'uk': ['united kingdom', 'britain', 'england'],
            'canada': ['canada'],
            'europe': ['europe', 'eu', 'european union'],
            'asia': ['asia', 'asian'],
            'australia': ['australia', 'oceania'],
            'africa': ['africa', 'african'],
            'south america': ['south america', 'latin america']
        }
        
        startup_country = None
        for country, aliases in country_mapping.items():
            if any(alias in startup_location for alias in aliases):
                startup_country = country
                break
        
        # Calculate match scores
        scores = []
        for _, investor in investors_df.iterrows():
            investor_location = investor.get('location', '').lower()
            
            # Exact city match is best
            if startup_location in investor_location or investor_location in startup_location:
                scores.append(1.0)
                continue
                
            # Country/region match is good
            if startup_country:
                if any(alias in investor_location for alias in country_mapping.get(startup_country, [])):
                    scores.append(0.8)
                    continue
            
            # Some investors are global or have no strong location preference
            if 'global' in investor_location or not investor_location:
                scores.append(0.6)
                continue
                
            # Default to moderate score
            scores.append(0.4)
        
        return np.array(scores)
    
    def _calculate_investment_size_match(self, investors_df: pd.DataFrame, startup_profile: Dict[str, Any]) -> np.ndarray:
        """Calculate match score based on investment size"""
        startup_funding_needed = startup_profile.get('funding_needed', '').lower()
        
        # Map funding needed to a numerical range
        funding_ranges = {
            '< $100k': (0, 100000),
            '$100k-$500k': (100000, 500000),
            '$500k-$1m': (500000, 1000000),
            '$1m-$5m': (1000000, 5000000),
            '$5m-$10m': (5000000, 10000000),
            '> $10m': (10000000, float('inf'))
        }
        
        # Determine startup's funding range
        startup_min, startup_max = 0, float('inf')
        for range_str, (min_val, max_val) in funding_ranges.items():
            if range_str.lower() in startup_funding_needed:
                startup_min, startup_max = min_val, max_val
                break
        
        # Calculate match scores
        scores = []
        for _, investor in investors_df.iterrows():
            investor_size = investor.get('investment_size', '').lower()
            
            # If no investment size specified, use a neutral score
            if not investor_size:
                scores.append(0.5)
                continue
            
            # Determine investor's typical investment range
            investor_min, investor_max = 0, float('inf')
            for range_str, (min_val, max_val) in funding_ranges.items():
                if range_str.lower() in investor_size:
                    investor_min, investor_max = min_val, max_val
                    break
            
            # Calculate overlap between ranges
            overlap_min = max(startup_min, investor_min)
            overlap_max = min(startup_max, investor_max)
            
            if overlap_max > overlap_min:
                # There is an overlap
                overlap_size = overlap_max - overlap_min
                startup_range_size = startup_max - startup_min if startup_max != float('inf') else investor_max - investor_min
                
                if startup_range_size == float('inf'):
                    scores.append(0.7)  # Good match if startup range is unlimited
                else:
                    match_percentage = overlap_size / startup_range_size
                    scores.append(min(1.0, match_percentage))
            else:
                # No overlap
                scores.append(0.2)  # Poor match
        
        return np.array(scores)
    
    def explain_match(self, investor: Dict[str, Any], startup_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate an explanation for why an investor matches a startup
        
        Args:
            investor: Dictionary containing investor information
            startup_profile: Dictionary containing startup information
            
        Returns:
            Dictionary with explanation details
        """
        explanation = {
            'overall_match': f"{investor.get('match_percentage', 0)}%",
            'stage_match': {
                'score': f"{investor.get('stage_match_percentage', 0)}%",
                'details': self._explain_stage_match(investor, startup_profile)
            },
            'sector_match': {
                'score': f"{investor.get('sector_match_percentage', 0)}%",
                'details': self._explain_sector_match(investor, startup_profile)
            },
            'location_match': {
                'score': f"{investor.get('location_match_percentage', 0)}%",
                'details': self._explain_location_match(investor, startup_profile)
            },
            'investment_size_match': {
                'score': f"{investor.get('investment_size_match_percentage', 0)}%",
                'details': self._explain_investment_size_match(investor, startup_profile)
            },
            'summary': self._generate_match_summary(investor, startup_profile)
        }
        
        return explanation
    
    def _explain_stage_match(self, investor: Dict[str, Any], startup_profile: Dict[str, Any]) -> str:
        """Generate explanation for stage match"""
        startup_stage = startup_profile.get('stage', 'Not specified')
        investor_stages = investor.get('investment_stages', [])
        
        if not investor_stages:
            return "This investor doesn't specify preferred investment stages."
            
        if startup_stage.lower() in [s.lower() for s in investor_stages]:
            return f"This investor specifically targets {startup_stage} stage companies."
        elif any(stage.lower() in startup_stage.lower() for stage in investor_stages):
            return f"This investor's preferred stages ({', '.join(investor_stages)}) align with your {startup_stage} stage."
        else:
            return f"This investor typically invests in {', '.join(investor_stages)} stages, which may not perfectly align with your {startup_stage} stage."
    
    def _explain_sector_match(self, investor: Dict[str, Any], startup_profile: Dict[str, Any]) -> str:
        """Generate explanation for sector match"""
        startup_sector = startup_profile.get('sector', 'Not specified')
        investor_sectors = investor.get('focus_areas', [])
        
        if not investor_sectors:
            return "This investor doesn't specify sector preferences."
            
        matching_sectors = []
        for sector in investor_sectors:
            if sector.lower() in startup_sector.lower():
                matching_sectors.append(sector)
                
        if matching_sectors:
            return f"This investor focuses on {', '.join(matching_sectors)}, which matches your sector."
        else:
            return f"This investor typically focuses on {', '.join(investor_sectors)}, which may have some overlap with your {startup_sector} sector."
    
    def _explain_location_match(self, investor: Dict[str, Any], startup_profile: Dict[str, Any]) -> str:
        """Generate explanation for location match"""
        startup_location = startup_profile.get('location', 'Not specified')
        investor_location = investor.get('location', 'Not specified')
        
        if 'global' in investor_location.lower():
            return "This investor has a global investment focus and is not limited by geography."
            
        if startup_location.lower() in investor_location.lower():
            return f"This investor is based in {investor_location}, which includes your location ({startup_location})."
        elif any(word in investor_location.lower() for word in startup_location.lower().split()):
            return f"This investor's location ({investor_location}) has some overlap with your location ({startup_location})."
        else:
            return f"This investor is based in {investor_location}, which is different from your location ({startup_location})."
    
    def _explain_investment_size_match(self, investor: Dict[str, Any], startup_profile: Dict[str, Any]) -> str:
        """Generate explanation for investment size match"""
        startup_funding = startup_profile.get('funding_needed', 'Not specified')
        investor_size = investor.get('investment_size', 'Not specified')
        
        if not investor_size or investor_size == 'Not specified':
            return "This investor doesn't specify typical investment sizes."
            
        # Simple text-based comparison
        if startup_funding.lower() in investor_size.lower() or investor_size.lower() in startup_funding.lower():
            return f"This investor's typical investment size ({investor_size}) aligns well with your funding needs ({startup_funding})."
        else:
            return f"This investor typically invests {investor_size}, which may be different from your funding needs ({startup_funding})."
    
    def _generate_match_summary(self, investor: Dict[str, Any], startup_profile: Dict[str, Any]) -> str:
        """Generate an overall match summary"""
        match_percentage = investor.get('match_percentage', 0)
        
        if match_percentage >= 80:
            return f"Excellent match! {investor.get('name', 'This investor')} is highly aligned with your startup's profile and needs."
        elif match_percentage >= 60:
            return f"Good match. {investor.get('name', 'This investor')} is well-suited for your startup with some strong alignment areas."
        elif match_percentage >= 40:
            return f"Moderate match. {investor.get('name', 'This investor')} has some alignment with your startup but also some differences."
        else:
            return f"Limited match. {investor.get('name', 'This investor')} may not be the best fit for your startup based on the criteria analyzed."

def render_matching_algorithm_section(investors_df: pd.DataFrame = None):
    """Render the matching algorithm section in the Streamlit app"""
    import streamlit as st
    
    st.header("Investor Matching Algorithm")
    
    with st.expander("About the Matching Algorithm", expanded=False):
        st.write("""
        The Investor Matching Algorithm helps you find the most suitable investors for your startup based on:
        
        1. **Investment Stage Match**: Aligns your startup's current stage with investors' preferred investment stages
        2. **Sector/Industry Match**: Matches your business sector with investors' focus areas
        3. **Location Preference**: Considers geographical alignment between your startup and potential investors
        4. **Investment Size**: Compares your funding needs with typical investment amounts
        
        The algorithm calculates a match percentage for each criterion and provides an overall match score.
        """)
    
    # Create form for startup profile input
    with st.form("startup_profile_form"):
        st.subheader("Enter Your Startup Profile")
        
        col1, col2 = st.columns(2)
        
        with col1:
            startup_name = st.text_input("Startup Name")
            
            startup_stage = st.selectbox(
                "Current Stage",
                ["Idea/Concept", "Prototype", "MVP", "Pre-Seed", "Seed", 
                 "Early Revenue", "Series A", "Growth", "Series B", "Series C", "Expansion"]
            )
            
            startup_location = st.text_input(
                "Location",
                placeholder="e.g., San Francisco, US or Europe"
            )
        
        with col2:
            startup_sector = st.multiselect(
                "Industry/Sector",
                ["Technology", "Healthcare", "Finance", "Consumer", "Enterprise", "AI/ML", 
                 "Blockchain", "SaaS", "E-commerce", "Mobile", "IoT", "Clean Tech",
                 "B2B", "B2C", "Hardware", "Software", "Deep Tech"],
                default=[]
            )
            
            funding_needed = st.select_slider(
                "Funding Needed",
                options=["< $100K", "$100K-$500K", "$500K-$1M", "$1M-$5M", "$5M-$10M", "> $10M"]
            )
        
        startup_description = st.text_area(
            "Brief Description",
            placeholder="Describe your startup, product, and target market in a few sentences",
            max_chars=500
        )
        
        submitted = st.form_submit_button("Find Matching Investors", type="primary")
    
    # Process form submission
    if submitted:
        if not startup_name or not startup_description:
            st.warning("Please provide at least your startup name and description")
            return
            
        # Create startup profile
        startup_profile = {
            'name': startup_name,
            'stage': startup_stage,
            'location': startup_location,
            'sector': " ".join(startup_sector),
            'funding_needed': funding_needed,
            'description': startup_description
        }
        
        # Store in session state
        st.session_state.startup_profile = startup_profile
        
        # Check if we have investors to match
        if investors_df is None and 'search_results' in st.session_state:
            investors_df = st.session_state.search_results
            
        if investors_df is not None and not investors_df.empty:
            with st.spinner("Finding the best investor matches..."):
                # Initialize matching algorithm
                matching_algorithm = InvestorMatchingAlgorithm()
                
                # Get matches
                matches = matching_algorithm.match_investors(investors_df, startup_profile)
                
                if not matches.empty:
                    st.success(f"Found {len(matches)} potential investors for {startup_name}")
                    
                    # Display matches
                    st.subheader("Top Investor Matches")
                    
                    # Create tabs for different views
                    tab1, tab2 = st.tabs(["Match Overview", "Detailed Analysis"])
                    
                    with tab1:
                        # Create a summary table
                        summary_data = []
                        for _, investor in matches.iterrows():
                            summary_data.append({
                                'Investor': investor['name'],
                                'Type': investor['type'],
                                'Match Score': f"{investor['match_percentage']}%",
                                'Location': investor['location'],
                                'Investment Stages': ", ".join(investor['investment_stages'])
                            })
                            
                        summary_df = pd.DataFrame(summary_data)
                        st.dataframe(summary_df, use_container_width=True)
                        
                        # Show top 3 matches with visual indicators
                        st.subheader("Top 3 Matches")
                        top3 = matches.head(3)
                        
                        for i, (_, investor) in enumerate(top3.iterrows()):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.write(f"**{i+1}. {investor['name']} - {investor['type']}**")
                                st.write(f"**Match Score:** {investor['match_percentage']}%")
                                st.write(f"**Location:** {investor['location']}")
                                st.write(f"**Investment Stages:** {', '.join(investor['investment_stages'])}")
                                
                                # Generate match explanation
                                explanation = matching_algorithm.explain_match(investor, startup_profile)
                                st.write(f"**Why this matches:** {explanation['summary']}")
                            
                            with col2:
                                # Create a visual indicator of match quality
                                match_color = "green" if investor['match_percentage'] >= 70 else "orange" if investor['match_percentage'] >= 50 else "red"
                                st.markdown(f"""
                                <div style="width:100%; height:100px; background-color:{match_color}; 
                                border-radius:10px; display:flex; align-items:center; justify-content:center;">
                                <span style="color:white; font-size:24px; font-weight:bold;">{investor['match_percentage']}%</span>
                                </div>
                                """, unsafe_allow_html=True)
                    
                    with tab2:
                        # Show detailed breakdown for each match
                        for i, (_, investor) in enumerate(matches.iterrows()):
                            with st.expander(f"{investor['name']} - {investor['match_percentage']}% Match"):
                                col1, col2 = st.columns([2, 1])
                                
                                with col1:
                                    st.write(f"**Investor:** {investor['name']}")
                                    st.write(f"**Type:** {investor['type']}")
                                    st.write(f"**Location:** {investor['location']}")
                                    st.write(f"**Investment Stages:** {', '.join(investor['investment_stages'])}")
                                    if 'profile_url' in investor and investor['profile_url']:
                                        st.write(f"**Website:** [{investor['profile_url']}]({investor['profile_url']})")
                                
                                with col2:
                                    # Show match breakdown
                                    st.write("**Match Breakdown:**")
                                    st.write(f"- Stage: {investor['stage_match_percentage']}%")
                                    st.write(f"- Sector: {investor['sector_match_percentage']}%")
                                    st.write(f"- Location: {investor['location_match_percentage']}%")
                                    st.write(f"- Investment Size: {investor['investment_size_match_percentage']}%")
                                
                                # Generate detailed explanation
                                explanation = matching_algorithm.explain_match(investor, startup_profile)
                                
                                st.write("**Match Details:**")
                                st.write(f"- **Stage Match:** {explanation['stage_match']['details']}")
                                st.write(f"- **Sector Match:** {explanation['sector_match']['details']}")
                                st.write(f"- **Location Match:** {explanation['location_match']['details']}")
                                st.write(f"- **Investment Size Match:** {explanation['investment_size_match']['details']}")
                                
                                st.write(f"**Summary:** {explanation['summary']}")
                else:
                    st.warning("No matching investors found. Try adjusting your startup profile or search for more investors.")
        else:
            st.info("Please search for investors first using the search section on the left.") 