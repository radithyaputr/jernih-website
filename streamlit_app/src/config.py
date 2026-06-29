import os
import streamlit as st

VERSION = "2.0.0"
APP_NAME = "JERNIH OS"
TAGLINE = "AI Civic Operating System — Informasi yang Terang, Bukan yang Bising"

OPENROUTER_KEY = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
HAS_AI_API = bool(OPENROUTER_KEY)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "openai/gpt-4o-mini"
AI_TIMEOUT = 15.0
AI_MAX_TOKENS = 2000
AI_TEMPERATURE = 0.4
AI_RETRY_MAX = 2

SITE_URL = "https://jernih.app"
SITE_TITLE = "JERNIH OS"
