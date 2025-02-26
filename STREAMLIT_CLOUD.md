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
     
