"""Application entry point, global configuration, application structure"""

from config import app_config  
import data
import tab_capacity
import tab_summary
import tab_attrition
import tab_predictions
from tab_interview import render_interview_page, inject_global_css
import home
import utils
import filters
import plots
import pandas as pd

import streamlit as st


# Inject CSS for floating button
st.markdown("""
<style>
.float-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 24px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    text-decoration: none;
    z-index: 999;
    transition: all 0.3s ease;
    cursor: pointer;
}

.float-btn:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    transform: scale(1.1);
}
</style>

<a href="#export-section" class="float-btn" title="Export Report">📥</a>
""", unsafe_allow_html=True)


def render_kpi_header(df: pd.DataFrame):
    """Render floating KPI header with four key metrics"""
    
    # Calculate KPI values
    total_employees = len(df)
    attrition_count = (df["Attrition"] == "Yes").sum()
    attrition_pct = (attrition_count / total_employees * 100) if total_employees > 0 else 0
    
    avg_salary = df["MonthlyIncome"].mean()
    
    # High-risk calculation: employees with low satisfaction or high distance
    high_risk = ((df["JobSatisfaction"] == "Very Dissatisfied") | 
                 (df["DistanceFromHome"] > 20)).sum()
    high_risk_pct = (high_risk / total_employees * 100) if total_employees > 0 else 0
    
    avg_tenure = df["YearsAtCompany"].mean()
    
    # Create four-column layout
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FF6B6B 0%, #FF4444 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; color: white;">
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">Attrition Rate</p>
            <p style="margin: 5px 0; font-size: 32px; font-weight: bold;">{attrition_pct:.1f}%</p>
            <p style="margin: 0; font-size: 12px; opacity: 0.8;">{attrition_count}/{total_employees} employees</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4ECDC4 0%, #44A99E 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; color: white;">
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">Avg Monthly Salary</p>
            <p style="margin: 5px 0; font-size: 32px; font-weight: bold;">${avg_salary:,.0f}</p>
            <p style="margin: 0; font-size: 12px; opacity: 0.8;">Across all employees</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFE66D 0%, #FFD700 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; color: #333;">
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">High-Risk %</p>
            <p style="margin: 5px 0; font-size: 32px; font-weight: bold;">{high_risk_pct:.1f}%</p>
            <p style="margin: 0; font-size: 12px; opacity: 0.8;">{high_risk} at-risk employees</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #95E1D3 0%, #7BC8A8 100%); 
                    padding: 20px; border-radius: 10px; text-align: center; color: white;">
            <p style="margin: 0; font-size: 14px; opacity: 0.9;">Avg Tenure</p>
            <p style="margin: 5px 0; font-size: 32px; font-weight: bold;">{avg_tenure:.1f}</p>
            <p style="margin: 0; font-size: 12px; opacity: 0.8;">Years at company</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()


def render_filter_sidebar(df: pd.DataFrame) -> pd.DataFrame:
    """Render sticky filter sidebar and return filtered dataframe"""
    
    with st.sidebar:
        st.title("🔍 Filters")
        
        # Department filter
        departments = ["All"] + sorted(df["Department"].unique().tolist())
        selected_depts = st.multiselect(
            "Department",
            options=departments,
            default="All",
            key="dept_filter"
        )
        
        # JobRole filter
        job_roles = ["All"] + sorted(df["JobRole"].unique().tolist())
        selected_roles = st.multiselect(
            "Job Role",
            options=job_roles,
            default="All",
            key="role_filter"
        )
        
        # Gender filter
        genders = ["All"] + sorted(df["Gender"].unique().tolist())
        selected_genders = st.multiselect(
            "Gender",
            options=genders,
            default="All",
            key="gender_filter"
        )
        
        # Tenure slider
        min_tenure, max_tenure = int(df["YearsAtCompany"].min()), int(df["YearsAtCompany"].max())
        tenure_range = st.slider(
            "Years at Company",
            min_value=min_tenure,
            max_value=max_tenure,
            value=(min_tenure, max_tenure),
            key="tenure_filter"
        )
        
        # Apply filters
        df_filtered = df.copy()
        
        if "All" not in selected_depts:
            df_filtered = df_filtered[df_filtered["Department"].isin(selected_depts)]
        
        if "All" not in selected_roles:
            df_filtered = df_filtered[df_filtered["JobRole"].isin(selected_roles)]
        
        if "All" not in selected_genders:
            df_filtered = df_filtered[df_filtered["Gender"].isin(selected_genders)]
        
        df_filtered = df_filtered[
            (df_filtered["YearsAtCompany"] >= tenure_range[0]) &
            (df_filtered["YearsAtCompany"] <= tenure_range[1])
        ]
        
        # Show filter status
        st.divider()
        st.info(f"📊 Showing {len(df_filtered)} of {len(df)} employees")
        
        return df_filtered


def main():
    ### Inject interview page global CSS at app startup
    inject_global_css()
    
    ### Initialize session state for page navigation
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'
    
    ### Render home page
    if st.session_state['page'] == 'home':
        home.render_home()
        return
    
    ### setup app-wide configuration
    utils.setup_app(app_config)

    ### load data with caching
    df_hr = data.load_transform(app_config.data_file)
    
    ### Add back button to return to home
    col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
    with col1:
        if st.button("🏠 Home", help="Return to home page"):
            st.session_state['page'] = 'home'
            st.rerun()
    with col3:
        page_title = "Interview Session" if st.session_state['page'] == 'interview' else "HR Analytics"
        st.markdown(f"**Current: {page_title}**")
    
    st.divider()

    ### Render Interview Session page
    if st.session_state['page'] == 'interview':
        render_interview_page()
        return
    
    ### Render HR Analytics page
    if st.session_state['page'] == 'analytics':
        ### Render KPI header
        render_kpi_header(df_hr)
        
        ### apply session specific active filters from sidebar
        df_hr_filtered = render_filter_sidebar(df_hr)

        ### setup app structure
        exec_summary, capacity_analysis, attrition_analysis, ml_predictions = utils.create_tabs(
            ["EXECUTIVE SUMMARY 📝", "CAPACITY ANALYSIS 🚀", "ATTRITION ANALYSIS 🏃‍♂️", "ML PREDICTIONS 🤖"]
        )
        with exec_summary:
            tab_summary.render(df_hr_filtered)
        with capacity_analysis:
            tab_capacity.render(df_hr_filtered)
        with attrition_analysis:
            tab_attrition.render(df_hr_filtered)
        with ml_predictions:
            tab_predictions.render(df_hr_filtered)
        
        # Export section
        st.markdown('<div id="export-section"></div>', unsafe_allow_html=True)
        st.divider()
        
        with st.expander("📥 Export Report", expanded=False):
            st.subheader("Generate and Download Report")
            
            if st.button("Generate PDF Report", key="pdf_export_btn"):
                with st.spinner("Generating PDF report..."):
                    try:
                        import report
                        
                        # Prepare KPIs
                        total_employees = len(df_hr_filtered)
                        attrition_count = (df_hr_filtered["Attrition"] == "Yes").sum()
                        attrition_pct = (attrition_count / total_employees * 100) if total_employees > 0 else 0
                        avg_salary = df_hr_filtered["MonthlyIncome"].mean()
                        high_risk = ((df_hr_filtered["JobSatisfaction"] == "Very Dissatisfied") | 
                                    (df_hr_filtered["DistanceFromHome"] > 20)).sum()
                        high_risk_pct = (high_risk / total_employees * 100) if total_employees > 0 else 0
                        avg_tenure = df_hr_filtered["YearsAtCompany"].mean()
                        
                        kpis = {
                            'attrition_pct': attrition_pct,
                            'avg_salary': avg_salary,
                            'high_risk_pct': high_risk_pct,
                            'avg_tenure': avg_tenure,
                            'total_employees': total_employees
                        }
                        
                        # Create report
                        pdf_bytes, _ = report.create_pdf_report(df_hr_filtered, kpis)
                        
                        st.download_button(
                            label="📄 Download PDF Report",
                            data=pdf_bytes,
                            file_name=f"hr_analytics_report_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            key="pdf_download"
                        )
                        
                    except Exception as e:
                        st.error(f"Error generating PDF: {str(e)}")


if __name__ == "__main__":
    main()
