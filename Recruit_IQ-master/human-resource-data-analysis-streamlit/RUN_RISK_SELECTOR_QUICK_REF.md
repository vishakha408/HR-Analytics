# run_risk_selector() - Quick Reference

## Quick Start

### Basic Usage
```python
from ml_models import run_risk_selector
import pandas as pd

df = pd.read_csv('employees.csv')
run_risk_selector(df)
```

### In Streamlit App
```python
# tab_predictions.py
ml_models.run_risk_selector(df_filtered)
```

---

## Filtering Modes

### Mode 1: Top N Risky Employees
```
Select filtering mode: Top N Risky
Number to show: 1-100 (default: 20)
```
**Result**: Top N employees with highest attrition probability

**Use for**: 
- Quick identification of most at-risk employees
- Focus retention efforts
- Compliance checks

---

### Mode 2: Probability Threshold
```
Select filtering mode: Probability Threshold
Probability threshold: 0.0-1.0 (default: 0.6)
```
**Result**: All employees with probability >= threshold

**Use for**:
- Target specific risk levels
- Intervention programs
- Risk segmentation

---

## Output Columns

| Column | Format | Description |
|--------|--------|-------------|
| EmployeeNumber | Integer | Employee ID |
| EmployeeName | Text | Full name |
| Department | Text | Department name |
| JobRole | Text | Job title |
| MonthlyIncome | Currency | Salary |
| YearsAtCompany | Integer | Tenure |
| Age | Integer | Age in years |
| JobSatisfaction | Text | Satisfaction level |
| pred_attrition_prob | Percentage | Probability (0-100%) |
| pred_attrition_label | Text | "At Risk" or "Stable" |

---

## Summary Metrics

| Metric | Description |
|--------|-------------|
| Total Employees | Count of all employees in dataset |
| Avg Risk Probability | Mean probability (0-100%) |
| Predicted Attrition | Count of at-risk employees (%) |
| Filtered Results | Count matching current filter |

---

## Download Formats

### CSV Download
- All filtered rows
- Filename: `attrition_risk_employees_YYYYMMDD_HHMMSS.csv`
- Opens in Excel, Python, R, etc.

### Excel Download
- **Sheet 1**: Full results table
- **Sheet 2**: Summary metrics
- Filename: `attrition_risk_employees_YYYYMMDD_HHMMSS.xlsx`
- Professional formatting

---

## Example Workflows

### Workflow 1: Find Top 50 At-Risk Employees
1. Go to ML PREDICTIONS tab
2. Scroll to "Advanced Risk Analysis"
3. Select "Top N Risky"
4. Slide to 50
5. Download as Excel
6. Share with HR team

### Workflow 2: Target 75% Risk Threshold
1. ML PREDICTIONS tab
2. Select "Probability Threshold"
3. Slide to 0.75
4. Review "Very High Risk" employees
5. Download CSV
6. Plan interventions

### Workflow 3: Department Analysis
1. Filter sidebar: Select Sales department
2. ML PREDICTIONS tab
3. Generate predictions (already filtered)
4. Select Top 20 risky in Sales
5. Download to share with Sales Manager

### Workflow 4: Monthly Monitoring
1. Generate predictions (1st of each month)
2. Download Excel file
3. Save to tracking folder
4. Compare month-over-month
5. Track probability changes

---

## Tips & Tricks

### Tip 1: Filter First
Use sidebar filters before generating predictions to focus on specific groups:
- By department
- By job role
- By tenure
- By salary range

### Tip 2: Threshold Selection
- **0.5 (50%)**: Model's default decision threshold
- **0.6 (60%)**: Balanced risk assessment
- **0.75 (75%)**: High confidence at-risk
- **0.9 (90%)**: Very high risk only

### Tip 3: CSV vs Excel
- **CSV**: Better for data analysis in Python/R
- **Excel**: Better for sharing with non-technical users

### Tip 4: Export Often
Export results regularly to track trends over time

### Tip 5: Cross-Check Results
Review top at-risk employees manually to validate model

---

## Common Scenarios

### Scenario 1: Immediate Action Needed
```
Mode: Top N Risky
Value: 10-20
Goal: Identify most urgent cases for immediate intervention
```

### Scenario 2: Retention Program
```
Mode: Probability Threshold
Value: 0.6
Goal: Target moderate to high-risk for retention program
```

### Scenario 3: HR Planning
```
Mode: Top N Risky
Value: 50-100
Goal: Broad assessment for hiring/planning
```

### Scenario 4: Compliance Review
```
Mode: Probability Threshold
Value: 0.5
Goal: Flag any employee with risk above model threshold
```

---

## Error Messages

| Error | Solution |
|-------|----------|
| ❌ Model file not found | Train model in ATTRITION ANALYSIS tab first |
| ⚠️ Excel export unavailable | Use CSV download instead |
| No employees match criteria | Lower threshold or increase N value |

---

## Data Example

### Top 3 At-Risk Employees (Top N Mode)

| EmployeeNumber | EmployeeName | Department | JobRole | pred_attrition_prob | pred_attrition_label |
|---|---|---|---|---|---|
| 1247 | Sarah Johnson | Sales | Sales Executive | 89% | At Risk |
| 1089 | Mike Chen | IT | Senior Developer | 87% | At Risk |
| 1102 | Lisa Brown | HR | HR Specialist | 76% | At Risk |

### Threshold Example (0.6 threshold)

Shows 127 employees with probability >= 60%
- Min prob: 60.1%
- Max prob: 89.3%
- Avg prob: 71.2%

---

## Prediction Interpretation

### Probability Ranges

- **0-25%**: Low risk - Employee likely to stay
- **25-50%**: Medium-low risk - Monitor but likely stable
- **50-75%**: High risk - Active monitoring needed
- **75-100%**: Very high risk - Immediate intervention

### Label Interpretation

- **0 (Stable)**: Model predicts employee will stay (prob < 0.5)
- **1 (At Risk)**: Model predicts employee may leave (prob >= 0.5)

---

## Performance Indicators

| Metric | Interpretation |
|--------|-----------------|
| High % in "At Risk" | Organization has attrition pressure |
| High % in "Very High" | Immediate HR actions needed |
| Increasing trend | Attrition risk rising over time |
| Decreasing trend | Retention initiatives working |

---

## Advanced Options

### Expandable Section: Risk Distribution Statistics

Shows detailed probability distribution:
- **Probability Statistics**: Min, Q1, Median, Q3, Max
- **Class Distribution**: Count in each risk category

Use to understand overall risk profile of organization

---

## Prerequisites

✅ Model trained in ATTRITION ANALYSIS tab
✅ Model saved to `model/attrition_model.pkl`
✅ Metadata saved to `model/model_metadata.json`

---

## Related Sections

- **PREDICTIONS TAB**: Generate predictions for all employees
- **ATTRITION ANALYSIS**: Train the model
- **CAPACITY ANALYSIS**: See workforce trends
- **EXECUTIVE SUMMARY**: Overview metrics

---

**Quick Reference Version**: 1.0  
**Last Updated**: November 14, 2024  
**Status**: ✅ Ready to Use
