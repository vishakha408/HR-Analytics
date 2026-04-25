# Train Attrition Model Function Documentation

## Overview

The `train_attrition_model()` function provides a complete pipeline for training a RandomForestClassifier to predict employee attrition. It handles data preprocessing, model training, evaluation, and persistence.

## Function Signature

```python
def train_attrition_model(df: pd.DataFrame, target: str = 'Attrition', 
                         features: list = None, test_size: float = 0.2) -> dict
```

## Parameters

### `df` (pd.DataFrame) - **Required**
- Input dataset containing features and target column
- Must be a pandas DataFrame

### `target` (str) - Optional
- Name of the target column to predict
- Default: `'Attrition'`
- Values should be convertible to binary (Yes/No, True/False, 1/0)

### `features` (list) - Optional
- List of column names to use as features
- If `None` (default): automatically selects all numeric columns except target
- Example: `['Age', 'MonthlyIncome', 'YearsAtCompany']`

### `test_size` (float) - Optional
- Proportion of data to use for testing
- Default: `0.2` (20% test, 80% train)
- Must be between 0 and 1

## Return Value

Returns a **dictionary** containing:

```python
{
    'model': RandomForestClassifier,        # Trained model object
    'accuracy': float,                      # Test set accuracy (0-1)
    'roc_auc': float,                       # ROC-AUC score (0-1)
    'precision': float,                     # Precision score
    'recall': float,                        # Recall score
    'f1': float,                            # F1-score
    'model_path': str,                      # Path to saved model
    'metadata_path': str,                   # Path to metadata JSON
    'feature_names': list,                  # Features used in training
    'target_name': str,                     # Target column name
    'train_size': int,                      # Number of training samples
    'test_size': int,                       # Number of test samples
    'feature_importance': dict              # Feature importance scores
}
```

## Model Configuration

The function trains a RandomForestClassifier with:
- **n_estimators**: 200 trees
- **max_depth**: 15 levels
- **min_samples_split**: 10 samples
- **min_samples_leaf**: 4 samples
- **random_state**: 42 (for reproducibility)
- **n_jobs**: -1 (parallel processing on all cores)

## Files Created

1. **model/attrition_model.pkl**
   - Serialized RandomForest model using joblib
   - Can be loaded with `joblib.load()`

2. **model/model_metadata.json**
   - Training metadata (features, target, timestamp, etc.)

## Usage Examples

### Example 1: Default Usage (Auto Feature Selection)

```python
import pandas as pd
from ml_models import train_attrition_model

# Load data
df = pd.read_csv('input_data/raw_hr_data.csv')

# Train model with automatic numeric feature selection
result = train_attrition_model(df)

print(f"Accuracy: {result['accuracy']:.2%}")
print(f"ROC-AUC: {result['roc_auc']:.2%}")
print(f"Model saved to: {result['model_path']}")
```

### Example 2: Custom Features

```python
# Train with specific features
features = ['Age', 'MonthlyIncome', 'YearsAtCompany', 'DistanceFromHome']
result = train_attrition_model(df, features=features, test_size=0.2)

print(f"Features used: {result['feature_names']}")
for feature, importance in result['feature_importance'].items():
    print(f"  {feature}: {importance:.4f}")
```

### Example 3: Custom Target Column

```python
# If your target column has a different name
result = train_attrition_model(df, target='Attrition_Status', test_size=0.25)
```

### Example 4: Different Train/Test Split

```python
# Use 70/30 split instead of 80/20
result = train_attrition_model(df, test_size=0.3)
```

## Helper Functions

### `load_trained_model(model_path)`
Load a previously trained model from disk.

```python
from ml_models import load_trained_model

model = load_trained_model('model/attrition_model.pkl')
```

### `predict_attrition(model, df, features, return_proba=False)`
Make predictions using a trained model.

```python
from ml_models import predict_attrition

# Get binary predictions (0 or 1)
predictions = predict_attrition(model, df_new, features=result['feature_names'])

# Get probabilities (0-1)
probabilities = predict_attrition(model, df_new, 
                                 features=result['feature_names'], 
                                 return_proba=True)
```

## Data Preprocessing Steps

The function automatically:

1. **Selects numeric features** if none are provided
2. **Converts target to binary** (1 for "Yes"/True/1, 0 otherwise)
3. **Handles missing values** by filling with mean of numeric columns
4. **Stratifies train/test split** to maintain target distribution

## Model Performance Metrics

The function calculates and returns:

- **Accuracy**: Percentage of correct predictions
- **ROC-AUC**: Area under the Receiver Operating Characteristic curve (0-1, where 1 is perfect)
- **Precision**: Correctly identified at-risk employees / total predicted at-risk
- **Recall**: Correctly identified at-risk / total actual at-risk
- **F1-Score**: Harmonic mean of precision and recall

## Error Handling

The function raises exceptions for:

- **Missing features**: If specified features don't exist in DataFrame
- **Missing target**: If target column not in DataFrame
- **Invalid data**: If features contain non-numeric data

Example:
```python
try:
    result = train_attrition_model(df, features=['NonExistentColumn'])
except ValueError as e:
    print(f"Error: {e}")
    # Output: Error: Features not found in dataframe: ['NonExistentColumn']
```

## Feature Importance

Access feature importance scores:

```python
importance_dict = result['feature_importance']

# Top 5 features
top_5 = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)[:5]
for feature, score in top_5:
    print(f"{feature}: {score:.4f}")
```

## Reproducibility

- Uses `random_state=42` for all random operations
- Save metadata to recreate exact same training conditions
- Model path saved in result for easy reloading

## Performance Considerations

- **Execution Time**: ~5-30 seconds depending on dataset size
- **Memory Usage**: Depends on dataset size and number of features
- **Parallelization**: Uses all CPU cores (`n_jobs=-1`)

## Common Issues & Solutions

### Issue: "Attrition column not found"
**Solution**: Verify column name in your DataFrame
```python
print(df.columns)  # Check available columns
result = train_attrition_model(df, target='ActualColumnName')
```

### Issue: "Too many features selected automatically"
**Solution**: Explicitly specify desired features
```python
features = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
features = features[:10]  # Use only first 10 numeric features
result = train_attrition_model(df, features=features)
```

### Issue: Model accuracy is too low
**Solution**: Try adjusting test_size or using different features
```python
result = train_attrition_model(df, test_size=0.15)  # Larger training set
# Or select more relevant features
```

## Integration with Streamlit App

The function is integrated in the ML Predictions tab:

```python
# In tab_predictions.py
if st.button("Train Model"):
    result = train_attrition_model(df_filtered)
    st.session_state['trained_model'] = result['model']
    st.metric("Accuracy", f"{result['accuracy']:.1%}")
```

## Example Script

Run the example script to see the function in action:

```bash
python example_train_model.py
```

This demonstrates:
- Automatic feature selection
- Custom feature selection
- Model loading and prediction
- Feature importance display
