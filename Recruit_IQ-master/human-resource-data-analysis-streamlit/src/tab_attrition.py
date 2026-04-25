"""Attrition tab rendering functionality"""

import pandas as pd
import streamlit
import utils
import data
import plots
import ml_models


###
### render the capacity page
###
def render(df: pd.DataFrame):
    # Show KPI & plots
    __build_attrition_plots(df)
    # Show new analysis
    __build_new_analysis(df)


###
### module's internal functions
###
def __build_attrition_plots(df):
    with streamlit.expander("Analysis: Employee Attrition...", expanded=True):
        utils.show_questions(
            [
                "* Do we have attrition rate higher than 10%?",
                "* What are the factors directly contributes to attrition?",
            ]
        )
        utils.sep()
        ### gather attrition statistics
        attrition_stats = data.get_attrition_stats(df)

        ### overall, male and female attrition rates
        with streamlit.container():
            (
                c1_col1,
                c1_col2,
                c1_col3,
            ) = streamlit.columns(3)
            with c1_col1:
                attr_tot = attrition_stats["CompanyWide"]["Total Attrition"]
                attr_pct = attrition_stats["CompanyWide"]["Attrition Rate"]
                utils.render_card(
                    key="attrition_card1",
                    title="Overall<br>Attrition",
                    value=attr_tot,
                    secondary_text=f" ({attr_pct})%",
                    icon="fa-sharp fa-solid fa-venus-mars fa-xs",
                    progress_value=int(attr_pct),
                    progress_color="red",
                )
            with c1_col2:
                male_attr_tot = attrition_stats.get("Male", {}).get(
                    "Total Attrition", 0
                )
                male_attr_pct = attrition_stats.get("Male", {}).get("Attrition Rate", 0)
                utils.render_card(
                    key="attrition_card2",
                    title="Male<br>Attrition",
                    value=male_attr_tot,
                    secondary_text=f" ({male_attr_pct})%",
                    icon="fa-sharp fa-solid fa-mars fa-xs",
                    progress_value=int(male_attr_pct),
                    progress_color="red",
                )
            with c1_col3:
                female_attr_tot = attrition_stats.get("Female", {}).get(
                    "Total Attrition", 0
                )
                female_attr_pct = attrition_stats.get("Female", {}).get(
                    "Attrition Rate", 0
                )
                utils.render_card(
                    key="attrition_card3",
                    title="Female<br>Attrition",
                    value=female_attr_tot,
                    secondary_text=f" ({female_attr_pct})%",
                    icon="fa-sharp fa-solid fa-venus fa-xs",
                    progress_value=int(female_attr_pct),
                    progress_color="red",
                )
        utils.sep()

        ### attrition by department & job role
        with streamlit.container():
            (
                c2_col1,
                c2_col2,
            ) = streamlit.columns(2)
            with c2_col1:
                streamlit.plotly_chart(
                    plots.plot_dept_attrition(attrition_stats["Department"]),
                    use_container_width=True,
                )
            with c2_col2:
                streamlit.plotly_chart(
                    plots.plot_jobrole_attrition(attrition_stats["JobRole"]),
                    use_container_width=True,
                )
        utils.sep()

        ### attrition by distance to work & job satisfaction
        with streamlit.container():
            (
                c3_col1,
                c3_col2,
            ) = streamlit.columns(2)
            with c3_col1:
                streamlit.plotly_chart(
                    plots.plot_dist_attrition(attrition_stats["WorkplaceProximity"]),
                    use_container_width=True,
                )
            with c3_col2:
                streamlit.plotly_chart(
                    plots.plot_satis_attrition(attrition_stats["JobSatisfaction"]),
                    use_container_width=True,
                )
        utils.sep()

        ### attrition by age & work-experience
        with streamlit.container():
            (
                c4_col1,
                c4_col2,
            ) = streamlit.columns(2)
            with c4_col1:
                streamlit.plotly_chart(
                    plots.plot_ages_attrition(attrition_stats["Ages"]),
                    use_container_width=True,
                )
            with c4_col2:
                # attrition by work exp buckets - horizontal bar
                streamlit.plotly_chart(
                    plots.plot_exp_attrition(attrition_stats["WorkExperience"]),
                    use_container_width=True,
                )
        utils.sep()

        with streamlit.expander("View Insights...", expanded=True):
            utils.show_insights(
                [
                    "* Overall attrition rate is > 16%, well above the stipulated max"
                    " rate (10%). Company needs to act upon it quickly",
                    "* R&D and Sales are biggest departments by head-count and "
                    "proportionately attrition rate are highest among them which is "
                    "expected",
                    "* Attrition is rising exponentially for non-director and "
                    "non-manager level employees. This may indicate junior level "
                    "employees do not prefer to stick around for some reason",
                    "* Its also evident that most of the people leaving the company "
                    "living far off, is traveling distance/cost is driving this "
                    "this behavior? what action company can take to remedy this issue?"
                    "* Over 58% of dissatisfied employees leave, company needs to "
                    "have closer look at satisfaction survey and try to pin point "
                    "the root cause and then fix it",
                    "* Over 76% people leaving the company have work experience <= 10 "
                    "years. This is not a good sign, this means people in early phase "
                    "of their career do not find company attractive, why?",
                    "Over 57% of people leaning are between age 25 to 38 years, "
                    "why this particular age group does not prefer to stay longer?",
                ]
            )


def __build_new_analysis(df):
    """Build new analysis visualizations and ML predictions"""
    
    # Section 1: Salary Analysis
    with streamlit.expander("Analysis: Compensation by Department...", expanded=False):
        utils.show_questions(
            [
                "* What is the average salary by department?",
                "* Are there compensation disparities between departments?",
            ]
        )
        utils.sep()
        
        fig = plots.plot_avg_salary_by_dept(df)
        streamlit.pyplot(fig, use_container_width=True)
        
        with streamlit.expander("View Insights...", expanded=False):
            utils.show_insights(
                [
                    "* Compare average salaries across departments to identify potential compensation gaps",
                    "* Higher salaries may reduce attrition if employees feel valued",
                    "* Consider whether salary levels align with job responsibilities and market rates",
                ]
            )
    
    utils.sep()
    
    # Section 2: Attrition Rate by Department
    with streamlit.expander("Analysis: Attrition Rate by Department...", expanded=False):
        utils.show_questions(
            [
                "* Which department has the highest attrition rate?",
                "* Are attrition rates correlated with compensation?",
            ]
        )
        utils.sep()
        
        fig = plots.plot_attrition_rate_by_dept(df)
        streamlit.pyplot(fig, use_container_width=True)
        
        with streamlit.expander("View Insights...", expanded=False):
            utils.show_insights(
                [
                    "* Monitor department-level attrition trends to identify problem areas",
                    "* Use departmental attrition rates to develop targeted retention strategies",
                    "* Consider linking attrition rates with salary and other compensation metrics",
                ]
            )
    
    utils.sep()
    
    # Section 3: Correlation Heatmap
    with streamlit.expander("Analysis: Feature Correlations...", expanded=False):
        utils.show_questions(
            [
                "* What numeric features are correlated with attrition?",
                "* Which employee characteristics are most related to each other?",
            ]
        )
        utils.sep()
        
        fig = plots.plot_correlation_heatmap(df)
        streamlit.pyplot(fig, use_container_width=True)
        
        with streamlit.expander("View Insights...", expanded=False):
            utils.show_insights(
                [
                    "* Strong positive/negative correlations can reveal hidden relationships in the data",
                    "* Red regions indicate strong negative correlations, blue regions indicate positive correlations",
                    "* Use this analysis to identify key factors that may influence attrition decisions",
                ]
            )
    
    utils.sep()
    
    # Section 4: ML Predictions
    with streamlit.expander("Predictive Analytics: Attrition Risk Prediction...", expanded=False):
        utils.show_questions(
            [
                "* Can we predict which employees are at risk of attrition?",
                "* What is the model's accuracy in predicting attrition?",
                "* Which factors are most important in predicting attrition?",
            ]
        )
        utils.sep()
        
        streamlit.info("Training Random Forest model to predict attrition risk...")
        
        # Train model
        result = ml_models.train_attrition_model(df)
        
        # Display metrics
        col1, col2, col3, col4 = streamlit.columns(4)
        with col1:
            utils.render_card(
                key="ml_accuracy",
                title="Test<br>Accuracy",
                value=int(result['accuracy'] * 100),
                secondary_text="%",
                icon="fa-sharp fa-solid fa-check fa-xs",
                progress_value=int(result['accuracy'] * 100),
                progress_color="green",
            )
        with col2:
            utils.render_card(
                key="ml_precision",
                title="Precision",
                value=int(result['precision'] * 100),
                secondary_text="%",
                icon="fa-sharp fa-solid fa-bullseye fa-xs",
                progress_value=int(result['precision'] * 100),
                progress_color="blue",
            )
        with col3:
            utils.render_card(
                key="ml_recall",
                title="Recall",
                value=int(result['recall'] * 100),
                secondary_text="%",
                icon="fa-sharp fa-solid fa-magnifying-glass fa-xs",
                progress_value=int(result['recall'] * 100),
                progress_color="orange",
            )
        with col4:
            utils.render_card(
                key="ml_roc_auc",
                title="ROC-AUC",
                value=int(result['roc_auc'] * 100),
                secondary_text="%",
                icon="fa-sharp fa-solid fa-chart-line fa-xs",
                progress_value=int(result['roc_auc'] * 100),
                progress_color="purple",
            )
        
        utils.sep()
        
        # Feature Importance
        streamlit.subheader("Top 10 Attrition Predictors")
        # Get feature importance (convert dict to list, sort by importance, keep top 10)
        feature_importance = dict(sorted(result['feature_importance'].items(), 
                                        key=lambda x: x[1], reverse=True)[:10])
        
        # Create dataframe for visualization
        feat_df = pd.DataFrame(
            list(feature_importance.items()),
            columns=["Feature", "Importance"]
        ).sort_values("Importance", ascending=True)
        
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=feat_df, x="Importance", y="Feature", palette="viridis", ax=ax)
        ax.set_title("Top 10 Features Contributing to Attrition Prediction", fontsize=14, fontweight="bold")
        ax.set_xlabel("Importance Score")
        
        streamlit.pyplot(fig, use_container_width=True)
        
        with streamlit.expander("View Insights...", expanded=False):
            utils.show_insights(
                [
                    f"* Model achieved {result['accuracy']:.1%} accuracy on test data",
                    f"* Precision of {result['precision']:.1%} means {result['precision']:.0%} of predicted attrition cases are correct",
                    f"* Recall of {result['recall']:.1%} means the model catches {result['recall']:.0%} of actual attrition cases",
                    f"* ROC-AUC score of {result['roc_auc']:.1%} indicates good model performance",
                    "* The top predictors indicate which employee characteristics should be monitored for attrition risk",
                ]
            )
