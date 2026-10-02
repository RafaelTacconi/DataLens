"""Streamlit app shell (R13).

The entry point of the application. It renders the chat view and wires the
views together. No LLM call or database execution happens in the normal script
body (SDD §33): pipeline stages run only from explicit submit events, and
rendering reads stored state only.
"""

import streamlit as st

st.set_page_config(page_title="DataLens", layout="wide")
st.title("DataLens — Natural-Language SQLite Data Analyst")
st.caption("Ask a question about your SQLite data.")