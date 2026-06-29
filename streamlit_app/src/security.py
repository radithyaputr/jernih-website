import re
import html

def sanitize_input(text: str, max_length: int = 5000) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.strip()[:max_length]
    text = html.escape(text, quote=True)
    text = re.sub(r'<[^>]*>', '', text)
    return text

def sanitize_html(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = html.escape(text, quote=True)
    return text

def detect_prompt_injection(text: str) -> bool:
    patterns = [
        r'ignor(e|ing).*(previous|above|system|instruction)',
        r'forget.*(previous|all|instruction)',
        r'you\s+are\s+(not|now)',
        r'act\s+as\s+',
        r'override',
        r'new\s+instruction',
        r'disregard',
    ]
    text_lower = text.lower()
    for pattern in patterns:
        if re.search(pattern, text_lower):
            return True
    return False

def validate_filename(name: str) -> str:
    return re.sub(r'[^\w\-_. ]', '', name)[:100]

def truncate_text(text: str, max_chars: int = 3000) -> str:
    return text[:max_chars] if text and len(text) > max_chars else text
