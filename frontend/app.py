import os
import streamlit as st

import html
import os

import pandas as pd
import requests
import streamlit as st

API_URL = f"{os.getenv('API_URL', 'http://127.0.0.1:8000').rstrip('/')}/analyze"

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000/analyze"
).rstrip("/")

if not API_URL.endswith("/analyze"):
    API_URL += "/analyze"

st.set_page_config(
    page_title="SWARMWATCH | Coordination Intelligence",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# DARK DASHBOARD THEME
# --------------------------------------------------

st.markdown(
    """
    <style>
    :root {
        color-scheme: dark;
    }

    .stApp {
        background: #0B1220;
        color: #E2E8F0;
    }

    [data-testid="stSidebar"] {
        background: #101B2D;
        border-right: 1px solid #253650;
    }

    [data-testid="stHeader"] {
        background: rgba(11, 18, 32, 0.92);
    }

    [data-testid="stToolbar"] {
        color: #CBD5E1;
    }

    h1, h2, h3 {
        color: #F8FAFC !important;
        letter-spacing: -0.02em;
    }

    p, label {
        color: #CBD5E1;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    div.stButton > button[kind="primary"] {
        background: #0284C7;
        color: white;
        border: 1px solid #38BDF8;
        border-radius: 10px;
        font-weight: 700;
    }

    div.stButton > button[kind="primary"]:hover {
        background: #0369A1;
        color: white;
    }

    [data-testid="stFileUploader"] {
        background: #101B2D;
        border: 1px solid #253650;
        border-radius: 12px;
        padding: 10px;
    }

    [data-testid="stExpander"] {
        background: #101B2D;
        border: 1px solid #253650;
        border-radius: 12px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #253650;
        border-radius: 10px;
    }

    .sw-header {
        padding: 24px 26px;
        border-radius: 16px;
        background: linear-gradient(
            120deg,
            #10243B 0%,
            #101B2D 60%,
            #152B40 100%
        );
        border: 1px solid #29445E;
        margin-bottom: 22px;
    }

    .sw-eyebrow {
        color: #38BDF8;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    .sw-title {
        color: #F8FAFC;
        font-size: 36px;
        font-weight: 800;
        margin: 8px 0 5px 0;
        letter-spacing: -1px;
    }

    .sw-description {
        color: #94A3B8;
        font-size: 14px;
        line-height: 1.7;
    }

    .sw-card {
        background: #142238;
        border: 1px solid #263B54;
        border-radius: 14px;
        padding: 20px;
        min-height: 125px;
        margin-bottom: 12px;
    }

    .sw-card-label {
        color: #94A3B8;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .sw-card-value {
        color: #F8FAFC;
        font-size: 33px;
        font-weight: 800;
        margin-top: 12px;
        line-height: 1.2;
    }

    .sw-card-note {
        color: #64748B;
        font-size: 11px;
        margin-top: 8px;
    }

    .sw-panel {
        background: #142238;
        border: 1px solid #263B54;
        border-radius: 12px;
        padding: 18px 20px;
        margin: 10px 0 18px 0;
    }

    .sw-section {
        color: #F8FAFC;
        font-size: 19px;
        font-weight: 750;
        padding: 10px 0;
        margin-top: 18px;
    }

    .sw-badge {
        display: inline-block;
        background: #17324A;
        color: #7DD3FC;
        border: 1px solid #24567A;
        padding: 5px 11px;
        border-radius: 100px;
        font-size: 12px;
        font-weight: 700;
        margin: 3px 4px 3px 0;
    }

    .sw-warning {
        color: #FCD34D;
        background: #3A2A16;
        border: 1px solid #78532A;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 10px 0;
    }

    .sw-muted {
        color: #94A3B8;
        font-size: 13px;
        line-height: 1.6;
    }

    .sw-footer {
        text-align: center;
        color: #64748B;
        font-size: 12px;
        padding: 20px;
        border-top: 1px solid #253650;
        margin-top: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# DATASET COLUMN DETECTION
# --------------------------------------------------

COLUMN_ALIASES = {
    "id": [
        "id", "post_id", "tweet_id", "external_author_id",
        "status_id", "message_id"
    ],
    "account": [
        "account", "author", "username", "user",
        "screen_name", "account_name", "user_id"
    ],
    "text": [
        "text", "content", "message", "post",
        "tweet", "body", "description"
    ],
    "timestamp": [
        "timestamp", "publish_date", "created_at",
        "date", "time", "posted_at"
    ]
}


def detect_columns(columns):
    detected = {}

    normalized = {
        str(column).strip().lower(): column
        for column in columns
    }

    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                detected[field] = normalized[alias]
                break

    return detected


# --------------------------------------------------
# REUSABLE DASHBOARD COMPONENTS
# --------------------------------------------------

def safe(value):
    """Escape dynamic text before inserting into HTML."""
    return html.escape(str(value), quote=True)


def metric_card(label, value, note=""):
    st.markdown(
        f"""
        <div class="sw-card">
            <div class="sw-card-label">{safe(label)}</div>
            <div class="sw-card-value">{safe(value)}</div>
            <div class="sw-card-note">{safe(note)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def section_title(title, subtitle=None):
    st.markdown(
        f'<div class="sw-section">{safe(title)}</div>',
        unsafe_allow_html=True
    )

    if subtitle:
        st.caption(subtitle)


def show_badge(text):
    st.markdown(
        f'<span class="sw-badge">{safe(text)}</span>',
        unsafe_allow_html=True
    )


# --------------------------------------------------
# SWARM INVESTIGATION
# --------------------------------------------------

def display_swarm(swarm):
    swarm_id = swarm.get("id", "Unknown swarm")
    score = float(swarm.get("score", 0))

    ai = swarm.get("ai_analysis") or {}
    verdict = ai.get("verdict", "Not assessed")

    with st.expander(
        f"🔗 {swarm_id} | Score {score:.2f} | {verdict}",
        expanded=True
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
                signals = edge.get("signals") or {}

                evidence_rows.append({
                    "Account A": edge.get("account_1", ""),
                    "Account B": edge.get("account_2", ""),
                    "Score": edge.get("score", 0),
                    "Signals": ", ".join(signals.keys())
                })

            st.dataframe(
                pd.DataFrame(evidence_rows),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No evidence edges available.")

        section_title("AI Investigation")

        if not ai:
            st.info("AI analysis is disabled or unavailable.")
            return

        st.write("**Combined verdict:**", verdict)

        st.write(
            "**Verdict explanation:**",
            ai.get("explanation", "")
        )

        gemini = ai.get("gemini")

        if not gemini:
            st.warning("Gemini analysis is unavailable.")
            return

        st.markdown("#### Gemini Intelligence Summary")

        st.markdown("**Shared narrative**")
        st.write(gemini.get("narrative", "Not available"))

        st.markdown("**Coordination assessment**")
        st.write(
            gemini.get(
                "coordination_assessment",
                "Not available"
            )
        )

        confidence = gemini.get("confidence")

        if confidence is not None:
            confidence = max(
                0.0,
                min(1.0, float(confidence))
            )

            st.write(
                f"**Gemini confidence estimate:** "
                f"{confidence:.0%}"
            )

            st.progress(confidence)

        st.markdown("**Potential manipulation techniques**")

        techniques = gemini.get("techniques") or []

        if techniques:
            for technique in techniques:
                show_badge(technique)
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


# --------------------------------------------------
# POST EXPLORER
# --------------------------------------------------

def display_post_analysis(post_results):
    if not post_results:
        st.info("No post results available.")
        return

    rows = []

    for post in post_results:
        ai = post.get("ai_analysis") or {}

        techniques = [
            item.get("name", "")
            for item in (post.get("techniques") or [])
        ]

        rows.append({
            "Post ID": post.get("id", ""),
            "Phase 1 Verdict": post.get(
                "verdict",
                "uncertain"
            ),
            "Detection Score": post.get("confidence", 0),
            "Flagged By": ", ".join(
                post.get("flagged_by") or []
            ),
            "Techniques": (
                ", ".join(techniques)
                if techniques else "None identified"
            ),
            "Nemotron Status": ai.get(
                "status",
                "Not available"
            ),
            "Nemotron Confidence": ai.get("confidence"),
            "Nemotron Explanation": ai.get(
                "explanation",
                ""
            )
        })

    results_df = pd.DataFrame(rows)

    search = st.text_input(
        "Search posts",
        placeholder="Search by post ID or technique..."
    )

    if search:
        mask = results_df.astype(str).apply(
            lambda column: column.str.contains(
                search,
                case=False,
                regex=False
            )
        ).any(axis=1)

        filtered_df = results_df[mask]
    else:
        filtered_df = results_df

    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "⬇ Download Post Results CSV",
        data=results_df.to_csv(index=False).encode("utf-8"),
        file_name="swarmwatch_post_results.csv",
        mime="text/csv"
    )

    st.markdown("#### Individual Post Details")

    show_all = st.checkbox(
        "Show details for all posts",
        value=False
    )

    if show_all:
        visible_posts = post_results
    else:
        visible_posts = [
            post for post in post_results
            if post.get("flagged_by")
            or post.get("techniques")
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
            st.write(
                "**Phase 1 verdict:**",
                post.get("verdict", "uncertain")
            )

            st.write(
                "**Detection score:**",
                post.get("confidence", 0)
            )

            st.write(
                "**Flagged by:**",
                post.get("flagged_by", [])
            )

            ai = post.get("ai_analysis")

            if ai:
                st.write(
                    "**Nemotron confidence:**",
                    ai.get("confidence")
                )

                st.write(
                    "**Nemotron explanation:**",
                    ai.get("explanation", "")
                )
            else:
                st.info("Nemotron analysis unavailable.")

            techniques = post.get("techniques") or []

            if techniques:
                for technique in techniques:
                    st.markdown(
                        f"**Technique:** "
                        f"{technique.get('name', '')}"
                    )

                    st.write(
                        "**Evidence span:**",
                        technique.get("span", "")
                    )

                    st.write(
                        "**Explanation:**",
                        technique.get("explanation", "")
                    )
            else:
                st.write(
                    "No manipulation techniques identified."
                )


# --------------------------------------------------
# EVALUATION DASHBOARD
# --------------------------------------------------

def display_evaluation(df, mapping, post_results):
    section_title(
        "Evaluation Metrics",
        "Performance against labeled coordination examples."
    )

    label_column = next(
        (
            column for column in df.columns
            if str(column).strip().lower() == "is_coordinated"
        ),
        None
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
            f"post_{index}"
            if pd.isna(raw_id)
            else str(raw_id)
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

    # Compare only posts actually returned by the backend.
    # Swarm membership is the prediction, not Nemotron's
    # manipulation-technique classification.
    tp = tn = fp = fn = 0
    evaluated_ids = set()

    for post in post_results:
        post_id = str(post.get("id", ""))

        if post_id not in labels:
            st.warning(
                f"No ground-truth label for post {post_id}."
            )
            return

        if post_id in evaluated_ids:
            st.warning(
                "Duplicate post IDs returned by backend."
            )
            return

        evaluated_ids.add(post_id)

        actual = labels[post_id]

        predicted = int(
            bool(post.get("flagged_by"))
        )

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
        [
            [tn, fp],
            [fn, tp]
        ],
        index=[
            "Actual: Not coordinated",
            "Actual: Coordinated"
        ],
        columns=[
            "Predicted: Not coordinated",
            "Predicted: Coordinated"
        ]
    )

    st.dataframe(
        confusion,
        use_container_width=True
    )

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


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🔍 SWARMWATCH")
    st.caption("Coordination Intelligence Platform")

    st.divider()

    st.markdown("### Investigation Workflow")

    st.write("📁 Upload dataset")
    st.write("🔎 Detect coordinated activity")
    st.write("🧠 Review AI assessments")
    st.write("📊 Evaluate detection results")

    st.divider()

    st.markdown("### Analysis Engines")

    st.write("**Phase 1:** Coordination detection")
    st.write("**Nemotron:** Post classification")
    st.write("**Gemini:** Swarm interpretation")

    st.divider()

    st.caption(
        "Research and investigation support tool. "
        "Detected coordination is not proof of manipulation."
    )


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="sw-header">
        <div class="sw-eyebrow">
            Social Coordination Intelligence
        </div>
        <div class="sw-title">
            🔍 SWARMWATCH
        </div>
        <div class="sw-description">
            Detect potential coordinated social media activity,
            inspect supporting evidence, and review AI-assisted
            assessments in one investigation workspace.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# CSV UPLOAD
# --------------------------------------------------

section_title(
    "Dataset Upload",
    "Import a CSV containing social media posts."
)

uploaded_file = st.file_uploader(
    "Choose a CSV dataset",
    type=["csv"]
)


if uploaded_file is not None:

    try:
        # Keep identifiers as strings so large tweet IDs
        # are not converted to floating-point values.
        df = pd.read_csv(uploaded_file, dtype=str)

        if df.empty:
            st.error("The uploaded CSV is empty.")
            st.stop()

        st.success("Dataset uploaded successfully.")

        col1, col2 = st.columns([1, 3])

        with col1:
            metric_card(
                "Total Posts",
                len(df),
                "Rows in uploaded dataset"
            )

        with col2:
            st.markdown("#### Dataset Preview")

            st.dataframe(
                df.head(15),
                use_container_width=True,
                hide_index=True
            )

        section_title("Column Mapping")

        st.caption(
            "Check the automatically detected columns "
            "before running the analysis."
        )

        detected = detect_columns(df.columns)

        available_columns = (
            ["-- Select column --"] + list(df.columns)
        )

        mapping = {}

        columns = st.columns(4)

        for position, field in enumerate(
            ["id", "account", "text", "timestamp"]
        ):
            default_column = detected.get(field)

            default_index = (
                available_columns.index(default_column)
                if default_column in available_columns
                else 0
            )

            with columns[position]:
                mapping[field] = st.selectbox(
                    field.capitalize(),
                    available_columns,
                    index=default_index,
                    key=f"mapping_{field}"
                )

        st.divider()

        analyze_clicked = st.button(
            "🚀 Analyze Dataset",
            type="primary",
            use_container_width=True
        )

        # Preserve results when Streamlit reruns because
        # of search fields, checkboxes or expanders.
        file_signature = (
            uploaded_file.name,
            uploaded_file.size
        )

        if (
            st.session_state.get("file_signature")
            != file_signature
        ):
            st.session_state["file_signature"] = file_signature
            st.session_state.pop("analysis_result", None)
            st.session_state.pop("analysis_mapping", None)

        if analyze_clicked:
            st.session_state.pop("analysis_result", None)

            missing = [
                field
                for field, column in mapping.items()
                if column == "-- Select column --"
            ]

            if missing:
                st.error(
                    "Please select columns for: "
                    + ", ".join(missing)
                )

            else:
                posts = []

                for index, row in df.iterrows():
                    post_id = row[mapping["id"]]
                    account = row[mapping["account"]]
                    content = row[mapping["text"]]
                    timestamp = row[mapping["timestamp"]]

                    if (
                        pd.isna(account)
                        or pd.isna(content)
                        or pd.isna(timestamp)
                    ):
                        continue

                    if pd.isna(post_id):
                        post_id = f"post_{index}"

                    posts.append({
                        "id": str(post_id),
                        "account": str(account),
                        "text": str(content),
                        "timestamp": str(timestamp),
                        "reply_to": None,
                        "image_url": None
                    })

                if not posts:
                    st.error(
                        "No valid posts found in the dataset."
                    )

                else:
                    try:
                        with st.spinner(
                            f"Analyzing {len(posts)} posts..."
                        ):
                            response = requests.post(
                                API_URL,
                                json={"posts": posts},
                                timeout=120
                            )

                        if response.status_code == 200:
                            st.session_state[
                                "analysis_result"
                            ] = response.json()

                            st.session_state[
                                "analysis_mapping"
                            ] = mapping.copy()

                            st.success(
                                "Analysis completed successfully!"
                            )
                        else:
                            st.error(
                                "Backend error: "
                                f"{response.status_code}"
                            )

                            st.code(response.text)

                    except requests.exceptions.ConnectionError:
                        st.error(
                            "Cannot connect to FastAPI. "
                            "Check that the backend is running."
                        )

                    except requests.exceptions.Timeout:
                        st.error(
                            "Analysis timed out. "
                            "Try a smaller dataset."
                        )

                    except requests.exceptions.RequestException as error:
                        st.error(
                            f"Request failed: {error}"
                        )

        # --------------------------------------------------
        # ANALYSIS RESULTS
        # --------------------------------------------------

        result = st.session_state.get("analysis_result")

        if result is not None:
            swarms = result.get("swarms") or []
            post_results = result.get("posts") or []

            flagged_count = sum(
                1
                for post in post_results
                if post.get("flagged_by")
            )

            max_score = max(
                (
                    float(swarm.get("score", 0))
                    for swarm in swarms
                ),
                default=0.0
            )

            section_title(
                "Investigation Overview",
                "Summary of detected coordination patterns."
            )

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                metric_card(
                    "Posts Analyzed",
                    len(post_results),
                    "Processed by FastAPI"
                )

            with col2:
                metric_card(
                    "Potential Swarms",
                    len(swarms),
                    "Detected account groups"
                )

            with col3:
                metric_card(
                    "Flagged Posts",
                    flagged_count,
                    "Coordination indicators"
                )

            with col4:
                metric_card(
                    "Highest Swarm Score",
                    f"{max_score:.2f}",
                    "Detector score, not probability"
                )

            # ----------------------------------------------
            # SWARM RESULTS
            # ----------------------------------------------

            section_title(
                "Detected Swarms",
                "Explore account groups and supporting evidence."
            )

            if swarms:
                for swarm in swarms:
                    display_swarm(swarm)
            else:
                st.info(
                    "No potential swarms detected in "
                    "this dataset under the current rules."
                )

            # ----------------------------------------------
            # POST RESULTS
            # ----------------------------------------------

            section_title(
                "Post Explorer",
                "Inspect individual detection and Nemotron results."
            )

            display_post_analysis(post_results)

            # ----------------------------------------------
            # EVALUATION
            # ----------------------------------------------

            display_evaluation(
                df,
                st.session_state.get(
                    "analysis_mapping",
                    mapping
                ),
                post_results
            )

            # ----------------------------------------------
            # RAW RESPONSE
            # ----------------------------------------------

            with st.expander(
                "🔧 Developer Details — Raw API Response"
            ):
                st.json(result)

    except Exception as error:
        st.error(
            f"Could not process dataset: {error}"
        )

else:
    st.markdown(
        """
        <div class="sw-panel">
            <div class="sw-card-label">
                Ready for investigation
            </div>
            <p class="sw-muted">
                Upload a CSV to start analyzing potential
                coordinated social media activity.
                Supported fields include post ID, account,
                text and timestamp.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="sw-footer">
        SWARMWATCH · Coordination Intelligence Platform<br>
        AI-assisted assessments are not proof of malicious intent.
    </div>
    """,
    unsafe_allow_html=True
)
