"""Benchmark and evaluation report page."""

from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from components.metrics import metric_card, section_title
from services.paths import reports_path


def render() -> None:
    section_title(
        "Benchmark Reports",
        "Reproducible evaluation against human-reviewed synthetic datasets.",
    )

    st.markdown(
        """
        <div class="sw-warning">
            These datasets are synthetic and relatively small.
            Metrics demonstrate pipeline behaviour under controlled conditions —
            they are not proof of real-world detection accuracy.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="sw-panel">
            <p class="sw-muted" style="margin:0;">
                <strong style="color:#F1F5F9;">What these benchmarks measure</strong><br/>
                Phase 1 reports evaluate whether accounts/posts involved in planted
                coordination are recovered by the swarm detector (precision, recall, F1,
                accuracy, confusion matrix). Phase 2 AI evaluation measures Nemotron
                technique classification false-positive behaviour and Gemini swarm-level
                technique recovery on the challenge set.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    report_files = {
        "Baseline": reports_path("detector_evaluation_posts.json"),
        "Challenge": reports_path("detector_evaluation_challenge_posts.json"),
        "AI Evaluation": reports_path("ai_evaluation_challenge.json"),
    }

    loaded: dict[str, dict] = {}
    for name, path in report_files.items():
        if not path.exists():
            st.warning(f"{name} report not found: {path.name}")
            continue
        try:
            with path.open("r", encoding="utf-8") as handle:
                loaded[name] = json.load(handle)
        except (OSError, json.JSONDecodeError) as error:
            st.error(f"Could not load {path.name}: {error}")

    if not loaded:
        st.info("No benchmark reports are available.")
        return

    detector_reports = {
        name: loaded[name]
        for name in ("Baseline", "Challenge")
        if name in loaded
    }

    if detector_reports:
        st.markdown("### Phase 1 — Detector Evaluation")
        tabs = st.tabs(list(detector_reports.keys()))

        for tab, (name, report) in zip(tabs, detector_reports.items()):
            with tab:
                metrics = report.get("metrics", {})
                ground_truth = report.get("ground_truth", {})
                swarms = report.get("detected_swarms", [])

                st.caption(
                    f"Dataset: {report.get('dataset', name)} | "
                    f"Posts: {report.get('total_posts', 0)} | "
                    f"Accounts: {report.get('total_accounts', 0)}"
                )

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    metric_card("Precision", f"{metrics.get('precision', 0):.1%}")
                with col2:
                    metric_card("Recall", f"{metrics.get('recall', 0):.1%}")
                with col3:
                    metric_card("F1 Score", f"{metrics.get('f1', 0):.1%}")
                with col4:
                    metric_card("Accuracy", f"{metrics.get('accuracy', 0):.1%}")

                fp = metrics.get("FP", 0)
                tn = metrics.get("TN", 0)
                fpr = fp / (fp + tn) if (fp + tn) else 0
                st.metric("False-positive rate", f"{fpr:.1%}")

                st.markdown("#### Confusion Matrix")
                confusion = pd.DataFrame(
                    [
                        [metrics.get("TN", 0), metrics.get("FP", 0)],
                        [metrics.get("FN", 0), metrics.get("TP", 0)],
                    ],
                    index=["Actual organic", "Actual coordinated"],
                    columns=["Predicted organic", "Predicted coordinated"],
                )
                st.dataframe(confusion, use_container_width=True)

                col1, col2, col3, col4 = st.columns(4)
                col1.metric("True Positives", metrics.get("TP", 0))
                col2.metric("False Positives", metrics.get("FP", 0))
                col3.metric("False Negatives", metrics.get("FN", 0))
                col4.metric("True Negatives", metrics.get("TN", 0))

                st.markdown("#### Detected Accounts")
                predicted = report.get("predicted_coordinated_accounts", [])
                st.write(
                    ", ".join(predicted)
                    if predicted
                    else "No coordinated accounts detected."
                )

                st.markdown("#### Detected Swarms")
                for swarm in swarms:
                    with st.expander(
                        f"{swarm.get('id', 'Swarm')} "
                        f"— Score {swarm.get('score', 0):.3f}"
                    ):
                        st.write("Accounts:", swarm.get("accounts", []))
                        st.write(
                            "Evidence pairs:",
                            len(swarm.get("evidence", [])),
                        )

                st.caption(
                    f"Ground truth: "
                    f"{len(ground_truth.get('coordinated_accounts', []))} "
                    f"coordinated accounts and "
                    f"{len(ground_truth.get('organic_accounts', []))} "
                    f"organic accounts."
                )

    if "AI Evaluation" in loaded:
        report = loaded["AI Evaluation"]
        st.divider()
        st.markdown("### Phase 2 — AI Evaluation")

        nemotron = report.get("nemotron", {})
        gemini = report.get("gemini", {})

        st.markdown("#### Nemotron — Post Classification")
        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card(
                "Evaluated Posts",
                nemotron.get("evaluated_posts", 0),
            )
        with col2:
            metric_card(
                "False Positive Rate",
                f"{nemotron.get('false_positive_rate', 0):.1%}",
            )
        with col3:
            metric_card(
                "Missing Posts",
                len(nemotron.get("missing_posts", [])),
            )

        st.write(
            "**Precision / Recall / F1:**",
            nemotron.get("precision_recall_f1", "Not available"),
        )
        st.write(
            "**False-positive posts:**",
            nemotron.get("false_positive_posts", []),
        )

        predictions = nemotron.get("predictions", {})
        if predictions:
            prediction_rows = []
            for post_id, prediction in predictions.items():
                prediction_rows.append({
                    "Post ID": post_id,
                    "Expected": ", ".join(prediction.get("expected", [])) or "None",
                    "Predicted": ", ".join(prediction.get("predicted", [])) or "None",
                    "Correct": prediction.get("correct", False),
                    "AI Confidence": prediction.get("ai_confidence"),
                    "Explanation": prediction.get("explanation", ""),
                })
            st.dataframe(
                pd.DataFrame(prediction_rows),
                use_container_width=True,
                hide_index=True,
            )

        st.caption(
            "All reviewed Nemotron labels are negative. "
            "Therefore, precision, recall and F1 are not meaningful. "
            "The false-positive rate is measured across "
            f"{nemotron.get('total_binary_decisions', 0)} "
            "binary technique decisions."
        )

        st.divider()
        st.markdown("#### Gemini — Swarm Analysis")
        st.write(
            "**Detected swarms evaluated:**",
            gemini.get("number_of_detected_swarms", 0),
        )

        for result in gemini.get("results", []):
            with st.expander(
                f"{result.get('swarm_id', 'Swarm')} — "
                f"{result.get('status', 'unknown')}",
                expanded=True,
            ):
                col1, col2, col3 = st.columns(3)
                col1.metric(
                    "Precision",
                    f"{result.get('metrics', {}).get('precision', 0):.1%}",
                )
                col2.metric(
                    "Recall",
                    f"{result.get('metrics', {}).get('recall', 0):.1%}",
                )
                col3.metric(
                    "F1 Score",
                    f"{result.get('metrics', {}).get('f1', 0):.1%}",
                )
                st.write("**Accounts:**", result.get("accounts", []))
                st.write("**Expected techniques:**", result.get("expected", []))
                st.write("**Predicted techniques:**", result.get("predicted", []))
                st.write(
                    "**Coordination assessment:**",
                    result.get("coordination_assessment", "Unavailable"),
                )
                st.write(
                    "**Confidence:**",
                    f"{result.get('confidence', 0):.0%}",
                )
                st.write(
                    "**Malicious intent established:**",
                    result.get("malicious_intent_established", False),
                )
                st.write("**Explanation:**", result.get("explanation", ""))

        st.warning(
            gemini.get(
                "note",
                "Gemini evaluation uses a limited synthetic dataset.",
            )
        )

    st.caption(
        "These are synthetic benchmark results, not proof of "
        "real-world detection accuracy. Coordination does not "
        "establish malicious intent."
    )
