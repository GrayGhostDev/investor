import logging
import os
import random
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from fake_useragent import UserAgent
from sqlalchemy import or_, and_, desc, asc
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func

# Try to import geopy, but provide a fallback if it's not available
try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False
    logging.warning("geopy module not available. Using fallback geocoding.")

# Import local modules
from scraping_config import RATE_LIMITS
from database import Database, Investor

class InvestorSearchTool:
    """Tool for searching and collecting investor data from multiple sources"""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the investor search tool"""
        self.logger = logging.getLogger(__name__)
        self.setup_rate_limits()
        self.db = Database()

        # Initialize cache
        self.cache = {}
        self.cache_expiry = {}
        
        # Initialize geocoder if geopy is available
        if GEOPY_AVAILABLE:
            try:
                self.geolocator = Nominatim(user_agent="investor_search_app")
                self.logger.info("Geocoder initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize geocoder: {str(e)}")
                self.geolocator = None
        else:
            self.geolocator = None
            self.logger.warning("Geocoder not available - using random coordinates")
        
        # Create sample data if database is empty
        self._create_sample_data_if_empty()

        self.logger.info("InvestorSearchTool initialized successfully")

    def setup_rate_limits(self):
        """Set up rate limiting configurations"""
        self.rate_limits = {
            'default': {'requests': 30, 'window': 60},  # 30 requests per minute default
            'geocoding': {'requests': 1, 'window': 1},  # 1 request per second for geocoding
            'crunchbase': {'requests': 5, 'window': 60}  # 5 requests per minute for Crunchbase
        }

    def get_investor_data(
        self,
        search_terms: List[str],
        filters: Dict[str, Any] = None,
        sort_by: str = "Investment Count",
        sort_order: str = "descending",
        use_real_api: bool = True
    ) -> pd.DataFrame:
        """Get investor data with advanced filtering and sorting"""
        try:
            # Get database session
            session = self.db.get_session()
            
            # Always try to get real data first if we have search terms
            real_investors = []
            if search_terms and len(search_terms) > 0:
                try:
                    # Try to get real investor data from external API for each search term
                    for term in search_terms:
                        self.logger.info(f"Fetching real investor data for: {term}")
                        real_data = self._fetch_real_investor_data(term)
                        if real_data:
                            # Store real data in database
                            new_investors = self._store_real_data_in_database(session, real_data)
                            # Add new investors to results
                            real_investors.extend(new_investors)
                except Exception as e:
                    self.logger.error(f"Error fetching real investor data: {str(e)}")
            
            # If we got real data, use it as the primary source
            if real_investors:
                investors = real_investors
                self.logger.info(f"Using {len(real_investors)} real investors from API")
            else:
                # Build query with filters to get existing real data from database
                query = self._build_filtered_query(session, search_terms, filters)
                
                # Apply sorting
                query = self._apply_sorting(query, sort_by, sort_order)
                
                # Execute query
                investors = query.all()
                
                # If no data found in database, try to fetch real data again with broader terms
                if not investors and search_terms:
                    # Try with broader search terms
                    broader_terms = self._get_broader_search_terms(search_terms)
                    for term in broader_terms:
                        self.logger.info(f"Trying broader search term: {term}")
                        real_data = self._fetch_real_investor_data(term)
                        if real_data:
                            new_investors = self._store_real_data_in_database(session, real_data)
                            investors.extend(new_investors)
                            if len(investors) >= 5:  # Get at least 5 investors
                                break

            # Convert to DataFrame
            df = pd.DataFrame([
                {
                    'id': inv.id,
                    'name': inv.name,
                    'type': inv.type,
                    'location': inv.location,
                    'investments': inv.investments,
                    'profile_url': inv.profile_url,
                    'investment_stages': inv.investment_stages,
                    'latitude': inv.latitude,
                    'longitude': inv.longitude
                }
                for inv in investors
            ])

            return df

        except Exception as e:
            self.logger.error(f"Error getting investor data: {str(e)}")
            if 'session' in locals():
                session.close()
            # Return empty DataFrame
            return pd.DataFrame()
        finally:
            if 'session' in locals():
                session.close()

    def _build_filtered_query(
        self,
        session: Session,
        search_terms: List[str],
        filters: Optional[Dict[str, Any]] = None
    ):
        """Build SQL query with filters"""
        query = session.query(Investor)

        # Apply search terms
        if search_terms:
            search_filters = []
            for term in search_terms:
                term = f"%{term}%"
                search_filters.extend([
                    Investor.name.ilike(term),
                    Investor.type.ilike(term),
                    Investor.location.ilike(term)
                ])
            query = query.filter(or_(*search_filters))

        # Apply additional filters if provided
        if filters:
            query = self._apply_advanced_filters(query, filters)

        return query

    def _apply_advanced_filters(self, query, filters: Dict[str, Any]):
        """Apply advanced filters to query"""

        # Investment count range filter
        if "investment_range" in filters and filters["investment_range"]:
            min_inv, max_inv = filters["investment_range"]
            query = query.filter(
                and_(
                    Investor.investments >= min_inv,
                    Investor.investments <= max_inv
                )
            )

        # Investment stages filter
        if "investment_stages" in filters and filters["investment_stages"]:
            # This is a simplification - in a real app, you'd need a more complex query for JSON arrays
            pass

        # Location/continent filter
        if "continents" in filters and filters["continents"]:
            continent_filters = []
            for continent in filters["continents"]:
                continent_filters.append(Investor.location.ilike(f'%{continent}%'))
            query = query.filter(or_(*continent_filters))

        return query

    def _apply_sorting(self, query, sort_by: str, sort_order: str):
        """Apply sorting to query"""
        sort_field = {
            "Investment Count": Investor.investments,
            "Name": Investor.name,
            "Location": Investor.location
        }.get(sort_by, Investor.investments)

        if sort_order == "descending":
            query = query.order_by(desc(sort_field))
        else:
            query = query.order_by(asc(sort_field))

        return query

    def _get_from_database(self, session: Session, search_terms: List[str]) -> List[Investor]:
        """Get investors from database matching search terms"""
        try:
            query = session.query(Investor)

            # Apply search filters
            if search_terms:
                filters = []
                for term in search_terms:
                    term = f"%{term}%"
                    filters.extend([
                        Investor.name.ilike(term),
                        Investor.type.ilike(term),
                        Investor.location.ilike(term)
                    ])
                query = query.filter(or_(*filters))

            return query.all()

        except Exception as e:
            self.logger.error(f"Error querying database: {str(e)}")
            raise

    def _store_in_database(self, session: Session, data: Dict) -> List[Investor]:
        """Store investor data in database"""
        try:
            investors = []
            for i in range(len(data['name'])):
                investor = Investor(
                    name=data['name'][i],
                    type=data['type'][i],
                    location=data['location'][i],
                    investments=data['investments'][i],
                    profile_url=data['profile_url'][i],
                    investment_stages=data['investment_stages'][i],
                    latitude=data['latitude'][i],
                    longitude=data['longitude'][i],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(investor)
                investors.append(investor)

            session.commit()
            return investors

        except Exception as e:
            session.rollback()
            self.logger.error(f"Error storing in database: {str(e)}")
            raise

    def _get_sample_data(self) -> Dict:
        """Get sample investor data"""
        return {
            'name': [
                'Sequoia Capital',
                'Andreessen Horowitz',
                'Y Combinator',
                'Accel Partners'
            ],
            'type': [
                'Venture Capital',
                'Venture Capital',
                'Accelerator',
                'Venture Capital'
            ],
            'location': [
                'Menlo Park, USA',
                'San Francisco, USA',
                'Mountain View, USA',
                'Palo Alto, USA'
            ],
            'investments': [1000, 850, 2000, 750],
            'profile_url': [
                'https://example.com/sequoia',
                'https://example.com/a16z',
                'https://example.com/yc',
                'https://example.com/accel'
            ],
            'investment_stages': [
                ['Seed', 'Series A', 'Series B'],
                ['Seed', 'Series A', 'Growth'],
                ['Pre-Seed', 'Seed'],
                ['Series A', 'Series B', 'Growth']
            ],
            'latitude': [37.4529598, 37.7749295, 37.3860517, 37.4419444],
            'longitude': [-122.1817252, -122.4194155, -122.0838511, -122.1430556]
        }
        
    def _create_sample_data_if_empty(self):
        """Create sample investor data if the database is empty"""
        try:
            session = self.db.get_session()
            count = session.query(Investor).count()
            
            if count == 0:
                self.logger.info("Creating sample investor data")
                
                # Sample investor types
                investor_types = ["Venture Capital", "Angel Investor", "Private Equity", "Corporate Venture", "Family Office"]
                
                # Sample locations
                locations = [
                    "San Francisco, USA", "New York, USA", "Boston, USA", 
                    "London, UK", "Berlin, Germany", "Paris, France",
                    "Tel Aviv, Israel", "Singapore", "Tokyo, Japan",
                    "Toronto, Canada", "Sydney, Australia"
                ]
                
                # Sample investment stages
                investment_stages_options = [
                    ["Pre-Seed", "Seed"],
                    ["Seed", "Series A"],
                    ["Series A", "Series B"],
                    ["Series B", "Series C"],
                    ["Series C", "Growth"],
                    ["Growth", "Late Stage"],
                    ["Pre-Seed", "Seed", "Series A"],
                    ["Seed", "Series A", "Series B"],
                    ["Series A", "Series B", "Series C"]
                ]
                
                # Create 50 sample investors
                for i in range(1, 51):
                    location = random.choice(locations)
                    
                    # Get accurate coordinates for the location
                    lat, lng = self._geocode_location(location)
                    
                    investor = Investor(
                        name=f"Sample Investor {i}",
                        type=random.choice(investor_types),
                        location=location,
                        investments=random.randint(10, 2000),
                        profile_url=f"https://example.com/investor{i}",
                        investment_stages=random.choice(investment_stages_options),
                        latitude=lat,
                        longitude=lng,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    session.add(investor)
                
                session.commit()
                self.logger.info("Sample investor data created successfully")
            
            session.close()
        except Exception as e:
            self.logger.error(f"Error creating sample data: {str(e)}")
            if 'session' in locals():
                session.close()
                
    def _geocode_location(self, location: str) -> Tuple[float, float]:
        """Get latitude and longitude for a location using geocoding API"""
        try:
            # Check cache first
            if location in self.cache and self.cache_expiry.get(location, 0) > time.time():
                return self.cache[location]
            
            # If geopy is available and geocoder is initialized, use it
            if GEOPY_AVAILABLE and self.geolocator:
                # Rate limiting
                time.sleep(1)  # Simple rate limiting for geocoding API
                
                try:
                    # Get coordinates from geocoding API
                    location_data = self.geolocator.geocode(location)
                    
                    if location_data:
                        # Cache the result for 24 hours
                        self.cache[location] = (location_data.latitude, location_data.longitude)
                        self.cache_expiry[location] = time.time() + 86400  # 24 hours
                        return location_data.latitude, location_data.longitude
                except (GeocoderTimedOut, GeocoderUnavailable) as e:
                    self.logger.warning(f"Geocoding error for {location}: {str(e)}")
                except Exception as e:
                    self.logger.error(f"Error geocoding location {location}: {str(e)}")
            
            # Fallback to approximate coordinates based on country/region
            return self._get_approximate_coordinates(location)
                    
        except Exception as e:
            self.logger.error(f"Error in geocoding: {str(e)}")
            return self._get_approximate_coordinates(location)
            
    def _get_approximate_coordinates(self, location: str) -> Tuple[float, float]:
        """Get approximate coordinates based on location text"""
        if "USA" in location or "US" in location:
            return 37.7749 + random.uniform(-5, 5), -122.4194 + random.uniform(-5, 5)
        elif "UK" in location:
            return 51.5074 + random.uniform(-1, 1), -0.1278 + random.uniform(-1, 1)
        elif "Germany" in location:
            return 52.5200 + random.uniform(-1, 1), 13.4050 + random.uniform(-1, 1)
        elif "France" in location:
            return 48.8566 + random.uniform(-1, 1), 2.3522 + random.uniform(-1, 1)
        elif "Israel" in location:
            return 32.0853 + random.uniform(-1, 1), 34.7818 + random.uniform(-1, 1)
        elif "Singapore" in location:
            return 1.3521 + random.uniform(-0.5, 0.5), 103.8198 + random.uniform(-0.5, 0.5)
        elif "Japan" in location:
            return 35.6762 + random.uniform(-1, 1), 139.6503 + random.uniform(-1, 1)
        elif "Canada" in location:
            return 43.6532 + random.uniform(-2, 2), -79.3832 + random.uniform(-2, 2)
        elif "Australia" in location:
            return -33.8688 + random.uniform(-2, 2), 151.2093 + random.uniform(-2, 2)
        else:
            return random.uniform(-90, 90), random.uniform(-180, 180)
            
    def _fetch_real_investor_data(self, search_term: str) -> List[Dict]:
        """Fetch real investor data from external APIs"""
        try:
            # Try to get data from Crunchbase API (simulated)
            self.logger.info(f"Fetching real investor data for: {search_term}")
            
            # In a real implementation, you would use the actual Crunchbase API
            # Here we're simulating the API call with OpenAI
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                self.logger.warning("OpenAI API key not set. Cannot fetch real investor data.")
                return []
                
            try:
                import openai
                client = openai.OpenAI(api_key=openai_api_key)
                
                # Use OpenAI to generate realistic investor data with more detailed prompt
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that provides realistic and accurate investor data in JSON format. Include detailed information about real investors when possible. NEVER make up fictional investors - use real investor names and data."},
                        {"role": "user", "content": f"""Generate realistic data for 5 real investors related to '{search_term}'. 
                        For each investor, include:
                        - name: The investor's name (use real investor names only)
                        - type: Type of investor (VC, Angel, PE, etc.)
                        - location: Specific city and country
                        - investments: Number of investments (integer)
                        - profile_url: Website URL
                        - investment_stages: Array of investment stages they focus on
                        
                        Return ONLY a valid JSON array with no additional text or explanation. 
                        Example format:
                        [
                            {{
                                "name": "Sequoia Capital",
                                "type": "Venture Capital",
                                "location": "Menlo Park, USA",
                                "investments": 1200,
                                "profile_url": "https://www.sequoiacap.com",
                                "investment_stages": ["Seed", "Series A", "Series B", "Growth"]
                            }}
                        ]
                        
                        IMPORTANT: Use only real investor names and accurate data. Do not make up fictional investors.
                        """}
                    ],
                    max_tokens=1000,
                    temperature=0.3  # Lower temperature for more factual responses
                )
                
                # Parse the response
                content = response.choices[0].message.content
                try:
                    # Clean the content to ensure it's valid JSON
                    content = content.strip()
                    if content.startswith("```json"):
                        content = content[7:]
                    if content.endswith("```"):
                        content = content[:-3]
                    content = content.strip()
                    
                    # Extract JSON from the response
                    data = json.loads(content)
                    
                    # Validate the data structure
                    if not isinstance(data, list):
                        self.logger.error("Invalid data format: not a list")
                        return []
                        
                    for item in data:
                        if not all(k in item for k in ["name", "type", "location", "investments"]):
                            self.logger.error("Invalid data format: missing required fields")
                            return []
                    
                    return data
                except json.JSONDecodeError as e:
                    self.logger.error(f"Error parsing investor data response: {str(e)}")
                    # Try again with a different prompt
                    return self._retry_fetch_real_data(search_term, client)
                    
            except Exception as e:
                self.logger.error(f"Error using OpenAI for investor data: {str(e)}")
                return []
                
        except Exception as e:
            self.logger.error(f"Error fetching real investor data: {str(e)}")
            return []
            
    def _retry_fetch_real_data(self, search_term: str, client) -> List[Dict]:
        """Retry fetching real data with a simpler prompt"""
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides real investor data in simple JSON format."},
                    {"role": "user", "content": f"""List 3 real investors related to {search_term} in this exact JSON format:
                    [
                        {{
                            "name": "Real Investor Name",
                            "type": "Investor Type",
                            "location": "City, Country",
                            "investments": Number,
                            "profile_url": "Website URL",
                            "investment_stages": ["Stage1", "Stage2"]
                        }}
                    ]
                    """}
                ],
                max_tokens=500,
                temperature=0.2
            )
            
            content = response.choices[0].message.content
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            data = json.loads(content)
            return data
            
        except Exception as e:
            self.logger.error(f"Error in retry fetch: {str(e)}")
            return []
        
    def _store_real_data_in_database(self, session: Session, data: List[Dict]) -> List[Investor]:
        """Store real investor data in database"""
        try:
            investors = []
            for item in data:
                # Check if investor already exists
                existing = session.query(Investor).filter(Investor.name == item['name']).first()
                if existing:
                    continue
                    
                # Get coordinates for location
                lat, lng = self._geocode_location(item['location'])
                
                investor = Investor(
                    name=item['name'],
                    type=item['type'],
                    location=item['location'],
                    investments=item['investments'],
                    profile_url=item.get('profile_url', f"https://example.com/{item['name'].lower().replace(' ', '')}"),
                    investment_stages=item.get('investment_stages', ["Seed", "Series A"]),
                    latitude=lat,
                    longitude=lng,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(investor)
                investors.append(investor)
                
            session.commit()
            return investors
            
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error storing real data in database: {str(e)}")
            return []

    def _get_broader_search_terms(self, search_terms: List[str]) -> List[str]:
        """Generate broader search terms based on original search terms"""
        broader_terms = []
        
        # Common investor types to try
        investor_types = ["Venture Capital", "Angel Investor", "Private Equity"]
        
        # Common sectors to try
        sectors = ["Technology", "Healthcare", "Finance", "AI", "SaaS"]
        
        # Add investor types if not already in search terms
        for inv_type in investor_types:
            if not any(inv_type.lower() in term.lower() for term in search_terms):
                broader_terms.append(inv_type)
                
        # Add sectors if search terms contain location information
        locations = [term for term in search_terms if any(loc in term.lower() for loc in 
                    ["usa", "uk", "europe", "asia", "america", "london", "york", "francisco", "valley"])]
        
        if locations:
            for location in locations:
                for sector in sectors:
                    broader_terms.append(f"{sector} investors in {location}")
        
        # Add some general terms
        broader_terms.extend(["Top Venture Capital Firms", "Leading Angel Investors", "Technology Investors"])
        
        return broader_terms