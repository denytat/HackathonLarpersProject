"""Dashboard overview page."""

from __future__ import annotations

import streamlit as st

from components.metrics import hero_banner, metric_card, section_title
from components.sidebar import go_to
from services.api import check_health
from services.stats import benchmark_snapshot, session_analysis_stats, summarize_verdict


def render() -> None:
    health = check_health()
    session = session_analysis_stats()
    bench = benchmark_snapshot()
    verdict = summarize_verdict(st.session_state.get("analysis_result"))

    if health["ok"]:
        status_html = """
        <div style="margin-top:14px;display:inline-flex;align-items:center;gap:8px;
            font-size:13px;font-weight:600;color:#6EE7B7;">
            <span class="sw-pulse"></span> Backend pipelines reachable
        </div>
        """
    else:
        status_html = f"""
        <div style="margin-top:14px;font-size:13px;font-weight:600;color:#FCA5A5;">
            Backend unavailable — {health['detail']}
        </div>
        """

    hero_banner(
        eyebrow="Coordination Intelligence",
        title="Uncover coordinated activity before narratives scale",
        description=(
            "Swarmwatch combines temporal burst detection, text similarity, "
            "account-behaviour graphs, NVIDIA Nemotron technique classification, "
            "and Google Gemini swarm narrative analysis — with evidence you can inspect."
        ),
        status_html=status_html,
    )

    section_title(
        "Workspace Summary",
        "Figures below come from your current session or labeled synthetic benchmarks. "
        "No invented live telemetry.",
    )

    if session:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            metric_card("Posts analyzed", session["posts"], "Current session")
        with c2:
            metric_card("Accounts involved", session["accounts"], "Current session")
        with c3:
            metric_card("Detected swarms", session["swarms"], "Current session")
        with c4:
            metric_card(
                "Flagged posts",
                session["flagged_posts"],
                f"Max swarm score {session['max_swarm_score']:.2f}",
            )
        st.markdown(
            f"""
            <div class="sw-panel">
                <div class="sw-card-label">Latest session verdict</div>
                <div class="sw-verdict {verdict['css']}" style="margin-top:10px;">
                    {verdict['label']}
                </div>
                <p class="sw-muted" style="margin-top:8px;">{verdict['detail']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="sw-panel">
                <div class="sw-card-label">No session analysis yet</div>
                <p class="sw-muted">
                    Upload a CSV on the Analyze page to populate live workspace metrics.
                    Until then, synthetic benchmark totals are shown below for reference.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if bench:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                metric_card(
                    "Sample posts",
                    bench["posts"],
                    "From synthetic baseline report",
                )
            with c2:
                metric_card(
                    "Sample accounts",
                    bench["accounts"],
                    "From synthetic baseline report",
                )
            with c3:
                metric_card(
                    "Sample swarms",
                    bench["swarms"],
                    "Detected in baseline benchmark",
                )
            with c4:
                metric_card(
                    "Dataset",
                    str(bench.get("dataset", "posts")),
                    "Labeled synthetic data",
                )
            st.caption(
                "These values are from `reports/detector_evaluation_posts.json` "
                "(synthetic). They are not live production counters."
            )
        else:
            st.info("Benchmark reports are not available in this environment.")

    section_title(
        "How Swarmwatch Works",
        "One investigation pipeline from raw posts to explainable findings.",
    )

    st.markdown(
        """
        <div class="sw-panel">
            <div class="sw-step">
                <div class="sw-step-num">1</div>
                <div class="sw-step-body">
                    <strong>Coordination detection</strong>
                    <span>Timing bursts, near-duplicate text, and account-similarity
                    graphs identify candidate swarm clusters with measurable evidence.</span>
                </div>
            </div>
            <div class="sw-step">
                <div class="sw-step-num">2</div>
                <div class="sw-step-body">
                    <strong>Nemotron post classification</strong>
                    <span>NVIDIA Nemotron labels manipulation techniques on individual
                    posts and explains the supporting text spans.</span>
                </div>
            </div>
            <div class="sw-step">
                <div class="sw-step-num">3</div>
                <div class="sw-step-body">
                    <strong>Gemini swarm narrative analysis</strong>
                    <span>Google Gemini reviews the whole suspected cluster for shared
                    narrative, coordination assessment, and analyst-facing explanation.</span>
                </div>
            </div>
            <div class="sw-step">
                <div class="sw-step-num">4</div>
                <div class="sw-step-body">
                    <strong>Transparent verdict</strong>
                    <span>Results distinguish coordinated signals, suspicious patterns,
                    and uncertain cases. Coordination is not equated with malicious intent.</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Start new analysis", type="primary", use_container_width=True):
            go_to("Analyze")
    with col2:
        if st.button("View latest results", use_container_width=True):
            go_to("Results")
