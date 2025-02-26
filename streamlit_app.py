import os
import streamlit as st
import sys
import importlib
import traceback

# Configure page
st.set_page_config(
    page_title="Investor Search Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Display a loading message
st.write("# Investor Search Platform")
st.write("Loading application...")

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up environment variables from Streamlit secrets
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    
if "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]

# Check for required dependencies
required_packages = [
    "streamlit", 
    "pandas", 
    "sqlalchemy", 
    "openai", 
    "geopy", 
    "requests", 
    "beautifulsoup4",
    "fake_useragent",
    "scikit-learn"
]

missing_packages = []
for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    st.error(f"Missing required packages: {', '.join(missing_packages)}")
    st.info("Please install the missing packages or check your environment.")
    st.stop()

try:
    # Import the main application
    from main import main
    
    # Run the main application
    if __name__ == "__main__":
        main()
except Exception as e:
    st.error(f"Error loading application: {str(e)}")
    
    # Get detailed traceback
    error_details = traceback.format_exc()
    
    # Show debugging information in an expander
    with st.expander("Debugging Information", expanded=True):
        st.write("### System Information")
        st.write(f"Python version: {sys.version}")
        st.write(f"Current directory: {os.getcwd()}")
        
        st.write("### Directory Contents")
        st.write(f"Root directory: {os.listdir('.')}")
        if os.path.exists('components'):
            st.write(f"Components directory: {os.listdir('components')}")
        
        st.write("### Error Details")
        st.code(error_details)
        
        st.write("### Environment Variables")
        st.write("OPENAI_API_KEY: " + ("Set" if "OPENAI_API_KEY" in os.environ else "Not set"))
        st.write("DATABASE_URL: " + ("Set" if "DATABASE_URL" in os.environ else "Not set"))
        
        # Try to import specific modules to see where it fails
        st.write("### Module Import Tests")
        for module in ["geopy", "pandas", "sqlalchemy", "openai", "requests", "bs4", "fake_useragent", "sklearn"]:
            try:
                importlib.import_module(module)
                st.write(f"✅ {module} imported successfully")
            except ImportError as e:
                st.write(f"❌ Failed to import {module}: {str(e)}")