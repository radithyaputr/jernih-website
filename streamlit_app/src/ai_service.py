import json
import re
import time
import httpx
from src.config import (
    OPENROUTER_KEY, HAS_AI_API, OPENROUTER_URL, AI_MODEL,
    AI_TIMEOUT, AI_MAX_TOKENS, AI_TEMPERATURE, AI_RETRY_MAX,
    SITE_URL, SITE_TITLE
)

def _extract_json(text: str) -> dict:
    text = re.sub(r"```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?```", "", text)
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
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

def _repair_json(text: str) -> dict:
    repaired = text.strip()
    open_braces = repaired.count("{") - repaired.count("}")
    open_brackets = repaired.count("[") - repaired.count("]")
    repaired += "]" * max(0, open_brackets) + "}" * max(0, open_braces)
    return _extract_json(repaired)

def _build_headers() -> dict:
    return {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,
        "X-Title": SITE_TITLE,
    }

def _build_payload(messages: list, model: str = None) -> dict:
    return {
        "model": model or AI_MODEL,
        "messages": messages,
        "temperature": AI_TEMPERATURE,
        "max_tokens": AI_MAX_TOKENS,
    }

def _call_api(headers: dict, payload: dict) -> str | None:
    for attempt in range(AI_RETRY_MAX):
        try:
            with httpx.Client(timeout=AI_TIMEOUT) as http:
                resp = http.post(OPENROUTER_URL, headers=headers, json=payload)
            if resp.status_code in (401, 403):
                return None
            if resp.status_code == 429:
                time.sleep(3)
                continue
            if resp.status_code != 200:
                return None
            data = resp.json()
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if raw and raw.strip():
                return raw
            return None
        except httpx.TimeoutException:
            time.sleep(3)
        except Exception:
            if attempt < AI_RETRY_MAX - 1:
                time.sleep(2)
            else:
                return None
    return None

def chat_with_ai(system_prompt: str, user_message: str, history: list = None) -> dict | None:
    if not HAS_AI_API:
        return None
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        for h in history[-6:]:
            messages.append({"role": h["role"], "content": h["content"]})
    messages.append({"role": "user", "content": user_message})
    headers = _build_headers()
    payload = _build_payload(messages)
    raw = _call_api(headers, payload)
    if not raw:
        return None
    result = _extract_json(raw)
    if not result:
        result = _repair_json(raw)
    return result if result else None

def chat_with_images(system_prompt: str, text: str, images: list, model: str = None) -> dict | None:
    if not HAS_AI_API:
        return None
    content = [{"type": "text", "text": text}]
    for img_data in images:
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/{img_data['format']};base64,{img_data['base64']}"}
        })
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content},
    ]
    headers = _build_headers()
    payload = _build_payload(messages, model=model)
    raw = _call_api(headers, payload)
    if not raw:
        return None
    result = _extract_json(raw)
    if not result:
        result = _repair_json(raw)
    return result if result else None


def analyze_with_ai(message: str, history: list = None) -> dict | None:
    if not HAS_AI_API:
        return None
    from src.agents import CITIZEN_SYSTEM_PROMPT
    result = chat_with_ai(CITIZEN_SYSTEM_PROMPT, f"Pertanyaan warga: {message}", history)
    if not result:
        return None
    resp_type = result.get("type", "analysis")
    if resp_type == "casual":
        if "message" in result and isinstance(result["message"], str) and len(result["message"]) > 0:
            return {"type": "casual", "message": result["message"]}
        return None
    required = ["summary", "analysis", "relevant_programs", "required_documents",
                 "risk_factors", "timeline", "action_plan", "success_probability"]
    if not all(k in result for k in required):
        return None
    result["timeline"] = result.get("timeline", {})
    result["timeline"].setdefault("steps", [])
    result["timeline"].setdefault("estimated_days", 14)
    result["action_plan"] = result.get("action_plan", {})
    result["action_plan"].setdefault("today", [])
    result["action_plan"].setdefault("this_week", [])
    result["action_plan"].setdefault("next_step", [])
    result["type"] = "analysis"
    return result
