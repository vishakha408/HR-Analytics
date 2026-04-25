"""SHAP explainability for model predictions"""

import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import shap
from ml_models import AttritionPredictor


@st.cache_resource
def compute_shap_values(model: AttritionPredictor, X: pd.DataFrame):
    """Compute SHAP values for model predictions (cached)"""
    try:
        # Create SHAP explainer
        explainer = shap.TreeExplainer(model.model)
        shap_values = explainer.shap_values(X)
        
        # For binary classification, SHAP returns array for both classes
        # We want the positive class (attrition = 1)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]
        
        return explainer, shap_values, X.values
    except Exception as e:
        st.error(f"Error computing SHAP values: {str(e)}")
        return None, None, None


def plot_shap_summary(explainer, shap_values, X: pd.DataFrame, plot_type: str = "bar"):
    """Plot SHAP summary visualization"""
    try:
        fig = plt.figure()
        
        if plot_type == "bar":
            shap.summary_plot(shap_values, X, plot_type="bar", show=False)
        else:  # "beeswarm"
            shap.summary_plot(shap_values, X, show=False)
        
        st.pyplot(fig, use_container_width=True)
        plt.close()
    except Exception as e:
        st.error(f"Error plotting SHAP summary: {str(e)}")


def plot_shap_waterfall(explainer, shap_values, X: pd.DataFrame, instance_idx: int):
    """Plot SHAP waterfall for a single prediction"""
    try:
        # Create explainer object for waterfall
        explanation = shap.Explanation(
            values=shap_values[instance_idx],
            base_values=explainer.expected_value,
            data=X.iloc[instance_idx].values,
            feature_names=X.columns.tolist()
        )
        
        fig = plt.figure()
        shap.plots.waterfall(explanation, show=False)
        
        st.pyplot(fig, use_container_width=True)
        plt.close()
    except Exception as e:
        st.error(f"Error plotting SHAP waterfall: {str(e)}")


def get_top_features_for_prediction(shap_values, X: pd.DataFrame, instance_idx: int, 
                                    top_n: int = 5):
    """Get top positive and negative SHAP features for a prediction"""
    try:
        instance_shap = shap_values[instance_idx]
        feature_names = X.columns.tolist()
        
        # Create DataFrame of features and their SHAP values
        shap_df = pd.DataFrame({
            "Feature": feature_names,
            "SHAP_Value": instance_shap,
            "Actual_Value": X.iloc[instance_idx].values
        })
        
        # Sort by absolute SHAP value
        shap_df["Abs_SHAP"] = np.abs(shap_df["SHAP_Value"])
        shap_df = shap_df.sort_values("Abs_SHAP", ascending=False)
        
        top_positive = shap_df[shap_df["SHAP_Value"] > 0].head(top_n)
        top_negative = shap_df[shap_df["SHAP_Value"] < 0].tail(top_n)
        
        return top_positive, top_negative
    except Exception as e:
        st.error(f"Error getting top features: {str(e)}")
        return None, None


def render_explanation_summary(top_positive: pd.DataFrame, top_negative: pd.DataFrame, 
                               prediction_prob: float):
    """Render explanation summary in markdown format"""
    
    summary = f"""
### Prediction Summary
**Predicted Attrition Probability:** {prediction_prob:.1%}

#### ✅ Factors Reducing Attrition Risk (Negative SHAP):
"""
    
    if top_negative is not None and len(top_negative) > 0:
        for idx, row in top_negative.iterrows():
            summary += f"\n- **{row['Feature']}** ({row['Actual_Value']:.2f}): {abs(row['SHAP_Value']):.4f}"
    else:
        summary += "\n- No reducing factors identified"
    
    summary += "\n\n#### ❌ Factors Increasing Attrition Risk (Positive SHAP):\n"
    
    if top_positive is not None and len(top_positive) > 0:
        for idx, row in top_positive.iterrows():
            summary += f"\n- **{row['Feature']}** ({row['Actual_Value']:.2f}): {row['SHAP_Value']:.4f}"
    else:
        summary += "\n- No increasing factors identified"
    
    return summary
