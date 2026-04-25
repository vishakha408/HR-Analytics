# Quick Reference: train_attrition_model()

## One-Liner Training
```python
from ml_models import train_attrition_model
result = train_attrition_model(df)
```

## Complete Workflow

```python
import pandas as pd
from ml_models import train_attrition_model, load_trained_model, predict_attrition

# 1. Load data
df = pd.read_csv('input_data/raw_hr_data.csv')

# 2. Train model
result = train_attrition_model(df, test_size=0.2)

# 3. Check metrics
print(f"Accuracy:  {result['accuracy']:.2%}")
print(f"ROC-AUC:   {result['roc_auc']:.2%}")
print(f"Precision: {result['precision']:.2%}")
print(f"Recall:    {result['recall']:.2%}")
print(f"F1-Score:  {result['f1']:.2%}")

# 4. View feature importance
for feature, importance in sorted(result['feature_importance'].items(), 
                                  key=lambda x: x[1], reverse=True)[:5]:
    print(f"  {feature}: {importance:.4f}")

# 5. Load model later
model = load_trained_model(result['model_path'])

# 6. Make predictions
predictions = predict_attrition(model, df, features=result['feature_names'])
probabilities = predict_attrition(model, df, features=result['feature_names'], 
                                 return_proba=True)
```

## Key Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df` | DataFrame | Required | Input dataset |
| `target` | str | `'Attrition'` | Target column name |
| `features` | list | `None` | Feature columns (auto-selects numeric if None) |
| `test_size` | float | `0.2` | Test/train split ratio |

## Return Dictionary Keys

| Key | Type | Description |
|-----|------|-------------|
| `model` | RandomForest | Trained model object |
| `accuracy` | float | Test accuracy (0-1) |
| `roc_auc` | float | ROC-AUC score (0-1) |
| `precision` | float | Precision score |
| `recall` | float | Recall score |
| `f1` | float | F1-score |
| `model_path` | str | Path to saved model |
| `metadata_path` | str | Path to metadata JSON |
| `feature_names` | list | Features used |
| `target_name` | str | Target column |
| `train_size` | int | Train set size |
| `test_size` | int | Test set size |
| `feature_importance` | dict | Feature importance scores |

## Common Patterns

### Automatic Feature Selection (Recommended)
```python
result = train_attrition_model(df)
```

### Specific Features Only
```python
features = ['Age', 'MonthlyIncome', 'YearsAtCompany', 'JobSatisfaction']
result = train_attrition_model(df, features=features)
```

### Different Test Size
```python
result = train_attrition_model(df, test_size=0.25)  # 75/25 split
```

### Custom Target Name
```python
result = train_attrition_model(df, target='Employee_Left')
```

### Top Features
```python
top_5 = dict(sorted(result['feature_importance'].items(), 
                    key=lambda x: x[1], reverse=True)[:5])
print(top_5)
```

## Files Created

```
✓ model/attrition_model.pkl      - Trained model (joblib)
✓ model/model_metadata.json      - Training metadata
✓ src/ml_models.py               - Main module with function
✓ TRAIN_MODEL_DOCS.md            - Full documentation
✓ example_train_model.py         - Example script
✓ tests/test_train_model.py      - Unit tests (15+ cases)
```

## Running Examples

```bash
# Run example script
python example_train_model.py

# Run unit tests
pytest tests/test_train_model.py -v

# Run specific test
pytest tests/test_train_model.py::test_train_attrition_model_basic -v
```

## Error Messages & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `ValueError: Features not found` | Feature doesn't exist | Check column names in df |
| `ValueError: Target column not found` | Target doesn't exist | Verify target column name |
| `FileNotFoundError: Model file not found` | Model path incorrect | Check model directory exists |
| `AssertionError: test_size out of range` | Invalid test_size | Use value between 0 and 1 |

## Performance Metrics Explained

| Metric | Meaning | Good Value |
|--------|---------|------------|
| **Accuracy** | % correct predictions | > 0.80 |
| **ROC-AUC** | Ranking ability | > 0.85 |
| **Precision** | True positives / predicted positives | > 0.70 |
| **Recall** | True positives / actual positives | > 0.70 |
| **F1-Score** | Harmonic mean of precision & recall | > 0.70 |

## Model Configuration

```python
RandomForestClassifier(
    n_estimators=200,          # Number of trees
    max_depth=15,              # Tree depth limit
    min_samples_split=10,      # Min samples to split
    min_samples_leaf=4,        # Min samples in leaf
    random_state=42,           # Reproducibility
    n_jobs=-1                  # Use all CPU cores
)
```

## Reproducibility

The function uses `random_state=42` ensuring:
- Same results across runs
- Consistent train/test splits
- Reproducible feature selection

To use a different seed:
```python
# Modify in ml_models.py, line ~280:
# X_train, X_test, y_train, y_test = train_test_split(..., random_state=YOUR_SEED)
```

## Integration with Streamlit

```python
# In tab_predictions.py
if st.button("Train Model"):
    result = train_attrition_model(df_filtered)
    st.session_state['model'] = result['model']
    st.session_state['features'] = result['feature_names']
    st.metric("Accuracy", f"{result['accuracy']:.1%}")
    st.metric("ROC-AUC", f"{result['roc_auc']:.1%}")
```

## Dependencies

- pandas
- scikit-learn
- joblib
- numpy

## Status
✅ **Production Ready** - Fully tested and documented
