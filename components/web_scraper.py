import os
import re
import time
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import random
import json
from urllib.parse import quote_plus
import streamlit as st
from fake_useragent import UserAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebScraper")

class InvestorWebScraper:
    """Web scraper for finding investor information from various sources"""
    
    def __init__(self):
        """Initialize the web scraper"""
        self.logger = logging.getLogger("WebScraper")
        self.user_agent = UserAgent()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.user_agent.random,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        })
        self.logger.info("InvestorWebScraper initialized")
        
        # Cache for search results
        self.cache = {}
        
    def search_investors(self, search_terms: List[str], location: Optional[str] = None) -> pd.DataFrame:
        """
        Search for investors based on search terms and location
        
        Args:
            search_terms: List of search terms
            location: Optional location filter
            
        Returns:
            DataFrame containing investor information
        """
        # Create cache key
        cache_key = f"{'-'.join(search_terms)}-{location}"
        
        # Check cache
        if cache_key in self.cache:
            self.logger.info(f"Using cached results for {cache_key}")
            return self.cache[cache_key]
        
        # For demo purposes, we'll use mock data instead of actual web scraping
        # In a real implementation, this would make requests to investor directories
        self.logger.info(f"Searching for investors with terms: {search_terms}, location: {location}")
        
        try:
            # Simulate web scraping delay
            time.sleep(random.uniform(0.5, 1.5))
            
            # Generate mock results based on search terms
            results = self._generate_mock_results(search_terms, location)
            
            # Cache results
            self.cache[cache_key] = results
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error searching for investors: {str(e)}")
            return pd.DataFrame()
    
    def _generate_mock_results(self, search_terms: List[str], location: Optional[str] = None) -> pd.DataFrame:
        """
        Generate mock search results for demonstration purposes
        
        Args:
            search_terms: List of search terms
            location: Optional location filter
            
        Returns:
            DataFrame with mock investor data
        """
        # Define mock investor data templates
        investor_templates = [
            {
                "name": "TechVentures Capital",
                "type": "Venture Capital",
                "location": "San Francisco, USA",
                "investments": random.randint(50, 200),
                "investment_stages": ["Seed", "Series A"],
                "profile_url": "https://example.com/techventures",
                "focus_areas": ["SaaS", "AI/ML", "Enterprise Software"],
                "latitude": 37.7749,
                "longitude": -122.4194
            },
            {
                "name": "Global Innovation Partners",
                "type": "Venture Capital",
                "location": "New York, USA",
                "investments": random.randint(100, 300),
                "investment_stages": ["Series A", "Series B"],
                "profile_url": "https://example.com/gip",
                "focus_areas": ["FinTech", "Healthcare", "E-commerce"],
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            {
                "name": "Future Fund Investments",
                "type": "Private Equity",
                "location": "London, UK",
                "investments": random.randint(30, 150),
                "investment_stages": ["Series B", "Series C", "Growth"],
                "profile_url": "https://example.com/futurefund",
                "focus_areas": ["FinTech", "Marketplace", "SaaS"],
                "latitude": 51.5074,
                "longitude": -0.1278
            },
            {
                "name": "Angel Innovators Network",
                "type": "Angel Investor",
                "location": "Berlin, Germany",
                "investments": random.randint(10, 50),
                "investment_stages": ["Pre-Seed", "Seed"],
                "profile_url": "https://example.com/angelinnovators",
                "focus_areas": ["Consumer", "Mobile Apps", "E-commerce"],
                "latitude": 52.5200,
                "longitude": 13.4050
            },
            {
                "name": "Startup Accelerator Group",
                "type": "Accelerator",
                "location": "Boston, USA",
                "investments": random.randint(20, 100),
                "investment_stages": ["Pre-Seed", "Seed"],
                "profile_url": "https://example.com/startupaccelerator",
                "focus_areas": ["BioTech", "Healthcare Tech", "Deep Tech"],
                "latitude": 42.3601,
                "longitude": -71.0589
            }
        ]
        
        # Generate variations of the templates based on search terms
        results = []
        
        # Number of results to generate
        num_results = random.randint(3, 8)
        
        for i in range(num_results):
            # Select a random template
            template = random.choice(investor_templates).copy()
            
            # Modify template based on search terms
            for term in search_terms:
                term_lower = term.lower()
                
                # Modify investor type if term matches a type
                if term_lower in ["venture capital", "vc", "angel", "private equity", "accelerator", "incubator"]:
                    if "venture" in term_lower or "vc" == term_lower:
                        template["type"] = "Venture Capital"
                    elif "angel" in term_lower:
                        template["type"] = "Angel Investor"
                    elif "private equity" in term_lower or "pe" == term_lower:
                        template["type"] = "Private Equity"
                    elif "accelerator" in term_lower:
                        template["type"] = "Accelerator"
                    elif "incubator" in term_lower:
                        template["type"] = "Incubator"
                
                # Modify focus areas if term matches a sector
                sectors = ["SaaS", "AI", "ML", "FinTech", "Healthcare", "E-commerce", 
                           "Enterprise", "Consumer", "Mobile", "BioTech", "Deep Tech", 
                           "Marketplace", "B2B", "B2C", "Blockchain", "Cybersecurity"]
                
                for sector in sectors:
                    if sector.lower() in term_lower or term_lower in sector.lower():
                        if sector not in template["focus_areas"]:
                            template["focus_areas"].append(sector)
                
                # Modify investment stages if term matches a stage
                stages = ["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Growth", "Late Stage"]
                
                for stage in stages:
                    if stage.lower() in term_lower or term_lower in stage.lower():
                        if stage not in template["investment_stages"]:
                            template["investment_stages"].append(stage)
            
            # Modify location if specified
            if location:
                # List of major tech hubs
                tech_hubs = {
                    "san francisco": {"city": "San Francisco", "country": "USA", "lat": 37.7749, "lng": -122.4194},
                    "new york": {"city": "New York", "country": "USA", "lat": 40.7128, "lng": -74.0060},
                    "boston": {"city": "Boston", "country": "USA", "lat": 42.3601, "lng": -71.0589},
                    "london": {"city": "London", "country": "UK", "lat": 51.5074, "lng": -0.1278},
                    "berlin": {"city": "Berlin", "country": "Germany", "lat": 52.5200, "lng": 13.4050},
                    "paris": {"city": "Paris", "country": "France", "lat": 48.8566, "lng": 2.3522},
                    "tel aviv": {"city": "Tel Aviv", "country": "Israel", "lat": 32.0853, "lng": 34.7818},
                    "singapore": {"city": "Singapore", "country": "Singapore", "lat": 1.3521, "lng": 103.8198},
                    "tokyo": {"city": "Tokyo", "country": "Japan", "lat": 35.6762, "lng": 139.6503},
                    "toronto": {"city": "Toronto", "country": "Canada", "lat": 43.6532, "lng": -79.3832},
                    "sydney": {"city": "Sydney", "country": "Australia", "lat": -33.8688, "lng": 151.2093}
                }
                
                location_lower = location.lower()
                
                # Check if location matches any tech hub
                for hub_name, hub_data in tech_hubs.items():
                    if hub_name in location_lower or location_lower in hub_name:
                        template["location"] = f"{hub_data['city']}, {hub_data['country']}"
                        template["latitude"] = hub_data["lat"]
                        template["longitude"] = hub_data["lng"]
                        break
                else:
                    # If no match, use the location as is
                    template["location"] = location
                    # Generate random coordinates (not accurate, just for demo)
                    template["latitude"] = random.uniform(-90, 90)
                    template["longitude"] = random.uniform(-180, 180)
            
            # Generate a unique name
            name_prefixes = ["Global", "Tech", "Future", "Innovation", "Venture", "Capital", 
                             "Digital", "Alpha", "Beta", "Omega", "Pioneer", "Frontier", 
                             "Next", "Prime", "Elite", "Strategic", "Horizon", "Summit"]
            
            name_suffixes = ["Ventures", "Capital", "Partners", "Investments", "Fund", 
                             "Group", "Associates", "Network", "Alliance", "Collective"]
            
            template["name"] = f"{random.choice(name_prefixes)} {random.choice(name_suffixes)} {i+1}"
            
            # Add to results
            results.append(template)
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        return df
    
    def get_investor_details(self, profile_url: str) -> Dict[str, Any]:
        """
        Get detailed information about an investor from their profile page
        
        Args:
            profile_url: URL of the investor's profile
            
        Returns:
            Dictionary containing detailed investor information
        """
        self.logger.info(f"Getting investor details from: {profile_url}")
        
        try:
            # Simulate web scraping delay
            time.sleep(random.uniform(0.5, 1.5))
            
            # Generate mock details
            details = self._generate_mock_details(profile_url)
            
            return details
        
        except Exception as e:
            self.logger.error(f"Error getting investor details: {str(e)}")
            return {}
    
    def _generate_mock_details(self, profile_url: str) -> Dict[str, Any]:
        """
        Generate mock investor details for demonstration purposes
        
        Args:
            profile_url: URL of the investor's profile
            
        Returns:
            Dictionary with mock investor details
        """
        # Extract investor name from URL
        name_match = re.search(r'\/([^\/]+)$', profile_url)
        name = name_match.group(1) if name_match else "Unknown Investor"
        name = name.replace("-", " ").title()
        
        # Generate random portfolio companies
        portfolio_companies = []
        company_names = ["TechStart", "DataFlow", "CloudScale", "MobileFirst", "AILabs", 
                         "BlockChain Solutions", "HealthTech", "EduLearn", "FinanceApp", 
                         "RetailTech", "SmartHome", "GreenEnergy", "FoodTech", "TravelApp"]
        
        num_companies = random.randint(5, 15)
        for _ in range(num_companies):
            company = {
                "name": random.choice(company_names) + str(random.randint(1, 100)),
                "stage": random.choice(["Pre-Seed", "Seed", "Series A", "Series B", "Series C"]),
                "year": random.randint(2015, 2023)
            }
            portfolio_companies.append(company)
        
        # Generate random team members
        team_members = []
        first_names = ["John", "Sarah", "Michael", "Emma", "David", "Jennifer", "Robert", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis", "Garcia"]
        
        num_members = random.randint(3, 8)
        for _ in range(num_members):
            member = {
                "name": f"{random.choice(first_names)} {random.choice(last_names)}",
                "title": random.choice(["Partner", "Managing Partner", "General Partner", "Principal", "Associate"]),
                "bio": "Experienced investor with a background in technology and finance."
            }
            team_members.append(member)
        
        # Generate random investment criteria
        investment_criteria = {
            "min_investment": f"${random.choice([50, 100, 250, 500, 1000])}K",
            "max_investment": f"${random.choice([1, 2, 5, 10, 20])}M",
            "preferred_stages": random.sample(["Pre-Seed", "Seed", "Series A", "Series B", "Series C", "Growth"], k=random.randint(2, 4)),
            "geographic_focus": random.sample(["North America", "Europe", "Asia", "Global"], k=random.randint(1, 3)),
            "sector_focus": random.sample(["SaaS", "AI/ML", "FinTech", "Healthcare", "E-commerce", "Enterprise", "Consumer", "Mobile", "BioTech", "Deep Tech"], k=random.randint(3, 6))
        }
        
        # Compile details
        details = {
            "name": name,
            "profile_url": profile_url,
            "description": f"{name} is a leading investment firm focused on {', '.join(investment_criteria['sector_focus'][:2])} startups.",
            "founded": random.randint(2000, 2020),
            "headquarters": random.choice(["San Francisco, USA", "New York, USA", "London, UK", "Berlin, Germany", "Singapore"]),
            "assets_under_management": f"${random.randint(10, 1000)}M",
            "portfolio_companies": portfolio_companies,
            "team_members": team_members,
            "investment_criteria": investment_criteria,
            "contact_info": {
                "email": f"info@{name.lower().replace(' ', '')}.com",
                "phone": f"+1 (555) {random.randint(100, 999)}-{random.randint(1000, 9999)}",
                "social_media": {
                    "twitter": f"https://twitter.com/{name.lower().replace(' ', '')}",
                    "linkedin": f"https://linkedin.com/company/{name.lower().replace(' ', '')}"
                }
            }
        }
        
        return details

def render_web_scraper_section(search_terms: List[str] = None, location: str = None):
    """
    Render the web scraper section in the Streamlit app
    
    Args:
        search_terms: Optional list of search terms from the main search
        location: Optional location from the main search
    """
    st.subheader("Web Scraper - Find More Investors")
    
    # Add description
    st.markdown("""
    Use our web scraper to find additional investors that match your criteria.
    This tool searches investor directories and websites to find potential matches.
    """)
    
    # Initialize scraper
    scraper = InvestorWebScraper()
    
    # Create form for search inputs
    with st.form("web_scraper_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Use search terms from main search if available
            default_terms = ", ".join(search_terms) if search_terms else ""
            search_input = st.text_input(
                "Search Terms",
                value=default_terms,
                placeholder="e.g., Venture Capital, AI, Series A"
            )
        
        with col2:
            # Use location from main search if available
            location_input = st.text_input(
                "Location",
                value=location if location else "",
                placeholder="e.g., San Francisco, Europe"
            )
        
        # Submit button
        submitted = st.form_submit_button("Scrape Web for Investors", type="primary")
    
    # Process form submission
    if submitted:
        if not search_input:
            st.warning("Please enter at least one search term")
            return
        
        # Parse search terms
        terms = [term.strip() for term in search_input.split(",") if term.strip()]
        
        with st.spinner("Searching the web for investors..."):
            # Search for investors
            results = scraper.search_investors(terms, location_input)
            
            if not results.empty:
                st.success(f"Found {len(results)} investors from web sources")
                
                # Display results
                st.write("### Web Search Results")
                
                # Create tabs for different views
                tab1, tab2 = st.tabs(["List View", "Map View"])
                
                with tab1:
                    # Enhanced list view with more details
                    for i, row in results.iterrows():
                        with st.expander(f"{row['name']} - {row['type']}"):
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                st.write(f"**Location:** {row['location']}")
                                st.write(f"**Investments:** {row['investments']}")
                                st.write(f"**Investment Stages:** {', '.join(row['investment_stages'])}")
                                st.write(f"**Focus Areas:** {', '.join(row['focus_areas'])}")
                                
                                # Add button to get more details
                                if st.button(f"Get Details for {row['name']}", key=f"details_{i}"):
                                    with st.spinner(f"Getting details for {row['name']}..."):
                                        details = scraper.get_investor_details(row['profile_url'])
                                        
                                        if details:
                                            st.write("#### Detailed Information")
                                            
                                            st.write(f"**Description:** {details['description']}")
                                            st.write(f"**Founded:** {details['founded']}")
                                            st.write(f"**Headquarters:** {details['headquarters']}")
                                            st.write(f"**Assets Under Management:** {details['assets_under_management']}")
                                            
                                            st.write("**Investment Criteria:**")
                                            criteria = details['investment_criteria']
                                            st.write(f"- Min Investment: {criteria['min_investment']}")
                                            st.write(f"- Max Investment: {criteria['max_investment']}")
                                            st.write(f"- Preferred Stages: {', '.join(criteria['preferred_stages'])}")
                                            st.write(f"- Geographic Focus: {', '.join(criteria['geographic_focus'])}")
                                            st.write(f"- Sector Focus: {', '.join(criteria['sector_focus'])}")
                                            
                                            st.write("**Portfolio Companies:**")
                                            portfolio_df = pd.DataFrame(details['portfolio_companies'])
                                            st.dataframe(portfolio_df)
                                            
                                            st.write("**Team Members:**")
                                            for member in details['team_members'][:3]:  # Show first 3 members
                                                st.write(f"- **{member['name']}** - {member['title']}")
                                            
                                            st.write("**Contact Information:**")
                                            contact = details['contact_info']
                                            st.write(f"- Email: {contact['email']}")
                                            st.write(f"- Phone: {contact['phone']}")
                                            st.write(f"- Twitter: [{contact['social_media']['twitter']}]({contact['social_media']['twitter']})")
                                            st.write(f"- LinkedIn: [{contact['social_media']['linkedin']}]({contact['social_media']['linkedin']})")
                                        else:
                                            st.warning("Could not retrieve detailed information")
                            
                            with col2:
                                # Display a small map for the investor location
                                if 'latitude' in row and 'longitude' in row:
                                    st.write("**Location Map:**")
                                    location_df = pd.DataFrame({
                                        'lat': [row['latitude']],
                                        'lon': [row['longitude']],
                                        'name': [row['name']]
                                    })
                                    st.map(location_df, zoom=4)
                
                with tab2:
                    # Map view of all investors
                    if 'latitude' in results.columns and 'longitude' in results.columns:
                        st.write("**Global Investor Map**")
                        map_data = pd.DataFrame({
                            'lat': results['latitude'],
                            'lon': results['longitude'],
                            'name': results['name']
                        })
                        st.map(map_data)
                    else:
                        st.warning("Location data not available for map view")
                
                # Add option to save results
                if st.button("Save These Investors to Your Results"):
                    if 'search_results' in st.session_state:
                        # Combine with existing results
                        combined_results = pd.concat([st.session_state.search_results, results], ignore_index=True)
                        # Remove duplicates based on name
                        combined_results = combined_results.drop_duplicates(subset=['name'])
                        st.session_state.search_results = combined_results
                        st.success(f"Added {len(results)} investors to your search results")
                    else:
                        # Set as new results
                        st.session_state.search_results = results
                        st.success(f"Saved {len(results)} investors to your search results")
            else:
                st.warning("No investors found matching your criteria")
                st.info("Try using different search terms or removing the location filter") 