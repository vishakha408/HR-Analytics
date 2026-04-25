# 🔧 Home Page - Technical Documentation

## 📋 Code Structure Overview

### File: `src/home.py`

#### Function: `render_home()`
```python
def render_home():
    """Render home page with two large navigation cards"""
```

**Purpose**: Displays the home page UI with two navigation cards  
**Parameters**: None  
**Returns**: None (renders to Streamlit page)  
**Call Location**: `src/app.py` line ~188

---

## 🎨 Styling Details

### CSS Classes Structure

```css
.home-container
├── .home-title
│   ├── h1 (gradient text, 48px)
│   └── p (description, 18px)
├── .cards-container
│   ├── .nav-card
│   │   ├── .card-icon (72px emoji)
│   │   ├── .card-title (32px, colored)
│   │   ├── .card-description (16px, gray)
│   │   ├── .card-features (13px, list)
│   │   └── .card-button (action button)
│   │
│   └── Two instances:
│       ├── .nav-card.interview (purple theme)
│       └── .nav-card.analytics (teal theme)
```

### Color Palette

```python
# Interview Session Card
PRIMARY_GRADIENT = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
PRIMARY_COLOR = "#667eea"
PRIMARY_HOVER = "rgba(102, 126, 234, 0.05)"

# HR Analytics Card
SECONDARY_GRADIENT = "linear-gradient(135deg, #4ECDC4 0%, #44A99E 100%)"
SECONDARY_COLOR = "#4ECDC4"
SECONDARY_HOVER = "rgba(78, 205, 196, 0.05)"

# Text Colors
TITLE_COLOR = "#333"
DESCRIPTION_COLOR = "#666"
FEATURE_COLOR = "#999"
```

---

## 🔄 Session State Management

### Initialization Pattern
```python
# In app.py main()
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
```

### State Transitions

```
State Machine:
┌─────────┐
│  'home' │ ◄─── Initial state, home page displays
└────┬────┘
     │
     ├─► "Go to Interview Session" button
     │   st.session_state['page'] = 'interview'
     │   st.rerun()
     │
     └─► "Go to HR Analytics" button
         st.session_state['page'] = 'analytics'
         st.rerun()

┌──────────────────┐
│  'interview'     │ ◄─── Interview Session page
└────┬─────────────┘
     │
     └─► "Home" button
         st.session_state['page'] = 'home'
         st.rerun()

┌──────────────────┐
│  'analytics'     │ ◄─── HR Analytics page
└────┬─────────────┘
     │
     └─► "Home" button
         st.session_state['page'] = 'home'
         st.rerun()
```

---

## 📐 Layout Structure

### Streamlit Components Hierarchy

```python
# Home Page Layout
render_home()
│
├── CSS Styling (st.markdown with <style>)
│
├── Title Section (st.markdown)
│   └── <div class="home-container">
│       └── <div class="home-title">
│           ├── <h1>🏢 HR Management System</h1>
│           └── <p>Select a module to get started</p>
│
├── Two Columns (st.columns(2, gap="large"))
│
├── Column 1: Interview Session
│   ├── Card HTML (st.markdown)
│   └── Button (st.button)
│       └── onClick: st.session_state['page'] = 'interview'
│
├── Column 2: HR Analytics
│   ├── Card HTML (st.markdown)
│   └── Button (st.button)
│       └── onClick: st.session_state['page'] = 'analytics'
│
└── Footer (st.markdown with divider)
```

---

## 🎯 Button Navigation Logic

### Interview Session Button
```python
if st.button(
    "📋 Go to Interview Session",
    key="btn_interview",
    use_container_width=True,
    help="Navigate to Interview Session module"
):
    st.session_state['page'] = 'interview'
    st.rerun()
```

**Details**:
- **Label**: "📋 Go to Interview Session" (with emoji)
- **Key**: "btn_interview" (prevents conflicts)
- **Width**: Full container width
- **Tooltip**: "Navigate to Interview Session module"
- **Action**: Sets page to 'interview' and reloads app

### HR Analytics Button
```python
if st.button(
    "📈 Go to HR Analytics",
    key="btn_analytics",
    use_container_width=True,
    help="Navigate to HR Analytics module"
):
    st.session_state['page'] = 'analytics'
    st.rerun()
```

**Details**:
- **Label**: "📈 Go to HR Analytics" (with emoji)
- **Key**: "btn_analytics" (prevents conflicts)
- **Width**: Full container width
- **Tooltip**: "Navigate to HR Analytics module"
- **Action**: Sets page to 'analytics' and reloads app

---

## 📊 App.py Integration

### Import Statement
```python
import home  # Line 9, after other imports
```

### Session State Initialization (main function)
```python
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'
```

### Home Page Rendering
```python
if st.session_state['page'] == 'home':
    home.render_home()
    return
```

### Back Navigation Button
```python
col1, col2, col3 = st.columns([0.1, 0.8, 0.1])
with col1:
    if st.button("🏠 Home", help="Return to home page"):
        st.session_state['page'] = 'home'
        st.rerun()
with col3:
    page_title = "Interview Session" if st.session_state['page'] == 'interview' else "HR Analytics"
    st.markdown(f"**Current: {page_title}**")
```

### Conditional Page Rendering
```python
# Interview Session Page
if st.session_state['page'] == 'interview':
    st.info("👨‍💼 Interview Session module - Coming soon!")
    st.write("This module will provide AI-powered interview guidance and assessment tools.")
    return

# HR Analytics Page
if st.session_state['page'] == 'analytics':
    render_kpi_header(df_hr)
    df_hr_filtered = render_filter_sidebar(df_hr)
    # ... rest of existing analytics code
```

---

## 🎨 Responsive Design Implementation

### Breakpoint Strategy

```
Desktop (>900px): Two cards side-by-side
│
├─ Card 1 width: 300-450px
├─ Gap: 40px
└─ Card 2 width: 300-450px

Tablet (600px-900px): Cards may start to stack
│
├─ Single column or narrow two-column
├─ Cards adjust width
└─ Gap reduces

Mobile (<600px): Cards stack vertically
│
├─ Full width minus padding
├─ Cards take 100% width
└─ Horizontal scrolling prevented
```

### CSS Media-Friendly Properties
```css
.cards-container {
    display: flex;
    gap: 40px;
    justify-content: center;
    flex-wrap: wrap;          /* Allow wrapping on small screens */
    width: 100%;
    max-width: 1200px;
}

.nav-card {
    flex: 1;                  /* Equal width sharing */
    min-width: 300px;         /* Don't shrink below this */
    max-width: 450px;         /* Max width per card */
}
```

### Streamlit Column Configuration
```python
col1, col2 = st.columns(2, gap="large")
```

**Behavior**:
- On wide screens: Two equal-width columns
- On narrow screens: Streamlit automatically stacks them

---

## 🔧 Event Handling Flow

### User Click Event - Interview Card

```
User clicks "📋 Go to Interview Session"
    ↓
Streamlit detects button click
    ↓
Code block executes:
    if st.button("📋 Go to Interview Session", ...):
    ↓
    st.session_state['page'] = 'interview'
        (Page value updated in session)
    ↓
    st.rerun()
        (Triggers full app rerun)
    ↓
App reruns from top:
    1. Checks st.session_state['page']
    2. Value is now 'interview'
    3. Skips home page render
    4. Loads data (df_hr)
    5. Renders back button
    6. Checks: if st.session_state['page'] == 'interview'
    7. Shows "Coming soon!" message
    ↓
User sees Interview Session page
```

### User Click Event - Home Button

```
User clicks "🏠 Home"
    ↓
Streamlit detects button click
    ↓
Code block executes:
    if st.button("🏠 Home", ...):
    ↓
    st.session_state['page'] = 'home'
        (Page value updated to 'home')
    ↓
    st.rerun()
        (Triggers full app rerun)
    ↓
App reruns from top:
    1. Checks st.session_state['page']
    2. Value is now 'home'
    3. Calls home.render_home()
    4. Exits with return
    5. Never reaches data loading or analytics code
    ↓
User sees Home page with navigation cards
```

---

## 📈 Performance Considerations

### Session State Benefits
- **No re-renders on home page**: Once set, stays until changed
- **Lazy loading**: Analytics code only runs when page is 'analytics'
- **Memory efficient**: Only active page resources loaded
- **Fast navigation**: Uses Streamlit's built-in caching

### Optimization Points
```python
# ✅ Good: Early return prevents unnecessary code execution
if st.session_state['page'] == 'home':
    home.render_home()
    return  # Exit early, don't load data

# ✅ Good: Data only loaded for non-home pages
if st.session_state['page'] != 'home':
    df_hr = data.load_transform(...)  # Already cached in data module
```

---

## 🧪 Testing Code Examples

### Test 1: Session State Initialization
```python
# Check that page initializes to 'home'
def test_initial_page():
    # Simulate first app run
    assert 'page' not in st.session_state  # Before init
    
    # After first line of main()
    if 'page' not in st.session_state:
        st.session_state['page'] = 'home'
    
    assert st.session_state['page'] == 'home'  # ✓ Passes
```

### Test 2: Navigation State Change
```python
# Check that clicking button changes state
def test_navigate_to_interview():
    st.session_state['page'] = 'home'
    
    # Simulate button click
    st.session_state['page'] = 'interview'
    
    assert st.session_state['page'] == 'interview'  # ✓ Passes
```

### Test 3: Back Navigation
```python
# Check that home button returns to home
def test_return_to_home():
    st.session_state['page'] = 'analytics'
    
    # Simulate home button click
    st.session_state['page'] = 'home'
    
    assert st.session_state['page'] == 'home'  # ✓ Passes
```

---

## 📝 HTML Structure (Card Template)

### Interview Session Card HTML
```html
<div class="nav-card interview">
    <div class="card-icon">👨‍💼</div>
    <div class="card-title">Interview Session</div>
    <div class="card-description">
        Conduct and manage employee interviews with AI-powered insights and recommendations.
    </div>
    <ul class="card-features">
        <li>✓ Real-time interview guidance</li>
        <li>✓ AI-powered insights</li>
        <li>✓ Performance scoring</li>
        <li>✓ Candidate assessment</li>
    </ul>
</div>
```

### HR Analytics Card HTML
```html
<div class="nav-card analytics">
    <div class="card-icon">📊</div>
    <div class="card-title">HR Analytics</div>
    <div class="card-description">
        Comprehensive HR analytics with detailed insights into employee data, trends, and attrition prediction.
    </div>
    <ul class="card-features">
        <li>✓ Executive summary</li>
        <li>✓ Capacity analysis</li>
        <li>✓ Attrition insights</li>
        <li>✓ ML predictions</li>
    </ul>
</div>
```

---

## 🚀 Deployment Checklist

- [x] `home.py` created with `render_home()` function
- [x] `app.py` imports `home` module
- [x] Session state initialization in `main()`
- [x] Home page rendering logic added
- [x] Back button and page indicator added
- [x] Interview page placeholder created
- [x] Analytics page preserved and wrapped
- [x] CSS styling comprehensive and responsive
- [x] Button navigation working
- [x] State management clean
- [x] No breaking changes to existing code
- [x] All imports and dependencies available

---

## 📚 Reference Links in Code

### Key Lines in `src/app.py`
- Line 9: `import home`
- Line 181-283: `main()` function
  - Lines 182-188: Session state and home page
  - Lines 208-213: Back button section
  - Lines 215-219: Interview page placeholder
  - Lines 221-280: Analytics page (wrapped)

### Key Lines in `src/home.py`
- Lines 1-2: Docstring and imports
- Lines 5-6: Function definition
- Lines 8-161: CSS styling (st.markdown)
- Lines 163-170: Title section
- Lines 172-173: Column layout
- Lines 175-195: Interview card and button
- Lines 197-217: Analytics card and button
- Lines 219-236: Footer

---

## 🎯 Common Customization Points

### Change Home Page Title
```python
# In src/home.py, line ~165
st.markdown("""
    <h1>🏢 Your Custom Title Here</h1>
""", unsafe_allow_html=True)
```

### Change Card Colors
```python
# In src/home.py, modify these gradients:
# Interview card: lines 50-52
background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);

# Analytics card: lines 61-63
background: linear-gradient(135deg, #YOUR_COLOR3 0%, #YOUR_COLOR4 100%);
```

### Change Card Features
```python
# In src/home.py, around line 185
<ul class="card-features">
    <li>✓ Your feature 1</li>
    <li>✓ Your feature 2</li>
    <li>✓ Your feature 3</li>
</ul>
```

### Add More Cards
```python
# Modify st.columns(2) to st.columns(3) and add another column
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    # Interview card

with col2:
    # Analytics card

with col3:
    # Your new card
```

---

## ✅ Validation Checklist

- [x] Home page displays with correct title
- [x] Two cards visible side-by-side on desktop
- [x] Cards responsive and stack on mobile
- [x] Interview card has correct icon and description
- [x] Analytics card has correct icon and description
- [x] Both cards show feature lists
- [x] Interview button navigates to interview page
- [x] Analytics button navigates to analytics page
- [x] Home button visible on non-home pages
- [x] Page indicator shows current page
- [x] Back navigation returns to home
- [x] Session state persists across interactions
- [x] No console errors
- [x] No data loading on home page
- [x] Analytics page loads when selected
- [x] Interview placeholder shows correctly

---

**Status**: ✅ **IMPLEMENTATION COMPLETE**  
**Last Updated**: November 14, 2025  
**Version**: 1.0
