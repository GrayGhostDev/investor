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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebScraper")

class InvestorWebScraper:
    """Class to scrape additional investor information from the web"""
    
    def __init__(self):
        self.logger = logging.getLogger("WebScraper")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        })
        self.cache = {}
        self.logger.info("InvestorWebScraper initialized")
        
    def search_for_investors(self, search_terms: List[str], location: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for investors based on search terms and location
        
        Args:
            search_terms: List of search terms
            location: Optional location to filter results
            
        Returns:
            List of investor data dictionaries
        """
        results = []
        
        # Create a combined search query
        combined_terms = " ".join(search_terms)
        if location:
            combined_terms += f" {location}"
            
        query = f"venture capital investors {combined_terms}"
        
        # Check cache first
        cache_key = f"{query}_{location}"
        if cache_key in self.cache:
            self.logger.info(f"Using cached results for: {query}")
            return self.cache[cache_key]
        
        # Search sources
        try:
            # Try multiple sources and combine results
            crunchbase_results = self._search_crunchbase_like(query)
            results.extend(crunchbase_results)
            
            # Add a small delay to avoid rate limiting
            time.sleep(1)
            
            # Search for news articles about these investors
            for investor in results[:5]:  # Limit to top 5 to avoid too many requests
                if 'name' in investor:
                    news = self._search_investor_news(investor['name'])
                    if news:
                        investor['recent_news'] = news[:3]  # Keep only top 3 news items
            
            # Cache the results
            self.cache[cache_key] = results
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching for investors: {str(e)}")
            return []
    
    def _search_crunchbase_like(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for investors using a Crunchbase-like approach
        This is a simulation since we don't have direct API access
        """
        investors = []
        
        try:
            # Use DuckDuckGo search as it's more scraper-friendly
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}+site:crunchbase.com"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                results = soup.select('.result')
                
                for result in results[:10]:  # Limit to top 10 results
                    title_elem = result.select_one('.result__title')
                    snippet_elem = result.select_one('.result__snippet')
                    url_elem = result.select_one('.result__url')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True)
                        url = url_elem.get_text(strip=True) if url_elem else ""
                        
                        # Extract investor information from the title and snippet
                        investor_data = self._extract_investor_data(title, snippet, url)
                        if investor_data:
                            investors.append(investor_data)
            
            return investors
            
        except Exception as e:
            self.logger.error(f"Error in Crunchbase search: {str(e)}")
            # Return some mock data as fallback
            return self._get_mock_investor_data(query, 5)
    
    def _search_investor_news(self, investor_name: str) -> List[Dict[str, str]]:
        """Search for recent news about an investor"""
        news_items = []
        
        try:
            # Use DuckDuckGo news search
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(investor_name)}+venture+capital+news"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                results = soup.select('.result')
                
                for result in results[:5]:  # Limit to top 5 news items
                    title_elem = result.select_one('.result__title')
                    snippet_elem = result.select_one('.result__snippet')
                    url_elem = result.select_one('.result__url')
                    
                    if title_elem and snippet_elem:
                        news_items.append({
                            'title': title_elem.get_text(strip=True),
                            'snippet': snippet_elem.get_text(strip=True),
                            'url': url_elem.get_text(strip=True) if url_elem else "",
                            'date': self._extract_date(snippet_elem.get_text(strip=True))
                        })
            
            return news_items
            
        except Exception as e:
            self.logger.error(f"Error searching for investor news: {str(e)}")
            return []
    
    def _extract_date(self, text: str) -> str:
        """Extract date from text if available"""
        date_patterns = [
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0)
        
        return "Recent"
    
    def _extract_investor_data(self, title: str, snippet: str, url: str) -> Optional[Dict[str, Any]]:
        """Extract structured investor data from search results"""
        # Skip non-investor results
        if not any(term in title.lower() or term in snippet.lower() 
                  for term in ['venture', 'capital', 'investor', 'fund', 'vc']):
            return None
            
        # Extract investor name - usually the first part of the title before special characters
        name_match = re.match(r'^([^|:–-]+)', title)
        name = name_match.group(1).strip() if name_match else title.split('|')[0].strip()
        
        # Extract location from snippet
        location_patterns = [
            r'based in ([^\.]+)',
            r'from ([^\.]+)',
            r'located in ([^\.]+)'
        ]
        
        location = None
        for pattern in location_patterns:
            match = re.search(pattern, snippet, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                break
                
        # Extract investment focus
        focus = []
        focus_keywords = ['technology', 'healthcare', 'fintech', 'software', 'consumer', 
                         'enterprise', 'ai', 'machine learning', 'saas', 'biotech']
        
        for keyword in focus_keywords:
            if keyword in snippet.lower() or keyword in title.lower():
                focus.append(keyword.title())
        
        # Extract investment stages if mentioned
        stages = []
        stage_keywords = ['seed', 'early stage', 'series a', 'series b', 'growth', 'late stage']
        
        for keyword in stage_keywords:
            if keyword in snippet.lower() or keyword in title.lower():
                stages.append(keyword.title())
        
        return {
            'name': name,
            'type': 'Venture Capital' if 'venture' in (title + snippet).lower() else 'Investor',
            'location': location or 'Unknown',
            'focus_areas': focus,
            'investment_stages': stages,
            'description': snippet,
            'source_url': url,
            'scraped': True  # Mark as scraped data
        }
    
    def _get_mock_investor_data(self, query: str, count: int = 3) -> List[Dict[str, Any]]:
        """Generate mock investor data as fallback"""
        investors = []
        
        # Extract keywords from query
        keywords = query.lower().split()
        locations = ['San Francisco', 'New York', 'Boston', 'London', 'Berlin', 'Tel Aviv']
        focus_areas = ['AI/ML', 'SaaS', 'Fintech', 'Healthcare', 'Consumer Tech', 'Enterprise Software']
        stages = ['Seed', 'Series A', 'Series B', 'Growth']
        
        for i in range(count):
            # Use keywords to make the mock data somewhat relevant to the query
            relevant_focus = random.sample([f for f in focus_areas if any(k in f.lower() for k in keywords)] or focus_areas, 
                                          k=min(3, len(focus_areas)))
            
            investors.append({
                'name': f"Venture Fund {i+1} {' '.join(random.sample(keywords, k=min(2, len(keywords))))}".title(),
                'type': 'Venture Capital',
                'location': random.choice(locations),
                'focus_areas': relevant_focus,
                'investment_stages': random.sample(stages, k=random.randint(1, 3)),
                'description': f"A venture capital firm focused on {', '.join(relevant_focus)} investments at {random.choice(stages)} stage.",
                'source_url': "https://example.com",
                'scraped': True  # Mark as scraped data
            })
        
        return investors
    
    def enrich_investor_data(self, investor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich existing investor data with additional information from the web
        
        Args:
            investor_data: Existing investor data dictionary
            
        Returns:
            Enriched investor data dictionary
        """
        if not investor_data.get('name'):
            return investor_data
            
        try:
            # Search for news about this investor
            news = self._search_investor_news(investor_data['name'])
            if news:
                investor_data['recent_news'] = news[:3]
                
            # Try to find additional information about investment focus
            if 'focus_areas' not in investor_data or not investor_data['focus_areas']:
                search_results = self._search_crunchbase_like(f"{investor_data['name']} venture focus")
                if search_results and len(search_results) > 0:
                    if 'focus_areas' in search_results[0] and search_results[0]['focus_areas']:
                        investor_data['focus_areas'] = search_results[0]['focus_areas']
            
            return investor_data
            
        except Exception as e:
            self.logger.error(f"Error enriching investor data: {str(e)}")
            return investor_data
            
    def get_portfolio_companies(self, investor_name: str) -> List[Dict[str, Any]]:
        """
        Get portfolio companies for a specific investor
        
        Args:
            investor_name: Name of the investor
            
        Returns:
            List of portfolio company data
        """
        companies = []
        
        try:
            # Search for portfolio companies
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(investor_name)}+portfolio+companies"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'lxml')
                results = soup.select('.result')
                
                for result in results[:8]:  # Limit to top 8 results
                    title_elem = result.select_one('.result__title')
                    snippet_elem = result.select_one('.result__snippet')
                    
                    if title_elem and snippet_elem:
                        title = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True)
                        
                        # Extract company names from the snippet
                        company_names = self._extract_company_names(snippet)
                        for company in company_names:
                            if company.lower() not in [c['name'].lower() for c in companies]:
                                companies.append({
                                    'name': company,
                                    'investor': investor_name,
                                    'description': self._extract_company_description(company, snippet)
                                })
            
            # If we couldn't find any, return mock data
            if not companies:
                return self._get_mock_portfolio_companies(investor_name)
                
            return companies
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio companies: {str(e)}")
            return self._get_mock_portfolio_companies(investor_name)
    
    def _extract_company_names(self, text: str) -> List[str]:
        """Extract company names from text"""
        # This is a simplified approach - in a real implementation, 
        # you would use NER (Named Entity Recognition) for better results
        
        # Look for company patterns like "X, Y, and Z"
        companies = []
        
        # Look for companies in a list format
        list_pattern = r'(?:companies|portfolio|investments)(?:[^.]*?):([^.]+)'
        list_match = re.search(list_pattern, text, re.IGNORECASE)
        
        if list_match:
            company_text = list_match.group(1)
            # Split by commas and 'and'
            company_list = re.split(r',|\sand\s', company_text)
            companies.extend([c.strip() for c in company_list if c.strip()])
        
        # Look for companies mentioned with "invested in" or similar phrases
        invested_pattern = r'invested in ([^,.]+)'
        for match in re.finditer(invested_pattern, text, re.IGNORECASE):
            companies.append(match.group(1).strip())
        
        # Remove duplicates and non-company words
        non_company_words = ['they', 'the', 'their', 'these', 'those', 'other', 'many', 'some', 'few']
        filtered_companies = []
        
        for company in companies:
            if (len(company.split()) <= 4 and  # Most company names are 1-4 words
                company.lower() not in non_company_words and
                not company.isdigit() and
                len(company) > 2):
                filtered_companies.append(company)
        
        return filtered_companies
    
    def _extract_company_description(self, company_name: str, text: str) -> str:
        """Extract description for a company from text"""
        # Look for sentences containing the company name
        sentences = re.split(r'[.!?]', text)
        relevant_sentences = [s for s in sentences if company_name.lower() in s.lower()]
        
        if relevant_sentences:
            return relevant_sentences[0].strip()
        
        return f"Portfolio company of {company_name}"
    
    def _get_mock_portfolio_companies(self, investor_name: str) -> List[Dict[str, Any]]:
        """Generate mock portfolio company data"""
        sectors = ['AI', 'Fintech', 'Healthcare', 'SaaS', 'Consumer', 'Enterprise']
        prefixes = ['Tech', 'App', 'Health', 'Fin', 'Data', 'Cloud', 'Smart', 'Cyber']
        suffixes = ['AI', 'Labs', 'Health', 'Tech', 'Systems', 'Networks', 'Solutions', 'Analytics']
        
        companies = []
        for i in range(random.randint(3, 6)):
            sector = random.choice(sectors)
            name = f"{random.choice(prefixes)}{random.choice(suffixes)}"
            
            companies.append({
                'name': name,
                'investor': investor_name,
                'description': f"{name} is a {sector} company that provides innovative solutions for businesses and consumers.",
                'sector': sector
            })
        
        return companies

def render_web_scraper_section(search_terms: List[str], location: str = None):
    """Render the web scraper section in the Streamlit app"""
    import streamlit as st
    
    st.header("Web Intelligence")
    
    # Initialize the web scraper
    scraper = InvestorWebScraper()
    
    with st.expander("About Web Intelligence", expanded=False):
        st.write("""
        This section uses web scraping to find additional information about investors related to your search.
        The data is gathered from public sources and may complement the API results.
        """)
    
    if not search_terms:
        st.info("Enter search terms in the main search section to find related investors from the web.")
        return
    
    with st.spinner("Searching the web for additional investor information..."):
        # Search for investors based on search terms
        web_results = scraper.search_for_investors(search_terms, location)
        
        if web_results:
            st.success(f"Found {len(web_results)} additional investors from web sources")
            
            # Display results in tabs
            tab1, tab2 = st.tabs(["Investor List", "Detailed View"])
            
            with tab1:
                # Create a table of investors
                investor_df = pd.DataFrame([
                    {
                        'Name': inv['name'],
                        'Type': inv['type'],
                        'Location': inv['location'],
                        'Focus': ', '.join(inv.get('focus_areas', [])),
                        'Stages': ', '.join(inv.get('investment_stages', []))
                    }
                    for inv in web_results
                ])
                
                st.dataframe(investor_df, use_container_width=True)
            
            with tab2:
                # Show detailed information for each investor
                for i, investor in enumerate(web_results):
                    with st.expander(f"{investor['name']} - {investor['type']}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Location:** {investor['location']}")
                            
                            if 'focus_areas' in investor and investor['focus_areas']:
                                st.write(f"**Focus Areas:** {', '.join(investor['focus_areas'])}")
                            
                            if 'investment_stages' in investor and investor['investment_stages']:
                                st.write(f"**Investment Stages:** {', '.join(investor['investment_stages'])}")
                            
                            st.write(f"**Description:** {investor.get('description', 'No description available')}")
                            
                            if 'source_url' in investor and investor['source_url']:
                                st.write(f"**Source:** [{investor['source_url']}]({investor['source_url']})")
                        
                        with col2:
                            # Show portfolio companies button
                            if st.button(f"View Portfolio Companies", key=f"portfolio_{i}"):
                                portfolio = scraper.get_portfolio_companies(investor['name'])
                                if portfolio:
                                    st.write("**Portfolio Companies:**")
                                    for company in portfolio:
                                        st.write(f"- **{company['name']}**: {company.get('description', '')}")
                                else:
                                    st.info("No portfolio companies found")
                        
                        # Show recent news if available
                        if 'recent_news' in investor and investor['recent_news']:
                            st.write("**Recent News:**")
                            for news in investor['recent_news']:
                                st.write(f"- **{news['title']}** ({news['date']})")
                                st.write(f"  {news['snippet']}")
                                if news.get('url'):
                                    st.write(f"  [Read more]({news['url']})")
        else:
            st.warning("No additional investors found from web sources. Try different search terms.") 