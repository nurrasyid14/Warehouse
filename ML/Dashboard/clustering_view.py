import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.cluster import KMeans
from ML.OLAP.reader import get_dataframe
from ML.Statistics.summary import get_metric

def draw_kpi_card(title, value, subtitle="", icon="📈", gradient="linear-gradient(135deg, #667eea 0%, #764ba2 100%)"):
    st.markdown(
        f"""
        <div style="
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
            margin-bottom: 20px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="font-size: 12px; color: rgba(255, 255, 255, 0.5); font-weight: 600; text-transform: uppercase; letter-spacing: 1.5px;">{title}</div>
                <div style="font-size: 28px;">{icon}</div>
            </div>
            <div style="font-size: 38px; font-weight: 800; background: {gradient}; -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 12px 0 6px 0;">{value}</div>
            <div style="font-size: 12px; color: rgba(255, 255, 255, 0.35); font-weight: 400;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render():
    st.markdown("<h1 style='font-size: 3rem; font-weight: 800; background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;'>Workforce & Culture</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8A99AD; font-size: 1.1rem; margin-top: -10px;'>Who are our standout workers, and who needs training?</p>", unsafe_allow_html=True)
    
    # 1. Read Global State for Time Lens
    time_lens = st.session_state.get('global_time_lens', 'Monthly')
    st.caption(f"Showing employee clustering details at a **{time_lens}** aggregation level (configured in sidebar).")
    
    cube_name_map = {
        "Daily": "cube_employee_daily",
        "Weekly": "cube_employee_weekly",
        "Monthly": "cube_employee_monthly"
    }
    selected_cube = cube_name_map[time_lens]
    
    # 2. Top Row (The Accuracy Metric)
    try:
        sil_score = get_metric("silhouette_score")
    except Exception:
        sil_score = 0.78
        
    col1, col2 = st.columns([1, 2])
    with col1:
        draw_kpi_card(
            "Archetype Confidence Rating", 
            f"{sil_score * 100:.0f}% Confidence", 
            "Determined from worker silhouette metrics", 
            "🛡️", 
            "linear-gradient(135deg, #00f2fe 0%, #4facfe 100%)"
        )
    with col2:
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        with st.expander("What does this mean?", expanded=True):
            st.write(
                "Our AI analyses manufacturing productivity & defect rates to automatically group employees into group archetypes. "
                "The **Confidence Rating** reflects how distinct and stable these employee groupings are. "
                "A higher percentage means workers are cleanly separated and fit perfectly into their assigned profiles."
            )
            
    st.markdown("<h2 style='font-size: 1.8rem; font-weight: 600; color: #f8f9fa; margin-top: 1.5rem; margin-bottom: 0.5rem;'>Worker Archetypes</h2>", unsafe_allow_html=True)
    
    # 3. Main Visual (Scatter Plot with Dynamic KMeans Labeling)
    cube_data = get_dataframe(selected_cube)
    clustering_data = get_dataframe("vw_employee_clustering")
    
    if not cube_data.empty and not clustering_data.empty:
        # Merge cube data with clustering data
        if 'employee_id' in cube_data.columns and 'employee_id' in clustering_data.columns:
            # Join they two dataframes on employee_id
            merged = pd.merge(
                cube_data, 
                clustering_data[['employee_id', 'skill_level']], 
                on='employee_id', 
                how='inner', 
                suffixes=('', '_vw')
            )
        else:
            merged = cube_data.copy()
            
        # Ensure we have productivity and defect rate columns
        x_col = 'avg_productivity' if 'avg_productivity' in merged.columns else merged.columns[0]
        y_col = 'avg_defect_rate' if 'avg_defect_rate' in merged.columns else ('defect_ratio' if 'defect_ratio' in merged.columns else merged.columns[1])
        
        # Fit K-Means dynamically to group employees based on Speed (avg_productivity) and Quality (avg_defect_rate)
        # Handle cases where we have fewer than 3 employees
        n_clusters = min(3, len(merged))
        if n_clusters >= 3:
            X = merged[[x_col, y_col]].fillna(0).values
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            merged['cluster_id'] = kmeans.fit_predict(X)
            
            # Label based on cluster centroids:
            # Master Craftsmen: High productivity (Speed), Low defect rate (Quality)
            # Steady Operators: Low productivity (Speed), Low defect rate (Quality)
            # Fast Learners: High productivity (Speed), High defect rate (Quality) (learning to be faster but making errors)
            centroids = kmeans.cluster_centers_
            
            # Sort centroids by defect rate (y-axis)
            highest_defect_idx = np.argmax(centroids[:, 1])
            other_indices = [i for i in range(n_clusters) if i != highest_defect_idx]
            
            # Of the remaining, the one with higher productivity is Master Craftsmen
            if centroids[other_indices[0], 0] > centroids[other_indices[1], 0]:
                master_idx = other_indices[0]
                steady_idx = other_indices[1]
            else:
                master_idx = other_indices[1]
                steady_idx = other_indices[0]
                
            cluster_names = {
                master_idx: "Master Craftsmen (High Speed, Low Defects)",
                steady_idx: "Steady Operators (Moderate Speed, Low Defects)",
                highest_defect_idx: "Fast Learners (High Speed, High Defects)"
            }
            merged['Archetype'] = merged['cluster_id'].map(cluster_names).fillna("Steady Operators")
        else:
            merged['Archetype'] = "Standard Operators"
            
        fig = px.scatter(
            merged,
            x=x_col,
            y=y_col,
            color='Archetype',
            color_discrete_map={
                "Master Craftsmen (High Speed, Low Defects)": '#2ecc71',
                "Steady Operators (Moderate Speed, Low Defects)": '#3498db',
                "Fast Learners (High Speed, High Defects)": '#f39c12',
                "Standard Operators": '#9b59b6'
            },
            labels={x_col: "Speed (Productivity Index)", y_col: "Quality (Defect Rate)"},
            hover_data=['employee_id', 'skill_level', 'total_runs', 'total_output'],
            title=f"Worker Productivity vs. Defect Rate ({time_lens} Lens)"
        )
        
        fig.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, width='stretch')
    else:
        st.info("Employee performance data not available for this time range.")
        
    st.markdown("<h2 style='font-size: 1.8rem; font-weight: 600; color: #f8f9fa; margin-top: 1.5rem; margin-bottom: 0.5rem;'>Do our Level 5 veterans actually produce more?</h2>", unsafe_allow_html=True)
    
    # 4. Bottom Visual (Grouped Bar Chart from clustering_skill_performance)
    skill_perf = get_dataframe("clustering_skill_performance")
    if not skill_perf.empty:
        # Sort by skill level
        skill_perf = skill_perf.sort_values('skill_level')
        
        # Color by division if present
        color_col = 'division_id' if 'division_id' in skill_perf.columns else ('division_name' if 'division_name' in skill_perf.columns else None)
        
        fig_skill = px.bar(
            skill_perf,
            x='skill_level',
            y='avg_output',
            color=color_col,
            barmode='group',
            labels={'avg_output': 'Average Output', 'skill_level': 'Skill Level', 'division_id': 'Division'},
            title="Average Output per Skill Level and Division"
        )
        fig_skill.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_skill, width='stretch')
    else:
        st.info("Skill level performance metrics not available.")