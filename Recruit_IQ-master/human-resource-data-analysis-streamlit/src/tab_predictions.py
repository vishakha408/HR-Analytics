"""ML Predictions tab rendering functionality"""

import pandas as pd
import streamlit as st
import ml_models
import plots
import utils
from datetime import datetime
from io import BytesIO
import os
import joblib
import numpy as np


@st.cache_resource
def load_trained_model():
    """Load trained model from disk (cached)"""
    model_path = "model/attrition_model.pkl"
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None


@st.cache_resource
def load_model_metadata():
    """Load model metadata from disk (cached)"""
    metadata_path = "model/model_metadata.json"
    if os.path.exists(metadata_path):
        import json
        with open(metadata_path, 'r') as f:
            return json.load(f)
    return None


def prepare_features_for_prediction(df, feature_names, model):
    """
    Prepare features for prediction:
    - Select only numeric features used in training
    - One-hot encode categorical columns if needed
    - Align with model's expected columns
    - Add missing columns with zeros
    """
    X = df.copy()
    
    # Get numeric columns
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    
    # Remove target if present
    if 'Attrition' in numeric_cols:
        numeric_cols.remove('Attrition')
    
    # If no feature_names available, use available numeric columns
    if not feature_names:
        feature_names = numeric_cols
    
    # Select only the features the model was trained on
    available_features = [f for f in feature_names if f in X.columns]
    X = X[available_features].copy()
    
    # Handle missing values
    X = X.fillna(X.mean(numeric_only=True))
    
    # Add missing features as zeros (model.feature_names_in_ vs training features)
    if hasattr(model, 'feature_names_in_'):
        expected_features = list(model.feature_names_in_)
        for feat in expected_features:
            if feat not in X.columns:
                X[feat] = 0
        # Reorder to match model's expected order
        X = X[expected_features]
    
    return X


def render(df: pd.DataFrame):
    """Render the ML predictions tab"""
    
    st.subheader("🔮 Predict & Download Results")
    
    # Check if model exists
    model_path = "model/attrition_model.pkl"
    
    if not os.path.exists(model_path):
        st.warning("⚠️ No trained model found — train first in the Analysis tab!")
        st.info("💡 Go to the 'Attrition' tab and scroll to 'Build New Analysis' to train the model.")
        return
    
    try:
        # Load model and metadata
        model = load_trained_model()
        metadata = load_model_metadata()
        
        if model is None:
            st.error("❌ Error loading model file")
            return
        
        # Display model info
        col_info1, col_info2 = st.columns(2)
        
        with col_info1:
            st.metric("Model Status", "✅ Ready")
        
        with col_info2:
            if metadata and 'timestamp' in metadata:
                st.metric("Model Date", metadata['timestamp'][:10])
        
        st.divider()
        
        # Make predictions
        st.subheader("📊 Generate Predictions")
        
        if st.button("Generate Predictions for Current Dataset", key="predict_btn", use_container_width=True):
            with st.spinner("Generating predictions... This may take a moment"):
                try:
                    # Get feature names from metadata
                    feature_names = metadata.get('feature_names', []) if metadata else []
                    
                    # Prepare features
                    X = prepare_features_for_prediction(df, feature_names, model)
                    
                    # Get predictions
                    pred_proba = model.predict_proba(X)
                    pred_labels = model.predict(X)
                    
                    # Create results dataframe
                    df_results = df.copy()
                    df_results['pred_attrition_prob'] = pred_proba[:, 1]
                    df_results['pred_attrition_label'] = pred_labels
                    
                    # Store in session
                    st.session_state['predictions_df'] = df_results
                    
                    st.success("✅ Predictions generated successfully!")
                    
                except Exception as e:
                    st.error(f"❌ Error generating predictions: {str(e)}")
                    return
        
        # Display predictions
        if 'predictions_df' in st.session_state:
            df_results = st.session_state['predictions_df']
            
            st.divider()
            st.subheader("📈 Prediction Summary")
            
            # Summary statistics
            stat_col1, stat_col2, stat_col3 = st.columns(3)
            
            count_at_risk = (df_results['pred_attrition_label'] == 1).sum()
            count_stable = (df_results['pred_attrition_label'] == 0).sum()
            avg_prob = df_results['pred_attrition_prob'].mean()
            
            with stat_col1:
                st.metric("At Risk (1)", f"{count_at_risk}", f"{count_at_risk/len(df_results)*100:.1f}%")
            
            with stat_col2:
                st.metric("Stable (0)", f"{count_stable}", f"{count_stable/len(df_results)*100:.1f}%")
            
            with stat_col3:
                st.metric("Avg Risk Probability", f"{avg_prob:.1%}")
            
            st.divider()
            st.subheader("📋 Top 50 Predictions (Sorted by Risk)")
            
            # Prepare display dataframe
            display_cols = []
            base_cols = ['EmployeeNumber', 'EmployeeName', 'Department', 'JobRole', 
                        'MonthlyIncome', 'YearsAtCompany', 'Age', 'JobSatisfaction']
            
            for col in base_cols:
                if col in df_results.columns:
                    display_cols.append(col)
            
            # Add prediction columns
            display_cols.extend(['pred_attrition_prob', 'pred_attrition_label'])
            
            df_display = df_results.nlargest(50, 'pred_attrition_prob')[display_cols].copy()
            df_display['pred_attrition_prob'] = df_display['pred_attrition_prob'].apply(lambda x: f"{x:.2%}")
            df_display['pred_attrition_label'] = df_display['pred_attrition_label'].apply(lambda x: "At Risk" if x == 1 else "Stable")
            
            st.dataframe(df_display, use_container_width=True, height=400)
            
            st.divider()
            st.subheader("📥 Download Results")
            
            # CSV Download
            csv_data = df_results.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv_data,
                file_name=f"attrition_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                key="csv_download",
                use_container_width=True
            )
            
            # Excel Download
            try:
                excel_buffer = BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_results.to_excel(writer, sheet_name='Predictions', index=False)
                    
                    # Add summary sheet
                    summary_data = {
                        'Metric': ['Total Employees', 'At Risk Count', 'Stable Count', 'At Risk %', 'Avg Risk Probability'],
                        'Value': [
                            len(df_results),
                            count_at_risk,
                            count_stable,
                            f"{count_at_risk/len(df_results)*100:.1f}%",
                            f"{avg_prob:.2%}"
                        ]
                    }
                    pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                
                excel_buffer.seek(0)
                
                st.download_button(
                    label="📊 Download as Excel",
                    data=excel_buffer.getvalue(),
                    file_name=f"attrition_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    key="excel_download",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"⚠️ Excel download unavailable: {str(e)}")
    
    except Exception as e:
        st.error(f"❌ Error in predictions section: {str(e)}")
    
    # ============================================================================
    # Risk Selector Section - Interactive filtering and analysis
    # ============================================================================
    
    st.divider()
    st.markdown("## 🎯 Advanced Risk Analysis")
    st.markdown("Identify and filter at-risk employees with custom selection criteria")
    
    # Call the risk selector function
    ml_models.run_risk_selector(df)
