import streamlit as st
import pandas as pd
from ML.OLAP.reader import get_dataframe

st.set_page_config(page_title="Business Intelligence Dashboard", layout="wide", page_icon="🏭")

from clustering_view import render as render_clustering
from statistics_view import render as render_statistics
from forecasting_view import render as render_forecasting

@st.cache_data
def fetch_data(view_name):
    try:
        df = get_dataframe(view_name)
        return df if df is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def render_executive_command_center():
    st.header("Executive Command Center")
    st.subheader("How is the factory doing right now?")
    
    # Top Row
    kpi_monthly = fetch_data("kpi_monthly")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        val = 0
        if not kpi_monthly.empty and 'fulfillment_rate' in kpi_monthly.columns:
            val = kpi_monthly['fulfillment_rate'].iloc[0] * 100
        st.metric("Target Hit", f"{val:.1f}%")
        
    with col2:
        val = 0
        if not kpi_monthly.empty and 'avg_defect_rate' in kpi_monthly.columns:
            def_rate = kpi_monthly['avg_defect_rate'].iloc[0]
            val = (1 - def_rate) * 100
        st.metric("Quality Score", f"{val:.1f}%")
        
    with col3:
        val = 0
        if not kpi_monthly.empty and 'total_output' in kpi_monthly.columns:
            val = kpi_monthly['total_output'].iloc[0]
        st.metric("Total Output", f"{val:,.0f}")
        
    st.markdown("---")
    
    # Middle Row
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.markdown("**Daily View (Chaotic)**")
        cube_forecast_daily = fetch_data("cube_forecast_daily")
        if not cube_forecast_daily.empty:
            cols_to_plot = [c for c in ['total_output', 'total_defects'] if c in cube_forecast_daily.columns]
            index_col = 'date' if 'date' in cube_forecast_daily.columns else cube_forecast_daily.columns[0]
            if cols_to_plot:
                chart_data = cube_forecast_daily.set_index(index_col)[cols_to_plot]
                st.line_chart(chart_data)
            else:
                st.line_chart(cube_forecast_daily)
        else:
            st.info("Daily forecast data not available.")
            
    with col_right:
        st.markdown("**Monthly View (Stable)**")
        cube_forecast_monthly = fetch_data("cube_forecast_monthly")
        if not cube_forecast_monthly.empty:
            cols_to_plot = [c for c in ['total_output', 'total_defects'] if c in cube_forecast_monthly.columns]
            index_col = 'month' if 'month' in cube_forecast_monthly.columns else cube_forecast_monthly.columns[0]
            if cols_to_plot:
                chart_data = cube_forecast_monthly.set_index(index_col)[cols_to_plot]
                st.line_chart(chart_data)
            else:
                st.line_chart(cube_forecast_monthly)
        else:
            st.info("Monthly forecast data not available.")
            
    st.caption("Why does time matter? Zooming out to a monthly view removes daily 'noise' (like machine breakdowns or sick days), allowing our AI to accurately group workers and forecast cashflow.")
    
    st.markdown("---")
    
    # Bottom Row
    st.markdown("**Month-Over-Month Production Momentum**")
    trend_mom_growth = fetch_data("trend_mom_growth")
    if not trend_mom_growth.empty:
        index_col = 'month' if 'month' in trend_mom_growth.columns else trend_mom_growth.columns[0]
        st.bar_chart(trend_mom_growth.set_index(index_col))
    else:
        st.info("Month-over-month growth data not available.")

# App Router
st.title("Business Intelligence Dashboard")

page = st.sidebar.radio("Navigation", [
    "Executive Command Center", 
    "Workforce & Culture", 
    "Factory Floor", 
    "The Horizon"
])

if page == "Executive Command Center":
    render_executive_command_center()
elif page == "Workforce & Culture":
    render_clustering()
elif page == "Factory Floor":
    render_statistics()
elif page == "The Horizon":
    render_forecasting()