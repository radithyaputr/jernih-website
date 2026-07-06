import re
from src.config import HAS_AI_API
from src.ai_service import chat_with_ai
from src.security import sanitize_input

CITIZEN_SYSTEM_PROMPT = """Anda adalah JERNIH, asisten AI Civic Copilot. Jawab pertanyaan warga dengan ramah, jelas, dan informatif.
Untuk pertanyaan umum (sapaan, definisi, fakta), jawab langsung menggunakan pengetahuan Anda.
Untuk pertanyaan tentang layanan publik, gunakan konteks yang tersedia jika ada.
JANGAN pernah kembalikan JSON untuk pertanyaan percakapan biasa - hanya kembalikan teks biasa yang natural."""

POLICY_EXPERT_PROMPT = CITIZEN_SYSTEM_PROMPT + "\n\nAnda adalah analis kebijakan publik yang ahli."
FACT_CHECKER_PROMPT = CITIZEN_SYSTEM_PROMPT + "\n\nAnda adalah pemeriksa fakta yang teliti."
DECISION_ENGINE_PROMPT = CITIZEN_SYSTEM_PROMPT + "\n\nAnda adalah mesin pengambil keputusan."
CLIMATE_EXPERT_PROMPT = CITIZEN_SYSTEM_PROMPT + "\n\nAnda adalah ahli lingkungan dan iklim."
LEGAL_ASSISTANT_PROMPT = CITIZEN_SYSTEM_PROMPT + "\n\nAnda adalah asisten hukum."
EMERGENCY_ASSISTANT_PROMPT = CITIZEN_SYSTEM_PROMPT + "\n\nAnda adalah asisten penanganan darurat."

def detect_intent(message: str) -> str:
    m = message.lower().strip()
    emergency_kw = ["darurat", "kecelakaan", "kebakaran", "gempa", "banjir", "longsor",
                    "tsunami", "ambulans", "polisi", "tolong", "emergency"]
    if any(kw in m for kw in emergency_kw):
        return "emergency"
    legal_kw = ["hukum", "undang-undang", "uu", "peraturan", "pasal", "pidana",
                 "perdata", "haki", "paten", "sengketa"]
    if any(kw in m for kw in legal_kw):
        return "legal"
    climate_kw = ["lingkungan", "iklim", "karbon", "polusi", "sampah", "daur ulang",
                   "green", "hijau", "energi", "limbah"]
    if any(kw in m for kw in climate_kw):
        return "climate"
    policy_kw = ["kebijakan", "peraturan", "undang-undang", "pp", "perpres",
                  "permendikbud", "permen", "regulasi"]
    if any(kw in m for kw in policy_kw):
        return "policy"
    decision_kw = ["keputusan", "pilih", "rekomendasi", "tindakan", "aksi",
                    "rencana", "strategi", "solusi"]
    if any(kw in m for kw in decision_kw):
        return "decision"
    fact_kw = ["hoax", "hoaks", "bohong", "tipu", "penipuan", "fake", "viral",
                "berita", "informasi", "benar", "cek fakta"]
    if any(kw in m for kw in fact_kw):
        return "fact_check"
    return "civic"

def get_agent_prompt(intent: str) -> str:
    prompts = {
        "civic": CITIZEN_SYSTEM_PROMPT,
        "policy": POLICY_EXPERT_PROMPT,
        "fact_check": FACT_CHECKER_PROMPT,
        "decision": DECISION_ENGINE_PROMPT,
        "climate": CLIMATE_EXPERT_PROMPT,
        "legal": LEGAL_ASSISTANT_PROMPT,
        "emergency": EMERGENCY_ASSISTANT_PROMPT,
    }
    return prompts.get(intent, CITIZEN_SYSTEM_PROMPT)

def smart_route(message: str, history: list = None) -> dict:
    intent = detect_intent(message)
    prompt = get_agent_prompt(intent)
    result = chat_with_ai(prompt, f"Pertanyaan warga: {message}", history)
    if result:
        result["intent"] = intent
        return result
    return {"type": "fallback", "intent": intent, "message": message}

def route_analysis(message: str, history: list = None):
    from src.ai_service import analyze_with_ai
    result = analyze_with_ai(message, history)
    if result:
        return result
    result = smart_route(message, history)
    if result.get("type") != "fallback":
        return result
    from src.fallback import analyze_situation_fallback, CasualResponse, CopilotResponse
    return analyze_situation_fallback(message)
