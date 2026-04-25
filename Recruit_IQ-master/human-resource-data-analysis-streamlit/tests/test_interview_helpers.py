import json
import os
import pytest
import pandas as pd

from src import interview_scoring, interview_storage

def test_compute_weighted_score():
    candidate = {
        "scores": {
            "Communication": 8,
            "Technical Skills": 6,
        }
    }
    weights = {"Communication": 0.25, "Technical Skills": 0.75}
    score = interview_scoring.compute_weighted_score(candidate, weights)
    assert pytest.approx(score, rel=1e-6) == 8 * 0.25 + 6 * 0.75

def test_rank_candidates():
    candidates = [
        {"name": "Alice", "scores": {"Communication": 8, "Technical Skills": 9}},
        {"name": "Bob", "scores": {"Communication": 7, "Technical Skills": 6}},
        {"name": "Carol", "scores": {"Communication": 9, "Technical Skills": 8}},
    ]

    # Use weights favoring Technical Skills
    weights = {"Communication": 0.2, "Technical Skills": 0.8}

    df = interview_scoring.rank_candidates(candidates, weights)

    # The DataFrame should be sorted by weighted_score descending
    names_order = df['name'].tolist()
    assert names_order[0] == 'Alice' or names_order[0] == 'Carol'
    # Check rank column is present and dense
    assert 'rank' in df.columns
    # Scores should be numeric
    assert df['weighted_score'].dtype.kind in 'fc'

def test_storage_roundtrip(tmp_path):
    # create a fresh sqlite db in tmp_path
    db_file = tmp_path / "interviews.db"
    db_path = str(db_file)
    interview_storage.init_interview_db(db_path=db_path)

    session_meta = {
        "name": "Test Session",
        "date": "2025-11-14",
        "interviewer": "Unit Tester",
        "notes": "roundtrip test",
        "custom_metrics": ["Communication", "Technical Skills"]
    }

    candidates = [
        {
            "roll": "R1",
            "name": "Test A",
            "email": "a@example.com",
            "position": "Dev",
            "experience_years": 3,
            "phone": "",
            "notes": "",
            "added_at": "2025-11-14T10:00:00",
            "score": 8.5,
            "scores": {"Communication": 8, "Technical Skills": 9},
            "feedback": "Good"
        }
    ]

    session_id = interview_storage.save_session(session_meta, candidates, db_path=db_path)
    assert isinstance(session_id, int) and session_id > 0

    loaded_meta, loaded_candidates = interview_storage.load_session(session_id, db_path=db_path)
    assert loaded_meta is not None
    assert loaded_meta['name'] == session_meta['name']
    assert len(loaded_candidates) == len(candidates)
    # compare first candidate name and scores
    assert loaded_candidates[0]['name'] == candidates[0]['name']
    assert loaded_candidates[0]['scores'] == candidates[0]['scores']
import os
import pytest
import pandas as pd

from src import interview_scoring, interview_storage


def test_compute_weighted_score():
    candidate = {
        "scores": {
            "Communication": 8,
            "Technical Skills": 6,
        }
    }
    weights = {"Communication": 0.25, "Technical Skills": 0.75}
    score = interview_scoring.compute_weighted_score(candidate, weights)
    assert pytest.approx(score, rel=1e-6) == 8 * 0.25 + 6 * 0.75


def test_rank_candidates():
    candidates = [
        {"name": "Alice", "scores": {"Communication": 8, "Technical Skills": 9}},
        {"name": "Bob", "scores": {"Communication": 7, "Technical Skills": 6}},
        {"name": "Carol", "scores": {"Communication": 9, "Technical Skills": 8}},
    ]

    # Use weights favoring Technical Skills
    weights = {"Communication": 0.2, "Technical Skills": 0.8}

    df = interview_scoring.rank_candidates(candidates, weights)

    # The DataFrame should be sorted by weighted_score descending
    names_order = df['name'].tolist()
    assert names_order[0] == 'Alice' or names_order[0] == 'Carol'
    # Check rank column is present and dense
    assert 'rank' in df.columns
    # Scores should be numeric
    assert df['weighted_score'].dtype.kind in 'fc'


def test_storage_roundtrip(tmp_path):
    # create a fresh sqlite db in tmp_path
    db_file = tmp_path / "interviews.db"
    db_path = str(db_file)
    interview_storage.init_interview_db(db_path=db_path)

    session_meta = {
        "name": "Test Session",
        "date": "2025-11-14",
        "interviewer": "Unit Tester",
        "notes": "roundtrip test",
        "custom_metrics": ["Communication", "Technical Skills"]
    }

    candidates = [
        {
            "roll": "R1",
            "name": "Test A",
            "email": "a@example.com",
            "position": "Dev",
            "experience_years": 3,
            "phone": "",
            "notes": "",
            "added_at": "2025-11-14T10:00:00",
            "score": 8.5,
            "scores": {"Communication": 8, "Technical Skills": 9},
            "feedback": "Good"
        }
    ]

    session_id = interview_storage.save_session(session_meta, candidates, db_path=db_path)
    assert isinstance(session_id, int) and session_id > 0

    loaded_meta, loaded_candidates = interview_storage.load_session(session_id, db_path=db_path)
    assert loaded_meta is not None
    assert loaded_meta['name'] == session_meta['name']
    assert len(loaded_candidates) == len(candidates)
    # compare first candidate name and scores
    assert loaded_candidates[0]['name'] == candidates[0]['name']
    assert loaded_candidates[0]['scores'] == candidates[0]['scores']
