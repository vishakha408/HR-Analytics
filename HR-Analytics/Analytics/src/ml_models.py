"""Machine Learning models for HR analytics"""

import pandas as pd
import numpy as np
import os
import json
import pickle
import joblib
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    roc_curve,
)
import streamlit as st


class AttritionPredictor:
    """Random Forest Classifier for predicting employee attrition"""

    def __init__(self, random_state=42):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=random_state,
            n_jobs=-1,
        )
        self.label_encoders = {}
        self.feature_columns = None
        self.is_trained = False
        self.metrics = {}

    def _preprocess_data(self, df: pd.DataFrame, fit_encoders=False):
        """Preprocess data by encoding categorical variables"""
        df_processed = df.copy()

        # Identify categorical columns
        categorical_cols = df_processed.select_dtypes(
            include=["object"]
        ).columns.tolist()

        # Remove Attrition column if it exists in categorical columns
        if "Attrition" in categorical_cols:
            categorical_cols.remove("Attrition")

        # Encode categorical variables
        for col in categorical_cols:
            if fit_encoders:
                le = LabelEncoder()
                df_processed[col] = le.fit_transform(df_processed[col])
                self.label_encoders[col] = le
            else:
                if col in self.label_encoders:
                    df_processed[col] = self.label_encoders[col].transform(
                        df_processed[col]
                    )

        return df_processed

    def train(self, df: pd.DataFrame, test_size=0.2, verbose=False):
        """Train the random forest model"""
        # Preprocess data
        df_processed = self._preprocess_data(df, fit_encoders=True)

        # Separate features and target
        X = df_processed.drop("Attrition", axis=1)
        y = (df_processed["Attrition"] == "Yes").astype(int)

        # Store feature columns for prediction
        self.feature_columns = X.columns.tolist()

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Calculate metrics
        y_pred_train = self.model.predict(X_train)
        y_pred_test = self.model.predict(X_test)
        y_pred_proba_test = self.model.predict_proba(X_test)[:, 1]

        self.metrics = {
            "train_accuracy": accuracy_score(y_train, self.model.predict(X_train)),
            "test_accuracy": accuracy_score(y_test, y_pred_test),
            "precision": precision_score(y_test, y_pred_test),
            "recall": recall_score(y_test, y_pred_test),
            "f1": f1_score(y_test, y_pred_test),
            "roc_auc": roc_auc_score(y_test, y_pred_proba_test),
            "confusion_matrix": confusion_matrix(y_test, y_pred_test),
            "classification_report": classification_report(y_test, y_pred_test),
            "feature_importance": dict(
                sorted(
                    zip(self.feature_columns, self.model.feature_importances_),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),
        }

        if verbose:
            print("Model Training Complete!")
            print(f"Train Accuracy: {self.metrics['train_accuracy']:.4f}")
            print(f"Test Accuracy: {self.metrics['test_accuracy']:.4f}")
            print(f"Precision: {self.metrics['precision']:.4f}")
            print(f"Recall: {self.metrics['recall']:.4f}")
            print(f"F1-Score: {self.metrics['f1']:.4f}")
            print(f"ROC-AUC: {self.metrics['roc_auc']:.4f}")

        return self.metrics

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """Predict attrition for new data"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        df_processed = self._preprocess_data(df, fit_encoders=False)
        X = df_processed[self.feature_columns]

        return self.model.predict(X)

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Predict attrition probability for new data"""
        if not self.is_trained:
            raise ValueError("Model must be trained before making predictions")

        df_processed = self._preprocess_data(df, fit_encoders=False)
        X = df_processed[self.feature_columns]

        return self.model.predict_proba(X)

    def get_feature_importance(self, top_n=10) -> dict:
        """Get top N important features"""
        if not self.is_trained:
            raise ValueError("Model must be trained before getting feature importance")

        feature_importance = self.metrics["feature_importance"]
        return dict(list(feature_importance.items())[:top_n])

    def get_metrics(self) -> dict:
        """Get model metrics"""
        return self.metrics

    def save(self, path: str = "model/attrition_model.pkl"):
        """Save model to disk"""
        if not self.is_trained:
            raise ValueError("Model must be trained before saving")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Save model and metadata
        model_data = {
            "model": self.model,
            "label_encoders": self.label_encoders,
            "feature_columns": self.feature_columns,
            "metrics": self.metrics,
            "timestamp": datetime.now().isoformat()
        }
        
        with open(path, "wb") as f:
            pickle.dump(model_data, f)
        
        return path

    @classmethod
    def load(cls, path: str = "model/attrition_model.pkl"):
        """Load model from disk"""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Model file not found at {path}")
        
        with open(path, "rb") as f:
            model_data = pickle.load(f)
        
        # Create new instance and restore state
        predictor = cls()
        predictor.model = model_data["model"]
        predictor.label_encoders = model_data["label_encoders"]
        predictor.feature_columns = model_data["feature_columns"]
        predictor.metrics = model_data["metrics"]
        predictor.is_trained = True
        
        return predictor


@st.cache_resource
def get_trained_model(df: pd.DataFrame) -> AttritionPredictor:
    """Get or train the attrition predictor model (cached)"""
    predictor = AttritionPredictor()
    predictor.train(df, test_size=0.2, verbose=False)
    return predictor


def train_attrition_model(df: pd.DataFrame, target: str = 'Attrition', 
                         features: list = None, test_size: float = 0.2) -> dict:
    """
    Train a RandomForestClassifier to predict attrition.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataset with features and target column
    target : str
        Name of target column (default: 'Attrition')
    features : list, optional
        List of feature column names. If None, all numeric columns are used
    test_size : float
        Proportion of data to use for testing (default: 0.2)
    
    Returns:
    --------
    dict : Dictionary containing:
        - 'model': trained RandomForestClassifier
        - 'accuracy': accuracy score on test set
        - 'roc_auc': ROC-AUC score on test set
        - 'model_path': path where model was saved
        - 'feature_names': list of feature column names used
        - 'target_name': target column name
    
    Example:
    --------
    >>> result = train_attrition_model(df_hr, target='Attrition', test_size=0.2)
    >>> print(f"Model accuracy: {result['accuracy']:.2%}")
    >>> print(f"Model saved to: {result['model_path']}")
    """
    
    # Step 1: Select features (numeric columns if not provided)
    if features is None:
        # Select only numeric columns, excluding target
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        features = [col for col in numeric_cols if col != target]
    
    # Validate features exist in dataframe
    missing_features = [f for f in features if f not in df.columns]
    if missing_features:
        raise ValueError(f"Features not found in dataframe: {missing_features}")
    
    if target not in df.columns:
        raise ValueError(f"Target column '{target}' not found in dataframe")
    
    # Step 2: Prepare features and target
    X = df[features].copy()
    y = df[target].copy()
    
    # Convert target to binary (1 for "Yes"/True/1, 0 otherwise)
    if y.dtype == 'object':  # String type
        y = (y.str.upper() == 'YES').astype(int)
    else:  # Numeric type
        y = (y == 1).astype(int)
    
    # Handle missing values in features
    X = X.fillna(X.mean(numeric_only=True))
    
    # Step 3: Split data into train and test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )
    
    # Step 4: Train RandomForestClassifier with 200 trees
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    model.fit(X_train, y_train)
    
    # Step 5: Calculate metrics
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    
    # Step 6: Save model using joblib
    model_dir = "model"
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, "attrition_model.pkl")
    
    joblib.dump(model, model_path)
    
    # Also save metadata
    metadata = {
        'features': features,
        'target': target,
        'timestamp': datetime.now().isoformat(),
        'test_size': test_size,
        'n_samples': len(df),
        'n_features': len(features)
    }
    
    metadata_path = os.path.join(model_dir, "model_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=4)
    
    # Step 7: Return dictionary with results
    result = {
        'model': model,
        'accuracy': accuracy,
        'roc_auc': roc_auc,
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'model_path': model_path,
        'metadata_path': metadata_path,
        'feature_names': features,
        'target_name': target,
        'train_size': len(X_train),
        'test_size': len(X_test),
        'feature_importance': dict(zip(features, model.feature_importances_))
    }
    
    return result


def load_trained_model(model_path: str = "model/attrition_model.pkl"):
    """
    Load a trained model from disk.
    
    Parameters:
    -----------
    model_path : str
        Path to the saved model file
    
    Returns:
    --------
    sklearn model object or None if file not found
    
    Example:
    --------
    >>> model = load_trained_model("model/attrition_model.pkl")
    """
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model file not found at {model_path}")
    
    model = joblib.load(model_path)
    return model


def predict_attrition(model, df: pd.DataFrame, features: list, 
                     return_proba: bool = False) -> np.ndarray:
    """
    Make predictions using a trained model.
    
    Parameters:
    -----------
    model : sklearn model
        Trained RandomForest model
    df : pd.DataFrame
        Input dataset with feature columns
    features : list
        Names of feature columns to use
    return_proba : bool
        If True, return probabilities instead of binary predictions
    
    Returns:
    --------
    np.ndarray : Predictions (0/1 or probabilities)
    
    Example:
    --------
    >>> predictions = predict_attrition(model, df_new, features=['Age', 'Salary'])
    >>> probs = predict_attrition(model, df_new, features, return_proba=True)
    """
    
    X = df[features].copy()
    X = X.fillna(X.mean(numeric_only=True))
    
    if return_proba:
        return model.predict_proba(X)[:, 1]
    else:
        return model.predict(X)


def run_risk_selector(df_filtered: pd.DataFrame, model_path: str = "model/attrition_model.pkl",
                      metadata_path: str = "model/model_metadata.json"):
    """
    Interactive risk selector UI for identifying employees at risk of attrition.
    
    Loads trained model, generates predictions, and provides UI controls to filter
    and explore at-risk employees with download options.
    
    Parameters:
    -----------
    df_filtered : pd.DataFrame
        Input dataset with employee records (with filters applied)
    model_path : str
        Path to saved model (default: 'model/attrition_model.pkl')
    metadata_path : str
        Path to model metadata (default: 'model/model_metadata.json')
    
    Returns:
    --------
    None (renders UI directly using streamlit)
    
    Features:
    ---------
    - Two UI modes: Top N employees or Threshold-based filtering
    - Real-time prediction updates
    - Summary metrics (total, average risk, predicted attrition count)
    - CSV and Excel download options
    - Streamlit cached functions for performance
    
    Example:
    --------
    >>> import streamlit as st
    >>> import pandas as pd
    >>> from ml_models import run_risk_selector
    >>> 
    >>> df = pd.read_csv('data.csv')
    >>> run_risk_selector(df)
    """
    
    # Import streamlit here to avoid issues when used outside streamlit
    import streamlit as st
    from io import BytesIO
    
    # ============================================================================
    # Section 1: Load Model and Metadata
    # ============================================================================
    
    # Check if model file exists
    if not os.path.exists(model_path):
        st.error(f"❌ Model file not found at {model_path}")
        st.info("💡 Please train the model first in the ATTRITION ANALYSIS tab")
        return
    
    # Load model (use caching for performance)
    @st.cache_resource
    def load_model():
        return joblib.load(model_path)
    
    @st.cache_resource
    def load_metadata():
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                return json.load(f)
        return {}
    
    model = load_model()
    metadata = load_metadata()
    feature_names = metadata.get('feature_names', [])
    
    # ============================================================================
    # Section 2: Prepare Features for Prediction
    # ============================================================================
    
    def prepare_features(df):
        """Prepare features for prediction with model"""
        X = df.copy()
        
        # Select only numeric features
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove Attrition if present (it's the target)
        if 'Attrition' in numeric_cols:
            numeric_cols.remove('Attrition')
        
        # Use feature names from metadata if available
        if feature_names:
            cols_to_use = [f for f in feature_names if f in X.columns]
        else:
            cols_to_use = numeric_cols
        
        # Select features
        X = X[cols_to_use].copy()
        
        # Fill missing values with column mean
        X = X.fillna(X.mean(numeric_only=True))
        
        # Align with model's expected features
        if hasattr(model, 'feature_names_in_'):
            expected_features = list(model.feature_names_in_)
            
            # Add missing features as zeros
            for feat in expected_features:
                if feat not in X.columns:
                    X[feat] = 0
            
            # Reorder columns to match model
            X = X[expected_features]
        
        return X
    
    # Prepare features
    X = prepare_features(df_filtered)
    
    # ============================================================================
    # Section 3: Generate Predictions
    # ============================================================================
    
    # Get predictions
    pred_proba = model.predict_proba(X)[:, 1]  # Probability of class 1 (attrition)
    pred_labels = (pred_proba >= 0.5).astype(int)  # Binary label with 0.5 threshold
    
    # Add predictions to dataframe
    df_results = df_filtered.copy()
    df_results['pred_attrition_prob'] = pred_proba
    df_results['pred_attrition_label'] = pred_labels
    
    # ============================================================================
    # Section 4: UI Controls - Selection Mode
    # ============================================================================
    
    st.subheader("🎯 Filter At-Risk Employees")
    
    # Create two columns for mode selection
    col_mode1, col_mode2 = st.columns(2)
    
    selection_mode = col_mode1.radio(
        "Select filtering mode:",
        ["Top N Risky", "Probability Threshold"],
        horizontal=True
    )
    
    # ============================================================================
    # Section 5: Apply Selected Filter
    # ============================================================================
    
    if selection_mode == "Top N Risky":
        # Top N mode
        top_n = col_mode2.slider(
            "Number of employees to show:",
            min_value=1,
            max_value=min(100, len(df_results)),
            value=20,
            step=1
        )
        
        df_filtered_risk = df_results.nlargest(top_n, 'pred_attrition_prob').copy()
        filter_desc = f"Top {top_n} employees by attrition probability"
    
    else:
        # Threshold mode
        threshold = col_mode2.slider(
            "Probability threshold:",
            min_value=0.0,
            max_value=1.0,
            value=0.6,
            step=0.05
        )
        
        df_filtered_risk = df_results[df_results['pred_attrition_prob'] >= threshold].copy()
        df_filtered_risk = df_filtered_risk.sort_values('pred_attrition_prob', ascending=False)
        filter_desc = f"Employees with attrition probability >= {threshold:.0%}"
    
    # ============================================================================
    # Section 6: Summary Metrics
    # ============================================================================
    
    st.divider()
    st.subheader("📊 Summary Metrics")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("Total Employees", len(df_results))
    
    with metric_col2:
        avg_risk = df_results['pred_attrition_prob'].mean()
        st.metric("Avg Risk Probability", f"{avg_risk:.1%}")
    
    with metric_col3:
        predicted_attrition = (df_results['pred_attrition_label'] == 1).sum()
        st.metric("Predicted Attrition", f"{predicted_attrition} ({predicted_attrition/len(df_results)*100:.1f}%)")
    
    with metric_col4:
        st.metric("Filtered Results", len(df_filtered_risk))
    
    # ============================================================================
    # Section 7: Display Results Table
    # ============================================================================
    
    st.divider()
    st.subheader(f"📋 Results: {filter_desc}")
    
    # Prepare columns for display
    display_cols = []
    base_cols = ['EmployeeNumber', 'EmployeeName', 'Department', 'JobRole', 
                 'MonthlyIncome', 'YearsAtCompany', 'Age', 'JobSatisfaction']
    
    for col in base_cols:
        if col in df_filtered_risk.columns:
            display_cols.append(col)
    
    # Add prediction columns
    display_cols.extend(['pred_attrition_prob', 'pred_attrition_label'])
    
    # Create display dataframe
    df_display = df_filtered_risk[display_cols].copy()
    
    # Format for display
    df_display['pred_attrition_prob'] = df_display['pred_attrition_prob'].apply(lambda x: f"{x:.1%}")
    df_display['pred_attrition_label'] = df_display['pred_attrition_label'].apply(
        lambda x: "At Risk" if x == 1 else "Stable"
    )
    
    # Display table
    st.dataframe(df_display, use_container_width=True, height=400)
    
    if len(df_filtered_risk) == 0:
        st.info("ℹ️ No employees match the selected criteria")
        return
    
    # ============================================================================
    # Section 8: Download Options
    # ============================================================================
    
    st.divider()
    st.subheader("📥 Download Selected Results")
    
    # Prepare download data (keep numeric predictions, not formatted)
    df_download = df_filtered_risk[display_cols[:-2] + ['pred_attrition_prob', 'pred_attrition_label']].copy()
    df_download['pred_attrition_label'] = df_download['pred_attrition_label'].apply(
        lambda x: "At Risk" if x == 1 else "Stable"
    )
    
    download_col1, download_col2 = st.columns(2)
    
    # CSV Download
    with download_col1:
        csv_data = df_download.to_csv(index=False)
        st.download_button(
            label="📄 Download as CSV",
            data=csv_data,
            file_name=f"attrition_risk_employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    # Excel Download
    with download_col2:
        try:
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                # Results sheet
                df_download.to_excel(writer, sheet_name='At-Risk Employees', index=False)
                
                # Summary sheet
                summary_data = {
                    'Metric': [
                        'Filter Criteria',
                        'Total Employees',
                        'Filtered Results',
                        'Avg Risk Probability',
                        'Predicted Attrition',
                        'Attrition %',
                        'Export Time'
                    ],
                    'Value': [
                        filter_desc,
                        len(df_results),
                        len(df_filtered_risk),
                        f"{df_results['pred_attrition_prob'].mean():.1%}",
                        predicted_attrition,
                        f"{predicted_attrition/len(df_results)*100:.1f}%",
                        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    ]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            excel_buffer.seek(0)
            
            st.download_button(
                label="📊 Download as Excel",
                data=excel_buffer.getvalue(),
                file_name=f"attrition_risk_employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        except Exception as e:
            st.warning(f"⚠️ Excel export unavailable: {str(e)}")
    
    # ============================================================================
    # Section 9: Additional Details (Optional)
    # ============================================================================
    
    with st.expander("📈 Risk Distribution Statistics", expanded=False):
        # Risk distribution
        col_stats1, col_stats2 = st.columns(2)
        
        with col_stats1:
            st.write("**Probability Statistics**")
            st.write(f"- Min: {df_results['pred_attrition_prob'].min():.1%}")
            st.write(f"- Q1: {df_results['pred_attrition_prob'].quantile(0.25):.1%}")
            st.write(f"- Median: {df_results['pred_attrition_prob'].median():.1%}")
            st.write(f"- Q3: {df_results['pred_attrition_prob'].quantile(0.75):.1%}")
            st.write(f"- Max: {df_results['pred_attrition_prob'].max():.1%}")
        
        with col_stats2:
            st.write("**Class Distribution**")
            
            # Risk category distribution
            risk_dist = pd.cut(
                df_results['pred_attrition_prob'],
                bins=[0, 0.25, 0.5, 0.75, 1.0],
                labels=['Low (0-25%)', 'Medium (25-50%)', 'High (50-75%)', 'Very High (75-100%)']
            ).value_counts().sort_index()
            
            for label, count in risk_dist.items():
                st.write(f"- {label}: {count} ({count/len(df_results)*100:.1f}%)")
