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
   - **Important**: In the "Advanced Settings" section, set the requirements file to `requirements-streamlit.txt` instead of the default `requirements.txt`
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
   - The `requirements-streamlit.txt` file contains only the essential packages with relaxed version constraints
   - This approach helps avoid dependency conflicts on Streamlit Cloud
   - The following packages are included:
     - streamlit
     - openai
     - geopy
     - beautifulsoup4
     - requests
     - pandas
     - sqlalchemy
     - httpx
     - scikit-learn
     - and other essential dependencies

5. **Troubleshooting Common Issues**
   - **Module Not Found Errors**: 
     - If you see "ModuleNotFoundError", check the app logs in Streamlit Cloud
     - The enhanced error handling in streamlit_app.py will show which modules are missing
     - You may need to manually add the missing package to requirements-streamlit.txt
   
   - **API Key Issues**: 
     - Ensure your OpenAI API key is valid and has sufficient credits
     - Check that it's properly set in the Streamlit Cloud secrets
   
   - **Path Issues**: 
     - The application uses relative imports, so ensure the file structure matches the repository
     - The streamlit_app.py file includes debugging information to help identify path issues
   
   - **Database Errors**: 
     - If using a custom database, ensure the connection string is correct in secrets
     - The application will fall back to SQLite if no database URL is provided

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
├── requirements.txt (full dependencies for local development)
├── requirements-streamlit.txt (simplified dependencies for Streamlit Cloud)
└── ... (other files)
```

</rewritten_file>

