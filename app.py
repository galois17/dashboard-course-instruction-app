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


def show_daily_events() -> None:
    """
    """
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


def show_top_pages():
    """
    """
    st.markdown(f"<h3 style='color:{HEADER_COLOR}'> Top Pages</h3>", unsafe_allow_html=True)
    df = load_csv("ga4_top_pages.csv")

    col1, col2 = st.columns([2, 1])
    with col1:
        if "avg_time_on_page_sec" in df.columns:
            fig = px.scatter(
                df, x="page_views", y="avg_time_on_page_sec",
                size="bounce_rate" if "bounce_rate" in df.columns else None,
                hover_data=["page_title"],
                title="Page Views vs Avg Time on Page (bubble size = bounce rate)"
            )
        else:
            fig = px.bar(df.head(15), x="page_views", y="page_title",
                         orientation="h", title="Top 15 Pages by Views")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("Top Page", df.loc[df["page_views"].idxmax(), "page_title"])
        st.metric("Total Views", f"{df['page_views'].sum():,}")

    st.dataframe(df.head(25), use_container_width=True)

def show_top_countries():
    """
    """
    st.markdown(f"<h3 style='color:{HEADER_COLOR}'>Top Countries</h3>", unsafe_allow_html=True)
    df = load_csv("ga4_top_countries.csv")

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = px.bar(df, x="users", y="country", orientation="h",
                     title="Users by Country", height=500)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.metric("Top Country", df.loc[df["users"].idxmax(), "country"])
        st.metric("Total Users", f"{df['users'].sum():,}")

    if "conversion_rate" in df.columns:
        st.subheader("Conversion Rate vs Users")
        fig = px.scatter(
            df, x="users", y="conversion_rate",
            size="avg_session_duration" if "avg_session_duration" in df.columns else None,
            color="conversion_rate", hover_data=["country"],
            title="Conversion Rate by Country"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


def show_devices():
    """
    """
    st.markdown(f"<h3 style='color:{HEADER_COLOR}'>Device Breakdown</h3>", unsafe_allow_html=True)
    df = load_csv("ga4_devices.csv")

    fig = px.pie(df, names="device_type", values="users",
                 title="Users by Device Type", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

    if "avg_sessions_per_user" in df.columns:
        fig = px.bar(df, x="device_type", y="avg_sessions_per_user",
                     title="Average Sessions per User by Device")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


def show_traffic_sources():
    """
    """
    st.markdown(f"<h3 style='color:{HEADER_COLOR}'>Traffic Sources</h3>", unsafe_allow_html=True)
    df = load_csv("ga4_traffic_sources.csv")

    fig = px.bar(df, x="source", y="users", color="medium",
                 title="Users by Source / Medium", height=500)
    st.plotly_chart(fig, use_container_width=True)

    if "conversion_rate" in df.columns:
        st.subheader("CTR vs Conversion Rate")
        fig = px.scatter(
            df, x="click_through_rate", y="conversion_rate",
            size="users", color="medium", hover_data=["source"],
            title="Click-through vs Conversion Rate"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


def show_hourly_activity():
    st.markdown(f"<h3 style='color:{HEADER_COLOR}'>Hourly Activity</h3>", unsafe_allow_html=True)
    df = load_csv("ga4_hourly_activity.csv")

    if {"event_share", "engagement_intensity"}.issubset(df.columns):
        tab1, tab2 = st.tabs(["Event Share", "Engagement Intensity"])
        with tab1:
            fig = px.density_heatmap(df, x="hour", y="event_name", z="event_share",
                                     color_continuous_scale="Blues", title="Event Share by Hour")
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            fig = px.box(df, x="event_name", y="engagement_intensity",
                         title="Engagement Intensity by Event")
            st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.density_heatmap(df, x="hour", y="event_name", z="events",
                                 color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


                                    
PAGES = {
    "Daily Events": show_daily_events,
    "Top Pages": show_top_pages,
    "Top Countries": show_top_countries,
    "Devices": show_devices,
    "Traffic Sources": show_traffic_sources,
    "Hourly Activity": show_hourly_activity,
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
