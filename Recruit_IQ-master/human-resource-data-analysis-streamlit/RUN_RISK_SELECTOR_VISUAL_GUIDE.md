# run_risk_selector() - Visual Guide & Examples

## 🎯 Quick Visual Overview

### Function Location
```
src/
├── ml_models.py
│   ├── train_attrition_model()    ← Trains model
│   ├── load_trained_model()       ← Loads model
│   ├── predict_attrition()        ← Makes predictions
│   └── run_risk_selector()        ← NEW: Interactive filtering
│
└── tab_predictions.py
    └── render(df)
        └── ml_models.run_risk_selector(df)  ← Called here
```

---

## 🖼️ UI Layout

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 Filter At-Risk Employees                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Select filtering mode:                                    │
│  ☒ Top N Risky    ○ Probability Threshold                 │
│                                                             │
│  Number of employees to show:    [==================◊==] 20 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  📊 Summary Metrics                                        │
├──────────────┬──────────────┬──────────────┬──────────────┤
│ Total        │ Avg Risk     │ Predicted    │ Filtered     │
│ Employees    │ Probability  │ Attrition    │ Results      │
│              │              │              │              │
│    1,470     │    64.2%     │  437 (29.7%) │      20      │
├─────────────────────────────────────────────────────────────┤
│  📋 Results: Top 20 employees by attrition probability   │
├─────────────────────────────────────────────────────────────┤
│ # │ Emp # │ Name          │ Dept  │ Role  │ Risk │ Label  │
├───┼───────┼───────────────┼───────┼───────┼──────┼────────┤
│ 1 │ 1247  │ Sarah Johnson │ Sales │ Exec  │ 89%  │ At Risk│
│ 2 │ 1089  │ Mike Chen     │ IT    │ Dev   │ 87%  │ At Risk│
│ 3 │ 1102  │ Lisa Brown    │ HR    │ Spec  │ 76%  │ At Risk│
│ ... more rows ...                                          │
├─────────────────────────────────────────────────────────────┤
│  📥 Download Selected Results                             │
├─────────────────────────────────────────────────────────────┤
│ [📄 Download as CSV]  [📊 Download as Excel]             │
├─────────────────────────────────────────────────────────────┤
│  📈 Risk Distribution Statistics                          │
│  ◄ click to expand                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Mode Selection Examples

### Mode A: Top N Risky

```
Input: Slider = 20
       
Processing:
  1. Sort all employees by pred_attrition_prob (descending)
  2. Take top 20
  
Output:
  Employees with highest attrition probability:
  
  Rank │ Employee      │ Department │ Risk Prob
  ─────┼───────────────┼────────────┼──────────
   1   │ Sarah Johnson │ Sales      │  89.2%
   2   │ Mike Chen     │ IT         │  87.5%
   3   │ Lisa Brown    │ HR         │  76.3%
   ...
```

### Mode B: Probability Threshold

```
Input: Slider = 0.6 (60%)
       
Processing:
  1. Filter all employees where pred_attrition_prob >= 0.6
  2. Sort by probability (descending)
  
Output:
  All employees with >= 60% attrition probability:
  
  Count: 217 employees
  Min Prob: 60.1%
  Max Prob: 93.8%
  Avg Prob: 71.4%
```

---

## 📋 Output Format Examples

### Display Table

```
| EmployeeNumber | EmployeeName | Department | JobRole | ... | pred_attrition_prob | pred_attrition_label |
|---|---|---|---|---|---|---|
| 1247 | Sarah Johnson | Sales | Sales Executive | ... | 89.2% | At Risk |
| 1089 | Mike Chen | IT | Senior Developer | ... | 87.5% | At Risk |
| 1102 | Lisa Brown | HR | HR Specialist | ... | 76.3% | At Risk |
| 1156 | Tom Davis | Finance | Analyst | ... | 42.1% | Stable |
```

### CSV Export Example

```csv
EmployeeNumber,EmployeeName,Department,JobRole,MonthlyIncome,YearsAtCompany,Age,JobSatisfaction,pred_attrition_prob,pred_attrition_label
1247,Sarah Johnson,Sales,Sales Executive,8500,3,42,Very Low,0.892,At Risk
1089,Mike Chen,IT,Senior Developer,12000,5,39,Medium,0.875,At Risk
1102,Lisa Brown,HR,HR Specialist,6500,2,35,Low,0.763,At Risk
1156,Tom Davis,Finance,Analyst,7200,8,51,High,0.421,Stable
```

### Excel Export - Sheet 1 (Results)

```
EmployeeNumber │ EmployeeName │ Department │ JobRole │ ... │ pred_attrition_prob │ pred_attrition_label
───────────────┼──────────────┼────────────┼─────────┼─────┼─────────────────────┼──────────────────
       1247    │ Sarah...     │ Sales      │ Exec    │ ... │ 0.892               │ At Risk
       1089    │ Mike...      │ IT         │ Dev     │ ... │ 0.875               │ At Risk
       1102    │ Lisa...      │ HR         │ Spec    │ ... │ 0.763               │ At Risk
```

### Excel Export - Sheet 2 (Summary)

```
Metric                  │ Value
────────────────────────┼─────────────────────────────────────
Filter Criteria          │ Top 20 employees by attrition probability
Total Employees          │ 1470
Filtered Results         │ 20
Avg Risk Probability     │ 81.2%
Predicted Attrition      │ 437
Attrition %              │ 29.7%
Export Time              │ 2024-11-14 15:30:45
```

---

## 🔄 Data Flow Diagram

```
┌─────────────────────────┐
│   User Opens App        │
│   Applies Filters       │
└────────────┬────────────┘
             │ df_hr_filtered
             ▼
┌─────────────────────────────────────┐
│  ML PREDICTIONS Tab                 │
│  render(df_hr_filtered)             │
└────────────┬────────────────────────┘
             │
             ▼
┌─────────────────────────────────────┐
│  run_risk_selector(df_filtered)     │
└────────────┬────────────────────────┘
             │
             ├─────────────────────────┐
             │                         │
    ┌────────▼─────────┐  ┌──────────▼────────┐
    │ Load Model       │  │ Load Metadata     │
    │ (cached)         │  │ (cached)          │
    └────────┬─────────┘  └──────────┬────────┘
             │                         │
             └────────────┬────────────┘
                          │
                          ▼
            ┌─────────────────────────────┐
            │  Prepare Features           │
            │  - Select numeric cols      │
            │  - Remove target            │
            │  - Use metadata names       │
            │  - Impute missing           │
            │  - Align with model         │
            │  - Add missing as zeros     │
            └────────────┬────────────────┘
                         │
                         ▼
            ┌─────────────────────────────┐
            │  Generate Predictions       │
            │  - predict_proba()          │
            │  - Binary labels (>= 0.5)   │
            │  - Add to dataframe         │
            └────────────┬────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────┐
        │  Display UI Controls               │
        │  - Mode selection (radio)          │
        │  - Parameter slider                │
        │  - Summary metrics (4 cards)       │
        └────────────┬───────────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  User Selects Mode & Value     │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  Apply Filter                  │
        │  ├─ Top N: sort, take top N    │
        │  └─ Threshold: filter >= val   │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  Display Results               │
        │  - Results table (top 50)      │
        │  - Filter description          │
        │  - Advanced stats (optional)   │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  Download Options              │
        │  ├─ CSV (all filtered rows)    │
        │  └─ Excel (2 sheets)           │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  User Clicks Download          │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  Generate File                 │
        │  ├─ CSV: all rows              │
        │  └─ Excel: results + summary   │
        └────────────┬───────────────────┘
                     │
        ┌────────────▼───────────────────┐
        │  Download File                 │
        │  Saved to user's computer      │
        └────────────────────────────────┘
```

---

## 💡 Usage Scenarios

### Scenario 1: Weekly High-Risk Check

```
Monday Morning:
  1. Open ML PREDICTIONS tab
  2. Select "Top N Risky"
  3. Set to 30
  4. Download Excel
  5. Share with HR Manager
  6. Plan weekly interventions

Time to complete: 2 minutes
Files downloaded: attrition_risk_employees_20241114_090000.xlsx
```

### Scenario 2: Department Focus

```
Sales Manager Request:
  1. Filter sidebar: Department = "Sales"
  2. ML PREDICTIONS tab
  3. Select "Top N Risky"
  4. Set to 15 (top sales at-risk)
  5. Download CSV
  6. Share with team leads

Time to complete: 3 minutes
Files downloaded: attrition_risk_employees_20241114_100000.csv
Recipients: Sales team
```

### Scenario 3: Retention Program

```
HR Director Planning:
  1. ML PREDICTIONS tab
  2. Select "Probability Threshold"
  3. Set to 0.65
  4. Review 200+ medium-high risk employees
  5. Download Excel with summary
  6. Allocate retention budget
  7. Schedule interventions

Time to complete: 5 minutes
Files downloaded: attrition_risk_employees_20241114_140000.xlsx
Decisions made: Budget allocation, intervention plan
```

### Scenario 4: Monthly Tracking

```
End of Month Analysis:
  1. Generate predictions
  2. Download CSV with timestamp
  3. Save to: /reports/predictions_2024_11.csv
  4. Compare with previous month
  5. Identify trends
  6. Present to leadership

Time to complete: 10 minutes
Files saved: Historical trend data
Analysis: Risk trend over time
```

---

## 📊 Metrics Interpretation

### Summary Metrics

```
Total Employees: 1,470
├─ Baseline for comparison
└─ Shows dataset size

Avg Risk Probability: 64.2%
├─ Mean attrition probability
├─ Higher = more at-risk organization
└─ Range: 0-100%

Predicted Attrition: 437 (29.7%)
├─ Count with label = 1
├─ Percentage of total
└─ High number = retention concern

Filtered Results: 20
├─ Matching current filter criteria
├─ Shows filter effectiveness
└─ Number of rows to download
```

### Risk Probability Ranges

```
0-25%    Low Risk       ████░░░░░░
         └─ Likely to stay, stable employees

25-50%   Medium Risk    ████████░░
         └─ Monitor, generally stable

50-75%   High Risk      ████████████░░
         └─ Active monitoring needed

75-100%  Very High Risk ██████████████
         └─ Immediate intervention urgent
```

---

## 🎨 Color & Symbol Guide

| Symbol | Meaning |
|--------|---------|
| 🎯 | Filter/Selection controls |
| 📊 | Metrics and statistics |
| 📋 | Results table/display |
| 📥 | Download options |
| 📈 | Advanced analysis |
| ✅ | Successfully completed |
| ❌ | Error or issue |
| ⚠️ | Warning message |
| ℹ️ | Information/help |

---

## 🔧 Feature Preparation Example

```
Input DataFrame:
┌─────┬─────────────┬────────────┬────────┬─────────┐
│ ID  │ Name        │ Age        │ Salary │ JobRole │
├─────┼─────────────┼────────────┼────────┼─────────┤
│ 101 │ John Smith  │ 42         │ 8500   │ Manager │
│ 102 │ Jane Doe    │ 35 (MISS)  │ 9200   │ Senior  │
│ 103 │ Bob Jones   │ 50         │ 7800   │ Junior  │
└─────┴─────────────┴────────────┴────────┴─────────┘

Step 1: Select numeric columns
├─ ID (numeric) ✓
├─ Age (numeric) ✓
├─ Salary (numeric) ✓
└─ JobRole (text) ✗

Step 2: Remove target (Attrition)
├─ Age ✓
└─ Salary ✓

Step 3: Use metadata feature names
├─ Feature list: [Age, Salary]
└─ Match available: ✓

Step 4: Impute missing
├─ Age column missing: 35 → mean(42,50) = 46
└─ Result: [42, 46, 50]

Step 5: Align with model
├─ Model expects: [Age, Salary, Experience, ...]
├─ Available: [Age, Salary]
└─ Add missing: Experience = 0 (not in input)

Step 6: Final X for prediction
┌────────┬────────┬────────────┐
│ Age    │ Salary │ Experience │
├────────┼────────┼────────────┤
│ 42     │ 8500   │ 0          │
│ 46     │ 9200   │ 0          │
│ 50     │ 7800   │ 0          │
└────────┴────────┴────────────┘
```

---

## 🚀 Performance Example

```
Dataset Size: 1,470 employees

Operation Timeline:
├─ Load Model (cached): 100ms      ⚡ Fast
├─ Load Metadata (cached): 50ms    ⚡ Fast
├─ Prepare Features: 150ms         ⚡ Fast
├─ Generate Predictions: 250ms     ⚡ Fast
├─ Prepare Display: 50ms           ⚡ Fast
├─ Render UI: 100ms                ⚡ Fast
└─ TOTAL: ~700ms                   ✅ < 1 second

User Clicks Download:
├─ CSV Export: 100ms               ⚡ Instant
└─ Excel Export: 1.5s              ✅ Fast

Overall User Experience: Responsive, no lag
```

---

## 📚 Documentation Structure

```
├─ RUN_RISK_SELECTOR_DOCS.md
│  ├─ Complete API reference
│  ├─ Implementation details
│  ├─ 4 Usage examples
│  └─ Troubleshooting guide
│
├─ RUN_RISK_SELECTOR_QUICK_REF.md
│  ├─ Quick start (5 min)
│  ├─ Filtering modes
│  ├─ 4 Workflows
│  └─ Tips & tricks
│
├─ RUN_RISK_SELECTOR_IMPLEMENTATION.md
│  ├─ Feature checklist
│  ├─ Code structure
│  ├─ Technical decisions
│  └─ Testing checklist
│
├─ RUN_RISK_SELECTOR_COMPLETE.md
│  ├─ Complete summary
│  ├─ Architecture overview
│  └─ Deployment status
│
└─ RUN_RISK_SELECTOR_VISUAL_GUIDE.md (THIS FILE)
   ├─ Visual examples
   ├─ UI layouts
   ├─ Data flow diagrams
   └─ Usage scenarios
```

---

## ✅ Checklist for First Use

```
Pre-Requirements:
☐ Model trained in ATTRITION ANALYSIS tab
☐ Model saved to model/attrition_model.pkl
☐ Metadata saved to model/model_metadata.json

First Time Using:
☐ Navigate to ML PREDICTIONS tab
☐ Scroll to "Advanced Risk Analysis" section
☐ Read the description
☐ Select a filtering mode
☐ Adjust slider to desired value
☐ Review results table
☐ Check summary metrics
☐ Download results

Advanced Usage:
☐ Try both filtering modes
☐ Explore advanced statistics
☐ Export to CSV for analysis
☐ Export to Excel for sharing
☐ Use filters with sidebar
☐ Track results over time
```

---

**Visual Guide Version**: 1.0  
**Created**: November 14, 2024  
**Status**: ✅ Complete
