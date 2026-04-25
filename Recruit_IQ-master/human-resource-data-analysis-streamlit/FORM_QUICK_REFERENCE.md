# Candidate Form Quick Reference

## 🚀 Quick Start

### Form Triggers
- **Create Block**: Click "➕ Add Candidate Block" button
- **Edit Block**: Form appears in expander (expanded if most recently added)
- **Save**: Fill required fields (Name, Position), adjust scores, click "💾 Save Candidate"
- **Remove**: Click "🗑️ Remove Block" to delete without saving

### Required Fields
- ✅ Full Name (cannot save without this)
- ✅ Applied Position (cannot save without this)

### Optional Fields
- Email, Phone, Notes, Experience, Candidate ID

### Scoring
- 5 metrics: Communication, Technical, Projects, Problem Solving, Cultural Fit
- Range: 0-10
- Default: 5
- Can add custom metrics before entering candidates

## 📍 Key Session State Keys

```python
# Form fields (per block)
f"{block_id}_id"                          # Candidate ID
f"{block_id}_name"                        # Full Name
f"{block_id}_email"                       # Email
f"{block_id}_position"                    # Applied Position
f"{block_id}_phone"                       # Phone
f"{block_id}_exp"                         # Experience years
f"{block_id}_notes"                       # Notes

# Scores (per block)
f"{block_id}_metric_Communication"        # Communication score
f"{block_id}_metric_Technical"            # Technical score
f"{block_id}_metric_Projects"             # Projects score
f"{block_id}_metric_Problem_Solving"      # Problem Solving score
f"{block_id}_metric_Cultural_Fit"         # Cultural Fit score

# Block management
st.session_state['candidate_blocks']      # List of active block IDs
st.session_state['candidates_draft']      # Auto-saved drafts

# Session data
st.session_state['session_candidates']    # List of saved candidates
st.session_state['current_session']       # Current session dict
st.session_state['role']                  # 'Interviewer' or 'Analyst'
```

## 🔄 Data Flow

```
User fills form
    ↓ (each field change)
on_change=save_draft callback fires
    ↓
Saves to st.session_state['candidates_draft']
    ↓ (user clicks Save Candidate)
Form submit handler fires
    ↓
Validate (name + position)
    ↓
Collect all values from session_state
    ↓
Build candidate_record dict
    ↓
Append to st.session_state['session_candidates']
    ↓
save_session_data() → JSON file
    ↓
st.success() message
    ↓
Remove block from UI
    ↓
st.rerun() refresh
```

## 🎛️ Form Configuration

```python
# Form container
with st.form(key=f"candidate_block_form_{safe_block}"):
    
    # --- Column 1: Basic Info ---
    st.text_input("Candidate ID / Roll")      # key: f"{block}_id"
    st.text_input("Full Name")                # key: f"{block}_name"  (required)
    st.text_input("Email")                    # key: f"{block}_email"
    
    # --- Column 2: More Info ---
    st.text_input("Applied Position")         # key: f"{block}_position"  (required)
    st.text_input("Phone (Optional)")         # key: f"{block}_phone"
    st.number_input("Experience (years)")     # key: f"{block}_exp"
    
    # --- Notes ---
    st.text_area("Candidate Notes")           # key: f"{block}_notes"
    
    # --- Scoring (3 columns) ---
    st.slider("Communication", 0, 10, 5)      # key: f"{block}_metric_Communication"
    st.slider("Technical Skills", 0, 10, 5)   # key: f"{block}_metric_Technical"
    st.slider("Projects", 0, 10, 5)           # key: f"{block}_metric_Projects"
    st.slider("Problem Solving", 0, 10, 5)    # key: f"{block}_metric_Problem_Solving"
    st.slider("Cultural Fit", 0, 10, 5)       # key: f"{block}_metric_Cultural_Fit"
    
    # --- Actions ---
    st.form_submit_button("💾 Save Candidate")
    st.form_submit_button("🗑️ Remove Block")
```

## 🧪 Testing Checklist

### Basic Form Display
- [ ] Form renders with all fields visible
- [ ] Scoring section shows 5 sliders
- [ ] Buttons visible and clickable
- [ ] Fields have placeholder text

### Field Interaction
- [ ] Text fields accept input
- [ ] Sliders move 0-10 range
- [ ] Notes textarea expands vertically
- [ ] Experience input accepts decimals

### Validation
- [ ] Saving without Name shows error
- [ ] Saving without Position shows error
- [ ] Saving with both required fields succeeds
- [ ] Optional fields can be empty

### Save & Persist
- [ ] Success message appears after save
- [ ] Block disappears from UI after save
- [ ] Candidate appears in candidates_draft
- [ ] Data saves to JSON file
- [ ] On page reload, data persists

### Role-Based Access
- [ ] In Interviewer mode: form enabled, buttons visible
- [ ] Switch to Analyst mode: form disabled, buttons hidden
- [ ] "Read-only" message appears in Analyst mode
- [ ] Switch back to Interviewer: form enabled again

### Auto-Save Drafts
- [ ] Fill a field → value in candidates_draft
- [ ] Adjust slider → draft updates
- [ ] Clear field → draft updates
- [ ] Drafts saved even without clicking Save

### Remove Block
- [ ] Click Remove Block button
- [ ] Block disappears from UI
- [ ] Session state keys cleaned up
- [ ] Success message shows

### Save All
- [ ] Create multiple blocks
- [ ] Fill some blocks with valid data
- [ ] Click "Save All Candidate Blocks"
- [ ] Shows count of successfully saved
- [ ] All blocks with complete data saved
- [ ] Blocks with incomplete data skipped

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Fields not saving | on_change callbacks not firing | Check form context is active |
| "Required field" error keeps showing | Validation check failing | Ensure name AND position filled |
| Block doesn't remove after save | st.rerun() not called | Verify rerun() at end of save logic |
| Scores not in candidate record | Custom metric not included | Check metrics_list includes custom metrics |
| Form appears disabled | role != 'Interviewer' | Switch to Interviewer mode in sidebar |
| Data lost after refresh | save_session_data() failed | Check file write permissions |
| Draft not auto-saving | on_change callback disabled | Verify disabled=not is_interviewer not breaking save |

## 💡 Tips & Tricks

1. **Bulk Edit**: Use "Save All" to quickly save multiple candidates at once
2. **Draft Recovery**: Use "Save draft to local" to backup work-in-progress
3. **Quick Reset**: Remove block and add new one to start fresh
4. **Metric Weights**: Custom metrics auto-included in average score calculation
5. **Batch Operations**: Can create/edit multiple blocks before saving any

## 📊 Saved Candidate Record

```python
{
    'id': 'EMP123',                    # Candidate ID (auto-gen if blank)
    'roll': 'EMP123',                  # Roll number (same as ID)
    'name': 'John Doe',                # Required
    'email': 'john@example.com',       # Optional
    'position': 'Senior Engineer',     # Required
    'experience_years': 5.5,           # Optional (default 0.0)
    'phone': '+1-555-0123',            # Optional
    'notes': 'Great background...',    # Optional
    'added_at': '2024-01-15T10:30:45', # ISO timestamp
    'score': 7.4,                      # Average of all metrics
    'scores': {                        # Individual scores
        'Communication': 8,
        'Technical': 7,
        'Projects': 6,
        'Problem Solving': 8,
        'Cultural Fit': 8,
        'Custom Metric': 7             # If added
    },
    'feedback': ''                     # For interviewer notes
}
```

## 🔗 Related Functions

- `save_draft(block_id)` - Auto-save draft callback (lines 74-102)
- `save_session_data(session_data)` - Persist to JSON (lines 37-47)
- `render_active_session()` - Main form container (lines 540+)
- `interview_scoring.compute_weighted_score()` - Score calculation

## 📚 Files Involved

- **Main**: `src/tab_interview.py` (lines 540-835)
- **Storage**: `src/interview_storage.py` (save_session function)
- **Scoring**: `src/interview_scoring.py` (optional)
- **Data**: `interview_sessions/{session_name}.json`
- **Drafts**: `data/drafts/{session_name}_draft.json`

---

**Last Updated**: 2024
**Status**: Production Ready ✅
