"""Threat analysis results page."""

from __future__ import annotations

import streamlit as st

from components.evidence import (
    display_labeled_evaluation,
    display_post_analysis,
    display_swarm,
)
from components.metrics import metric_card, section_title, verdict_banner
from components.network_graph import render_network_graph
from components.sidebar import go_to
from services.stats import summarize_verdict


def render() -> None:
    result = st.session_state.get("analysis_result")

    if result is None:
        st.markdown(
            """
            <div class="sw-panel">
                <div class="sw-card-label">No results yet</div>
                <p class="sw-muted">
                    Run an analysis from the Analyze page. Results persist in this
                    session so you can navigate freely without losing findings.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Go to Analyze", type="primary"):
            go_to("Analyze")
        return

    swarms = result.get("swarms") or []
    post_results = result.get("posts") or []
    verdict = summarize_verdict(result)

    section_title("Final Verdict", "Derived from detected swarms and post flags.")
    verdict_banner(verdict["label"], verdict["css"], verdict["detail"])

    flagged_count = sum(1 for post in post_results if post.get("flagged_by"))
    accounts: set[str] = set()
    for swarm in swarms:
        for account in swarm.get("accounts") or []:
            accounts.add(str(account))
    uploaded_accounts = st.session_state.get("uploaded_accounts") or []
    accounts.update(str(a) for a in uploaded_accounts)

    max_score = max(
        (float(swarm.get("score", 0)) for swarm in swarms),
        default=0.0,
    )

    # Aggregate signal types from evidence
    signal_counts: dict[str, int] = {}
    for swarm in swarms:
        for edge in swarm.get("evidence") or []:
            if not isinstance(edge, dict):
                continue
            signals = edge.get("signals") or {}
            if isinstance(signals, dict):
                for key in signals:
                    signal_counts[key] = signal_counts.get(key, 0) + 1

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Posts analyzed", len(post_results), "From FastAPI response")
    with col2:
        metric_card("Accounts involved", len(accounts), "Across upload + swarms")
    with col3:
        metric_card("Detected swarms", len(swarms), "Account clusters")
    with col4:
        metric_card(
            "Highest swarm score",
            f"{max_score:.2f}",
            f"{flagged_count} flagged posts",
        )

    if signal_counts:
        section_title(
            "Detected Coordination Signals",
            "Counts of evidence signal types across swarm edges.",
        )
        signal_cols = st.columns(min(4, len(signal_counts)) or 1)
        for idx, (name, count) in enumerate(sorted(signal_counts.items())):
            with signal_cols[idx % len(signal_cols)]:
                metric_card(name.replace("_", " ").title(), count, "Evidence edges")

    section_title(
        "Account Network",
        "Interactive graph built only from real evidence edges in the API response.",
    )
    if swarms:
        render_network_graph(swarms)
    else:
        st.info("No swarms detected — network graph has nothing to draw.")

    section_title(
        "Detected Swarms",
        "Explore clusters, evidence pairs, Nemotron/Gemini explanations.",
    )
    if swarms:
        for swarm in swarms:
            display_swarm(swarm)
    else:
        st.info(
            "No potential swarms detected in this dataset "
            "under the current rules."
        )

    section_title(
        "Individual Post Analysis",
        "Phase-1 verdicts and Nemotron manipulation technique classifications.",
    )
    display_post_analysis(post_results)

    analyzed_df = st.session_state.get("analyzed_df")
    mapping = st.session_state.get("analysis_mapping")
    if analyzed_df is not None and mapping:
        display_labeled_evaluation(analyzed_df, mapping, post_results)

    with st.expander("Developer details — raw API response"):
        st.json(result)

    st.caption(
        "Coordinated activity ≠ malicious intent. "
        "AI assessments require human review."
    )
