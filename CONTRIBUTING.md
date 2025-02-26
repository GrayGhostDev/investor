# Contributing to Investor Search Platform

Thank you for considering contributing to the Investor Search Platform! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue with the following information:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, browser, etc.)

### Suggesting Enhancements

If you have ideas for new features or improvements, please create an issue with:

- A clear, descriptive title
- Detailed description of the enhancement
- Rationale: why this would be useful
- Any implementation ideas you have

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests if available
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a Pull Request

#### Pull Request Guidelines

- Follow the existing code style
- Include comments in your code where necessary
- Update documentation if needed
- Add tests for new features
- Ensure all tests pass

## Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/YOUR_USERNAME/investor-search-platform.git
   cd investor-search-platform
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scriptsctivate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   ```
   export OPENAI_API_KEY="your-api-key"
   ```

5. Run the application:
   ```
   python -m streamlit run main.py
   ```

## Project Structure

- `main.py`: Main application entry point
- `InvestorSearchTool.py`: Core investor search functionality
- `database.py`: Database connection and operations
- `components/`: Application components
  - `search.py`: Investor search interface
  - `matching_algorithm.py`: Investor matching algorithm
  - `web_scraper.py`: Web scraping functionality
  - `dashboard.py`: Data visualization dashboard
  - `pitch_deck.py`: Pitch deck generator
  - `sentiment.py`: Market sentiment analysis
  - `comparison.py`: Investor comparison tool
  - `translator.py`: Translation functionality
  - `email_alerts.py`: Email notification system
- `utils/`: Utility functions and helpers
