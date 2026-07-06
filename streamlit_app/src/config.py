import os
import sys

VERSION = "2.0.0"
APP_NAME = "JERNIH OS"
TAGLINE = "AI Civic Operating System — Informasi yang Terang, Bukan yang Bising"

def _get_secret(primary: str, *fallbacks: str) -> str:
    for key in (primary, *fallbacks):
        val = os.environ.get(key, "")
        if val:
            return val
    try:
        import streamlit as st
        for key in (primary, *fallbacks):
            try:
                return st.secrets[key]
            except Exception:
                continue
    except Exception:
        pass
    return ""

OPENROUTER_KEY = _get_secret("OPENAI_API_KEY", "OPENROUTER_KEY", "OPENROUTER_API_KEY")
GEMINI_API_KEY = _get_secret("GEMINI_API_KEY")
HAS_AI_API = bool(OPENROUTER_KEY)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

AI_MODEL = "google/gemini-2.0-flash-exp:free"
AI_VISION_MODEL = "google/gemini-2.0-flash-exp:free"

AI_TIMEOUT = 45.0
AI_MAX_TOKENS = 2048
AI_TEMPERATURE = 0.4
AI_RETRY_MAX = 3

SITE_URL = "https://jernih.app"
SITE_TITLE = "JERNIH OS"
