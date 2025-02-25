"""Configuration for web scraping"""

# Rate limiting configuration
RATE_LIMITS = {
    'default': {'requests': 30, 'window': 60},  # 30 requests per minute
    'crunchbase': {'requests': 20, 'window': 60},  # 20 requests per minute
    'angellist': {'requests': 30, 'window': 60},   # 30 requests per minute
    'vcguide': {'requests': 40, 'window': 60}      # 40 requests per minute
}
