import logging
import os
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd
from fake_useragent import UserAgent
from sqlalchemy.orm import Session

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

        self.logger.info("InvestorSearchTool initialized successfully")

    def setup_rate_limits(self):
        """Set up rate limiting configurations"""
        self.rate_limits = {
            'default': {'requests': 30, 'window': 60}  # 30 requests per minute default
        }

    def get_investor_data(self, search_terms: List[str]) -> pd.DataFrame:
        """Get investor data with database integration"""
        try:
            # Get database session
            session = self.db.get_session()

            # First try to get data from database
            investors = self._get_from_database(session, search_terms)

            # If no data in database, use sample data and store it
            if not investors:
                sample_data = self._get_sample_data()
                investors = self._store_in_database(session, sample_data)

            # Convert to DataFrame
            df = pd.DataFrame([
                {
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
            raise
        finally:
            session.close()

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
                query = query.filter(*filters)

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
                    longitude=data['longitude'][i]
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
                'Menlo Park, US',
                'San Francisco, US',
                'Mountain View, US',
                'Palo Alto, US'
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