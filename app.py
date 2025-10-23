import os
import streamlit as st
import pandas as pd
import plotly.express as px

                                  
st.set_page_config(
    page_title="GA4 Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

DATA_DIR = "data"

                                            
px.defaults.template = "plotly_dark"
px.defaults.color_discrete_sequence = px.colors.qualitative.Safe
HEADER_COLOR = "#FDFEFE"
ACCENT_COLOR = "#58D68D"


@st.cache_data
def load_csv(filename: str) -> pd.DataFrame:
    """Load CSV from data/ folder with caching."""
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        st.error(f"File not found: {filename}")
        st.stop()
    return pd.read_csv(path)

button = st.button("Say Hello")
if button:
    st.write("Hello there!")

