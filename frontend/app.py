import os
import streamlit as st
import pandas as pd
import requests

API_URL = f"{os.getenv('API_URL', 'http://127.0.0.1:8000').rstrip('/')}/analyze"

st.set_page_config(
    page_title="SWARMWATCH",
    page_icon="🔍",
    layout="wide"
)

# Possible column names for automatic detection
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
    """Automatically detect columns using known aliases."""
    detected = {}

    normalized_columns = {
        str(column).strip().lower(): column
        for column in columns
    }

    for field, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized_columns:
                detected[field] = normalized_columns[alias]
                break

    return detected


st.title("🔍 SWARMWATCH")
st.subheader("Coordinated Manipulation Detection")

st.write(
    "Upload social media posts to analyze "
    "potential coordinated activity."
)

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        df = pd.read_csv(uploaded_file)

        if df.empty:
            st.error("The uploaded CSV is empty.")
            st.stop()

        st.success("CSV uploaded successfully!")

        st.metric("Total posts", len(df))

        st.subheader("Uploaded posts")
        st.dataframe(df.head(20), use_container_width=True)

        detected = detect_columns(df.columns)

        st.subheader("Column mapping")

        st.write(
            "Swarmwatch tries to recognize your dataset columns "
            "automatically. Check the detected mappings below."
        )

        available_columns = ["-- Select column --"] + list(df.columns)

        mapping = {}

        for field in ["id", "account", "text", "timestamp"]:

            default_column = detected.get(field)

            default_index = (
                available_columns.index(default_column)
                if default_column in available_columns
                else 0
            )

            mapping[field] = st.selectbox(
                f"Select column for {field}",
                available_columns,
                index=default_index,
                key=f"mapping_{field}"
            )

        if st.button("Analyze Posts", type="primary"):

            missing = [
                field for field, column in mapping.items()
                if column == "-- Select column --"
            ]

            if missing:
                st.error(
                    f"Please select columns for: {missing}"
                )

            else:
                posts = []

                for index, row in df.iterrows():

                    post_id = row[mapping["id"]]
                    account = row[mapping["account"]]
                    content = row[mapping["text"]]
                    timestamp = row[mapping["timestamp"]]

                    if pd.isna(account) or pd.isna(content) or pd.isna(timestamp):
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
                    st.error("No valid posts found in the dataset.")

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

                            result = response.json()

                            st.success(
                                "Analysis completed successfully!"
                            )

                            st.subheader("Detected Swarms")

                            swarms = result.get("swarms", [])

                            if swarms:
                                for swarm in swarms:

                                    with st.expander(
                                        f"{swarm['id']} — Score: {swarm['score']}"
                                    ):
                                        st.write("Accounts:")
                                        st.write(swarm["accounts"])

                                        st.write("Evidence:")
                                        st.json(swarm["evidence"])

                            else:
                                st.info("No potential swarms detected.")

                            st.subheader("Post Analysis")

                            post_results = result.get("posts", [])

                            if post_results:
                                st.dataframe(
                                    pd.DataFrame(post_results),
                                    use_container_width=True
                                )

                            st.subheader("Complete API Response")
                            st.json(result)

                        else:
                            st.error(
                                f"Backend error: {response.status_code}"
                            )
                            st.code(response.text)

                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to the backend.")

                    except requests.exceptions.Timeout:
                        st.error("Analysis timed out.")

                    except requests.exceptions.RequestException as error:
                        st.error(f"Request failed: {error}")

    except Exception as error:
        st.error(f"Could not read CSV: {error}")

st.divider()

st.subheader("Evaluation Metrics")
st.info("Evaluation results will appear here.")
