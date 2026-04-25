"""Storage helpers for interview sessions using SQLite.

Provides robust initialization and CRUD helpers with automatic table
initialization when missing-table errors occur.

API:
- init_interview_db(db_path='data/interviews.db') -> bool
- ensure_db_ready(db_path='data/interviews.db') -> bool
- list_sessions(db_path='data/interviews.db') -> list[dict]
- save_session(session_meta: dict, candidates: list[dict], db_path) -> int
- load_session(session_id, db_path) -> (session_meta, candidates_list)
- export_session_csv(session_id, out_path, db_path) -> str (path)

All DB functions will attempt to auto-initialize the DB if an
sqlite3.OperationalError mentioning 'no such table' is raised.
"""
from __future__ import annotations

import sqlite3
import json
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import csv
from datetime import datetime
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

try:
    from joblib import Memory
    _memory = Memory(location='data/cache', verbose=0)
except Exception:
    _memory = None


DEFAULT_DB = "data/interviews.db"


def init_interview_db(db_path: str = DEFAULT_DB) -> bool:
    """Initialize the interviews SQLite DB and required tables.

    Ensures the parent folder exists, creates required tables and returns True
    on success. Returns False if initialization failed.
    """
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_file))
    try:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")

        # Sessions table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                date TEXT,
                interviewer TEXT,
                notes TEXT,
                created_at TIMESTAMP,
                custom_metrics TEXT
            );
            """
        )

        # Candidates table: include requested columns and legacy ones for compatibility
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                candidate_id TEXT,
                roll TEXT,
                name TEXT,
                email TEXT,
                role TEXT,
                position TEXT,
                phone TEXT,
                notes TEXT,
                scores_json TEXT,
                scores TEXT,
                created_at TIMESTAMP,
                score REAL,
                feedback TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
            );
            """
        )

        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()


def _get_conn(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_file))
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def ensure_db_ready(db_path: str = DEFAULT_DB) -> bool:
    """Ensure the interview DB is initialized once per Streamlit session.

    Sets `st.session_state['interview_db_ready'] = True` on success.
    Returns True if DB ready, False otherwise.
    """
    try:
        import streamlit as st
        if st.session_state.get('interview_db_ready'):
            return True
        ok = init_interview_db(db_path=db_path)
        if ok:
            st.session_state['interview_db_ready'] = True
            return True
        return False
    except Exception:
        return False


def save_session(session_meta: Dict, candidates: List[Dict], db_path: str = DEFAULT_DB) -> int:
    """Save or update a session and its candidates to the DB.

    If `session_meta` contains an 'id' key, the session will be updated and
    existing candidates replaced. Returns the session_id (int) on success.

    On sqlite OperationalError that mentions missing tables, this function will
    attempt to initialize the DB and retry once.
    """
    try:
        conn = _get_conn(db_path)
        cur = conn.cursor()
        now = session_meta.get("created_at") or datetime.utcnow().isoformat()

        if session_meta.get("id"):
            session_id = int(session_meta["id"])
            cur.execute(
                "UPDATE sessions SET name=?, date=?, interviewer=?, notes=?, created_at=?, custom_metrics=? WHERE id=?",
                (
                    session_meta.get("name"),
                    session_meta.get("date"),
                    session_meta.get("interviewer"),
                    session_meta.get("notes"),
                    now,
                    json.dumps(session_meta.get("custom_metrics", [])),
                    session_id,
                ),
            )
            cur.execute("DELETE FROM candidates WHERE session_id=?", (session_id,))
        else:
            cur.execute(
                "INSERT INTO sessions (name, date, interviewer, notes, created_at, custom_metrics) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session_meta.get("name"),
                    session_meta.get("date"),
                    session_meta.get("interviewer"),
                    session_meta.get("notes"),
                    now,
                    json.dumps(session_meta.get("custom_metrics", [])),
                ),
            )
            session_id = cur.lastrowid

        for c in candidates:
            scores_json = json.dumps(c.get("scores")) if c.get("scores") is not None else None
            cur.execute(
                """
                INSERT INTO candidates (
                    session_id, candidate_id, roll, name, email, role, position, phone, notes, created_at, score, scores, scores_json, feedback
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    c.get("candidate_id") or c.get("roll"),
                    c.get("roll"),
                    c.get("name"),
                    c.get("email"),
                    c.get("role") or c.get("position"),
                    c.get("position"),
                    c.get("phone"),
                    c.get("notes"),
                    c.get("added_at") or datetime.utcnow().isoformat(),
                    c.get("score"),
                    json.dumps(c.get("scores")) if c.get("scores") is not None else None,
                    scores_json,
                    c.get("feedback"),
                ),
            )

        conn.commit()
        return session_id
    except sqlite3.OperationalError as e:
        msg = str(e)
        if 'no such table' in msg:
            # Initialize DB and retry once
            init_interview_db(db_path=db_path)
            return save_session(session_meta, candidates, db_path=db_path)
        raise RuntimeError(f"DB error saving session: {msg}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error saving session: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def load_session(session_id: int, db_path: str = DEFAULT_DB) -> Tuple[Optional[Dict], List[Dict]]:
    """Load session meta and candidates for a given session_id.

    Returns (session_meta_dict or None, candidates_list).
    On missing tables this will initialize DB and retry once.
    """
    try:
        conn = _get_conn(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, name, date, interviewer, notes, created_at, custom_metrics FROM sessions WHERE id=?", (session_id,))
        row = cur.fetchone()
        if not row:
            return None, []

        session_meta = {
            "id": row[0],
            "name": row[1],
            "date": row[2],
            "interviewer": row[3],
            "notes": row[4],
            "created_at": row[5],
            "custom_metrics": json.loads(row[6]) if row[6] else [],
        }

        cur.execute(
            "SELECT id, candidate_id, roll, name, email, role, position, phone, notes, created_at, score, scores, scores_json, feedback FROM candidates WHERE session_id=? ORDER BY id",
            (session_id,),
        )
        candidates = []
        for r in cur.fetchall():
            # scores field could be in either column; prefer `scores` then `scores_json`
            scores_text = r[11] or r[12]
            scores = json.loads(scores_text) if scores_text else None
            candidates.append(
                {
                    "id": r[0],
                    "candidate_id": r[1],
                    "roll": r[2],
                    "name": r[3],
                    "email": r[4],
                    "role": r[5],
                    "position": r[6],
                    "phone": r[7],
                    "notes": r[8],
                    "added_at": r[9],
                    "score": r[10],
                    "scores": scores,
                    "feedback": r[13],
                }
            )

        return session_meta, candidates
    except sqlite3.OperationalError as e:
        msg = str(e)
        if 'no such table' in msg:
            init_interview_db(db_path=db_path)
            return load_session(session_id, db_path=db_path)
        raise RuntimeError(f"DB error loading session: {msg}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error loading session: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def list_sessions(db_path: str = DEFAULT_DB) -> List[Dict]:
    """Return a list of saved sessions with basic info: id, name, date, interviewer."""
    try:
        conn = _get_conn(db_path)
        cur = conn.cursor()
        cur.execute("SELECT id, name, date, interviewer, created_at FROM sessions ORDER BY created_at DESC")
        rows = cur.fetchall()
        return [
            {"id": r[0], "name": r[1], "date": r[2], "interviewer": r[3], "created_at": r[4]}
            for r in rows
        ]
    except sqlite3.OperationalError as e:
        msg = str(e)
        if 'no such table' in msg:
            init_interview_db(db_path=db_path)
            return list_sessions(db_path=db_path)
        raise RuntimeError(f"DB error listing sessions: {msg}")
    except Exception as e:
        raise RuntimeError(f"Unexpected error listing sessions: {e}")
    finally:
        try:
            conn.close()
        except Exception:
            pass


def load_session_cached(session_id: int, db_path: str = DEFAULT_DB) -> Tuple[Optional[Dict], List[Dict]]:
    """Cached wrapper around `load_session` using joblib Memory when available."""
    if _memory is None:
        return load_session(session_id, db_path=db_path)

    # use a small wrapper so cache key includes session_id and db_path
    @ _memory.cache
    def _loader(sid, path):
        return load_session(sid, db_path=path)

    return _loader(session_id, db_path)


def export_session_csv(session_id: int, out_path: str, db_path: str = DEFAULT_DB) -> str:
    """Export the candidates of a session to a CSV file at out_path.

    Returns the path to the written CSV file.
    """
    try:
        session_meta, candidates = load_session(session_id, db_path=db_path)
    except Exception as e:
        raise RuntimeError(f"Failed to load session for export: {e}")
    if session_meta is None:
        raise ValueError(f"Session id {session_id} not found")

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Build CSV rows flattening scores dict
    fieldnames = [
        "id",
        "roll",
        "name",
        "email",
        "position",
        "experience_years",
        "phone",
        "notes",
        "added_at",
        "score",
        "feedback",
    ]

    # include custom metric columns if present
    custom = session_meta.get("custom_metrics") or []
    fieldnames.extend(custom)

    with out_file.open("w", newline='', encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for c in candidates:
            row = {k: c.get(k) for k in fieldnames if k in c}
            # fill custom metrics
            for m in custom:
                row[m] = (c.get("scores") or {}).get(m)
            writer.writerow(row)

    return str(out_file.resolve())


def export_session_excel(session_id: int, out_path: str, db_path: str = DEFAULT_DB) -> str:
    """Export session to Excel (.xlsx). Returns path to written file."""
    session_meta, candidates = load_session(session_id, db_path=db_path)
    if session_meta is None:
        raise ValueError(f"Session id {session_id} not found")

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    # Build DataFrame
    rows = []
    custom = session_meta.get("custom_metrics") or []
    for c in candidates:
        row = {
            "id": c.get("id"),
            "roll": c.get("roll"),
            "name": c.get("name"),
            "email": c.get("email"),
            "position": c.get("position"),
            "experience_years": c.get("experience_years"),
            "phone": c.get("phone"),
            "notes": c.get("notes"),
            "added_at": c.get("added_at"),
            "score": c.get("score"),
            "feedback": c.get("feedback"),
        }
        for m in custom:
            row[m] = (c.get("scores") or {}).get(m)
        rows.append(row)

    df = pd.DataFrame(rows)
    # Write to Excel
    df.to_excel(str(out_file), index=False)
    return str(out_file.resolve())


def export_session_pdf(session_id: int, out_path: str, db_path: str = DEFAULT_DB) -> str:
    """Export session candidate table to a simple PDF using matplotlib table.

    This creates a multi-page PDF if there are many rows. Returns path to written PDF.
    """
    session_meta, candidates = load_session(session_id, db_path=db_path)
    if session_meta is None:
        raise ValueError(f"Session id {session_id} not found")

    out_file = Path(out_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    custom = session_meta.get("custom_metrics") or []
    fieldnames = [
        "id",
        "roll",
        "name",
        "position",
        "email",
        "phone",
        "experience_years",
        "score",
        "feedback",
    ] + custom

    rows = []
    for c in candidates:
        row = [c.get(k) for k in ["id", "roll", "name", "position", "email", "phone", "experience_years", "score", "feedback"]]
        for m in custom:
            row.append((c.get("scores") or {}).get(m))
        rows.append(row)

    # paginated table: 25 rows per page
    per_page = 25
    pages = [rows[i:i+per_page] for i in range(0, len(rows), per_page)] or [[]]

    with PdfPages(str(out_file)) as pdf:
        for page_rows in pages:
            fig, ax = plt.subplots(figsize=(11, 8.5))
            ax.axis('off')
            # build table data with header
            table_data = [fieldnames] + page_rows
            table = ax.table(cellText=table_data, loc='center', cellLoc='left')
            table.auto_set_font_size(False)
            table.set_fontsize(8)
            table.scale(1, 1.5)
            ax.set_title(f"Session: {session_meta.get('name')} - Candidates")
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)

    return str(out_file.resolve())
