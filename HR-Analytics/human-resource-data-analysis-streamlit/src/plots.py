"""All app-specific plots are implemented here"""

import plotly.express as px
import plotly.io as io
import matplotlib.pyplot as plt
import seaborn as sns
from pandas import DataFrame
from plotly.graph_objects import Figure
from config import plot_config

# setup app-wide plotly theme
io.templates.default = plot_config.theme


###
### Summary tab plots
###
def plot_age_hist(df: DataFrame) -> Figure:
    fig = px.histogram(
        data_frame=df,
        x="Age",
        marginal="violin",
        title="Employee's age distribution overall",
        color_discrete_sequence=plot_config.cat_color_map,
    )
    return fig


def plot_age_marital_status_pie(df: DataFrame) -> Figure:
    df_group = (
        df.groupby("MaritalStatus", as_index=False)
        .size()
        .sort_values(by="size", ascending=True)
    )
    fig = px.pie(
        data_frame=df_group,
        names="MaritalStatus",
        values="size",
        color="MaritalStatus",
        hole=0.7,
        title="Employee count by marital-status",
        color_discrete_sequence=plot_config.cat_color_map,
    ).update_traces(textfont_color="white")
    return fig


def plot_age_marital_status_box(df: DataFrame) -> Figure:
    fig = px.box(
        data_frame=df,
        x="MaritalStatus",
        y="Age",
        color="MaritalStatus",
        title="Employee's age distribution by marital-status",
        color_discrete_sequence=plot_config.cat_color_map,
    )
    return fig


def plot_age_gender_box(df: DataFrame) -> Figure:
    fig = px.box(
        data_frame=df,
        x="Gender",
        y="Age",
        color="Gender",
        title="Employee's age distribution by gender",
        color_discrete_sequence=plot_config.cat_color_map,
    )
    return fig


def plot_dept_gender_count_sunburst(df: DataFrame) -> Figure:
    df_group = (
        df.groupby(["Department", "Gender"], as_index=False)
        .size()
        .assign(Top="Company")
    )
    fig = px.sunburst(
        data_frame=df_group,
        path=["Top", "Department", "Gender"],
        values="size",
        color_discrete_sequence=px.colors.qualitative.T10,
        title="Employee count in each department<br>segmented by gender",
    )
    fig.update_traces(
        textfont_color="white",
        textinfo="label+percent parent",
        textfont_size=18,
    )
    fig.update_layout(
        margin=dict(t=20, l=0, r=0, b=0),
        autosize=False,
        height=700,
    )

    return fig


def plot_dept_curr_mgr_scatter(df: DataFrame) -> Figure:
    df_group = (
        df.groupby("Department")["YearsWithCurrManager"]
        .mean()
        .to_frame()
        .reset_index()
        .sort_values(by="YearsWithCurrManager", ascending=False)
    )
    fig = px.scatter(
        data_frame=df_group,
        x="YearsWithCurrManager",
        y="Department",
        color="Department",
        size="YearsWithCurrManager",
        title="Avg number of years with current manager",
    )
    return fig


def plot_tot_work_exp_bar(df):
    tot_emp = len(df)
    df_group = df.groupby("WorkExperience", as_index=False).size()
    df_group["size"] = df_group["size"] / tot_emp * 100
    fig = px.bar(
        data_frame=df_group.sort_values(by="size", ascending=False),
        x="size",
        y="WorkExperience",
        color="WorkExperience",
        color_discrete_sequence=plot_config.cat_color_map,
    ).update_traces(
        text="size",
        texttemplate="%{x:.1f}%",
        textposition="auto",
        textfont_color="white",
    )
    return fig


def plot_cmp_work_exp_scatter(df, annot_text):
    fig = px.scatter(
        data_frame=df,
        x="TotalWorkingYears",
        y="YearsAtCompany",
        size="PctAtCompany",
        color="PctAtCompany",
        opacity=0.6,
        color_continuous_scale=plot_config.cont_color_map,
    )
    fig.add_annotation(
        x=0.1,
        y=35,
        xref="paper",
        yref="y",
        text=annot_text,
        align="left",
        showarrow=False,
        font=dict(family="Arial", size=14, color="#ffffff"),
        bordercolor="#4c78a8",
        borderwidth=1,
        borderpad=4,
        bgcolor="#4c78a8",
        opacity=0.7,
    )

    return fig


###
### Capacity tab plots - Promotion and Retrenchment
###
def plot_promotion_donut(df):
    df_group = (
        df["ToBePromoted"]
        .value_counts()
        .to_frame()
        .reset_index()
        .rename({"ToBePromoted": "Promotion", "count": "Count"}, axis=1)
    )
    fig = px.pie(
        df_group,
        names="Promotion",
        values="Count",
        hole=0.6,
        color_discrete_sequence=plot_config.cat_color_map,
        title="Company wide promotion",
    )
    fig.update_layout(
        legend_title_text="Promotion?",
        margin=dict(t=45, l=0, r=0, b=0),
    )
    fig.update_traces(pull=[0.1, 0])
    return fig


def plot_retrench_donut(df):
    df_group = (
        df["ToBeRetrenched"]
        .value_counts()
        .to_frame()
        .reset_index()
        .rename({"ToBeRetrenched": "Retrench", "count": "Count"}, axis=1)
    )

    fig = px.pie(
        df_group,
        names="Retrench",
        values="Count",
        hole=0.6,
        color_discrete_sequence=plot_config.cat_color_map_r,
        title="Company wide retrenchment",
    )
    fig.update_layout(
        legend_title_text="Retrench?",
        margin=dict(t=45, l=0, r=0, b=0),
    )
    fig.update_traces(pull=[0.1, 0])
    return fig


def plot_dept_promo_bar(df):
    fig = px.bar(
        data_frame=df,
        x="Department",
        y="PromotePct",
        color="ToBePromoted",
        barmode="group",
        color_discrete_sequence=plot_config.cat_color_map,
        title="To be promoted<br>in each department",
    )
    fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="auto",
        textfont_color="white",
    )
    return fig


def plot_dept_retrench_bar(df):
    df_group = df
    fig = px.bar(
        data_frame=df_group,
        x="Department",
        y="RetrenchPct",
        color="ToBeRetrenched",
        barmode="group",
        color_discrete_sequence=plot_config.cat_color_map_r,
        title="To be retrenched<br>in each department",
    )
    fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="auto",
        textfont_color="white",
    )
    return fig


###
### Capacity tab plots - Attrition
###
def plot_dept_attrition(df):
    fig = px.pie(
        data_frame=df,
        names="Department",
        values="% Attrition",
        hole=0.4,
        color_discrete_sequence=plot_config.cat_color_map_r,
        title="Attrition by Department",
    )
    fig.update_traces(
        textfont_color="white", textinfo="label+percent", showlegend=False
    )
    fig.update_layout(
        legend_title_text="Department",
        # margin=dict(t=0, l=0, r=0, b=0),
    )
    return fig


def plot_gender_attrition(df):
    fig = px.pie(
        data_frame=df,
        names="Gender",
        values="% Attrition",
        hole=0.4,
        color_discrete_sequence=plot_config.cat_color_map_r,
        title="Attrition by Gender",
    ).update_traces(textfont_color="white", textinfo="label+percent", showlegend=False)
    fig.update_layout(
        legend_title_text="Gender",
    )
    return fig


def plot_dist_attrition(df):
    fig = px.bar(
        data_frame=df,
        y="WorkplaceProximity",
        x="% Attrition",
        color="WorkplaceProximity",
        color_discrete_sequence=plot_config.cat_color_map_r,
        title="Attrition by Distance",
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        textposition="auto",
        textfont_color="white",
        showlegend=False,
    )
    return fig


def plot_jobrole_attrition(df):
    fig = px.bar(
        data_frame=df,
        x="JobRole",
        y="% Attrition",
        color="JobRole",
        color_discrete_sequence=plot_config.cat_color_map,
        title="Attrition by Job Role",
    )
    fig.update_traces(
        texttemplate="%{y:.1f}%",
        textposition="auto",
        textfont_color="white",
        showlegend=False,
    )
    return fig


def plot_satis_attrition(df):
    fig = px.bar(
        data_frame=df,
        y="JobSatisfaction",
        x="% Attrition",
        color="JobSatisfaction",
        color_discrete_sequence=plot_config.cat_color_map,
        title="Attrition by Job Satisfaction",
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        textposition="auto",
        textfont_color="white",
        showlegend=False,
    )
    return fig


def plot_ages_attrition(df):
    fig = px.bar(
        data_frame=df,
        y="Ages",
        x="% Attrition",
        color="Ages",
        color_discrete_sequence=plot_config.cat_color_map_r,
        title="Attrition by Age",
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        textposition="auto",
        textfont_color="white",
        showlegend=False,
    )
    return fig


def plot_exp_attrition(df):
    fig = px.bar(
        data_frame=df,
        y="WorkExperience",
        x="% Attrition",
        color="WorkExperience",
        color_discrete_sequence=plot_config.cat_color_map,
        title="Attrition by Work Experience",
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        textposition="auto",
        textfont_color="white",
        showlegend=False,
    )
    return fig


###
### New Analysis Functions - Seaborn & ML Visualizations
###
def plot_avg_salary_by_dept(df: DataFrame):
    """Create a bar chart of average salary by department using seaborn"""
    # Prepare data
    df_salary = df.groupby("Department")["MonthlyIncome"].mean().reset_index()
    df_salary = df_salary.sort_values("MonthlyIncome", ascending=False)
    
    # Create matplotlib figure for seaborn
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df_salary,
        x="Department",
        y="MonthlyIncome",
        palette="viridis",
        ax=ax
    )
    ax.set_title("Average Monthly Income by Department", fontsize=16, fontweight="bold")
    ax.set_xlabel("Department", fontsize=12)
    ax.set_ylabel("Average Monthly Income ($)", fontsize=12)
    
    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt="$%.0f", padding=3)
    
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    return fig


def plot_attrition_rate_by_dept(df: DataFrame):
    """Create a bar chart of attrition rate by department using seaborn"""
    # Calculate attrition rate by department
    df_attrition = df.groupby("Department").apply(
        lambda x: (x["Attrition"] == "Yes").sum() / len(x) * 100
    ).reset_index()
    df_attrition.columns = ["Department", "Attrition_Rate"]
    df_attrition = df_attrition.sort_values("Attrition_Rate", ascending=False)
    
    # Create matplotlib figure for seaborn
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=df_attrition,
        x="Department",
        y="Attrition_Rate",
        palette="RdYlGn_r",
        ax=ax
    )
    ax.set_title("Attrition Rate by Department", fontsize=16, fontweight="bold")
    ax.set_xlabel("Department", fontsize=12)
    ax.set_ylabel("Attrition Rate (%)", fontsize=12)
    
    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.1f%%", padding=3)
    
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    return fig


def plot_correlation_heatmap(df: DataFrame):
    """Create a correlation heatmap of numeric columns using seaborn"""
    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns
    df_numeric = df[numeric_cols]
    
    # Calculate correlation matrix
    corr_matrix = df_numeric.corr()
    
    # Create matplotlib figure for seaborn
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(
        corr_matrix,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        center=0,
        square=True,
        ax=ax,
        cbar_kws={"shrink": 0.8}
    )
    ax.set_title("Correlation Heatmap of Numeric Columns", fontsize=16, fontweight="bold", pad=20)
    
    plt.tight_layout()
    
    return fig

