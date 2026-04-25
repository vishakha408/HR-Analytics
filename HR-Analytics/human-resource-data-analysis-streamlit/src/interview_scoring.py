"""Scoring helpers for interview candidates.

Provides:
- compute_weighted_score(candidate_dict, weights_dict) -> float
- rank_candidates(candidates_list, weights_dict=None) -> pandas.DataFrame

Behavior:
- If `weights_dict` is None the functions use equal weights across the metrics found.
- If weights do not sum to 1 they are normalized automatically.
- Candidate metric values are taken from `candidate['scores']` (dict). If absent, falls back to candidate['score'] (single numeric) as overall score.
"""
from __future__ import annotations

from typing import Dict, List, Tuple, Optional
import pandas as pd


def _normalize_weights(weights: Dict[str, float], metrics: List[str]) -> Dict[str, float]:
    """Return a weights dict for `metrics` where values sum to 1. If a weight for a metric
    is missing it is treated as 0 before normalization. If total is 0, fall back to equal weights."""
    w = {m: float(weights.get(m, 0.0)) for m in metrics}
    total = sum(w.values())
    if total == 0:
        # equal weights
        eq = 1.0 / len(metrics) if metrics else 0.0
        return {m: eq for m in metrics}
    return {m: (w[m] / total) for m in metrics}


def compute_weighted_score(candidate: Dict, weights: Optional[Dict[str, float]] = None) -> float:
    """Compute a weighted score for a candidate.

    - `candidate` is expected to contain a `scores` dict mapping metric->value.
    - If `scores` is missing but `score` exists, that numeric score is returned.
    - `weights` maps metric->weight; if None equal weights are used across available metrics.
    - Weights are normalized automatically to sum to 1.

    Returns a float (0.0 - 10.0 range if inputs are in that range).
    """
    # Prefer detailed per-metric scores
    scores = candidate.get("scores")
    if not scores:
        # fallback to single numeric score if present
        s = candidate.get("score")
        return float(s) if s is not None else 0.0

    # metrics available for this candidate
    metrics = list(scores.keys())
    if not metrics:
        return 0.0

    if weights is None:
        # equal weights
        norm_weights = {m: 1.0 / len(metrics) for m in metrics}
    else:
        # normalize supplied weights but restrict to metrics present
        # This ensures absent metrics in the candidate don't consume weight
        supplied = {k: v for k, v in weights.items() if k in metrics}
        # if none of the supplied weights match, fall back to equal
        if not supplied:
            norm_weights = {m: 1.0 / len(metrics) for m in metrics}
        else:
            norm_weights = _normalize_weights(supplied, list(supplied.keys()))

    # If norm_weights doesn't include a metric (because user provided subset),
    # we will distribute any leftover weight equally among remaining metrics
    # (but since we normalized only over supplied metrics, treat missing metrics as weight 0).
    # Compute weighted average over metrics present in norm_weights; missing ones contribute 0.
    weighted_sum = 0.0
    for m, v in scores.items():
        w = norm_weights.get(m, 0.0)
        try:
            val = float(v) if v is not None else 0.0
        except Exception:
            val = 0.0
        weighted_sum += val * w

    return float(weighted_sum)


def rank_candidates(candidates: List[Dict], weights: Optional[Dict[str, float]] = None) -> pd.DataFrame:
    """Return a DataFrame of candidates with computed weighted score and rank.

    - `candidates` is a list of candidate dicts (as produced by the interview module).
    - `weights` optional mapping metric->weight. If None equal weights across union of metrics are used.
    - The returned DataFrame is sorted by `weighted_score` descending and contains a `rank` column (1..N).
    """
    if not candidates:
        return pd.DataFrame()

    # Determine all metric names across candidates
    all_metrics = set()
    for c in candidates:
        sc = c.get("scores")
        if sc:
            all_metrics.update(sc.keys())

    all_metrics = sorted(list(all_metrics))

    # If no detailed metrics exist, build a simple DataFrame with existing 'score'
    if not all_metrics:
        df = pd.DataFrame(candidates)
        if "score" not in df.columns:
            df["score"] = 0.0
        df = df.assign(weighted_score=df["score"].astype(float))
        df = df.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
        df["rank"] = df["weighted_score"].rank(method="dense", ascending=False).astype(int)
        return df

    # Build weights: if user provided weights, normalize; else equal weights
    if weights is None:
        # equal weights across all_metrics
        default_weights = {m: 1.0 / len(all_metrics) for m in all_metrics}
        norm_weights = default_weights
    else:
        # normalize provided weights across the metrics they specify — if they don't cover all metrics, remaining metrics get 0
        # but for ranking we'd prefer to normalize over union of metrics present in weights AND candidates; so compute intersection
        supplied = {k: float(v) for k, v in weights.items() if k in all_metrics}
        if not supplied:
            norm_weights = {m: 1.0 / len(all_metrics) for m in all_metrics}
        else:
            # normalize supplied to sum 1 across supplied metrics
            total = sum(supplied.values())
            if total == 0:
                norm_weights = {m: 1.0 / len(all_metrics) for m in all_metrics}
            else:
                # distribute weights: supplied metrics get normalized share, others zero
                norm_weights = {m: (supplied.get(m, 0.0) / total) for m in all_metrics}

    # Compute weighted_score for each candidate
    records = []
    for c in candidates:
        # compute using candidate's scores dict but using norm_weights
        scores = c.get("scores") or {}
        # sum over all_metrics using norm_weights (if metric missing from candidate treated as 0)
        weighted = 0.0
        for m in all_metrics:
            val = scores.get(m)
            try:
                v = float(val) if val is not None else 0.0
            except Exception:
                v = 0.0
            w = norm_weights.get(m, 0.0)
            weighted += v * w

        rec = dict(c)
        rec["weighted_score"] = weighted
        # ensure per-metric columns exist for convenience
        for m in all_metrics:
            rec[f"metric_{m}"] = (scores.get(m) if scores else None)
        records.append(rec)

    df = pd.DataFrame(records)
    df = df.sort_values(by="weighted_score", ascending=False).reset_index(drop=True)
    df["rank"] = df["weighted_score"].rank(method="dense", ascending=False).astype(int)
    return df


def prepare_input_for_model(candidates: List[Dict], metrics: Optional[List[str]] = None) -> pd.DataFrame:
    """Prepare a numeric table (pandas.DataFrame) suitable for feeding into a model.

    - `candidates` is a list of candidate dicts with optional `scores` dict and other fields.
    - `metrics` if provided forces the column order and inclusion; otherwise the union of metrics
      across candidates is used.

    Returns a DataFrame where rows are candidates and columns are numeric metric features.
    Non-present metric values are filled with 0.0.
    """
    if not candidates:
        return pd.DataFrame()

    # Determine metrics union if not provided
    if metrics is None:
        mset = set()
        for c in candidates:
            sc = c.get("scores") or {}
            mset.update(sc.keys())
        metrics = sorted(list(mset))

    # Build rows
    rows = []
    for c in candidates:
        sc = c.get("scores") or {}
        row = {m: float(sc.get(m) or 0.0) for m in metrics}
        # carry some metadata to help mapping back (name, id)
        row["_name"] = c.get("name")
        row["_id"] = c.get("id")
        rows.append(row)

    df = pd.DataFrame(rows)
    # Ensure metrics columns exist
    for m in metrics:
        if m not in df.columns:
            df[m] = 0.0

    # Reorder columns with metadata at the end
    cols = metrics + ["_name", "_id"]
    return df[cols]
