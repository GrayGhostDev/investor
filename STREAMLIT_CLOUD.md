# Deploying to Streamlit Cloud

This guide explains how to deploy the Investor Search Platform to Streamlit Cloud.

## Prerequisites

1. A GitHub account
2. Your repository pushed to GitHub
3. A Streamlit Cloud account
4. An OpenAI API key

## Deployment Steps

1. **Log in to Streamlit Cloud**
   - Go to https://streamlit.io/cloud and sign in with your GitHub account

2. **Create a New App**
   - Click "New app"
   - Select your GitHub repository (GrayGhostDev/investor)
   - Select the branch (main)
   - Set the main file path to `streamlit_app.py`
   - Click "Deploy"

3. **Configure Secrets**
   - Once your app is created, go to the app settings
   - Click on "Secrets"
   - Add your secrets in TOML format:
     ```toml
     # OpenAI API key (required)
     OPENAI_API_KEY = "your-openai-api-key"
     
     # Database connection (optional)
     # DATABASE_URL = "your-database-url-here"
     ```
   - Click "Save"

4. **Verify Dependencies**
   - Ensure that all required packages are listed in `requirements.txt`
   - The following packages are essential for the application:
     - streamlit
     - openai
     - geopy
     - beautifulsoup4
     - requests
     - pandas
     - sqlalchemy
     - httpx

5. **Troubleshooting Common Issues**
   - **Module Not Found Errors**: If you see "ModuleNotFoundError", check that the package is listed in requirements.txt
   - **API Key Issues**: Ensure your OpenAI API key is valid and has sufficient credits
   - **Path Issues**: The application uses relative imports, so ensure the file structure matches the repository
   - **Database Errors**: If using a custom database, ensure the connection string is correct in secrets

6. **Monitoring Your App**
   - Use the "Manage app" button in Streamlit Cloud to:
     - View logs
     - Check resource usage
     - Restart the app if needed
     - Update settings

7. **Updating Your App**
   - Simply push changes to your GitHub repository
   - Streamlit Cloud will automatically detect changes and rebuild your app

## File Structure for Deployment

```
investor/
├── .streamlit/
│   ├── config.toml
│   └── secrets.toml (local only, not in repo)
├── components/
│   ├── search.py
│   ├── matching_algorithm.py
│   └── ... (other components)
├── main.py
├── streamlit_app.py (entry point for Streamlit Cloud)
├── InvestorSearchTool.py
├── requirements.txt
└── ... (other files)
```

</rewritten_file>

