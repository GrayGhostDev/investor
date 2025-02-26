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
    "requests", 
    "beautifulsoup4",
    "fake_useragent"
]

# Optional packages that have fallbacks
optional_packages = [
    "geopy",
    "scikit-learn"
]

missing_required_packages = []
missing_optional_packages = []

# Check required packages
for package in required_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        missing_required_packages.append(package)

# Check optional packages
for package in optional_packages:
    try:
        importlib.import_module(package)
    except ImportError:
        missing_optional_packages.append(package)

# Show warnings for missing packages
if missing_required_packages:
    st.error(f"Missing required packages: {', '.join(missing_required_packages)}")
    st.info("Please install the missing packages or check your environment.")
    st.stop()

if missing_optional_packages:
    st.warning(f"Some optional packages are missing: {', '.join(missing_optional_packages)}")
    st.info("The application will use fallback implementations for these features.")

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
        for module in ["pandas", "sqlalchemy", "openai", "requests", "bs4", "fake_useragent"]:
            try:
                importlib.import_module(module)
                st.write(f"✅ {module} imported successfully")
            except ImportError as e:
                st.write(f"❌ Failed to import {module}: {str(e)}")
                
        st.write("### Optional Module Import Tests")
        for module in ["geopy", "sklearn"]:
            try:
                importlib.import_module(module)
                st.write(f"✅ {module} imported successfully")
            except ImportError as e:
                st.write(f"⚠️ Optional module {module} not available: {str(e)}")
                
        # Check for specific scikit-learn components
        if "sklearn" not in missing_optional_packages:
            st.write("### Scikit-learn Component Tests")
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                st.write("✅ TfidfVectorizer imported successfully")
            except ImportError as e:
                st.write(f"❌ Failed to import TfidfVectorizer: {str(e)}")
                
            try:
                from sklearn.metrics.pairwise import cosine_similarity
                st.write("✅ cosine_similarity imported successfully")
            except ImportError as e:
                st.write(f"❌ Failed to import cosine_similarity: {str(e)}")
                
        # Provide suggestions for fixing the issues
        st.write("### Suggestions")
        st.write("If you're seeing import errors, try the following:")
        st.write("1. Make sure all required packages are installed: `pip install -r requirements-streamlit.txt`")
        st.write("2. Check that you're using a compatible Python version (3.7-3.10)")
        st.write("3. If using Streamlit Cloud, make sure to set the requirements file to `requirements-streamlit.txt` in Advanced Settings")