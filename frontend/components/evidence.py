"""Evidence, swarm, and post result rendering."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.metrics import metric_card, section_title, show_badge


def technique_name(item) -> str:
    if isinstance(item, dict):
        return item.get("name", "")
    return str(item)


def display_swarm(swarm: dict) -> None:
    swarm_id = swarm.get("id", "Unknown swarm")
    score = float(swarm.get("score", 0))
    ai = swarm.get("ai_analysis") or {}
    verdict = ai.get("verdict", "Not assessed")

    with st.expander(
        f"{swarm_id} | Score {score:.2f} | {verdict}",
        expanded=True,
    ):
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("#### Connected Accounts")
            accounts = swarm.get("accounts") or []
            for account in accounts:
                show_badge(account)

        with col2:
            st.markdown("#### Detection Score")
            st.metric("Coordination score", f"{score:.2f}")

        st.markdown("#### Coordination Evidence")
        evidence = swarm.get("evidence") or []

        if evidence:
            evidence_rows = []
            for edge in evidence:
                if isinstance(edge, str):
                    evidence_rows.append({
                        "Account A": "",
                        "Account B": "",
                        "Score": "",
                        "Signals": edge,
                    })
                    continue

                signals = edge.get("signals") or {}
                if isinstance(signals, dict):
                    signal_text = ", ".join(
                        f"{k}: {v}" for k, v in signals.items()
                    )
                else:
                    signal_text = str(signals)

                evidence_rows.append({
                    "Account A": edge.get("account_1", ""),
                    "Account B": edge.get("account_2", ""),
                    "Score": edge.get("score", 0),
                    "Signals": signal_text,
                })

            st.dataframe(
                pd.DataFrame(evidence_rows),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No evidence edges available.")

        section_title("AI Investigation")

        if not ai:
            st.info("AI analysis is disabled or unavailable.")
            return

        st.write("**Combined verdict:**", verdict)
        st.write("**Verdict explanation:**", ai.get("explanation", ""))

        gemini = ai.get("gemini")
        if not gemini:
            st.warning("Gemini analysis is unavailable.")
            return

        st.markdown("#### Gemini Intelligence Summary")
        st.markdown("**Shared narrative**")
        st.write(gemini.get("narrative", "Not available"))

        st.markdown("**Coordination assessment**")
        st.write(
            gemini.get("coordination_assessment", "Not available")
        )

        confidence = gemini.get("confidence")
        if confidence is not None:
            confidence = max(0.0, min(1.0, float(confidence)))
            st.write(f"**Gemini confidence estimate:** {confidence:.0%}")
            st.progress(confidence)

        st.markdown("**Potential manipulation techniques**")
        techniques = gemini.get("techniques") or []
        if techniques:
            for technique in techniques:
                show_badge(str(technique))
        else:
            st.info(
                "No manipulation techniques identified "
                "from the available evidence."
            )

        st.markdown("**Analyst explanation**")
        st.write(gemini.get("explanation", ""))

        context = gemini.get("external_context") or []
        if context:
            with st.expander("External Context"):
                for item in context:
                    st.write(item)

        st.caption(
            "Coordination indicators do not establish "
            "malicious intent. AI assessments require "
            "human review."
        )


def display_post_analysis(post_results: list) -> None:
    if not post_results:
        st.info("No post results available.")
        return

    rows = []
    for post in post_results:
        ai = post.get("ai_analysis") or {}
        techniques = [
            technique_name(item)
            for item in (post.get("techniques") or [])
        ]
        rows.append({
            "Post ID": post.get("id", ""),
            "Phase 1 Verdict": post.get("verdict", "uncertain"),
            "Detection Score": post.get("confidence", 0),
            "Flagged By": ", ".join(post.get("flagged_by") or []),
            "Techniques": (
                ", ".join(techniques) if techniques else "None identified"
            ),
            "Nemotron Status": ai.get("status", "Not available"),
            "Nemotron Confidence": ai.get("confidence"),
            "Nemotron Explanation": ai.get("explanation", ""),
        })

    results_df = pd.DataFrame(rows)

    search = st.text_input(
        "Search posts",
        placeholder="Search by post ID or technique...",
        key="post_search",
    )

    if search:
        mask = results_df.astype(str).apply(
            lambda column: column.str.contains(
                search, case=False, regex=False
            )
        ).any(axis=1)
        filtered_df = results_df[mask]
    else:
        filtered_df = results_df

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download Post Results CSV",
        data=results_df.to_csv(index=False).encode("utf-8"),
        file_name="swarmwatch_post_results.csv",
        mime="text/csv",
        key="download_post_results",
    )

    st.markdown("#### Individual Post Details")

    show_all = st.checkbox(
        "Show details for all posts",
        value=False,
        key="show_all_posts",
    )

    if show_all:
        visible_posts = post_results
    else:
        visible_posts = [
            post for post in post_results
            if post.get("flagged_by") or post.get("techniques")
        ]

    if not visible_posts:
        st.info(
            "No posts were flagged. Enable "
            "'Show details for all posts' to inspect "
            "individual results."
        )

    for post in visible_posts:
        post_id = post.get("id", "Unknown")
        with st.expander(f"Post {post_id}"):
            st.write("**Phase 1 verdict:**", post.get("verdict", "uncertain"))
            st.write("**Detection score:**", post.get("confidence", 0))
            st.write("**Flagged by:**", post.get("flagged_by", []))

            ai = post.get("ai_analysis")
            if ai:
                st.write("**Nemotron confidence:**", ai.get("confidence"))
                st.write(
                    "**Nemotron explanation:**",
                    ai.get("explanation", ""),
                )
            else:
                st.info("Nemotron analysis unavailable.")

            techniques = post.get("techniques") or []
            if techniques:
                for technique in techniques:
                    if isinstance(technique, dict):
                        st.markdown(
                            f"**Technique:** {technique.get('name', '')}"
                        )
                        st.write(
                            "**Evidence span:**",
                            technique.get("span", ""),
                        )
                        st.write(
                            "**Explanation:**",
                            technique.get("explanation", ""),
                        )
                    else:
                        st.markdown(f"**Technique:** {technique}")
            else:
                st.write("No manipulation techniques identified.")


def display_labeled_evaluation(
    df: pd.DataFrame,
    mapping: dict,
    post_results: list,
) -> None:
    section_title(
        "Evaluation Metrics",
        "Performance against labeled coordination examples.",
    )

    label_column = next(
        (
            column for column in df.columns
            if str(column).strip().lower() == "is_coordinated"
        ),
        None,
    )

    if label_column is None:
        st.info(
            "Upload a labeled CSV containing an "
            "'is_coordinated' column to calculate "
            "precision, recall, F1 and accuracy."
        )
        return

    labels = {}
    for index, row in df.iterrows():
        raw_id = row[mapping["id"]]
        post_id = (
            f"post_{index}" if pd.isna(raw_id) else str(raw_id)
        )
        raw_label = str(row[label_column]).strip()

        if raw_label not in ("0", "1"):
            st.warning(
                f"Invalid ground-truth label for {post_id}. "
                "Labels must be 0 or 1."
            )
            return

        if post_id in labels:
            st.warning(
                "Duplicate post IDs found. "
                "Evaluation requires unique IDs."
            )
            return

        labels[post_id] = int(raw_label)

    tp = tn = fp = fn = 0
    evaluated_ids: set[str] = set()

    for post in post_results:
        post_id = str(post.get("id", ""))
        if post_id not in labels:
            st.warning(f"No ground-truth label for post {post_id}.")
            return
        if post_id in evaluated_ids:
            st.warning("Duplicate post IDs returned by backend.")
            return

        evaluated_ids.add(post_id)
        actual = labels[post_id]
        predicted = int(bool(post.get("flagged_by")))

        if actual == 1 and predicted == 1:
            tp += 1
        elif actual == 0 and predicted == 0:
            tn += 1
        elif actual == 0 and predicted == 1:
            fp += 1
        else:
            fn += 1

    total = tp + tn + fp + fn
    if total == 0:
        st.info("No posts available for evaluation.")
        return

    if len(evaluated_ids) != len(labels):
        st.warning(
            "The backend did not return all labeled posts. "
            "Metrics below cover returned posts only."
        )

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0
    )
    accuracy = (tp + tn) / total

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("Precision", f"{precision:.1%}")
    with col2:
        metric_card("Recall", f"{recall:.1%}")
    with col3:
        metric_card("F1 Score", f"{f1:.1%}")
    with col4:
        metric_card("Accuracy", f"{accuracy:.1%}")

    st.markdown("#### Confusion Matrix")
    confusion = pd.DataFrame(
        [[tn, fp], [fn, tp]],
        index=["Actual: Not coordinated", "Actual: Coordinated"],
        columns=["Predicted: Not coordinated", "Predicted: Coordinated"],
    )
    st.dataframe(confusion, use_container_width=True)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("True Positives", tp)
    col2.metric("True Negatives", tn)
    col3.metric("False Positives", fp)
    col4.metric("False Negatives", fn)

    st.caption(
        f"Evaluated {total} posts. "
        "These metrics measure post-level coordination "
        "detection, not malicious intent or AI accuracy. "
        "Synthetic evaluation results do not establish "
        "real-world performance."
    )
