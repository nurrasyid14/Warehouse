import streamlit as st
import pandas as pd
import plotly.express as px
from ML.OLAP.reader import get_dataframe

@st.cache_data
def fetch_data(view_name):
    try:
        df = get_dataframe(view_name)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def render():
    st.header("The Factory Floor (Operations)")
    st.subheader("Where are our bottlenecks?")
    
    time_lens = st.sidebar.radio("Time Lens (Aggregation Level)", ["Daily", "Weekly", "Monthly"], key="stats_time_lens")
    
    cube_name_map = {
        "Daily": "cube_workshop_daily",
        "Weekly": "cube_workshop_weekly",
        "Monthly": "cube_workshop_monthly"
    }
    selected_cube = cube_name_map[time_lens]
    
    # Main Visual
    st.markdown("### Output vs Defects by Workshop")
    cube_data = fetch_data(selected_cube)
    
    if not cube_data.empty:
        workshop_col = 'workshop_name' if 'workshop_name' in cube_data.columns else cube_data.columns[0]
        y_cols = [c for c in ['total_output', 'total_defects'] if c in cube_data.columns]
        if not y_cols:
            y_cols = cube_data.columns[1:3].tolist()
            
        fig1 = px.bar(cube_data, x=workshop_col, y=y_cols, barmode='group')
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("Workshop cube data not available.")
        
    # Secondary Visual
    st.markdown("### Productivity by Furnace Type")
    if not cube_data.empty and 'furnace_type' in cube_data.columns and 'avg_productivity' in cube_data.columns:
        fig2 = px.bar(cube_data, x='avg_productivity', y='furnace_type', orientation='h')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Furnace productivity data not available in the current cube.")
        
    # Data Table
    st.markdown("### Production Overview")
    prod_overview = fetch_data("production_overview")
    
    if not prod_overview.empty:
        # Streamlit Native Filtering
        filter_col1, filter_col2 = st.columns(2)
        filtered_data = prod_overview.copy()
        
        with filter_col1:
            if 'season' in filtered_data.columns:
                seasons = filtered_data['season'].dropna().unique().tolist()
                selected_seasons = st.multiselect("Filter by Season", options=seasons, default=seasons)
                filtered_data = filtered_data[filtered_data['season'].isin(selected_seasons)]
                
        with filter_col2:
            if 'workshop_name' in filtered_data.columns:
                workshops = filtered_data['workshop_name'].dropna().unique().tolist()
                selected_workshops = st.multiselect("Filter by Workshop", options=workshops, default=workshops)
                filtered_data = filtered_data[filtered_data['workshop_name'].isin(selected_workshops)]
                
        st.dataframe(filtered_data, use_container_width=True)
    else:
        st.info("Production overview data not available.")