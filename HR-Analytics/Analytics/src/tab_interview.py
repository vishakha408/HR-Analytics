import numpy as np

# Helper: Build base DataFrame from session candidates (do not mutate session_state)
def build_base_df_from_session():
    candidates = st.session_state.setdefault("candidates", [])
    rows = []
    for c in candidates:
        rows.append({
            "id": c.get("id", ""),
            "name": c.get("name", ""),
            "experience_years": float(c.get("experience_years", 0)),
            "metric_communication": float((c.get("scores") or {}).get("Communication", 0)),
            "metric_technical": float((c.get("scores") or {}).get("Technical Skills", 0)),
            "metric_projects": float((c.get("scores") or {}).get("Projects", 0)),
            "metric_problemSolving": float((c.get("scores") or {}).get("Problem Solving", 0)),
            "metric_cultureFit": float((c.get("scores") or {}).get("Cultural Fit", 0)),
            "notes": c.get("notes", "")
        })
    return pd.DataFrame(rows)

# Helper: Return a new DataFrame with min-max normalized metric columns (do not mutate input)
def compute_normalized_metrics(df):
    df_norm = df.copy()
    metric_cols = [c for c in df_norm.columns if c.startswith("metric_")]
    for col in metric_cols:
        min_v, max_v = df_norm[col].min(), df_norm[col].max()
        if min_v == max_v:
            df_norm[col] = 0.0
        else:
            df_norm[col] = (df_norm[col] - min_v) / (max_v - min_v)
    df_norm["weighted_score"] = df_norm[metric_cols].mean(axis=1)
    return df_norm

# Helper: Get top n rows by column, clamped, sorted descending (do not mutate input)
def get_top_n(df, n, by):
    if df.empty:
        return df.copy()
    n = max(1, min(int(n), len(df)))
    return df.sort_values(by, ascending=False).head(n).reset_index(drop=True)
"""Interview Session module - manage interview sessions and candidates"""

# Note: After saving changes to this file, restart Streamlit to apply CSS and form
# updates: Ctrl+C then run `python -m streamlit run src/app.py` from the project root.

import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os
from pathlib import Path
import uuid
import io
from io import BytesIO
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

import interview_storage
import interview_scoring


# Interview session storage path
INTERVIEW_SESSIONS_DIR = Path("interview_sessions")
INTERVIEW_SESSIONS_DIR.mkdir(exist_ok=True)


def load_session_data(session_name: str) -> dict:
    """Load interview session data from storage"""
    session_file = INTERVIEW_SESSIONS_DIR / f"{session_name}.json"
    
    if session_file.exists():
        with open(session_file, 'r') as f:
            return json.load(f)
    
    return None


def save_session_data(session_data: dict) -> bool:
    """Save interview session data to both JSON and SQLite database.
    
    Persists session metadata and all candidates to the database using interview_storage,
    and also saves a JSON backup to the interview_sessions folder.
    """
    try:
        session_name = session_data.get('name', 'untitled')
        session_file = INTERVIEW_SESSIONS_DIR / f"{session_name}.json"
        
        # Save JSON backup
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Persist to database
        session_meta = {
            'name': session_data.get('name'),
            'date': session_data.get('date'),
            'interviewer': session_data.get('interviewer'),
            'notes': session_data.get('notes'),
            'custom_metrics': session_data.get('custom_metrics', []),
        }
        candidates = session_data.get('candidates', [])
        
        # Store session_id in session_data for future updates
        session_id = interview_storage.save_session(session_meta, candidates)
        session_data['id'] = session_id
        
        return True
    except Exception as e:
        st.error(f"Error saving session: {str(e)}")
        return False


def get_available_sessions() -> list:
    """Get list of available interview sessions"""
    if not INTERVIEW_SESSIONS_DIR.exists():
        return []
    
    sessions = []
    for file in INTERVIEW_SESSIONS_DIR.glob("*.json"):
        sessions.append(file.stem)
    
    sorted_sessions = sorted(sessions)
    # ensure drafts folder exists when listing sessions (no-op if present)
    Path("data/drafts").mkdir(parents=True, exist_ok=True)
    return sorted_sessions


def _ensure_draft_state():
    """Ensure session_state keys for draft persistence exist."""
    if 'candidates_draft' not in st.session_state:
        st.session_state['candidates_draft'] = []  # Now a list, not a dict
    if 'current_session_id' not in st.session_state:
        st.session_state['current_session_id'] = None



def inject_global_css():
    """Inject CSS styles for the interview session page with error handling.
    
    Runs only once per session using st.session_state flag to avoid redundant injections.
    
    Includes:
    - Google Font (Inter) for consistent typography
    - Floating card styles for forms and expanders
    - Two-column responsive layout for candidate entry
    - Sticky right-side action panel styling
    - Block container padding to avoid overlap
    - Safety rule to hide any accidentally rendered CSS text
    
    Wrapped in try/except to fail gracefully.
    """
    # Check if CSS has already been injected this session
    if st.session_state.get('_css_injected', False):
        return
    
    try:
        css_code = """
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
        <style>
        /* Global font */
        html, body, .main, .block-container {
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial;
        }

        /* Floating candidate cards / expanders */
        div[data-testid="stExpander"] > div:first-child {
            background: #ffffff !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 30px rgba(36, 37, 38, 0.08) !important;
            padding: 12px 14px !important;
            margin-bottom: 12px !important;
        }

        /* Make form containers look like cards */
        div[data-testid="stForm"] {
            background: #fff !important;
            padding: 14px !important;
            border-radius: 10px !important;
            box-shadow: 0 8px 22px rgba(36,37,38,0.06) !important;
            margin-bottom: 16px !important;
        }

        /* Two-column responsive layout for candidate forms */
        @media (min-width: 900px) {
            .candidate-two-col .stColumn:nth-child(1) { width: 60%; }
            .candidate-two-col .stColumn:nth-child(2) { width: 40%; }
        }

        /* Sticky right-side action panel (visual) */
        #interview-action-panel {
            position: fixed;
            right: 18px;
            top: 120px;
            width: 260px;
            background: #ffffff;
            border-radius: 10px;
            box-shadow: 0 12px 30px rgba(36,37,38,0.12);
            padding: 12px 14px;
            z-index: 9999;
        }

        #interview-action-panel h4 { margin: 6px 0 8px 0; }

        /* Tidy up buttons inside panel when present */
        #interview-action-panel .stButton button {
            width: 100%;
            border-radius: 8px;
        }

        /* Slight padding for the page content to avoid overlap */
        .block-container { padding-right: 320px; }

        /* Safety rule: hide any accidentally rendered CSS or code blocks */
        pre, code { display: none !important; }
        </style>
        """
        st.markdown(css_code, unsafe_allow_html=True)
        # Mark CSS as injected for this session
        st.session_state['_css_injected'] = True
        # One-time safety call to hide any previously printed CSS text blocks
        safety_css = """
        <style> pre, code { display: none !important; } </style>
        """
        st.markdown(safety_css, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"⚠️ Failed to load interview page styles: {str(e)}")


def render_interview_page():
    """Render the interview session page"""
    
    # Inject global CSS styles at the start
    inject_global_css()
    
    st.title("👨‍💼 Interview Session")
    st.divider()
    # Sidebar role chooser: Interviewer vs Analyst
    if 'role' not in st.session_state:
        st.session_state['role'] = 'Analyst'

    with st.sidebar:
        st.markdown("**Role / Mode**")
        role = st.selectbox(
            "Select role",
            options=["Analyst", "Interviewer"],
            index=0 if st.session_state.get('role') != 'Interviewer' else 1,
            key='sidebar_role_select'
        )
        # Use a single `role` session state value to represent mode
        st.session_state['role'] = role
    
    # Initialize session state for interview module
    if 'interview_mode' not in st.session_state:
        st.session_state['interview_mode'] = None
    
    if 'current_session' not in st.session_state:
        st.session_state['current_session'] = None
    
    if 'session_candidates' not in st.session_state:
        st.session_state['session_candidates'] = []
    
    # Show mode selection if no session is active
    if st.session_state['current_session'] is None:
        render_session_creation_form()
    else:
        # Show active session
        render_active_session()


def render_session_creation_form():
    """Render form to create or load interview session"""
    
    st.subheader("📋 Interview Session Setup")
    
    # Two columns for Create vs Load
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("### ➕ Create New Session")
        
        with st.form("create_session_form", border=True):
            session_name = st.text_input(
                "Session Name",
                placeholder="e.g., Q4 2025 - Engineering Candidates",
                help="Unique name for this interview session"
            )
            
            interview_date = st.date_input(
                "Interview Date",
                value=datetime.now().date(),
                help="Date of the interview session"
            )
            
            interviewer_name = st.text_input(
                "Interviewer Name",
                placeholder="e.g., John Smith",
                help="Name of the primary interviewer"
            )
            
            notes = st.text_area(
                "Session Notes (Optional)",
                placeholder="Add any notes about this session...",
                height=100,
                help="Additional context or notes about the session"
            )
            
            create_btn = st.form_submit_button(
                "✅ Create Session",
                use_container_width=True,
                type="primary"
            )
            
            if create_btn:
                if not session_name.strip():
                    st.error("❌ Please enter a session name")
                else:
                    # Check if session already exists
                    if session_name in get_available_sessions():
                        st.error(f"❌ Session '{session_name}' already exists. Choose a different name.")
                    else:
                        # Create new session
                        session_data = {
                            'name': session_name,
                            'date': interview_date.isoformat(),
                            'interviewer': interviewer_name,
                            'notes': notes,
                            'created_at': datetime.now().isoformat(),
                            'candidates': []
                        }
                        
                        if save_session_data(session_data):
                            st.session_state['current_session'] = session_data
                            st.session_state['session_candidates'] = []
                            # custom metrics for scoring (strings)
                            st.session_state['custom_metrics'] = []
                            st.success(f"✅ Session '{session_name}' created successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to create session")
    
    with col2:
        st.markdown("### 📂 Load Existing Session")
        
        available_sessions = get_available_sessions()
        
        if available_sessions:
            with st.form("load_session_form", border=True):
                selected_session = st.selectbox(
                    "Select Session",
                    options=available_sessions,
                    help="Choose an existing interview session to load"
                )
                
                load_btn = st.form_submit_button(
                    "📖 Load Session",
                    use_container_width=True,
                    type="primary"
                )
                
                if load_btn:
                    session_data = load_session_data(selected_session)
                    
                    if session_data:
                        st.session_state['current_session'] = session_data
                        st.session_state['session_candidates'] = session_data.get('candidates', [])
                        # restore saved custom metrics if present
                        st.session_state['custom_metrics'] = session_data.get('custom_metrics', []) or []
                        st.success(f"✅ Session '{selected_session}' loaded successfully!")
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to load session '{selected_session}'")
        else:
            st.info("📭 No existing sessions found. Create a new one to get started!")


def render_active_session():
    """Render the active interview session with candidate management"""
    
    session = st.session_state['current_session']
    # ensure draft persistence keys
    _ensure_draft_state()
    if st.session_state.get('current_session_id') is None:
        # if session has an id (from DB) set it; otherwise leave as None
        try:
            st.session_state['current_session_id'] = session.get('id') if isinstance(session, dict) else None
        except Exception:
            st.session_state['current_session_id'] = None
    
    # Session header
    col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
    
    with col1:
        st.markdown(f"### 📍 Active Session: **{session['name']}**")
        
        # Session details
        session_col1, session_col2, session_col3 = st.columns(3)
        
        with session_col1:
            st.markdown(f"**Date:** {session['date']}")
        
        with session_col2:
            st.markdown(f"**Interviewer:** {session['interviewer']}")
        
        with session_col3:
            candidates_count = len(st.session_state['session_candidates'])
            st.markdown(f"**Candidates:** {candidates_count}")
        
        if session.get('notes'):
            st.markdown(f"**Notes:** {session['notes']}")
    
    with col3:
        if st.button("🏠 Back to Session Menu", use_container_width=True):
            st.session_state['current_session'] = None
            st.session_state['session_candidates'] = []
            st.rerun()
    
    st.divider()
    
    # Determine whether current user can edit (role-based)
    is_interviewer = st.session_state.get('role') == 'Interviewer'

    st.subheader("➕ Add Candidate")
    if not is_interviewer:
        st.info("ℹ️ Read-only mode: Switch to Interviewer role in sidebar to add/edit candidates")

    with st.form(key="candidate_form"):
        col1, col2 = st.columns(2)

        with col1:
            candidate_id = st.text_input("Candidate ID / Roll", placeholder="e.g., EMP123", help="Optional candidate identifier", disabled=not is_interviewer)
            candidate_name = st.text_input("Candidate Name", placeholder="e.g., Alice Johnson", help="Full name of the candidate", disabled=not is_interviewer)
            candidate_email = st.text_input("Email", placeholder="e.g., alice@example.com", help="Email address of the candidate", disabled=not is_interviewer)

        with col2:
            candidate_position = st.text_input("Position Applying For", placeholder="e.g., Senior Engineer", help="Job position the candidate is interviewing for", disabled=not is_interviewer)
            candidate_phone = st.text_input("Phone (Optional)", placeholder="e.g., +1-555-0123", help="Contact phone number", disabled=not is_interviewer)
            candidate_exp = st.number_input("Experience (years)", min_value=0.0, step=0.5, value=0.0, disabled=not is_interviewer)

        candidate_notes = st.text_area("Candidate Notes (Optional)", placeholder="Initial impressions, background info, etc.", height=80, help="Any notes about the candidate", disabled=not is_interviewer)

        # Scoring sliders (include custom metrics)
        st.markdown("**Scoring (0-10 scale)**")
        score_col1, score_col2, score_col3 = st.columns(3)

        fixed_metrics = [
            "Communication",
            "Technical Skills",
            "Projects",
            "Problem Solving",
            "Cultural Fit",
        ]
        metrics_list = fixed_metrics + list(st.session_state.get('custom_metrics', []))

        scores = {}
        with score_col1:
            scores['Communication'] = st.slider("Communication", 0, 10, 5, key="candidate_metric_Communication", disabled=not is_interviewer)
            scores['Technical Skills'] = st.slider("Technical Skills", 0, 10, 5, key="candidate_metric_Technical_Skills", disabled=not is_interviewer)
        with score_col2:
            scores['Projects'] = st.slider("Projects", 0, 10, 5, key="candidate_metric_Projects", disabled=not is_interviewer)
            scores['Problem Solving'] = st.slider("Problem Solving", 0, 10, 5, key="candidate_metric_Problem_Solving", disabled=not is_interviewer)
        with score_col3:
            scores['Cultural Fit'] = st.slider("Cultural Fit", 0, 10, 5, key="candidate_metric_Cultural_Fit", disabled=not is_interviewer)

        # custom metrics
        for cm in st.session_state.get('custom_metrics', []):
            key_cm = f"candidate_metric_{cm.replace(' ', '_')}"
            scores[cm] = st.slider(cm, 0, 10, 5, key=key_cm, disabled=not is_interviewer)

        # Submit button (always present, but form only processes if interviewer)
        submitted = st.form_submit_button("Save Candidate", disabled=not is_interviewer)

    # Handle submission (only Interviewers can submit)
    if submitted and is_interviewer:
        # Basic validation
        if not candidate_name or not candidate_name.strip():
            st.error("❌ Candidate name is required")
        elif not candidate_position or not candidate_position.strip():
            st.error("❌ Applied position is required")
        else:
            # Generate unique id if not provided
            cid = candidate_id.strip() if candidate_id and candidate_id.strip() else str(uuid.uuid4())

            # Build candidate dict with scores
            candidate_record = {
                'id': cid,
                'name': candidate_name.strip(),
                'position': candidate_position.strip(),
                'experience_years': candidate_exp,
                'email': candidate_email.strip() if candidate_email else "",
                'phone': candidate_phone.strip() if candidate_phone else "",
                'notes': candidate_notes.strip() if candidate_notes else "",
                'scores': scores,
            }

            # Get candidates list, do not mutate session_state["candidates"] during iteration
            candidates = st.session_state.setdefault("candidates", [])

            # Find index if editing (by id)
            found_idx = None
            for i, c in enumerate(candidates):
                if c.get('id') == cid:
                    found_idx = i
                    break

            # Update or append: only modify/add one item
            if found_idx is not None:
                candidates[found_idx] = candidate_record
            else:
                candidates.append(candidate_record)

            st.success("Candidate saved")

    # (Dynamic candidate blocks removed) Use the single Add Candidate form above for entries.
    # Save draft to local
    if st.button("💾 Save draft to local", use_container_width=False):
        try:
            drafts_dir = Path("data/drafts")
            drafts_dir.mkdir(parents=True, exist_ok=True)
            session_name_safe = st.session_state['current_session'].get('name', 'untitled').replace(' ', '_')
            out_file = drafts_dir / f"{session_name_safe}_draft.json"
            to_write = {
                'session': st.session_state.get('current_session') or {},
                'drafts': st.session_state.get('candidates_draft', []),  # Now a list
            }
            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(to_write, f, indent=2)
            st.success(f"✅ Draft saved to {out_file}")
        except Exception as e:
            st.error(f"Failed to save draft: {e}")

    st.divider()

    # Display candidates
    render_candidates_list()

    # Session actions
    st.divider()
    render_session_actions()

    # Rankings section
    st.divider()
    render_rankings_section()

    # Candidate comparison section
    st.divider()
    render_candidate_comparison()


def render_candidates_list():
    """Render list of candidates in current session"""
    
    candidates = st.session_state['session_candidates']
    
    if not candidates:
        st.info("📭 No candidates added to this session yet. Add your first candidate above!")
        return
    
    st.subheader(f"👥 Candidates ({len(candidates)})")
    
    # Create candidate cards
    for idx, candidate in enumerate(candidates):
        with st.expander(
            f"👤 {candidate['name']} - {candidate['position']}",
            expanded=False
        ):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Basic Info**")
                st.markdown(f"- **Name:** {candidate['name']}")
                st.markdown(f"- **Position:** {candidate['position']}")
                st.markdown(f"- **Email:** {candidate['email']}")
                if candidate['phone']:
                    st.markdown(f"- **Phone:** {candidate['phone']}")
                st.markdown(f"- **Added:** {candidate['added_at']}")
            
            with col2:
                st.markdown("**Interview Info**")
                
                # Score input
                score = st.slider(
                    f"Interview Score (0-10)",
                    min_value=0,
                    max_value=10,
                    value=int(candidate.get('score') or 5),
                    step=1,
                    key=f"score_{idx}"
                )
                
                # Feedback input
                feedback = st.text_area(
                    "Interview Feedback",
                    value=candidate.get('feedback', ''),
                    height=80,
                    key=f"feedback_{idx}"
                )
                
                # Save feedback button
                if st.button("💾 Save Feedback", key=f"save_feedback_{idx}", use_container_width=True):
                    st.session_state['session_candidates'][idx]['score'] = score
                    st.session_state['session_candidates'][idx]['feedback'] = feedback
                    st.session_state['current_session']['candidates'] = st.session_state['session_candidates']
                    
                    if save_session_data(st.session_state['current_session']):
                        st.success(f"✅ Feedback saved for {candidate['name']}")
                        st.rerun()

                # If detailed per-metric scores exist, show them
                if candidate.get('scores'):
                    st.markdown("**Detailed Scores**")
                    for m_name, m_val in candidate.get('scores', {}).items():
                        st.markdown(f"- **{m_name}:** {m_val}")
            
            # Notes section
            if candidate.get('notes'):
                st.markdown("**Candidate Notes**")
                st.info(candidate['notes'])
            
            # Delete button
            if st.button("🗑️ Remove Candidate", key=f"delete_{idx}", use_container_width=False):
                st.session_state['session_candidates'].pop(idx)
                st.session_state['current_session']['candidates'] = st.session_state['session_candidates']
                
                if save_session_data(st.session_state['current_session']):
                    st.success(f"✅ Candidate removed")
                    st.rerun()


def render_session_actions():
    """Render session action buttons"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("💾 Save to DB", use_container_width=True):
            try:
                session = st.session_state['current_session']
                candidates = st.session_state['session_candidates']
                
                # Prepare session metadata
                session_meta = {
                    'name': session.get('name'),
                    'date': session.get('date'),
                    'interviewer': session.get('interviewer'),
                    'notes': session.get('notes'),
                    'custom_metrics': session.get('custom_metrics', []),
                }
                
                # Save to database
                session_id = interview_storage.save_session(session_meta, candidates)
                st.session_state['current_session']['id'] = session_id
                
                st.success("✅ Session saved to database")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Failed to save session: {str(e)}")
    
    with col2:
        if st.button("📊 Session Summary", use_container_width=True):
            render_session_summary()
    
    with col3:
        if st.button("📥 Export Session", use_container_width=True):
            render_export_session()
    
    with col4:
        if st.button("🗑️ Delete Session", use_container_width=True):
            render_delete_session()
    
    with col5:
        if st.button("➕ New Session", use_container_width=True):
            st.session_state['current_session'] = None
            st.session_state['session_candidates'] = []
            st.rerun()


def render_session_summary():
    """Render session summary statistics"""
    
    session = st.session_state['current_session']
    candidates = st.session_state['session_candidates']
    
    st.subheader("📊 Session Summary")
    
    # Calculate statistics
    total_candidates = len(candidates)
    interviewed = sum(1 for c in candidates if c.get('score') is not None)
    avg_score = sum(c['score'] for c in candidates if c.get('score') is not None) / interviewed if interviewed > 0 else 0
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Candidates", total_candidates)
    
    with col2:
        st.metric("Interviewed", interviewed)
    
    with col3:
        st.metric("Pending", total_candidates - interviewed)
    
    with col4:
        st.metric("Avg Score", f"{avg_score:.1f}/10")
    
    # Score distribution
    if candidates:
        scores = [c['score'] for c in candidates if c.get('score') is not None]
        
        if scores:
            st.subheader("Score Distribution")
            
            score_distribution = {
                '9-10': sum(1 for s in scores if s >= 9),
                '7-8': sum(1 for s in scores if 7 <= s < 9),
                '5-6': sum(1 for s in scores if 5 <= s < 7),
                '3-4': sum(1 for s in scores if 3 <= s < 5),
                '0-2': sum(1 for s in scores if s < 3),
            }
            
            df_distribution = pd.DataFrame({
                'Score Range': list(score_distribution.keys()),
                'Count': list(score_distribution.values())
            })
            
            st.bar_chart(df_distribution.set_index('Score Range'))


def render_export_session():
    """Render export session functionality"""
    
    session = st.session_state['current_session']
    candidates = st.session_state['session_candidates']
    
    st.subheader("📥 Export Session")
    
    # Create export dataframe
    export_data = {
        'Candidate Name': [c['name'] for c in candidates],
        'Position': [c['position'] for c in candidates],
        'Email': [c['email'] for c in candidates],
        'Phone': [c['phone'] for c in candidates],
        'Score': [c.get('score', 'N/A') for c in candidates],
        'Feedback': [c.get('feedback', '') for c in candidates],
    }
    
    df_export = pd.DataFrame(export_data)
    
    # CSV download
    csv_data = df_export.to_csv(index=False)
    
    st.download_button(
        label="📄 Download as CSV",
        data=csv_data,
        file_name=f"{session['name'].replace(' ', '_')}_candidates.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # Show preview
    st.subheader("Preview")
    st.dataframe(df_export, use_container_width=True)


def render_delete_session():
    """Render delete session functionality"""
    
    session = st.session_state['current_session']
    
    st.subheader("🗑️ Delete Session")
    st.warning(f"Are you sure you want to delete session '{session['name']}'? This action cannot be undone.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("❌ Yes, Delete Session", use_container_width=True, type="secondary"):
            session_file = INTERVIEW_SESSIONS_DIR / f"{session['name']}.json"
            
            try:
                if session_file.exists():
                    session_file.unlink()
                    st.success(f"✅ Session '{session['name']}' deleted successfully")
                    st.session_state['current_session'] = None
                    st.session_state['session_candidates'] = []
                    st.rerun()
            except Exception as e:
                st.error(f"❌ Error deleting session: {str(e)}")
    
    with col2:
        if st.button("✅ Cancel", use_container_width=True):
            st.rerun()


def render_rankings_section():
    """Render the Rankings UI: select session, choose method, set weights/metric, filters, and view exports.
    
    Robustness:
    - All early returns if data is missing or invalid
    - All widgets have safe min_value <= default value <= max_value
    - No widgets created when dataframes are empty
    - Non-destructive filtering preserves full candidate list
    """
    st.subheader("🏆 View Rankings")

    # Load saved sessions from DB
    try:
        sessions = interview_storage.list_sessions()
    except Exception as e:
        st.error(f"Error accessing interview DB: {e}")
        return

    if not sessions:
        st.info("📭 No saved sessions found in DB. Save a session first to view rankings.")
        return

    # Validate sessions list is not empty before selectbox
    if len(sessions) == 0:
        st.info("📭 No sessions available.")
        return

    idx = st.selectbox(
        "Select saved session",
        options=list(range(len(sessions))),
        format_func=lambda i: f"{sessions[i]['name']} ({sessions[i].get('date') or 'no date'})"
    )
    session_id = sessions[idx]['id']

    # Load session details from DB
    try:
        session_meta, all_candidates = interview_storage.load_session(session_id)
    except Exception as e:
        st.error(f"Failed to load session: {e}")
        return

    # Validate session metadata
    if not session_meta:
        st.info("⚠️ No session data available. Session may be corrupted.")
        return

    st.markdown(f"**Session:** {session_meta.get('name')} — Interviewer: {session_meta.get('interviewer')} — Date: {session_meta.get('date')}")

    # **EARLY RETURN: Check for empty candidates BEFORE creating any widgets**
    if not all_candidates or len(all_candidates) == 0:
        st.info("ℹ️ No candidates available in this session. Add candidates first, then save to DB.")
        return

    # Validate all_candidates is a list
    if not isinstance(all_candidates, list):
        st.error(f"⚠️ Invalid candidates data format (expected list, got {type(all_candidates).__name__})")
        return

    # Extract available metrics with safe fallback
    metrics_set = set()
    for c in all_candidates:
        if not isinstance(c, dict):
            continue
        sc = c.get('scores') or {}
        if isinstance(sc, dict):
            metrics_set.update(sc.keys())
    
    metrics = sorted(list(metrics_set))


    # --- Compute weighted_score as mean of metric columns ---
    metric_cols = [c for c in metrics if f"metric_{c}" in [col for col in df_ranked.columns]]
    if metric_cols:
        metric_col_names = [f"metric_{c}" for c in metric_cols]
        # If not present, add metric columns to base_df
        for col in metric_col_names:
            if col not in df_ranked.columns:
                df_ranked[col] = 0.0
        df_ranked["weighted_score"] = df_ranked[metric_col_names].mean(axis=1)
    else:
        df_ranked["weighted_score"] = df_ranked["weighted_score"] if "weighted_score" in df_ranked.columns else 0.0

    # --- Focus metric selector ---
    metric_map = {"Weighted Score": "weighted_score"}
    for m in metrics:
        metric_map[m] = f"metric_{m}"
    focus_label = st.selectbox("Focus metric", list(metric_map.keys()), index=0)
    focus_column = metric_map[focus_label]

    # Filters section
    st.markdown("**Filters**")
    
    # Extract unique roles safely
    roles = sorted({c.get('position') for c in all_candidates if isinstance(c, dict) and c.get('position')})
    role_choice = st.selectbox(
        "Filter by Role",
        options=["All"] + list(roles),
        help="Select role to filter candidates"
    )

    # Experience range — handle edge cases safely
    exps = []
    for c in all_candidates:
        if isinstance(c, dict):
            exp_val = c.get('experience_years')
            if exp_val is not None:
                try:
                    exps.append(int(exp_val))
                except (ValueError, TypeError):
                    exps.append(0)
    
    min_exp = int(min(exps)) if exps else 0
    max_exp = int(max(exps)) if exps else 0
    
    # Create slider only if min_exp < max_exp; otherwise set fixed range
    if min_exp < max_exp:
        exp_range = st.slider(
            "Filter by Experience (years)",
            min_value=min_exp,
            max_value=max_exp,
            value=(min_exp, max_exp),
            help="Select experience range"
        )
    else:
        # All candidates have identical experience or only one candidate
        exp_range = (min_exp, max_exp)
        st.info(f"ℹ️ All candidates have {min_exp} years experience; experience filter disabled.")


    # --- Build ranking DataFrame and ensure 'experience_years' column exists ---
    try:
        if method == "Weighted score":
            df_ranked = interview_scoring.rank_candidates(all_candidates, weights if weights else None)
        else:
            # build DataFrame with selected metric or fallback to overall score
            if selected_metric and metrics:
                records = []
                for c in all_candidates:
                    val = (c.get('scores') or {}).get(selected_metric)
                    records.append(dict(c, weighted_score=float(val) if val is not None else 0.0))
                df_ranked = pd.DataFrame(records)
                df_ranked = df_ranked.sort_values(by='weighted_score', ascending=False).reset_index(drop=True)
                df_ranked['rank'] = df_ranked['weighted_score'].rank(method='dense', ascending=False).astype(int)
            else:
                df_ranked = interview_scoring.rank_candidates(all_candidates, None)
    except Exception as e:
        st.error(f"Failed to compute ranking: {e}")
        return

    if df_ranked is None or df_ranked.empty:
        st.info("⚠️ No ranking data available. Ensure candidates have valid scores.")
        return

    # --- Ensure 'experience_years' column exists and is numeric ---
    # Try to map from possible candidate keys if missing
    exp_col_candidates = ['experience_years', 'experience', 'years_experience', 'exp']
    if 'experience_years' not in df_ranked.columns:
        found_col = None
        for col in exp_col_candidates[1:]:
            if col in df_ranked.columns:
                found_col = col
                break
        if found_col:
            df_ranked['experience_years'] = pd.to_numeric(df_ranked[found_col], errors='coerce').fillna(0).astype(int)
        else:
            df_ranked['experience_years'] = 0
    else:
        df_ranked['experience_years'] = pd.to_numeric(df_ranked['experience_years'], errors='coerce').fillna(0).astype(int)


    # --- Build base_df: full candidate table, never modified ---
    base_df = df_ranked.sort_values("weighted_score", ascending=False).reset_index(drop=True)

    # --- Apply filters to a working copy ---
    filtered_df = base_df.copy()
    if role_choice != "All":
        filtered_df = filtered_df[filtered_df['position'] == role_choice]

    # Experience filter (optional and safe)
    if 'experience_years' in filtered_df.columns and not filtered_df.empty:
        min_exp = int(filtered_df['experience_years'].min())
        max_exp = int(filtered_df['experience_years'].max())
        if min_exp == max_exp:
            st.info(f"ℹ️ All candidates have {min_exp} years experience; experience filter disabled.")
            exp_range = (min_exp, max_exp)
        else:
            exp_range = st.slider(
                "Experience (years)",
                min_value=min_exp,
                max_value=max_exp,
                value=(min_exp, max_exp),
            )
        # Only filter if range is valid
        if min_exp != max_exp or (min_exp == max_exp and exp_range[0] != exp_range[1]):
            filtered_df = filtered_df[
                (filtered_df['experience_years'] >= exp_range[0]) &
                (filtered_df['experience_years'] <= exp_range[1])
            ]
    elif 'experience_years' not in filtered_df.columns:
        st.info("No experience field available; experience filter disabled.")

    # --- Sort filtered_df to get ranked_df ---
    ranked_df = filtered_df.sort_values("weighted_score", ascending=False).reset_index(drop=True)

def render_rankings_section():
    """Render the Rankings UI with focus metric selector and visualizations.
    
    Consistent variable naming:
    - base_df: full candidate ranking data with all metrics (never mutated)
    - ranked_df: base_df sorted by focus metric for display
    - top_df: ranked_df sliced to top N candidates
    """
    st.subheader("🏆 View Rankings")

    try:
        # 1. Build base_df from session candidates
        base_df = build_base_df_from_session()
        
        # Guard: ensure data exists before any column references
        if base_df is None or base_df.empty:
            st.info("No candidates available for ranking yet.")
            return

        # 2. Normalize metrics
        base_df = compute_normalized_metrics(base_df)

        # 3. Focus metric selectbox
        metric_map = {
            "Weighted Score": "weighted_score",
            "Communication": "metric_communication",
            "Technical": "metric_technical",
            "Projects": "metric_projects",
            "Problem Solving": "metric_problemSolving",
            "Cultural Fit": "metric_cultureFit"
        }
        focus_label = st.selectbox("Focus metric (visual only)", list(metric_map.keys()), index=0)
        focus_col = metric_map[focus_label]

        # 4. Safe Top-N widget
        max_n = len(base_df)
        default_n = min(5, max_n)
        top_n = int(st.number_input("Show top N", min_value=1, max_value=max_n, value=default_n, step=1))

        # 5. Rank candidates by focus metric
        ranked_df = base_df.sort_values(by=focus_col, ascending=False).reset_index(drop=True)
        top_df = get_top_n(ranked_df, top_n, by=focus_col)

        # 6. Display ranking table
        st.markdown(f"**Top {top_n} by {focus_label}**")
        st.dataframe(top_df)

        # 7. Single-metric bar chart for focus_col
        try:
            fig_bar = px.bar(
                ranked_df,
                x="name",
                y=focus_col,
                title=f"Top {top_n} Candidates by {focus_label}",
                labels={focus_col: focus_label, "name": "Candidate"}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render bar chart: {e}")

        # 8. Grouped bar chart for all metrics
        try:
            # Safe two-step: extract metric columns from base_df
            all_cols = list(base_df.columns)
            metric_cols = [c for c in all_cols if c.startswith("metric_")]

            if metric_cols:
                df_melt = ranked_df.melt(id_vars=["name"], value_vars=metric_cols, var_name="metric", value_name="score")
                fig_grouped = px.bar(
                    df_melt,
                    x="name",
                    y="score",
                    color="metric",
                    barmode="group",
                    title="All Parameters for All Candidates"
                )
                st.plotly_chart(fig_grouped, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render grouped chart: {e}")

    except Exception as e:
        st.error(f"Ranking error: {e}")
        return


def render_candidate_comparison():
    """Render comprehensive candidate comparison UI with overall and focused metric views."""
    st.subheader("📊 Candidate Comparison")

    try:
        # Build comparison_df from session candidates
        comparison_df = build_base_df_from_session()

        if comparison_df is None or comparison_df.empty:
            st.info("No candidates available yet. Add candidates in the Interview tab to see comparisons.")
            return

        # Extract metric columns
        all_cols = list(comparison_df.columns)
        metric_cols = [c for c in all_cols if c.startswith("metric_")]

        if not metric_cols:
            st.info("No metrics available for comparison.")
            return

        # =====================================================================
        # Section A: Overall Candidate Comparison
        # =====================================================================
        st.markdown("### Overall Comparison")

        # Display comparison table
        try:
            display_cols = ["name"] + (["position"] if "position" in comparison_df.columns else []) + metric_cols
            available_cols = [c for c in display_cols if c in comparison_df.columns]
            
            table_df = comparison_df[available_cols].copy()
            # Rename metric columns for readability
            rename_map = {c: c.replace("metric_", "").replace("_", " ") for c in metric_cols}
            table_df = table_df.rename(columns=rename_map)
            
            st.dataframe(table_df, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not display comparison table: {e}")

        # Display heatmap of all metrics
        try:
            if metric_cols and "name" in comparison_df.columns:
                heatmap_df = comparison_df[["name"] + metric_cols].set_index("name")
                # Rename columns for readability
                heatmap_df.columns = [c.replace("metric_", "").replace("_", " ") for c in heatmap_df.columns]
                
                fig, ax = plt.subplots(figsize=(10, max(4, len(heatmap_df) * 0.5)))
                import seaborn as sns
                sns.heatmap(heatmap_df, annot=True, fmt=".1f", cmap="RdYlGn", vmin=0, vmax=10, ax=ax, cbar_kws={"label": "Score"})
                ax.set_title("Candidate Performance Heatmap")
                st.pyplot(fig, use_container_width=True)
        except Exception as e:
            st.warning(f"Could not render heatmap: {e}")

        # =====================================================================
        # Section B: Focused Metric Comparison
        # =====================================================================
        st.markdown("### 🎯 Focused Comparison by Metric")

        # Build metric map for selector
        metric_display_map = {c.replace("metric_", "").replace("_", " "): c for c in metric_cols}
        if "weighted_score" in comparison_df.columns:
            metric_display_map = {"Overall Score": "weighted_score", **metric_display_map}

        focus_label = st.selectbox(
            "Select a parameter to compare",
            list(metric_display_map.keys()),
            index=0,
            help="Choose a metric to see which candidate performed best"
        )
        focus_col = metric_display_map[focus_label]

        # Verify column exists
        if focus_col not in comparison_df.columns:
            st.info(f"Parameter '{focus_label}' not available in candidate data.")
            return

        # Build focused comparison chart
        try:
            focus_df = comparison_df[["name", focus_col]].dropna().copy()
            focus_df = focus_df.sort_values(focus_col, ascending=False).reset_index(drop=True)

            if not focus_df.empty:
                fig, ax = plt.subplots(figsize=(10, 4))
                bars = ax.bar(focus_df["name"], focus_df[focus_col], color="steelblue")
                ax.set_xlabel("Candidate", fontsize=11, fontweight="bold")
                ax.set_ylabel("Score", fontsize=11, fontweight="bold")
                ax.set_title(f"Candidates Ranked by {focus_label}", fontsize=12, fontweight="bold")
                ax.set_ylim(0, 10)
                plt.xticks(rotation=45, ha="right")

                # Add value labels on bars
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width() / 2., height,
                            f"{height:.1f}", ha="center", va="bottom", fontsize=9)

                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
            else:
                st.info("No data available for this metric.")
        except Exception as e:
            st.warning(f"Could not render focused comparison chart: {e}")

        st.caption("Use the dropdown above to see who performed best in each interview parameter.")

    except Exception as e:
        st.error(f"Comparison error: {e}")
        return
