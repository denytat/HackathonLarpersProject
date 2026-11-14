"""About Swarmwatch page."""

from __future__ import annotations

import streamlit as st

from components.metrics import section_title


def render() -> None:
    section_title(
        "About Swarmwatch",
        "Transparent coordination intelligence for social media investigations.",
    )

    st.markdown(
        """
        <div class="sw-hero">
            <div class="sw-hero-eyebrow">Mission</div>
            <div class="sw-hero-title">Evidence-first detection of coordinated activity</div>
            <p class="sw-hero-desc">
                Swarmwatch helps analysts spot groups of accounts acting in sync —
                without pretending that automation can prove intent on its own.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sw-panel">
            <div class="sw-section" style="margin-top:0;">What is coordinated inauthentic behaviour?</div>
            <p class="sw-muted">
                Coordinated inauthentic behaviour (CIB) refers to groups of accounts
                working together to amplify messages, create artificial consensus, or
                obscure the true origin of a narrative. The key signal is the
                <em>pattern across accounts</em> — not any single post in isolation.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sw-panel">
            <div class="sw-section" style="margin-top:0;">Why analyzing groups matters</div>
            <p class="sw-muted">
                Organic posts can look persuasive on their own. Coordination shows up
                when many accounts post near-identical text within seconds, share
                behavioural fingerprints, or form dense similarity graphs. Swarmwatch
                therefore evaluates batches of posts and account relationships together.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sw-panel">
            <div class="sw-section" style="margin-top:0;">How Swarmwatch identifies coordination</div>
            <div class="sw-step">
                <div class="sw-step-num">1</div>
                <div class="sw-step-body">
                    <strong>Posting-time patterns</strong>
                    <span>Burst windows catch accounts posting in near-lockstep.</span>
                </div>
            </div>
            <div class="sw-step">
                <div class="sw-step-num">2</div>
                <div class="sw-step-body">
                    <strong>Text similarity</strong>
                    <span>Near-duplicate and paraphrased content links candidate peers.</span>
                </div>
            </div>
            <div class="sw-step">
                <div class="sw-step-num">3</div>
                <div class="sw-step-body">
                    <strong>Account-behaviour similarity</strong>
                    <span>Behavioural features strengthen or weaken pairwise evidence.</span>
                </div>
            </div>
            <div class="sw-step">
                <div class="sw-step-num">4</div>
                <div class="sw-step-body">
                    <strong>Clustering</strong>
                    <span>Graph communities become inspectable swarm candidates with scores.</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            """
            <div class="sw-panel">
                <div class="sw-section" style="margin-top:0;">What Nemotron contributes</div>
                <p class="sw-muted">
                    NVIDIA Nemotron classifies manipulation techniques on individual posts,
                    highlights supporting text spans, and provides confidence/explanation
                    for analyst review.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div class="sw-panel">
                <div class="sw-section" style="margin-top:0;">What Gemini contributes</div>
                <p class="sw-muted">
                    Google Gemini reviews an entire suspected swarm for shared narrative,
                    coordination assessment, and a transparent explanation of why the
                    cluster looks coordinated — without claiming proven malice.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        """
        <div class="sw-panel">
            <div class="sw-section" style="margin-top:0;">Why transparency and evidence matter</div>
            <p class="sw-muted">
                Every swarm finding should be inspectable: which accounts, which edges,
                which signals, which AI statements. Swarmwatch surfaces evidence tables,
                technique spans, and raw API responses so analysts can challenge the model.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sw-warning">
            <strong>Limitations of automated analysis</strong><br/>
            Detectors can miss sophisticated campaigns and can flag organic viral
            behaviour. Synthetic benchmarks are small and controlled. AI explanations
            can be incomplete or wrong. Coordination signals are not proof of
            malicious intent, foreign influence, or policy violations. Human review
            remains essential.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "Swarmwatch · Junction 2026 · Hostinger / Gemini / Nemotron challenges"
    )
