import os
import streamlit as st
import sys

# Add the current directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up environment variables from Streamlit secrets
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
    
if "DATABASE_URL" in st.secrets:
    os.environ["DATABASE_URL"] = st.secrets["DATABASE_URL"]

# Print debugging information
st.set_page_config(
    page_title="Investor Search Platform",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Display a message while the app is loading
st.write("Loading application...")

try:
    # Import the main application
    from main import main
    
    # Run the main application
    if __name__ == "__main__":
        main()
except Exception as e:
    st.error(f"Error loading application: {str(e)}")
    st.write("Debugging information:")
    st.write(f"Python version: {sys.version}")
    st.write(f"Current directory: {os.getcwd()}")
    st.write(f"Directory contents: {os.listdir('.')}")
    if os.path.exists('components'):
        st.write(f"Components directory contents: {os.listdir('components')}")
    
    # Try to import specific modules to see where it fails
    try:
        import geopy
        st.write("geopy imported successfully")
    except ImportError as e:
        st.write(f"Failed to import geopy: {str(e)}")