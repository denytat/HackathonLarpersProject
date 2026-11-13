
import os
import json
import httpx
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Swarmwatch", layout="wide")
st.title("Swarmwatch")
st.caption("Detect coordinated inauthentic behaviour and manipulation techniques.")

uploaded = st.file_uploader("Upload posts (CSV or JSON)", type=["csv", "json"])

posts = None
if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
        posts = df.to_dict(orient="records")
    else:
        posts = json.load(uploaded)["posts"]
    st.write(f"Loaded {len(posts)} posts")
    st.dataframe(pd.DataFrame(posts).head(20))

if st.button("Analyze", disabled=not posts):
    with st.spinner("Analyzing..."):
        try:
            r = httpx.post(f"{API_URL}/analyze",
                           json={"posts": posts}, timeout=120)
            r.raise_for_status()
            st.session_state["result"] = r.json()
        except Exception as e:
            st.error(f"API error: {e}")

result = st.session_state.get("result")
if result:
    st.subheader("Suspected swarms")
    for s in result["swarms"]:
        with st.expander(f"{s['id']}  score {s['score']:.2f}"):
            st.write(", ".join(s["accounts"]))
            for ev in s["evidence"]:
                st.write(f"- {ev}")
    st.subheader("Posts")
    st.dataframe(pd.DataFrame(result["posts"]))