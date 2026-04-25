# run_risk_selector() - Employee At-Risk Identification Function

## Overview

`run_risk_selector()` is an interactive Streamlit component that helps identify and filter employees at risk of attrition based on their predicted attrition probability. It provides two flexible filtering modes and comprehensive download options.

## Function Signature

```python
def run_risk_selector(df_filtered: pd.DataFrame, 
                     model_path: str = "model/attrition_model.pkl",
                     metadata_path: str = "model/model_metadata.json") -> None:
    """
    Interactive risk selector UI for identifying employees at risk of attrition.
    """
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `df_filtered` | pd.DataFrame | Required | Input dataset with employee records (can include filters applied) |
| `model_path` | str | `"model/attrition_model.pkl"` | Path to saved trained model file |
| `metadata_path` | str | `"model/model_metadata.json"` | Path to model metadata with feature names |

## Requirements

### 1. Trained Model
- Must exist at path specified by `model_path`
- Trained RandomForest classifier with `predict_proba()` support
- Should have `feature_names_in_` attribute (sklearn standard)

### 2. Model Metadata
- JSON file at path specified by `metadata_path`
- Should contain `feature_names` list
- Contains training timestamp and other info

### 3. Input DataFrame
- Must contain numeric feature columns used in training
- Can have any number of rows
- Employee identifier columns (e.g., EmployeeNumber, EmployeeName)
- Other HR attributes (Department, JobRole, etc.)

## Features

### 1. Two Filtering Modes

#### Mode A: Top N Risky Employees
- Shows top N employees with highest attrition probability
- Slider control: 1-100 employees
- Default: 20 employees
- Sorted by probability (highest first)

```python
# User selects: "Top N Risky"
# UI Shows: Slider to select N (1-100)
# Result: Top N employees with highest prob
```

#### Mode B: Probability Threshold
- Shows all employees with probability >= threshold
- Slider control: 0.0 to 1.0
- Default: 0.6 (60%)
- Sorted by probability (highest first)

```python
# User selects: "Probability Threshold"
# UI Shows: Slider to select threshold (0.0-1.0)
# Result: All employees with prob >= threshold
```

### 2. Prediction Columns

Automatically added to results:

| Column | Type | Description | Values |
|--------|------|-------------|--------|
| `pred_attrition_prob` | float | Probability of attrition | 0.0 to 1.0 |
| `pred_attrition_label` | int | Binary prediction | 0 (Stable) or 1 (At Risk, prob >= 0.5) |

### 3. Summary Metrics

Displayed in 4-column layout:

- **Total Employees**: Count of all employees in filtered dataset
- **Avg Risk Probability**: Mean probability across all predictions
- **Predicted Attrition**: Count and % of employees with label=1
- **Filtered Results**: Count of employees matching selected criteria

### 4. Results Display

- **Default Display**: Top 50 filtered rows
- **Height**: 400px scrollable table
- **Format**:
  - Base columns: EmployeeNumber, EmployeeName, Department, JobRole, MonthlyIncome, YearsAtCompany, Age, JobSatisfaction
  - Prediction columns: pred_attrition_prob (formatted %), pred_attrition_label (formatted as "At Risk"/"Stable")
  - Adjusts to available columns

### 5. Download Options

#### CSV Download
- Full filtered dataset
- All selected rows (not just top 50 displayed)
- Preserves original data types
- Filename: `attrition_risk_employees_YYYYMMDD_HHMMSS.csv`

#### Excel Download
- Two worksheets:
  1. **"At-Risk Employees"**: Full filtered results
  2. **"Summary"**: Key metrics and filter criteria
- Professional formatting
- Filename: `attrition_risk_employees_YYYYMMDD_HHMMSS.xlsx`

### 6. Additional Statistics

Optional expandable section showing:

**Probability Statistics:**
- Min, Q1, Median, Q3, Max values
- Shows distribution range

**Class Distribution:**
- Low Risk (0-25%): Count and %
- Medium Risk (25-50%): Count and %
- High Risk (50-75%): Count and %
- Very High Risk (75-100%): Count and %

## Implementation Details

### Feature Preparation

```python
def prepare_features(df):
    """
    1. Extract numeric columns
    2. Remove 'Attrition' target if present
    3. Use feature names from metadata
    4. Fill missing values with column mean
    5. Align with model.feature_names_in_
    6. Add missing features as zeros
    7. Reorder to match model's expected order
    """
```

Steps:
1. Get numeric columns only
2. Remove target variable if present
3. Use feature names from metadata (if available)
4. Impute missing values with mean
5. Add missing features as zeros
6. Reorder to match model training order

### Prediction Generation

```python
pred_proba = model.predict_proba(X)[:, 1]  # Probabilities
pred_labels = (pred_proba >= 0.5).astype(int)  # Binary labels
```

- Probabilities: Class 1 (attrition) probability from predict_proba
- Labels: Binary 0/1 with 0.5 threshold

### Caching

```python
@st.cache_resource
def load_model():
    return joblib.load(model_path)

@st.cache_resource
def load_metadata():
    # Load metadata
```

- Model loading cached per Streamlit session
- Metadata loading cached
- Predictions NOT cached (fresh each run)

### Error Handling

```python
if not os.path.exists(model_path):
    st.error("❌ Model file not found...")
    return

# Excel export try/catch
try:
    # Excel creation
except Exception as e:
    st.warning(f"⚠️ Excel export unavailable: {str(e)}")
```

- Checks model existence before proceeding
- Graceful failure for Excel export (CSV always works)
- Clear error messages to user

## Usage Examples

### Example 1: Basic Usage

```python
import streamlit as st
import pandas as pd
from ml_models import run_risk_selector

# In a Streamlit app
df = pd.read_csv('employees.csv')
run_risk_selector(df)
```

### Example 2: Integration in Tab

```python
# In tab_predictions.py
def render(df: pd.DataFrame):
    st.subheader("ML Predictions")
    
    # ... Other prediction sections ...
    
    # Risk Selector
    ml_models.run_risk_selector(df)
```

### Example 3: Custom Paths

```python
run_risk_selector(
    df_filtered,
    model_path="models/custom_model.pkl",
    metadata_path="models/custom_metadata.json"
)
```

### Example 4: Filtered Data

```python
# User filters sidebar
filtered_df = df[df['Department'] == 'Sales']

# Pass filtered data to risk selector
run_risk_selector(filtered_df)
```

## Output Files

### CSV Format
```
EmployeeNumber,EmployeeName,Department,JobRole,...,pred_attrition_prob,pred_attrition_label
1001,John Smith,Sales,Sales Executive,...,0.72,At Risk
1005,Jane Doe,IT,Developer,...,0.45,Stable
...
```

### Excel Format

**Sheet 1: At-Risk Employees**
| EmployeeNumber | EmployeeName | ... | pred_attrition_prob | pred_attrition_label |
|---|---|---|---|---|
| 1001 | John Smith | ... | 0.72 | At Risk |
| 1005 | Jane Doe | ... | 0.45 | Stable |

**Sheet 2: Summary**
| Metric | Value |
|--------|-------|
| Filter Criteria | Top 20 employees by attrition probability |
| Total Employees | 1470 |
| Filtered Results | 20 |
| Avg Risk Probability | 64.2% |
| Predicted Attrition | 437 (29.7%) |
| Attrition % | 29.7% |
| Export Time | 2024-11-14 15:30:45 |

## Key Features Summary

✅ **Two Filtering Modes**
- Top N employees (slider 1-100)
- Probability threshold (slider 0.0-1.0)

✅ **Intelligent Feature Handling**
- Automatic numeric column detection
- Missing value imputation
- Column alignment with trained model
- Missing feature padding with zeros

✅ **Comprehensive Metrics**
- Total employees
- Average risk probability
- Predicted attrition count
- Filtered results count

✅ **Results Display**
- Top 50 rows in scrollable table
- Multiple display modes
- Formatted output (percentages, readable labels)

✅ **Download Options**
- CSV export (all filtered rows)
- Excel export (2 sheets: results + summary)
- Timestamped filenames

✅ **Advanced Statistics**
- Risk probability distribution (min, Q1, median, Q3, max)
- Risk category breakdown (4 levels)
- Expandable UI section

✅ **Error Handling**
- Model existence validation
- Graceful fallback for exports
- Clear user messages

✅ **Performance**
- Cached model loading
- Cached metadata loading
- Efficient numpy operations

## Common Use Cases

### Use Case 1: Identify Top Performers to Retain
```
Mode: Top N Risky
Value: 50
Action: Review top 50 at-risk employees, plan retention strategies
```

### Use Case 2: Target High-Risk Employees
```
Mode: Probability Threshold
Value: 0.75 (75%)
Action: Focus immediate intervention on very high-risk employees
```

### Use Case 3: Department-Specific Analysis
```
1. Filter sidebar: Department = 'Sales'
2. run_risk_selector(filtered_df)
3. Download results for Sales department only
```

### Use Case 4: Monthly Monitoring
```
1. Generate predictions for all employees
2. Export results
3. Compare month-over-month trends
4. Track changes in risk probabilities
```

## Performance Considerations

- **Model Loading**: ~100ms (cached after first load)
- **Prediction Generation**: Depends on dataset size
  - 100 employees: ~50ms
  - 1000 employees: ~200ms
  - 10000 employees: ~1-2s
- **CSV Export**: Linear with dataset size
- **Excel Export**: ~1-2s (includes formatting)
- **UI Rendering**: <100ms (Streamlit caching)

## Integration with Streamlit App

### Location
- **Tab**: ML PREDICTIONS tab (`tab_predictions.py`)
- **Section**: "Advanced Risk Analysis"
- **Called from**: `render(df)` function

### Data Flow
```
app.py (main)
  ↓
render_filter_sidebar() → df_hr_filtered
  ↓
tab_predictions.render(df_hr_filtered)
  ↓
ml_models.run_risk_selector(df_hr_filtered)
```

### Session State
- No session state used (stateless design)
- Fresh predictions on each user interaction
- Streamlit handles caching

## Troubleshooting

### Issue: "Model file not found"
**Solution**: Train model first in ATTRITION ANALYSIS tab

### Issue: "Feature mismatch error"
**Solution**: Automatically handled - missing features added as zeros

### Issue: Excel download fails
**Solution**: Use CSV download instead (same data)

### Issue: Predictions look wrong
**Solution**: Check filter sidebar - may be using subset of data

### Issue: Performance is slow
**Solution**: 
- Filter data before passing (smaller dataset)
- Check model and data sizes
- Try threshold mode instead of top N

## Related Functions

- `train_attrition_model()` - Trains the model
- `load_trained_model()` - Loads model from disk
- `predict_attrition()` - Makes predictions
- `prepare_features_for_prediction()` - Feature prep helper

## File Dependencies

- `model/attrition_model.pkl` - Trained RandomForest model
- `model/model_metadata.json` - Training metadata
- `src/ml_models.py` - Function definition
- `src/tab_predictions.py` - Integration point

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-11-14 | Initial release with Top N and Threshold modes |

---

**Status**: ✅ Production Ready  
**Last Updated**: November 14, 2024
