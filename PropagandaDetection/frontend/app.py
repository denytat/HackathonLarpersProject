
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="SWARMWATCH",
    page_icon="🔍",
    layout="wide"
)

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
    df = pd.read_csv(uploaded_file)

    st.success("CSV uploaded successfully!")

    st.metric("Total posts", len(df))

    st.subheader("Uploaded posts")
    st.dataframe(df.head(20))

    if st.button("Analyze Posts"):
        st.info(
            "Frontend is ready. "
            "Waiting for Roman's /analyze API connection."
        )

st.divider()

st.subheader("Evaluation Metrics")
st.info("Evaluation results will appear here.")
