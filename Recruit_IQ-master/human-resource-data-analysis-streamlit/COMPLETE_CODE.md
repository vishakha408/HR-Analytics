# Complete Function Code: train_attrition_model()

## Full Implementation

Copy this code to `src/ml_models.py` (Lines 211-322)

```python
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
        - 'precision': precision score
        - 'recall': recall score
        - 'f1': F1-score
        - 'model_path': path where model was saved
        - 'metadata_path': path where metadata was saved
        - 'feature_names': list of feature column names used
        - 'target_name': target column name
        - 'train_size': number of training samples
        - 'test_size': number of test samples
        - 'feature_importance': dict of feature importance scores
    
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
```

## Helper Functions

Copy these to `src/ml_models.py` (Lines 324-394)

```python
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
```

## Required Imports

Add to top of `src/ml_models.py`:

```python
import joblib  # For model persistence (already in code)
```

Full import section should have:
```python
import pandas as pd
import numpy as np
import os
import json
import pickle
import joblib                        # ADD THIS
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
```

## Installation

```bash
# Install required packages
pip install -r requirements.txt

# Or install individually
pip install scikit-learn joblib pandas numpy
```

## Quick Test

```python
# Save as test_quick.py
import pandas as pd
from src.ml_models import train_attrition_model

# Load data
df = pd.read_csv('input_data/raw_hr_data.csv')

# Train model
result = train_attrition_model(df)

# Print results
print(f"✓ Model trained successfully!")
print(f"  Accuracy: {result['accuracy']:.4f}")
print(f"  ROC-AUC:  {result['roc_auc']:.4f}")
print(f"  Saved to: {result['model_path']}")

# Run with: python test_quick.py
```

## Step-by-Step Integration

1. **Copy** the main function code to `src/ml_models.py` after line 210
2. **Copy** helper functions to `src/ml_models.py` after the main function
3. **Add** `import joblib` to imports (already done)
4. **Update** `requirements.txt` with `joblib` (already done)
5. **Run** tests: `pytest tests/test_train_model.py -v`
6. **Run** example: `python example_train_model.py`

## Usage in Your App

```python
# In tab_predictions.py
from ml_models import train_attrition_model, load_trained_model, predict_attrition

# Train button
if st.button("Train Model"):
    result = train_attrition_model(df_filtered)
    st.session_state['trained_model'] = result['model']
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Accuracy", f"{result['accuracy']:.1%}")
    col2.metric("ROC-AUC", f"{result['roc_auc']:.1%}")
    col3.metric("F1-Score", f"{result['f1']:.1%}")

# Load and predict
if 'trained_model' in st.session_state:
    model = st.session_state['trained_model']
    predictions = predict_attrition(model, df_filtered, result['feature_names'])
```

## Files and Status

| File | Status | Purpose |
|------|--------|---------|
| src/ml_models.py | ✅ Updated | Function implementation |
| requirements.txt | ✅ Updated | Added joblib |
| TRAIN_MODEL_DOCS.md | ✅ Created | Full documentation |
| QUICK_REFERENCE.md | ✅ Created | Quick guide |
| IMPLEMENTATION_SUMMARY.md | ✅ Created | Summary |
| example_train_model.py | ✅ Created | Example script |
| tests/test_train_model.py | ✅ Created | 15+ tests |
| CODE_IMPLEMENTATION.md | ✅ Created | This file |

---

**Status**: ✅ **Ready to Use** - Copy code and run!
