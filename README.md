# Investor Search Platform

An advanced investor search and analysis platform that provides comprehensive data exploration, interactive insights, and AI-powered tools for investment research.

## Features

- 🔍 **Advanced Investor Search**: Comprehensive filtering and search capabilities
- 📊 **Interactive Dashboard**: Visual data exploration and analysis
- 📈 **Investment Analysis**: Detailed visualizations and metrics
- 📝 **AI-Powered Pitch Deck Generator**: Create customized investor presentations
- 🔄 **Investor Comparison**: Side-by-side investor analysis
- 📡 **Real-time Market Sentiment**: Track market trends and sentiment
- 🔤 **Financial Jargon Translator**: Simplify complex financial terms

## Technology Stack

- **Frontend**: Streamlit
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Data Processing**: Python, Pandas
- **Visualization**: Plotly
- **AI Integration**: OpenAI API
- **Web Scraping**: Trafilatura

## Project Structure

```
├── .streamlit/          # Streamlit configuration
├── assets/             # Static assets and styles
├── components/         # UI components
│   ├── search.py       # Search functionality
│   ├── dashboard.py    # Dashboard views
│   ├── visualizations.py # Data visualizations
│   ├── pitch_deck.py   # Pitch deck generator
│   ├── comparison.py   # Investor comparison
│   ├── sentiment.py    # Market sentiment tracker
│   └── translator.py   # Jargon translator
├── database.py        # Database configuration
├── main.py           # Main application entry
└── InvestorSearchTool.py # Core search functionality
```

## Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/investor-search-platform.git
cd investor-search-platform
```

2. Set up environment variables:
```bash
# Database configuration
export DATABASE_URL=your_database_url
export PGHOST=your_db_host
export PGPORT=your_db_port
export PGUSER=your_db_user
export PGPASSWORD=your_db_password
export PGDATABASE=your_db_name

# OpenAI API configuration
export OPENAI_API_KEY=your_openai_api_key
```

3. Run the application:
```bash
streamlit run main.py
```

## Dependencies

The application requires the following Python packages:
- streamlit
- pandas
- plotly
- sqlalchemy
- psycopg2-binary
- openai
- trafilatura
- fake-useragent
- openpyxl
- xlsxwriter
- beautifulsoup4

## Usage

1. **Search**: Use the search tab to find investors based on various criteria
2. **Dashboard**: View key metrics and insights about selected investors
3. **Analysis**: Explore detailed visualizations and trends
4. **Pitch Deck**: Generate AI-powered pitch deck content
5. **Compare**: Compare multiple investors side by side
6. **Market Sentiment**: Track real-time market trends
7. **Translator**: Translate complex financial terms

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.