"""AI service for JERNIH OS — OpenRouter integration (OpenAI-compatible)."""

import json
import re
import time
from datetime import datetime
from typing import Optional
from app.core.config import settings
import httpx

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OPENROUTER_KEY = settings.openai_api_key   # sk-or-v1-...
HAS_AI_API = bool(OPENROUTER_KEY)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Sekarang pakai 2048 token dengan JSON yang lebih ringkas
AI_MODEL = "openai/gpt-4o-mini"


# ---------------------------------------------------------------------------
# System prompt — with INTENT DETECTION (casual vs analysis)
# ---------------------------------------------------------------------------
CITIZEN_SYSTEM_PROMPT = f"Anda adalah AI Civic Assistant JERNIH OS untuk Indonesia. Waktu saat ini adalah {datetime.now().strftime('%d %B %Y')}. Presiden Indonesia saat ini adalah Prabowo Subianto.\n" + """
WAJIB: Balas HANYA dengan JSON valid. Mulai langsung dengan { tanpa teks apapun di luar JSON.

## ATURAN DETEKSI INTENT:

1. Jika user menyapa, berterima kasih, atau ngobrol santai (contoh: "halo", "hi", "terima kasih", "apa kabar", "siapa kamu", "test"), balas dengan format CASUAL:
{"type":"casual","message":"balasan ramah dan natural dalam Bahasa Indonesia"}

2. Jika user menyampaikan keluhan, masalah, kasus, atau pertanyaan seputar layanan publik/pemerintah, balas dengan format ANALYSIS:
{"type":"analysis","summary":"ringkasan 1 kalimat spesifik","analysis":"analisis 2-3 kalimat","relevant_programs":[{"name":"nama","agency":"instansi","description":"deskripsi singkat","match_score":85,"url":"https://..."}],"required_documents":[{"name":"nama","description":"keterangan","priority":"high"}],"risk_factors":[{"risk":"risiko","severity":"medium","mitigation":"solusi"}],"timeline":{"estimated_days":14,"steps":[{"step":1,"action":"langkah konkret","duration":"1 hari","office":"kantor tujuan"}]},"action_plan":{"today":["langkah hari ini"],"this_week":["langkah minggu ini"],"next_step":["langkah berikutnya"]},"success_probability":75}

Gunakan data nyata pemerintah Indonesia. Jawab SPESIFIK sesuai situasi warga."""


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_json(text: str) -> dict:
    """Extract first valid JSON object from text, handles markdown fences."""
    text = re.sub(r"```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```", "", text)
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Brace-matching fallback
    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                try:
                    return json.loads(text[start : i + 1])
                except json.JSONDecodeError:
                    depth = 0
                    start = None
    return {}


def _validate_analysis(result: dict) -> bool:
    """Validate that an analysis-type response has all required fields."""
    required = ["summary", "analysis", "relevant_programs", "required_documents",
                 "risk_factors", "timeline", "action_plan", "success_probability"]
    if not all(k in result for k in required):
        return False
    result["timeline"].setdefault("steps", [])
    result["timeline"].setdefault("estimated_days", 14)
    result["action_plan"].setdefault("today", [])
    result["action_plan"].setdefault("this_week", [])
    result["action_plan"].setdefault("next_step", [])
    return True


def _validate_casual(result: dict) -> bool:
    """Validate that a casual-type response has the required message field."""
    return "message" in result and isinstance(result["message"], str) and len(result["message"]) > 0


# ---------------------------------------------------------------------------
# Main AI function
# ---------------------------------------------------------------------------

def analyze_with_ai(message: str) -> Optional[dict]:
    """Call OpenRouter and return parsed JSON dict, or None to trigger fallback.

    Returns dict with "type" key:
      - {"type": "casual", "message": "..."} for greetings/casual chat
      - {"type": "analysis", ...full fields...} for civic analysis
      - None to trigger rule-based fallback
    """
    if not HAS_AI_API:
        print("[WARNING] No OPENAI_API_KEY set — using rule-based fallback")
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jernih.app",
        "X-Title": "JERNIH OS",
    }

    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": CITIZEN_SYSTEM_PROMPT},
            {"role": "user", "content": f"Pertanyaan warga: {message}"},
        ],
        "temperature": 0.4,
        "max_tokens": 2000,
    }

    for attempt in range(2):
        try:
            with httpx.Client(timeout=15.0) as http:
                resp = http.post(OPENROUTER_URL, headers=headers, json=payload)

            # Auth errors — don't retry
            if resp.status_code in (401, 403):
                print(f"[ERROR] OpenRouter auth error {resp.status_code}: {resp.text[:200]}")
                return None

            # Payment required — switch to free model
            if resp.status_code == 402:
                print("[WARNING] 402 Payment Required — switching to free model")
                payload["model"] = "google/gemma-2-9b-it:free"
                continue

            # Rate limit — fail fast to rule-based instead of hanging for 45s
            if resp.status_code == 429:
                print(f"[WARNING] Rate limited (429). Falling back to rule-based logic instantly.")
                return None

            if resp.status_code != 200:
                print(f"[WARNING] HTTP {resp.status_code}: {resp.text[:200]}")
                return None

            data = resp.json()
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")

            if not raw.strip():
                return None

            print(f"[INFO] AI raw (first 150 chars): {repr(raw[:150])}")

            result = _extract_json(raw)
            if not result:
                # If JSON is incomplete (token cutoff), try to recover
                print(f"[WARNING] JSON incomplete, attempting repair…")
                repaired = raw.strip()
                open_braces = repaired.count("{") - repaired.count("}")
                open_brackets = repaired.count("[") - repaired.count("]")
                repaired += "]" * max(0, open_brackets) + "}" * max(0, open_braces)
                result = _extract_json(repaired)
                if not result:
                    raise ValueError(f"JSON parse failed. Raw: {raw[:300]}")

            # Check response type
            resp_type = result.get("type", "analysis")

            if resp_type == "casual" and _validate_casual(result):
                print(f"[INFO] AI casual response served (model: {payload['model']})")
                return {"type": "casual", "message": result["message"]}

            # For analysis type, strip the "type" key and validate
            result.pop("type", None)
            if _validate_analysis(result):
                result["type"] = "analysis"
                print(f"[INFO] AI analysis response served (model: {payload['model']})")
                return result

            # Missing fields
            print(f"[WARNING] Missing fields: {[k for k in ['summary','analysis','relevant_programs','required_documents','risk_factors','timeline','action_plan','success_probability'] if k not in result]}")
            raise ValueError(f"Response missing required fields: {list(result.keys())}")

        except httpx.TimeoutException:
            print(f"[WARNING] Timeout attempt {attempt+1}/3")
            time.sleep(3)
        except Exception as e:
            err = str(e)
            if attempt < 2:
                wait = 2 ** attempt
                print(f"[WARNING] Error attempt {attempt+1}/3: {err[:120]} — retrying in {wait}s…")
                time.sleep(wait)
            else:
                print(f"[ERROR] AI failed after 3 attempts: {err[:120]}")

    return None

def ask_ai_json(system_prompt: str, user_prompt: str) -> Optional[dict]:
    """Generic AI JSON caller for other features (Action Plan, Hoax Checker)."""
    if not HAS_AI_API:
        return None

    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://jernih.app",
        "X-Title": "JERNIH OS",
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 2000,
    }

    for attempt in range(2):
        try:
            with httpx.Client(timeout=15.0) as http:
                resp = http.post(OPENROUTER_URL, headers=headers, json=payload)

            if resp.status_code in (401, 403, 429):
                return None
            if resp.status_code == 402:
                payload["model"] = "google/gemma-2-9b-it:free"
                continue
            if resp.status_code != 200:
                return None

            data = resp.json()
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not raw.strip():
                return None
            
            result = _extract_json(raw)
            if not result:
                repaired = raw.strip()
                open_braces = repaired.count("{") - repaired.count("}")
                open_brackets = repaired.count("[") - repaired.count("]")
                repaired += "]" * max(0, open_brackets) + "}" * max(0, open_braces)
                result = _extract_json(repaired)
            return result
        except httpx.TimeoutException:
            pass
        except Exception:
            pass
    return None
