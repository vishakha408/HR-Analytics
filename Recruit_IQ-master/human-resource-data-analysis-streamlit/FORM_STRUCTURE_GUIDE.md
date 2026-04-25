# Candidate Entry Form - Structure Guide

## Form Layout

```
┌─────────────────────────────────────────────────────────┐
│ Candidate Entry — [block_id]  [expand/collapse]         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │   COLUMN 1           │  │   COLUMN 2           │   │
│  ├──────────────────────┤  ├──────────────────────┤   │
│  │ Candidate ID / Roll  │  │ Applied Position     │   │
│  │ [______________]     │  │ [______________]     │   │
│  │                      │  │                      │   │
│  │ Full Name            │  │ Phone (Optional)     │   │
│  │ [______________]     │  │ [______________]     │   │
│  │                      │  │                      │   │
│  │ Email                │  │ Experience (years)   │   │
│  │ [______________]     │  │ [__]                 │   │
│  └──────────────────────┘  └──────────────────────┘   │
│                                                         │
│ Candidate Notes (Optional)                              │
│ ┌─────────────────────────────────────────────────┐   │
│ │                                                 │   │
│ │  [3 lines of textarea...]                       │   │
│ │                                                 │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ ** Scoring (0-10 scale) **                              │
│                                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐               │
│  │ Comm    │  │ Projects│  │ Cultural│               │
│  │ [|---5-]│  │ [|---5-]│  │ [|---5-]│               │
│  │ Tech    │  │ Problem │  │         │               │
│  │ [|---5-]│  │ [|---5-]│  │         │               │
│  └─────────┘  └─────────┘  └─────────┘               │
│                                                         │
│ ─────────────────────────────────────────────────────  │
│                                                         │
│  [💾 Save Candidate]  [🗑️ Remove Block]              │
│  (primary button)     (secondary button)              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Form State Management

### Session State Keys
Each candidate block creates session state keys following pattern: `{block_id}_{field_name}`

**Basic Fields**:
- `{block}_id` - Candidate ID / Roll
- `{block}_name` - Full Name (required)
- `{block}_email` - Email address
- `{block}_position` - Applied Position (required)
- `{block}_phone` - Phone number
- `{block}_exp` - Experience in years (numeric)
- `{block}_notes` - Candidate notes

**Metric Scores** (0-10 sliders):
- `{block}_metric_Communication` - Communication score
- `{block}_metric_Technical` - Technical Skills score
- `{block}_metric_Projects` - Projects score
- `{block}_metric_Problem_Solving` - Problem Solving score
- `{block}_metric_Cultural_Fit` - Cultural Fit score

### Data Flow on Form Submit

```
Form Submit (Save Candidate)
    ↓
[Collect all session state values]
    ↓
[Validate: name required, position required]
    ↓ (if validation fails)
Show error message, stay on form
    ↓ (if validation passes)
[Collect metric scores into dict]
[Compute average score]
[Build candidate_record dict]
    ↓
[Append to st.session_state['session_candidates']]
[Update st.session_state['current_session']['candidates']]
[Update st.session_state['current_session']['custom_metrics']]
    ↓
[Call save_session_data() → persist to JSON file]
    ↓ (if save succeeds)
Show success message
Remove block from st.session_state['candidate_blocks']
    ↓
st.rerun() (refresh UI)
    ↓ (if save fails)
Show error message
Stay on form
```

## Candidate Record Structure

After successful save, record stored in `session_candidates` list:

```python
candidate_record = {
    'id': 'EMP123' or auto-generated,      # Candidate ID / Roll
    'roll': 'EMP123',                       # Same as ID
    'name': 'John Doe',                     # Full Name (required)
    'email': 'john@example.com',            # Email (optional)
    'position': 'Senior Engineer',          # Applied Position (required)
    'experience_years': 5.0,                # Years of experience
    'phone': '+1-555-0123',                 # Phone (optional)
    'notes': 'Great candidate, ...',        # Candidate Notes (optional)
    'added_at': '2024-01-15T10:30:00',     # ISO timestamp
    'score': 7.2,                           # Average of all metric scores
    'scores': {                             # Individual metric scores
        'Communication': 8,
        'Technical': 7,
        'Projects': 6,
        'Problem Solving': 8,
        'Cultural Fit': 7,
        'Custom Metric': 6,                 # If any custom metrics added
        ...
    },
    'feedback': ''                          # Can be edited later
}
```

## Interaction Modes

### Interviewer Mode
- **Form State**: Fully enabled, all fields editable
- **Actions Available**: Save Candidate, Remove Block
- **Save Behavior**: Validates, saves, shows success, removes block
- **Buttons**: Primary (blue) for Save, Secondary (gray) for Remove

### Analyst Mode (Read-only)
- **Form State**: All fields disabled (grayed out)
- **Info Message**: "Read-only: Switch to Interviewer mode to edit"
- **Actions Available**: None (buttons hidden/disabled)
- **Use Case**: View previously entered candidates without modification

## Error States

| Condition | Error Message | User Action |
|-----------|---------------|------------|
| Name field empty | ❌ Candidate name is required | Fill in Full Name field |
| Position field empty | ❌ Applied position is required | Fill in Applied Position field |
| Save to JSON fails | ❌ Failed to save candidate | Check storage permissions, retry |
| Block remove fails | ❌ Candidate block removed | (auto-closes block) |

## Auto-save Drafts

Each form field includes `on_change=save_draft` callback that:
1. Fires when widget value changes (not on form submit)
2. Collects current block field values
3. Saves to `st.session_state['candidates_draft'][block_id]`
4. Does not interfere with form submission
5. Used for recovery in case of UI crash

Drafts stored in memory during session, can be persisted to `data/drafts/` via "Save draft to local" button.

## Form Disable Logic

```python
disabled=not is_interviewer

# If is_interviewer = True → disabled=False (form enabled)
# If is_interviewer = False → disabled=True (form disabled)
```

Applied to:
- All text inputs (id, name, email, position, phone)
- All number inputs (experience)
- All text areas (notes)
- All sliders (metric scores)
- Submit buttons (conditional rendering + disabled state)

## Button States

| Button | Is Interviewer | State | Function |
|--------|---|---|---|
| Save Candidate | Yes | Visible, enabled | Saves candidate record |
| Save Candidate | No | Hidden | -- |
| Remove Block | Yes | Visible, enabled | Removes block from UI |
| Remove Block | No | Hidden | -- |
| Save All Blocks | Yes | Visible, enabled | Batch saves all blocks |
| Save All Blocks | No | Shows info message | -- |
