"""JERNIH OS — AI Civic Operating System"""

import streamlit as st

st.set_page_config(
    page_title="JERNIH OS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.pages import main

if __name__ == "__main__":
    main()
