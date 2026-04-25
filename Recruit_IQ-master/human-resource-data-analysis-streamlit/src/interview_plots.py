"""Plotting helpers for interview rankings and candidate metrics.

Functions return Plotly or Matplotlib figure objects suitable for `st.plotly_chart` or `st.pyplot`.
"""
from __future__ import annotations

from typing import List
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def plot_top_candidates_bar(df_ranked: pd.DataFrame, top_n: int = 10):
    """Return a Plotly bar chart figure of the top N candidates by weighted score.

    Expects a DataFrame with at least columns: 'name' and 'weighted_score'.
    """
    if df_ranked is None or df_ranked.empty:
        fig = go.Figure()
        fig.update_layout(title="No data")
        return fig

    top_df = df_ranked.head(top_n)
    fig = px.bar(top_df, x='name', y='weighted_score', color='weighted_score', labels={'name':'Candidate','weighted_score':'Score'},
                 title=f'Top {min(top_n, len(top_df))} Candidates by Score')
    fig.update_layout(xaxis_tickangle=-45)
    return fig


def plot_candidate_radar(candidate_row: dict, metrics_list: List[str]):
    """Return a Plotly radar (polar) chart for a single candidate.

    - `candidate_row` can be a pandas Series or a dict that contains per-metric values
      either as keys of the form 'metric_{metric_name}' or as a 'scores' dict.
    - `metrics_list` is the ordered list of metric names to plot.
    """
    # Extract metric values
    scores = []
    for m in metrics_list:
        col_name = f"metric_{m}"
        if isinstance(candidate_row, dict):
            if col_name in candidate_row:
                v = candidate_row.get(col_name)
            else:
                # try scores dict
                v = (candidate_row.get('scores') or {}).get(m)
        else:
            # pandas Series
            if col_name in candidate_row.index:
                v = candidate_row[col_name]
            else:
                v = (candidate_row.get('scores') or {}).get(m)
        try:
            scores.append(float(v) if v is not None else 0.0)
        except Exception:
            scores.append(0.0)

    # close the polygon
    theta = metrics_list + [metrics_list[0]]
    r = scores + [scores[0]]

    fig = go.Figure()
    name = candidate_row.get('name') if isinstance(candidate_row, dict) else candidate_row.get('name')
    fig.add_trace(go.Scatterpolar(r=r, theta=theta, fill='toself', name=str(name)))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=True,
                      title=f"{name} - Metric Breakdown")
    return fig


def plot_metric_distribution(candidates_df: pd.DataFrame, metric: str):
    """Return a Plotly violin plot (with box) of a metric across candidates.

    - `candidates_df` may contain columns like 'metric_{metric}' or a 'scores' dict column.
    - `metric` is the metric name (e.g., 'Communication').
    """
    if candidates_df is None or candidates_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No data")
        return fig

    col_name = f"metric_{metric}"
    if col_name in candidates_df.columns:
        series = candidates_df[col_name].astype(float, errors='ignore')
    elif 'scores' in candidates_df.columns:
        series = candidates_df['scores'].apply(lambda s: (s or {}).get(metric)).astype(float, errors='ignore')
    else:
        # fallback to overall score
        if 'score' in candidates_df.columns:
            series = candidates_df['score'].astype(float, errors='ignore')
        else:
            # nothing to plot
            fig = go.Figure()
            fig.update_layout(title="Metric not found")
            return fig

    plot_df = pd.DataFrame({metric: series}).dropna()
    if plot_df.empty:
        fig = go.Figure()
        fig.update_layout(title="No metric data available")
        return fig

    fig = px.violin(plot_df, y=metric, box=True, points='all', title=f'Distribution of {metric}')
    return fig
