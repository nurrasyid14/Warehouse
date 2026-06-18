import streamlit as st
import pandas as pd
import plotly.express as px
from ML.OLAP.reader import get_dataframe

def render():
    st.markdown("<h1 style='font-size: 3rem; font-weight: 800; background: linear-gradient(45deg, #00f2fe 0%, #4facfe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 0.5rem;'>The Factory Floor</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #8A99AD; font-size: 1.1rem; margin-top: -10px;'>Where are our bottlenecks?</p>", unsafe_allow_html=True)
    
    # 1. Read Global State for Time Lens
    time_lens = st.session_state.get('global_time_lens', 'Monthly')
    st.caption(f"Showing workshop operations at a **{time_lens}** aggregation level (configured in sidebar).")
    
    cube_name_map = {
        "Daily": "cube_workshop_daily",
        "Weekly": "cube_workshop_weekly",
        "Monthly": "cube_workshop_monthly"
    }
    selected_cube = cube_name_map[time_lens]
    
    cube_data = get_dataframe(selected_cube)
    
    if not cube_data.empty:
        # Determine the latest period slice to display exactly one row per workshop (No Pandas groupby/resample)
        if 'full_date' in cube_data.columns:
            latest_val = cube_data['full_date'].max()
            display_data = cube_data[cube_data['full_date'] == latest_val].copy()
            period_label = f"Date: {latest_val}"
        elif 'week_of_year' in cube_data.columns:
            latest_year = cube_data['year'].max()
            latest_week = cube_data[cube_data['year'] == latest_year]['week_of_year'].max()
            display_data = cube_data[(cube_data['year'] == latest_year) & (cube_data['week_of_year'] == latest_week)].copy()
            period_label = f"Year {latest_year} Week {latest_week}"
        elif 'month' in cube_data.columns:
            latest_year = cube_data['year'].max()
            latest_month = cube_data[cube_data['year'] == latest_year]['month'].max()
            display_data = cube_data[(cube_data['year'] == latest_year) & (cube_data['month'] == latest_month)].copy()
            period_label = f"Year {latest_year} Month {latest_month}"
        else:
            display_data = cube_data.copy()
            period_label = "All Periods"
            
        st.markdown(f"### Output vs Defects by Workshop ({period_label})")
        
        # Build comparing Output vs Defects bar chart
        # Melt the display data so we can compare total_output vs total_defects side-by-side
        melted_workshop = display_data.melt(
            id_vars=['workshop_name'],
            value_vars=['total_output', 'total_defects'],
            var_name='Metric',
            value_name='Quantity'
        )
        
        fig_workshop = px.bar(
            melted_workshop,
            x='workshop_name',
            y='Quantity',
            color='Metric',
            barmode='group',
            color_discrete_map={'total_output': '#00f2fe', 'total_defects': '#ff7675'},
            labels={'Quantity': 'Quantity Count', 'workshop_name': 'Workshop Name'},
            title="Production Output vs. Detected Defects"
        )
        fig_workshop.update_layout(
            template="plotly_dark",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_workshop, width='stretch')
        
        st.markdown(f"### Productivity by Furnace Type ({period_label})")
        if 'furnace_type' in display_data.columns and 'avg_productivity' in display_data.columns:
            # Sort display data for cleaner display
            display_data = display_data.sort_values('avg_productivity')
            fig_furnace = px.bar(
                display_data,
                x='avg_productivity',
                y='furnace_type',
                color='workshop_name',
                orientation='h',
                labels={'avg_productivity': 'Average Productivity Index', 'furnace_type': 'Furnace Type', 'workshop_name': 'Workshop'},
                title="Furnace Productivity Index"
            )
            fig_furnace.update_layout(
                template="plotly_dark",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_furnace, width='stretch')
        else:
            st.info("Furnace productivity columns not found in the selected cube.")
    else:
        st.info("Workshop cube data is empty or not available.")
        
    st.markdown("<h2 style='font-size: 1.8rem; font-weight: 600; color: #f8f9fa; margin-top: 1.5rem; margin-bottom: 0.5rem;'>Production Overview</h2>", unsafe_allow_html=True)
    
    prod_overview = get_dataframe("production_overview")
    
    if not prod_overview.empty:
        # Streamlit Native Filtering controls
        filter_col1, filter_col2 = st.columns(2)
        filtered_data = prod_overview.copy()
        
        with filter_col1:
            if 'season' in filtered_data.columns:
                seasons = sorted(filtered_data['season'].dropna().unique().tolist())
                selected_seasons = st.multiselect(
                    "Filter by Season", 
                    options=seasons, 
                    default=seasons
                )
                filtered_data = filtered_data[filtered_data['season'].isin(selected_seasons)]
                
        with filter_col2:
            if 'workshop_name' in filtered_data.columns:
                workshops = sorted(filtered_data['workshop_name'].dropna().unique().tolist())
                selected_workshops = st.multiselect(
                    "Filter by Workshop", 
                    options=workshops, 
                    default=workshops
                )
                filtered_data = filtered_data[filtered_data['workshop_name'].isin(selected_workshops)]
                
        st.dataframe(filtered_data, width='stretch')
    else:
        st.info("Production overview data table is empty or not available.")