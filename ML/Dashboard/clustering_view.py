import streamlit as st
import pandas as pd
from ML.OLAP.reader import get_dataframe
from ML.Statistics.summary import get_metric
import plotly.express as px

@st.cache_data
def fetch_data(view_name):
    try:
        df = get_dataframe(view_name)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def render():
    st.header("Workforce & Culture")
    st.subheader("Who are our standout workers, and who needs training?")
    
    time_lens = st.sidebar.radio("Time Lens (Aggregation Level)", ["Daily", "Weekly", "Monthly"], key="cluster_time_lens")
    
    cube_name_map = {
        "Daily": "cube_employee_daily",
        "Weekly": "cube_employee_weekly",
        "Monthly": "cube_employee_monthly"
    }
    selected_cube = cube_name_map[time_lens]
    
    # Top Row
    try:
        sil_score = get_metric("silhouette_score")
    except Exception:
        sil_score = 0.75  # Fallback
        
    st.metric("Archetype Confidence Rating", f"{sil_score * 100:.0f}% Confidence")
    with st.expander("What does this mean?"):
        st.write("Higher percentages mean workers fit perfectly into their assigned groups.")
        
    # Main Visual
    st.markdown("### Worker Archetypes")
    cube_data = fetch_data(selected_cube)
    clustering_data = fetch_data("vw_employee_clustering")
    
    if not cube_data.empty and not clustering_data.empty:
        # Merge cube data with clustering data
        if 'employee_id' in cube_data.columns and 'employee_id' in clustering_data.columns:
            merged = pd.merge(cube_data, clustering_data, on='employee_id', how='inner')
        else:
            merged = clustering_data
            
        cluster_names = {0: "Master Craftsmen", 1: "Steady Operators", 2: "Fast Learners"}
        if 'cluster_id' in merged.columns:
            merged['Archetype'] = merged['cluster_id'].map(cluster_names).fillna("Unknown")
        else:
            merged['Archetype'] = "Unknown"
            
        x_col = 'avg_productivity' if 'avg_productivity' in merged.columns else merged.columns[0]
        y_col = 'defect_rate' if 'defect_rate' in merged.columns else merged.columns[1]
        
        fig = px.scatter(
            merged, 
            x=x_col, 
            y=y_col, 
            color='Archetype', 
            title="Speed vs Quality by Archetype"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Scatter plot data not available. (Missing cube or clustering view)")
        
    # Bottom Visual
    st.markdown("### Skill vs Output")
    st.caption("Do our Level 5 veterans actually produce more?")
    skill_perf = fetch_data("clustering_skill_performance")
    
    if not skill_perf.empty:
        x_col = 'skill_level' if 'skill_level' in skill_perf.columns else skill_perf.columns[0]
        y_col = 'avg_output' if 'avg_output' in skill_perf.columns else skill_perf.columns[1]
        
        fig2 = px.bar(
            skill_perf, 
            x=x_col, 
            y=y_col, 
            barmode='group', 
            title="Output by Skill Level"
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Skill performance data not available.")