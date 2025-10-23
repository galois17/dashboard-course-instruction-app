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

st.title("Hello World!")
st.write("Eeek...")

button = st.button("Say Hello")
if button:
    st.write("Hello there!")

