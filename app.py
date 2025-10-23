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


def show_daily_events():
    st.markdown(f"<h3 style='color:{HEADER_COLOR}'> Daily Events (7-Day Rolling Average)</h3>", unsafe_allow_html=True)
    df = load_csv("ga4_events_daily.csv")
    df["event_date"] = pd.to_datetime(df["event_date"], format="%Y%m%d", errors="coerce")

                              
    min_ts, max_ts = df["event_date"].min(), df["event_date"].max()
    min_date, max_date = min_ts.date(), max_ts.date()

                              
    if "date_range" not in st.session_state:
        st.session_state["date_range"] = (min_date, max_date)
    if "events_selected" not in st.session_state:
        all_events = sorted(df["event_name"].unique())
        st.session_state["events_selected"] = all_events[:3]

                     
    col_filter1, col_filter2 = st.columns([3, 1])
    with col_filter1:
        start, end = st.slider(
            "Select Date Range",
            min_value=min_date,
            max_value=max_date,
            value=st.session_state["date_range"],
            key="date_range",
        )
    with col_filter2:
        if st.button("🔄 Reset Filters"):
            for k in ["date_range", "events_selected"]:
                if k in st.session_state:
                    del st.session_state[k]
            try:
                st.rerun()
            except Exception:
                st.experimental_rerun()

                            
    df = df[(df["event_date"].dt.date >= start) & (df["event_date"].dt.date <= end)]

                            
    all_events = sorted(df["event_name"].unique())
    selected = st.multiselect(
        "Select Events",
        options=all_events,
        default=st.session_state.get("events_selected", all_events[:3]),
        key="events_selected",
    )
    filtered = df[df["event_name"].isin(selected)]

                     
    col1, col2 = st.columns(2)
    col1.metric("Total Events", f"{filtered['event_count'].sum():,}")
    col2.metric("Event Types", f"{len(selected)} selected")

                    
    tab1, tab2 = st.tabs(["Event Counts", "Rolling Average"])
    chart_df = filtered.pivot(index="event_date", columns="event_name", values="event_count")
    avg_df = (
        filtered.pivot(index="event_date", columns="event_name", values="rolling_7d_avg")
        if "rolling_7d_avg" in df.columns
        else None
    )

    with tab1:
        fig = px.line(chart_df, markers=True, title="Event Counts over Time")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if avg_df is not None:
            fig2 = px.line(avg_df, markers=False, title="7-Day Rolling Average")
            st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(filtered, use_container_width=True)




                                    
PAGES = {
    "Daily Events": show_daily_events,

}

                              
st.markdown(
    f"<h2 style='text-align:center; color:{ACCENT_COLOR};'>GA4 Analytics Dashboard</h2>",
    unsafe_allow_html=True,
)

                               
st.sidebar.markdown("## Navigation")
page = st.sidebar.radio("Go to", list(PAGES.keys()))
PAGES[page]()

                              
st.markdown("---")
st.caption("🌙")
