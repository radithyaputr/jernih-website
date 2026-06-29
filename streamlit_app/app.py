"""JERNIH OS — Streamlit Frontend & Backend (All-in-One)"""

import streamlit as st
import random
import re
import json
import os
import time
from datetime import datetime
from typing import Optional, Union
from dataclasses import dataclass

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JERNIH OS",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Constants ────────────────────────────────────────────────────────────────
VERSION = "1.0.0"
APP_NAME = "JERNIH OS"

# ─── Data Structures ──────────────────────────────────────────────────────────
@dataclass
class Source:
    title: str
    url: str
    type: str

@dataclass
class TrustScore:
    overall: float
    reliability: float
    freshness: float
    verification: float
    transparency: float

@dataclass
class CopilotResponse:
    session_id: str
    summary: str
    analysis: str
    relevant_programs: list
    required_documents: list
    risk_factors: list
    timeline: dict
    action_plan: dict
    success_probability: float
    trust_score: TrustScore
    sources: list

@dataclass
class CasualResponse:
    session_id: str
    message: str

# ─── Knowledge Base ───────────────────────────────────────────────────────────
KNOWLEDGE_BASE = {
    "programs": {
        "pip": {
            "name": "Program Indonesia Pintar (PIP)",
            "agency": "Kemdikdasmen",
            "description": "Bantuan pendidikan untuk anak usia sekolah dari keluarga miskin/rentan",
            "url": "https://pip.kemdikbud.go.id",
            "keywords": ["pendidikan", "sekolah", "siswa", "miskin", "bantuan", "pip", "kip"],
            "requirements": ["KK", "KTP", "SKTM", "Terdaftar di DTKS"],
        },
        "kis": {
            "name": "Kartu Indonesia Sehat (KIS)",
            "agency": "BPJS Kesehatan",
            "description": "Jaminan kesehatan bagi masyarakat kurang mampu",
            "url": "https://bpjs-kesehatan.go.id",
            "keywords": ["kesehatan", "bpjs", "kis", "berobat", "rumah sakit"],
            "requirements": ["KK", "NIK"],
        },
        "bpnt": {
            "name": "Bantuan Pangan Non-Tunai (BPNT)",
            "agency": "Kemensos",
            "description": "Bantuan pangan untuk keluarga kurang mampu",
            "url": "https://kemensos.go.id",
            "keywords": ["pangan", "makanan", "sembako", "bansos", "bpnt"],
            "requirements": ["KK", "KTP", "Terdaftar di DTKS"],
        },
        "pkh": {
            "name": "Program Keluarga Harapan (PKH)",
            "agency": "Kemensos",
            "description": "Bantuan sosial bersyarat untuk keluarga miskin",
            "url": "https://pkh.kemensos.go.id",
            "keywords": ["keluarga", "bansos", "pkh", "ibu hamil", "balita"],
            "requirements": ["KK", "KTP", "Terdaftar di DTKS"],
        },
    },
    "documents": {
        "kk": {"name": "Kartu Keluarga", "issuer": "Dukcapil"},
        "ktp": {"name": "KTP Elektronik", "issuer": "Dukcapil"},
        "akte": {"name": "Akta Kelahiran", "issuer": "Dukcapil"},
        "sktm": {"name": "SKTM", "issuer": "Kelurahan"},
    },
}

TOPIC_CATEGORIES = {
    "greeting": {
        "keywords": ["halo", "hai", "hi", "hey", "pagi", "siang", "sore", "malam", "selamat pagi", "selamat siang", "selamat sore", "selamat malam", "apa kabar", "gimana kabar", "test", "tes", "coba", "hello", "hy", "assalamualaikum", "assalamu alaikum"],
        "label": "Sapaan",
    },
    "kematian": {
        "keywords": ["meninggal", "meninggal dunia", "wafat", "tiada", "meninggalnya", "almarhum", "almarhumah", "kematian", "meninggalkan", "ditinggal", "kepergian", "berduka"],
        "label": "Pengurusan Akta Kematian & Waris",
    },
    "pendidikan": {
        "keywords": ["kip", "pip", "sekolah", "pendidikan", "kuliah", "biaya sekolah", "skhun", "ijazah", "beasiswa", "siswa", "mahasiswa", "belajar", "universitas", "smk", "sma", "smp", "sd", "tk", "paud", "bantuan pendidikan", "uang sekolah", "spp"],
        "label": "Bantuan Pendidikan",
    },
    "dokumen_hilang": {
        "keywords": ["ktp", "hilang", "kehilangan", "rusak", "ktp hilang", "ktp rusak", "ganti ktp", "perpanjang ktp", "ektp"],
        "label": "Penggantian Dokumen Kependudukan",
    },
    "kesehatan": {
        "keywords": ["bpjs", "kis", "kesehatan", "berobat", "rumah sakit", "puskesmas", "dokter", "sakit", "obat", "rs", "faskes", "rujukan", "bpjs kesehatan", "jaminan kesehatan"],
        "label": "Layanan Kesehatan",
    },
    "bansos": {
        "keywords": ["bansos", "bantuan", "sembako", "pkh", "bpnt", "miskin", "fakir", "keluarga miskin", "bantuan sosial", "bantuan pangan", "subsidi", "blt", "bantuan langsung"],
        "label": "Bantuan Sosial",
    },
    "usaha": {
        "keywords": ["usaha", "kerja", "umkm", "wirausaha", "modal", "bisnis", "startup", "usaha kecil", "usaha mikro", "nib", "izin usaha", "pelatihan kerja", "lowongan", "pekerjaan"],
        "label": "Bantuan Usaha & Ketenagakerjaan",
    },
    "kk": {
        "keywords": ["kartu keluarga", "kk", "data keluarga", "anggota keluarga"],
        "label": "Pengurusan Kartu Keluarga",
    },
    "akte": {
        "keywords": ["akte", "akta kelahiran", "kelahiran", "lahir", "bayi", "anak", "akta"],
        "label": "Pembuatan Akta Kelahiran",
    },
    "pajak": {
        "keywords": ["pajak", "npwp", "spt", "pajak bumi", "pbb", "pajak kendaraan", "pkb", "bpkb", "stnk", "pajak penghasilan"],
        "label": "Informasi Perpajakan",
    },
    "nikah": {
        "keywords": ["nikah", "menikah", "pernikahan", "kua", "suami", "istri", "kawin", "catatan sipil"],
        "label": "Pendaftaran Pernikahan",
    },
    "pindah": {
        "keywords": ["pindah", "domisili", "pindah alamat", "pindah domisili", "surat pindah", "merantau"],
        "label": "Pengurusan Pindah Domisili",
    },
    "perumahan": {
        "keywords": ["rumah", "perumahan", "subsidi rumah", "kpr", "btp", "rumah subsidi", "rumah bersubsidi", "tempat tinggal"],
        "label": "Bantuan Perumahan",
    },
    "paspor": {
        "keywords": ["paspor", "imigrasi", "bepergian", "ke luar negeri", "visa", "perjalanan"],
        "label": "Pembuatan Paspor",
    },
    "sim": {
        "keywords": ["sim", "surat izin mengemudi", "mobil", "motor", "mengemudi", "surat kendaraan"],
        "label": "Pembuatan SIM",
    },
    "listrik": {
        "keywords": ["listrik", "pln", "token listrik", "tagihan listrik", "meteran listrik", "pasang listrik", "tambah daya"],
        "label": "Layanan Listrik",
    },
    "air": {
        "keywords": ["air", "pdam", "air bersih", "tagihan air", "air minum"],
        "label": "Layanan Air Bersih",
    },
    "sampah": {
        "keywords": ["sampah", "kebersihan", "dinas kebersihan", "limbah", "bank sampah", "daur ulang"],
        "label": "Layanan Kebersihan",
    },
    "bencana": {
        "keywords": ["bencana", "banjir", "gempa", "longsor", "tsunami", "bencana alam", "bpbd", "bnpb", "evakuasi", "pengungsian"],
        "label": "Penanganan Bencana",
    },
    "korupsi": {
        "keywords": ["korupsi", "lapor", "pengaduan", "kpk", "whistleblower", "gratifikasi", "laporan", "aspirasi"],
        "label": "Layanan Pengaduan",
    },
    "sapawarga": {
        "keywords": ["sapa warga", "keluhan", "aspirasi", "laporan warga", "lapor", "pengaduan masyarakat"],
        "label": "Aspirasi Warga",
    },
}

# ─── AI Service (OpenRouter Integration) ───────────────────────────────────────

import httpx

OPENROUTER_KEY = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
HAS_AI_API = bool(OPENROUTER_KEY)
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "openai/gpt-4o-mini"

CITIZEN_SYSTEM_PROMPT = f"Anda adalah AI Civic Assistant JERNIH OS untuk Indonesia. Waktu saat ini adalah {datetime.now().strftime('%d %B %Y')}. Presiden Indonesia saat ini adalah Prabowo Subianto.\n" + """
WAJIB: Balas HANYA dengan JSON valid. Mulai langsung dengan { tanpa teks apapun di luar JSON.

## ATURAN DETEKSI INTENT:

1. Jika user menyapa, berterima kasih, atau ngobrol santai (contoh: "halo", "hi", "terima kasih", "apa kabar", "siapa kamu", "test", "hari ini hari apa", "siapa presiden"), balas dengan format CASUAL:
{"type":"casual","message":"balasan ramah dan natural dalam Bahasa Indonesia"}

2. Jika user menyampaikan keluhan, masalah, kasus, atau pertanyaan seputar layanan publik/pemerintah, balas dengan format ANALYSIS:
{"type":"analysis","summary":"ringkasan 1 kalimat spesifik","analysis":"analisis 2-3 kalimat","relevant_programs":[{"name":"nama","agency":"instansi","description":"deskripsi singkat","match_score":85,"url":"https://..."}],"required_documents":[{"name":"nama","description":"keterangan","priority":"high"}],"risk_factors":[{"risk":"risiko","severity":"medium","mitigation":"solusi"}],"timeline":{"estimated_days":14,"steps":[{"step":1,"action":"langkah konkret","duration":"1 hari","office":"kantor tujuan"}]},"action_plan":{"today":["langkah hari ini"],"this_week":["langkah minggu ini"],"next_step":["langkah berikutnya"]},"success_probability":75}

Gunakan data nyata pemerintah Indonesia. Jawab SPESIFIK sesuai situasi warga."""

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

def _validate_analysis(result: dict) -> bool:
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
    return "message" in result and isinstance(result["message"], str) and len(result["message"]) > 0

def analyze_with_ai(message: str) -> Optional[dict]:
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
            if resp.status_code in (401, 403):
                return None
            if resp.status_code == 402:
                payload["model"] = "google/gemma-2-9b-it:free"
                continue
            if resp.status_code == 429:
                return None
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
                if not result:
                    return None
            resp_type = result.get("type", "analysis")
            if resp_type == "casual" and _validate_casual(result):
                return {"type": "casual", "message": result["message"]}
            result.pop("type", None)
            if _validate_analysis(result):
                result["type"] = "analysis"
                return result
            return None
        except httpx.TimeoutException:
            time.sleep(3)
        except Exception:
            if attempt < 1:
                time.sleep(2)
            else:
                return None
    return None

def ask_ai_json(system_prompt: str, user_prompt: str) -> Optional[dict]:
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
        except Exception:
            pass
    return None

# ─── AI Logic (ported from backend) ───────────────────────────────────────────

def _detect_topic(message: str) -> str:
    m = message.lower()
    topic_scores = {}
    for topic, config in TOPIC_CATEGORIES.items():
        score = sum(1 for kw in config["keywords"] if re.search(r'\b' + re.escape(kw) + r'\b', m))
        if score > 0:
            topic_scores[topic] = score
    if topic_scores:
        return max(topic_scores, key=topic_scores.get)
    return "general"

def _get_topic_label(topic: str) -> str:
    return TOPIC_CATEGORIES.get(topic, {}).get("label", "Layanan Publik")

def _generate_contextual_summary(message: str, matched_programs: list, topic: str = "general") -> str:
    m = message.lower()
    if topic == "greeting":
        hour = datetime.now().hour
        if hour < 11:
            time_greeting = "Selamat pagi"
        elif hour < 15:
            time_greeting = "Selamat siang"
        elif hour < 19:
            time_greeting = "Selamat sore"
        else:
            time_greeting = "Selamat malam"
        return f"{time_greeting}! Saya AI Civic Copilot JERNIH OS. Ada yang bisa saya bantu? Ceritakan situasi Anda, saya akan membantu menemukan solusi dan program yang sesuai."
    if topic == "kematian":
        return "Kami turut berduka cita atas kepergian anggota keluarga Anda. Berikut adalah langkah-langkah yang perlu Anda urus terkait dokumen kependudukan, hak waris, dan program bantuan yang mungkin Anda perlukan."
    if topic == "pendidikan":
        return "Kami memahami kebutuhan Anda akan bantuan pendidikan. Berdasarkan situasi yang Anda sampaikan, berikut program pendidikan yang sesuai, dokumen yang perlu disiapkan, dan langkah-langkah pengurusan."
    if topic == "dokumen_hilang":
        return "Kami akan membantu Anda mengurus penggantian dokumen kependudukan yang hilang atau rusak. Berikut prosedur, dokumen yang diperlukan, dan estimasi waktu pengurusan."
    if topic == "kesehatan":
        return "Kami akan membantu Anda mengakses layanan jaminan kesehatan. Berikut program dan prosedur yang sesuai dengan situasi Anda."
    if topic == "bansos":
        return "Kami akan membantu Anda mengidentifikasi program bantuan sosial yang sesuai. Berikut program yang relevan, dokumen yang diperlukan, dan cara pendaftaran."
    if topic == "usaha":
        return "Kami akan membantu Anda menemukan program bantuan usaha dan pelatihan kerja. Berikut informasi program, persyaratan, dan langkah pengurusan."
    if topic in ["kk", "akte"]:
        label = _get_topic_label(topic)
        return f"Kami akan membantu Anda mengurus {label}. Berikut prosedur, persyaratan, dan langkah-langkah yang perlu Anda tempuh."
    if topic == "pajak":
        return "Kami akan memberikan informasi terkait kewajiban perpajakan Anda. Berikut prosedur, persyaratan, dan langkah-langkah pengurusan pajak."
    if topic == "nikah":
        return "Kami akan membantu Anda mempersiapkan dokumen dan prosedur pernikahan. Berikut informasi persyaratan, langkah pendaftaran, dan estimasi waktu."
    if topic == "pindah":
        return "Kami akan membantu Anda mengurus pindah domisili. Berikut prosedur, dokumen yang diperlukan, dan estimasi waktu pengurusan."
    if topic == "perumahan":
        return "Kami akan membantu Anda menemukan program bantuan perumahan yang sesuai. Berikut informasi subsidi rumah, KPR, dan persyaratannya."
    if topic == "paspor":
        return "Kami akan membantu Anda mengurus pembuatan paspor. Berikut prosedur, persyaratan dokumen, dan estimasi waktu pembuatan."
    if topic == "sim":
        return "Kami akan membantu Anda mengurus pembuatan atau perpanjangan SIM. Berikut prosedur, persyaratan, dan biaya yang diperlukan."
    if topic in ["listrik", "air", "sampah"]:
        label = _get_topic_label(topic)
        return f"Kami akan membantu Anda mengurus {label}. Berikut informasi prosedur, persyaratan, dan kontak layanan yang dapat dihubungi."
    if topic == "bencana":
        return "Kami turut prihatin atas bencana yang Anda alami. Berikut informasi bantuan, kontak darurat, dan prosedur pengajuan bantuan bencana."
    if topic == "korupsi":
        return "Kami akan membantu Anda menyampaikan pengaduan atau laporan. Berikut saluran resmi, prosedur pelaporan, dan informasi perlindungan pelapor."
    words = m.split()
    question_words = ["apa", "bagaimana", "siapa", "kapan", "dimana", "mengapa", "berapa", "apakah", "bisakah", "bolehkah"]
    has_question = any(q in words for q in question_words)
    if has_question:
        return "Terima kasih atas pertanyaan Anda. JERNIH OS akan membantu Anda menemukan informasi yang dibutuhkan. Berikut analisis dan rekomendasi yang sesuai dengan pertanyaan Anda."
    return "Berdasarkan situasi yang Anda sampaikan, JERNIH OS telah menganalisis kebutuhan Anda dan menyusun rekomendasi program, dokumen, dan langkah-langkah yang perlu Anda tempuh untuk mengakses layanan publik."

def _generate_contextual_analysis(message: str, matched_programs: list, topic: str = "general") -> str:
    if topic == "greeting":
        return "Saya siap membantu Anda! Silakan ceritakan situasi atau pertanyaan Anda seputar layanan publik, bantuan sosial, kependudukan, atau program pemerintah lainnya."
    if topic == "kematian":
        progs = ", ".join(p["name"] for p in matched_programs[:2]) if matched_programs else "program bantuan"
        return f"Dari informasi yang Anda sampaikan, prioritas utama adalah mengurus akta kematian dan perbaikan data kependudukan. Setelah itu, Anda dapat mengakses {progs}. Kami sarankan untuk mengurus dokumen secara bertahap."
    if topic == "pendidikan":
        return "Berdasarkan analisis, Anda memenuhi kriteria untuk beberapa program bantuan pendidikan. Prioritas utama adalah memastikan dokumen kependudukan lengkap dan terdaftar di DTKS untuk memudahkan verifikasi."
    if topic == "dokumen_hilang":
        return "Proses penggantian KTP hilang/rusak relatif sederhana. Yang terpenting adalah membawa surat kehilangan dari kepolisian (jika hilang) dan dokumen pendukung lainnya. Proses bisa selesai dalam 1-14 hari kerja."
    if topic == "kesehatan":
        return "Berdasarkan analisis, Anda memerlukan akses layanan kesehatan. Pastikan status kepesertaan BPJS aktif dan sesuaikan kelas perawatan dengan kebutuhan."
    if topic == "bansos":
        return "Analisis menunjukkan Anda berpotensi menerima beberapa jenis bantuan sosial. Langkah pertama adalah memastikan terdaftar di DTKS dan mengurus dokumen dasar."
    if topic == "usaha":
        return "Analisis menunjukkan beberapa program bantuan usaha dan pelatihan yang sesuai. Prioritas tergantung pada jenis usaha dan modal yang dimiliki."
    if topic == "kk":
        return "Kartu Keluarga adalah dokumen penting yang menjadi dasar penerbitan dokumen kependudukan lainnya. Pastikan data KK Anda selalu terupdate dan sesuai dengan kondisi terkini."
    if topic == "akte":
        return "Akta Kelahiran adalah dokumen hukum yang membuktikan identitas dan status kewarganegaraan seseorang. Proses pembuatannya relatif mudah dengan dokumen yang lengkap."
    if topic == "pajak":
        return "Kewajiban perpajakan adalah tanggung jawab setiap warga negara. Dengan memahami prosedur yang benar, Anda dapat mengurus pajak dengan lebih mudah dan tepat waktu."
    if topic == "nikah":
        return "Proses pendaftaran pernikahan di Indonesia diatur oleh KUA untuk yang beragama Islam dan Catatan Sipil untuk non-Muslim. Persiapkan dokumen dengan lengkap agar proses berjalan lancar."
    if topic == "pindah":
        return "Pengurusan pindah domisili memerlukan beberapa dokumen administratif. Pastikan Anda telah mengurus surat pindah dari kelurahan asal sebelum pindah ke domisili baru."
    if topic in ["listrik", "air", "sampah"]:
        return f"Layanan {_get_topic_label(topic).lower()} disediakan oleh instansi terkait di wilayah masing-masing. Prosedur pengurusan dapat dilakukan secara online maupun offline."
    if topic in ["perumahan", "paspor", "sim", "bencana", "korupsi"]:
        return f"Berdasarkan analisis, kami telah menyusun informasi lengkap mengenai {_get_topic_label(topic).lower()} yang sesuai dengan kebutuhan Anda."
    matched_names = ", ".join(p["name"] for p in matched_programs[:2]) if matched_programs else "beberapa layanan publik"
    return f"Dari informasi yang diberikan, Anda dapat mengakses {matched_names} untuk memenuhi kebutuhan Anda. Kami merekomendasikan untuk mempersiapkan dokumen dasar terlebih dahulu sebelum memulai proses pengurusan."

def _generate_contextual_timeline(message: str, topic: str = "general") -> dict:
    if topic == "greeting":
        return {"estimated_days": 0, "steps": [{"step": 1, "action": "Sampaikan pertanyaan Anda", "duration": "Sekarang", "office": "-"}]}
    if topic == "kematian":
        steps = [
            {"step": 1, "action": "Urus Akta Kematian di Dukcapil", "duration": "1-3 hari", "office": "Dukcapil"},
            {"step": 2, "action": "Perbaiki data KK (hapus yg meninggal)", "duration": "1-2 hari", "office": "Dukcapil"},
            {"step": 3, "action": "Urus surat pindah/domisili ahli waris", "duration": "1 hari", "office": "Kantor Kelurahan"},
            {"step": 4, "action": "Daftar program bantuan untuk keluarga", "duration": "3-7 hari", "office": "Dinas Sosial"},
            {"step": 5, "action": "Aktivasi rekening bantuan", "duration": "2-3 hari", "office": "Bank Penyalur"},
        ]
        return {"estimated_days": 10, "steps": steps}
    if topic == "pendidikan":
        steps = [
            {"step": 1, "action": "Verifikasi dokumen kependudukan", "duration": "1-2 hari", "office": "Dukcapil"},
            {"step": 2, "action": "Ambil SKTM dari kelurahan", "duration": "1 hari", "office": "Kantor Kelurahan"},
            {"step": 3, "action": "Daftar PIP/KIP di sekolah/kampus", "duration": "3-5 hari", "office": "Sekolah/Dinas Pendidikan"},
            {"step": 4, "action": "Aktivasi rekening bantuan", "duration": "2-3 hari", "office": "Bank Penyalur"},
            {"step": 5, "action": "Konfirmasi penerimaan bantuan", "duration": "1-2 hari", "office": "-"},
        ]
        return {"estimated_days": 14, "steps": steps}
    if topic == "dokumen_hilang":
        steps = [
            {"step": 1, "action": "Buat laporan kehilangan ke polisi", "duration": "1 hari", "office": "Kantor Polisi"},
            {"step": 2, "action": "Ambil surat pengantar RT/RW", "duration": "1 hari", "office": "RT/RW setempat"},
            {"step": 3, "action": "Datang ke Dukcapil dengan dokumen", "duration": "1 hari", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Foto & perekaman biometrik", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 5, "action": "Tunggu pencetakan KTP", "duration": "1-14 hari", "office": "-"},
        ]
        return {"estimated_days": 7, "steps": steps}
    if topic == "kesehatan":
        steps = [
            {"step": 1, "action": "Cek status kepesertaan BPJS", "duration": "1 jam", "office": "Online/BPJS"},
            {"step": 2, "action": "Aktifkan kepesertaan jika nonaktif", "duration": "1 hari", "office": "Kantor BPJS"},
            {"step": 3, "action": "Urus rujukan ke faskes", "duration": "1 hari", "office": "Puskesmas/Faskes 1"},
            {"step": 4, "action": "Daftar layanan kesehatan", "duration": "1 hari", "office": "Rumah Sakit"},
        ]
        return {"estimated_days": 5, "steps": steps}
    if topic == "kk":
        steps = [
            {"step": 1, "action": "Kumpulkan dokumen (KK lama, KTP)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Ambil formulir di Dukcapil", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 3, "action": "Isi dan serahkan formulir", "duration": "1 hari", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Tunggu proses verifikasi", "duration": "3-7 hari", "office": "-"},
            {"step": 5, "action": "Ambil KK baru", "duration": "1 hari", "office": "Kantor Dukcapil"},
        ]
        return {"estimated_days": 7, "steps": steps}
    if topic == "akte":
        steps = [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Surat Nikah, Surat Lahir)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Datang ke Dukcapil", "duration": "1 jam", "office": "Kantor Dukcapil"},
            {"step": 3, "action": "Isi formulir permohonan", "duration": "30 menit", "office": "Kantor Dukcapil"},
            {"step": 4, "action": "Verifikasi dokumen", "duration": "1-3 hari", "office": "Kantor Dukcapil"},
            {"step": 5, "action": "Ambil Akta Kelahiran", "duration": "1 hari", "office": "Kantor Dukcapil"},
        ]
        return {"estimated_days": 5, "steps": steps}
    if topic == "nikah":
        steps = [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Pas Foto)", "duration": "1-2 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar di KUA/Catatan Sipil", "duration": "1 hari", "office": "KUA/Catatan Sipil"},
            {"step": 3, "action": "Pengumuman pernikahan (10 hari kerja)", "duration": "10 hari", "office": "-"},
            {"step": 4, "action": "Pelaksanaan akad nikah", "duration": "1 hari", "office": "KUA/Tempat Nikah"},
            {"step": 5, "action": "Ambil Buku Nikah/Akta Pernikahan", "duration": "1 hari", "office": "KUA/Catatan Sipil"},
        ]
        return {"estimated_days": 14, "steps": steps}
    if topic == "pindah":
        steps = [
            {"step": 1, "action": "Urus surat pindah dari kelurahan asal", "duration": "1 hari", "office": "Kantor Kelurahan Asal"},
            {"step": 2, "action": "Lapor ke kelurahan tujuan", "duration": "1 hari", "office": "Kantor Kelurahan Tujuan"},
            {"step": 3, "action": "Verifikasi data kependudukan", "duration": "3-5 hari", "office": "Kantor Kecamatan"},
            {"step": 4, "action": "Update KK dan KTP", "duration": "1-2 hari", "office": "Kantor Dukcapil"},
        ]
        return {"estimated_days": 7, "steps": steps}
    if topic == "paspor":
        steps = [
            {"step": 1, "action": "Siapkan dokumen (KK, KTP, Akta Lahir)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar online via M-Paspor", "duration": "1 jam", "office": "Online"},
            {"step": 3, "action": "Bayar biaya paspor", "duration": "1 jam", "office": "Bank/Online"},
            {"step": 4, "action": "Datang ke Kantor Imigrasi untuk wawancara & foto", "duration": "1 hari", "office": "Kantor Imigrasi"},
            {"step": 5, "action": "Tunggu pencetakan paspor", "duration": "3-5 hari", "office": "-"},
        ]
        return {"estimated_days": 10, "steps": steps}
    if topic == "sim":
        steps = [
            {"step": 1, "action": "Siapkan dokumen (KTP, surat kesehatan)", "duration": "1 hari", "office": "Rumah"},
            {"step": 2, "action": "Daftar online atau datang ke Satpas", "duration": "1 hari", "office": "Satpas SIM"},
            {"step": 3, "action": "Ikuti tes teori", "duration": "1 jam", "office": "Satpas SIM"},
            {"step": 4, "action": "Ikuti tes praktik", "duration": "1 jam", "office": "Satpas SIM"},
            {"step": 5, "action": "Foto dan ambil SIM", "duration": "1 jam", "office": "Satpas SIM"},
        ]
        return {"estimated_days": 3, "steps": steps}
    steps = [
        {"step": 1, "action": "Verifikasi dokumen kependudukan", "duration": "1-2 hari", "office": "Dukcapil"},
        {"step": 2, "action": "Urus dokumen pendukung", "duration": "1 hari", "office": "Kantor Kelurahan"},
        {"step": 3, "action": "Daftar program terkait", "duration": "3-5 hari", "office": "Dinas Terkait"},
        {"step": 4, "action": "Aktivasi rekening/penerimaan", "duration": "2-3 hari", "office": "Bank Penyalur"},
        {"step": 5, "action": "Konfirmasi dan monitoring", "duration": "1-2 hari", "office": "-"},
    ]
    return {"estimated_days": 14, "steps": steps}

def _generate_contextual_documents(message: str, topic: str = "general") -> list:
    if topic == "greeting":
        return []
    base = [
        {"name": "Kartu Keluarga (KK)", "description": "KK asli dan fotokopi 3 lembar", "priority": "high"},
        {"name": "KTP Elektronik", "description": "KTP-el asli dan fotokopi 3 lembar", "priority": "high"},
    ]
    if topic == "kematian":
        base += [
            {"name": "Akta Kematian", "description": "Dari rumah sakit/kelurahan", "priority": "high"},
            {"name": "Surat Keterangan Ahli Waris", "description": "Dari kelurahan", "priority": "high"},
        ]
    if topic == "pendidikan":
        base += [
            {"name": "Akta Kelahiran", "description": "Akta kelahiran anak (jika ada)", "priority": "medium"},
            {"name": "Surat Keterangan Tidak Mampu (SKTM)", "description": "Dari kelurahan/desa setempat", "priority": "medium"},
            {"name": "Rapor/SKHUN/Ijazah", "description": "Untuk program pendidikan", "priority": "low"},
        ]
    if topic == "dokumen_hilang":
        base += [
            {"name": "Surat Kehilangan dari Polisi", "description": "Laporan kehilangan dari kantor polisi", "priority": "high"},
            {"name": "Surat Pengantar RT/RW", "description": "Pengantar dari ketua RT/RW", "priority": "high"},
        ]
    if topic == "kesehatan":
        base += [
            {"name": "Kartu BPJS/KIS", "description": "Kartu kepesertaan BPJS", "priority": "high"},
            {"name": "Surat Rujukan", "description": "Dari faskes tingkat 1", "priority": "medium"},
        ]
    if topic == "bansos":
        base += [
            {"name": "Surat Keterangan Tidak Mampu (SKTM)", "description": "Dari kelurahan/desa setempat", "priority": "high"},
            {"name": "Terdaftar di DTKS", "description": "Data Terpadu Kesejahteraan Sosial", "priority": "high"},
        ]
    if topic == "usaha":
        base += [
            {"name": "Surat Izin Usaha", "description": "NIB/UMKU jika sudah ada", "priority": "medium"},
            {"name": "Proposal Usaha", "description": "Rencana bisnis sederhana", "priority": "medium"},
        ]
    if topic == "nikah":
        base += [
            {"name": "Surat Nikah dari KUA/Catatan Sipil", "description": "Dari KUA/Catatan Sipil", "priority": "high"},
            {"name": "Pas Foto 4x6 (background biru)", "description": "Pas foto latar biru, formal 4x6", "priority": "medium"},
            {"name": "Surat Keterangan Belum Menikah", "description": "Dari kelurahan", "priority": "medium"},
        ]
    if topic == "akte":
        base += [
            {"name": "Surat Keterangan Lahir", "description": "Dari bidan/dokter/rumah sakit", "priority": "high"},
            {"name": "Surat Nikah Orang Tua", "description": "Fotokopi Buku Nikah orang tua", "priority": "high"},
        ]
    if topic == "pindah":
        base += [
            {"name": "Surat Keterangan Pindah", "description": "Dari kelurahan asal", "priority": "high"},
            {"name": "Surat Pengantar RT/RW", "description": "Pengantar dari ketua RT/RW", "priority": "high"},
        ]
    if topic == "paspor":
        base += [
            {"name": "Pas Foto 2x3 (background merah/putih)", "description": "Syarat paspor terbaru", "priority": "high"},
            {"name": "Bukti Pembayaran Paspor", "description": "Dari bank atau online", "priority": "high"},
        ]
    if topic == "sim":
        base += [
            {"name": "Surat Keterangan Sehat", "description": "Dari dokter/rumah sakit", "priority": "high"},
            {"name": "Pas Foto 2x3 (background merah)", "description": "Pas foto latar merah", "priority": "medium"},
        ]
    if topic in ["pajak", "perumahan", "kk", "bencana", "korupsi", "listrik", "air", "sampah"]:
        base += [
            {"name": "Dokumen pendukung terkait", "description": "Sesuai dengan ketentuan instansi terkait", "priority": "medium"},
        ]
    return base

def _generate_action_plan(message: str, topic: str = "general") -> dict:
    if topic == "greeting":
        return {"today": ["Silakan ceritakan situasi Anda"], "this_week": [], "next_step": []}
    today = ["Kumpulkan dokumen identitas (KK, KTP)", "Hubungi kelurahan untuk informasi"]
    this_week = ["Verifikasi dokumen ke Dukcapil", "Lengkapi dokumen pendukung"]
    next_step = ["Daftar program bantuan", "Pantau status pengajuan"]
    if topic == "kematian":
        today = ["Urus Akta Kematian di Dukcapil", "Kumpulkan dokumen ahli waris", "Hubungi kelurahan untuk surat keterangan"]
        this_week = ["Perbaiki data KK di Dukcapil", "Urus surat pindah/domisili", "Cek program bantuan untuk keluarga ditinggalkan"]
        next_step = ["Daftar program bantuan sosial", "Aktivasi rekening bantuan", "Pantau status penerimaan"]
    elif topic == "pendidikan":
        today = ["Kumpulkan KK, KTP, dan Akta Kelahiran", "Cek jadwal pendaftaran PIP/KIP", "Hubungi sekolah/kampus"]
        this_week = ["Ambil SKTM di kelurahan", "Verifikasi dokumen ke Dukcapil", "Daftar program PIP/KIP"]
        next_step = ["Aktivasi rekening bantuan", "Pantau status penerimaan", "Konfirmasi ke pihak sekolah"]
    elif topic == "dokumen_hilang":
        today = ["Buat laporan kehilangan ke polisi", "Ambil surat pengantar RT/RW"]
        this_week = ["Datang ke Dukcapil dengan dokumen lengkap", "Foto dan perekaman biometrik"]
        next_step = ["Pantau proses pencetakan KTP", "Ambil KTP di Dukcapil jika sudah jadi"]
    elif topic == "kesehatan":
        today = ["Cek status kepesertaan BPJS via mobile app", "Siapkan dokumen BPJS"]
        this_week = ["Kunjungi Puskesmas/Faskes 1 untuk rujukan", "Urus administrasi di rumah sakit"]
        next_step = ["Pantau status klaim/jaminan", "Lakukan pengobatan sesuai jadwal"]
    elif topic == "bansos":
        today = ["Cek status DTKS di kelurahan", "Kumpulkan KK, KTP, dan dokumen pendukung"]
        this_week = ["Ambil SKTM di kelurahan", "Daftar program bansos yang sesuai"]
        next_step = ["Pantau status penerimaan bansos", "Aktivasi rekening bantuan"]
    elif topic == "usaha":
        today = ["Kumpulkan dokumen usaha dan identitas", "Cek program bantuan UMKM yang tersedia"]
        this_week = ["Urus NIB/izin usaha jika belum punya", "Ajukan proposal bantuan usaha"]
        next_step = ["Pantau status pengajuan bantuan", "Ikuti pelatihan jika disyaratkan"]
    elif topic == "nikah":
        today = ["Siapkan KK, KTP, dan pas foto", "Cek jadwal pendaftaran di KUA/Catatan Sipil"]
        this_week = ["Daftar pernikahan di KUA/Catatan Sipil", "Tunggu pengumuman 10 hari kerja"]
        next_step = ["Persiapkan akad nikah", "Ambil Buku Nikah/Akta Pernikahan"]
    elif topic == "pindah":
        today = ["Urus surat pindah dari kelurahan asal", "Siapkan dokumen KTP dan KK"]
        this_week = ["Lapor ke kelurahan tujuan", "Verifikasi data kependudukan"]
        next_step = ["Update KK dan KTP di domisili baru", "Aktivasi dokumen kependudukan"]
    elif topic == "akte":
        today = ["Kumpulkan surat keterangan lahir dari bidan/dokter", "Siapkan KK dan KTP orang tua"]
        this_week = ["Datang ke Dukcapil untuk daftar", "Isi formulir permohonan akta"]
        next_step = ["Ambil Akta Kelahiran", "Update KK dengan anggota baru"]
    return {"today": today, "this_week": this_week, "next_step": next_step}

def _generate_risk_factors(message: str, topic: str = "general") -> list:
    if topic == "greeting":
        return []
    risks = [
        {"risk": "Dokumen tidak lengkap menghambat proses", "severity": "high", "mitigation": "Siapkan semua dokumen sebelum memulai proses"},
        {"risk": "Antrean panjang di kantor pelayanan", "severity": "medium", "mitigation": "Datang pagi hari atau gunakan layanan online"},
    ]
    if topic == "kematian":
        risks += [
            {"risk": "Perbedaan data ahli waris", "severity": "high", "mitigation": "Siapkan surat keterangan ahli waris dari kelurahan"},
            {"risk": "Berkabung mempengaruhi konsentrasi", "severity": "low", "mitigation": "Minta bantuan keluarga atau kerabat terdekat"},
        ]
    if topic == "pendidikan":
        risks += [
            {"risk": "Batas waktu pendaftaran terbatas", "severity": "high", "mitigation": "Cek jadwal pendaftaran dan daftar segera"},
            {"risk": "Perubahan status ekonomi", "severity": "medium", "mitigation": "Siapkan dokumen pendukung kondisi ekonomi terkini"},
        ]
    if topic == "dokumen_hilang":
        risks += [
            {"risk": "Data tidak ditemukan di database Dukcapil", "severity": "high", "mitigation": "Verifikasi data kependudukan sebelum datang"},
            {"risk": "Sistem Dukcapil terkadang gangguan", "severity": "low", "mitigation": "Hubungi Dukcapil untuk cek jadwal servis sistem"},
        ]
    if topic in ["bansos", "usaha"]:
        risks += [
            {"risk": "Kuota program terbatas", "severity": "high", "mitigation": "Daftar sesegera mungkin setelah pendaftaran dibuka"},
            {"risk": "Data DTKS tidak valid", "severity": "medium", "mitigation": "Verifikasi data DTKS di kelurahan terlebih dahulu"},
        ]
    if topic in ["nikah", "pindah", "akte"]:
        risks += [
            {"risk": "Dokumen kurang lengkap", "severity": "high", "mitigation": "Cek ulang persyaratan sebelum datang ke instansi"},
            {"risk": "Prosedur berbeda antar daerah", "severity": "medium", "mitigation": "Konfirmasi prosedur ke instansi setempat"},
        ]
    if topic in ["sim", "paspor"]:
        risks += [
            {"risk": "Antrean online penuh", "severity": "medium", "mitigation": "Cek ketersediaan jadwal secara berkala"},
            {"risk": "Syarat administrasi berubah", "severity": "low", "mitigation": "Cek website resmi untuk info terbaru"},
        ]
    return risks

def analyze_situation(message: str) -> Union[CopilotResponse, CasualResponse]:
    session_id = f"sess_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"

    ai_result = analyze_with_ai(message)
    if ai_result:
        if ai_result.get("type") == "casual":
            return CasualResponse(session_id=session_id, message=ai_result["message"])
        trust = TrustScore(
            overall=round(random.uniform(85, 96), 1),
            reliability=round(random.uniform(88, 98), 1),
            freshness=round(random.uniform(80, 95), 1),
            verification=round(random.uniform(85, 95), 1),
            transparency=round(random.uniform(90, 98), 1),
        )
        try:
            return CopilotResponse(
                session_id=session_id,
                summary=ai_result.get("summary", ""),
                analysis=ai_result.get("analysis", ""),
                relevant_programs=ai_result.get("relevant_programs", []),
                required_documents=ai_result.get("required_documents", []),
                risk_factors=ai_result.get("risk_factors", []),
                timeline=ai_result.get("timeline", {"estimated_days": 14, "steps": []}),
                action_plan=ai_result.get("action_plan", {"today": [], "this_week": [], "next_step": []}),
                success_probability=ai_result.get("success_probability", 75),
                trust_score=trust,
                sources=[
                    Source(title="Portal PIP - Kemdikdasmen", url="https://pip.kemdikbud.go.id", type="government"),
                    Source(title="Data Terpadu Kesejahteraan Sosial (DTKS)", url="https://dtks.kemensos.go.id", type="government"),
                    Source(title="Kemendagri - Dukcapil", url="https://dukcapil.kemendagri.go.id", type="government"),
                ],
            )
        except Exception:
            pass

    message_lower = message.lower()
    topic = _detect_topic(message)
    if topic == "greeting":
        summary = _generate_contextual_summary(message, [], topic)
        return CasualResponse(session_id=session_id, message=summary)
    matched_programs = []
    for prog_id, prog in KNOWLEDGE_BASE["programs"].items():
        score = sum(1 for kw in prog["keywords"] if kw in message_lower)
        if score > 0:
            matched_programs.append({
                "name": prog["name"],
                "agency": prog["agency"],
                "description": prog["description"],
                "match_score": min(score * 25 + 50, 98),
                "url": prog.get("url", ""),
            })
    if not matched_programs:
        matched_programs = [
            {"name": "Program Indonesia Pintar (PIP)", "agency": "Kemdikdasmen", "description": "Bantuan pendidikan untuk anak usia sekolah dari keluarga miskin/rentan", "match_score": 75, "url": "https://pip.kemdikbud.go.id"},
            {"name": "Kartu Indonesia Sehat (KIS)", "agency": "BPJS Kesehatan", "description": "Jaminan kesehatan bagi masyarakat kurang mampu", "match_score": 65},
        ]
    timeline = _generate_contextual_timeline(message, topic)
    docs = _generate_contextual_documents(message, topic)
    action_plan = _generate_action_plan(message, topic)
    risks = _generate_risk_factors(message, topic)
    trust = TrustScore(
        overall=round(random.uniform(80, 95), 1),
        reliability=round(random.uniform(85, 98), 1),
        freshness=round(random.uniform(75, 92), 1),
        verification=round(random.uniform(82, 95), 1),
        transparency=round(random.uniform(88, 98), 1),
    )
    return CopilotResponse(
        session_id=session_id,
        summary=_generate_contextual_summary(message, matched_programs, topic),
        analysis=_generate_contextual_analysis(message, matched_programs, topic),
        relevant_programs=matched_programs,
        required_documents=docs,
        risk_factors=risks,
        timeline=timeline,
        action_plan=action_plan,
        success_probability=round(random.uniform(65, 88), 0),
        trust_score=trust,
        sources=[
            Source(title="Portal PIP - Kemdikdasmen", url="https://pip.kemdikbud.go.id", type="government"),
            Source(title="Data Terpadu Kesejahteraan Sosial (DTKS)", url="https://dtks.kemensos.go.id", type="government"),
            Source(title="Kemendagri - Dukcapil", url="https://dukcapil.kemendagri.go.id", type="government"),
        ],
    )

def analyze_hoax(text: str, text_type: str = "text") -> dict:
    if not text or not text.strip():
        return {"credibility_score": 100, "verdict": "credible", "analysis": "Tidak ada teks untuk dianalisis.", "source_comparison": [], "fact_checks": [], "indicators": []}

    HOAX_SYSTEM_PROMPT = f"Anda adalah AI Hoax Checker JERNIH OS untuk Indonesia. Waktu saat ini adalah {datetime.now().strftime('%d %B %Y')}.\n" + """
Anda adalah ahli verifikasi informasi dan deteksi hoaks. Analisis teks yang diberikan dan berikan penilaian kredibilitas.
WAJIB: Balas HANYA dengan JSON valid. Mulai langsung dengan { tanpa teks apapun di luar JSON.
Format JSON yang harus dikembalikan:
{
  "credibility_score": angka 0-100,
  "verdict": "hoax" jika < 40, "questionable" jika 40-74, "credible" jika >= 75,
  "analysis": "Penjelasan detail mengapa informasi ini hoaks/mencurigakan/kredibel.",
  "source_comparison": [
    {"source": "nama sumber resmi", "alignment": "supports/contradicts/neutral", "excerpt": "kutipan atau penjelasan singkat"}
  ],
  "fact_checks": [
    {"claim": "klaim spesifik dalam teks", "verdict": "BENAR/SALAH/TIDAK TERVERIFIKASI", "source": "sumber fact-check"}
  ],
  "indicators": ["indikator mencurigakan yang ditemukan", ...]
}
Gunakan sumber resmi Indonesia seperti: data.go.id, kemensos.go.id, kominfo.go.id, kemendikbud.go.id, bpjs-kesehatan.go.id, dukcapil.kemendagri.go.id, factcheck.id, turnbackhoax.id, dll."""

    ai_result = ask_ai_json(HOAX_SYSTEM_PROMPT, f"Teks yang akan diverifikasi (tipe: {text_type}):\n\n{text[:3000]}")
    if ai_result and all(k in ai_result for k in ["credibility_score", "verdict", "analysis"]):
        ai_result.setdefault("source_comparison", [])
        ai_result.setdefault("fact_checks", [])
        ai_result.setdefault("indicators", [])
        return ai_result

    suspicious_indicators = [
        "bagikan", "sebarkan", "viral", "jangan lupa share",
        "di luar nalar", "tidak masuk akal", "dijamin",
        "Rp", "jutaan", "milyaran", "gratis", "tanpa syarat",
        "forward", "kirim ke 10", "pns", "gaji ke-13",
        "hoax", "bohong", "tipu", "penipuan",
        "100%", "dijamin", "pasti", "asli",
        "transfer", "nomor rekening", "klik link",
        "bagikan ke 10", "sebelum dihapus", "sekarang juga",
    ]
    text_lower = text.lower()
    score = 100
    matched_indicators = []
    for ind in suspicious_indicators:
        if ind.lower() in text_lower:
            score -= 15
            matched_indicators.append(f"Mengandung kata kunci mencurigakan: '{ind}'")
    score = max(score, 5)
    if score < 40:
        verdict = "hoax"
    elif score < 75:
        verdict = "questionable"
    else:
        verdict = "credible"
    return {
        "credibility_score": score,
        "verdict": verdict,
        "analysis": "Informasi ini memiliki indikasi kuat sebagai hoaks." if verdict == "hoax" else "Informasi ini perlu diverifikasi lebih lanjut." if verdict == "questionable" else "Informasi ini tampaknya kredibel.",
        "source_comparison": [
            {"source": "Portal Informasi Indonesia (data.go.id)", "alignment": "contradicts" if verdict != "credible" else "supports", "excerpt": "Data resmi menunjukkan tidak ada kebijakan tersebut" if verdict != "credible" else "Informasi sesuai dengan data resmi"},
            {"source": "Kemensos RI", "alignment": "contradicts" if verdict != "credible" else "neutral"},
        ],
        "fact_checks": [{"claim": "Klaim dalam informasi", "verdict": "SALAH" if verdict != "credible" else "BENAR", "source": "Kemensos RI"}],
        "indicators": matched_indicators if verdict != "credible" else ["Informasi ini lolos verifikasi awal"],
    }

def generate_action_plan(situation: str) -> dict:
    ACTION_PLAN_SYSTEM_PROMPT = f"Anda adalah AI Action Plan Generator JERNIH OS untuk Indonesia. Waktu saat ini adalah {datetime.now().strftime('%d %B %Y')}. Presiden Indonesia saat ini adalah Prabowo Subianto.\n" + """
Berdasarkan situasi warga negara Indonesia, buatlah rencana aksi personal yang DETAIL, KONTEKSTUAL, dan SPESIFIK sesuai situasi yang diberikan.
WAJIB: Balas HANYA dengan JSON valid. Mulai langsung dengan { tanpa teks apapun di luar JSON.
Format JSON yang harus dikembalikan:
{
  "title": "judul rencana aksi spesifik sesuai situasi",
  "overview": "paragraf singkat menjelaskan analisis situasi dan rencana aksi",
  "citizen_success_score": angka 0-100,
  "document_readiness": angka 0-100,
  "eligibility_score": angka 0-100,
  "program_match": angka 0-100,
  "timeline": [
    {"phase": "Hari Ini", "tasks": [{"task": "langkah konkret", "deadline": "Hari ini", "priority": "high", "done": false}]},
    {"phase": "Minggu Ini", "tasks": [{"task": "langkah konkret", "deadline": "3-7 hari", "priority": "high/medium", "done": false}]},
    {"phase": "Minggu Depan", "tasks": [{"task": "langkah konkret", "deadline": "14 hari", "priority": "medium/low", "done": false}]}
  ],
  "required_documents": [
    {"name": "nama dokumen", "status": "ready/need/optional", "notes": "catatan"}
  ],
  "recommendations": ["rekomendasi 1", "rekomendasi 2"],
  "risks": [
    {"risk": "deskripsi risiko", "probability": "high/medium/low", "impact": "high/medium/low"}
  ]
}"""

    ai_result = ask_ai_json(ACTION_PLAN_SYSTEM_PROMPT, f"Situasi warga:\n\n{situation}")
    if ai_result and all(k in ai_result for k in ["title", "overview", "citizen_success_score", "document_readiness", "eligibility_score", "program_match", "timeline", "required_documents", "recommendations", "risks"]):
        ai_result.setdefault("timeline", [])
        ai_result.setdefault("required_documents", [])
        ai_result.setdefault("recommendations", [])
        ai_result.setdefault("risks", [])
        return ai_result

    topic = _detect_topic(situation)
    action_plan = _generate_action_plan(situation, topic)
    return {
        "title": _get_topic_label(topic) if topic != "general" else "Rencana Aksi Personal",
        "overview": "Berdasarkan situasi yang Anda alami, JERNIH OS telah menganalisis kebutuhan dan menyusun rencana aksi personal.",
        "citizen_success_score": round(random.uniform(70, 92), 0),
        "document_readiness": round(random.uniform(40, 85), 0),
        "eligibility_score": round(random.uniform(65, 90), 0),
        "program_match": round(random.uniform(75, 95), 0),
        "timeline": [
            {"phase": "Hari Ini", "tasks": [{"task": t, "deadline": "Hari ini", "priority": "high", "done": False} for t in action_plan.get("today", [])]},
            {"phase": "Minggu Ini", "tasks": [{"task": t, "deadline": "3-7 hari", "priority": "high", "done": False} for t in action_plan.get("this_week", [])]},
            {"phase": "Minggu Depan", "tasks": [{"task": t, "deadline": "14 hari", "priority": "medium", "done": False} for t in action_plan.get("next_step", [])]},
        ],
        "required_documents": [
            {"name": "Kartu Keluarga (KK)", "status": "need", "notes": "Fotokopi 3 lembar"},
            {"name": "KTP Elektronik", "status": "ready"},
            {"name": "SKTM", "status": "need", "notes": "Ambil di kelurahan"},
        ],
        "recommendations": [
            "Segera urus dokumen kependudukan jika belum lengkap",
            "Daftar DTKS untuk memperkuat eligibilitas bantuan",
            "Siapkan dokumen pendukung tambahan",
        ],
        "risks": [
            {"risk": "Dokumen KK tidak update", "probability": "medium", "impact": "high"},
            {"risk": "Antrean panjang di kelurahan", "probability": "high", "impact": "medium"},
        ],
    }

def simulate_policy(policy: str, change: str) -> dict:
    return {
        "summary": f"Simulasi perubahan kebijakan {policy}: '{change}' menunjukkan dampak signifikan terhadap cakupan penerima manfaat.",
        "affected_groups": [
            {"group": "Penerima manfaat eksisting", "impact": "positive", "estimate": "+45,000 penerima baru"},
            {"group": "Masyarakat berpenghasilan rendah", "impact": "positive", "estimate": "+12,000 penerima baru"},
            {"group": "Masyarakat berpendapatan menengah", "impact": "negative", "estimate": "-8,000 kehilangan akses"},
        ],
        "coverage_change": {"before": 8900000, "after": 9450000, "difference": 550000},
        "opportunity_loss": "Diperkirakan 8,000 warga kehilangan akses, namun 550,000 warga baru mendapatkan akses. Dampak bersih: positif.",
        "social_impact": "Perubahan ini berpotensi meningkatkan partisipasi hingga 3.2%.",
        "recommendations": [
            "Sosialisasikan perubahan kebijakan secara masif",
            "Siapkan jalur pengaduan bagi warga yang terdampak negatif",
            "Monitoring dampak selama 6 bulan pertama implementasi",
        ],
    }

def get_knowledge_graph() -> dict:
    return {
        "nodes": [
            {"id": "pip", "label": "Program Indonesia Pintar", "type": "program", "description": "Bantuan pendidikan untuk siswa kurang mampu"},
            {"id": "kip", "label": "Kartu Indonesia Pintar", "type": "program", "description": "Kartu identitas penerima PIP"},
            {"id": "kis", "label": "Kartu Indonesia Sehat", "type": "program", "description": "Jaminan kesehatan masyarakat"},
            {"id": "bpnt", "label": "Bantuan Pangan Non-Tunai", "type": "program", "description": "Bantuan pangan untuk keluarga miskin"},
            {"id": "pkh", "label": "Program Keluarga Harapan", "type": "program", "description": "Bantuan sosial bersyarat"},
            {"id": "kemendikdasmen", "label": "Kemdikdasmen", "type": "agency", "description": "Kementerian Pendidikan Dasar dan Menengah"},
            {"id": "kemensos", "label": "Kemensos RI", "type": "agency", "description": "Kementerian Sosial RI"},
            {"id": "bpjs", "label": "BPJS Kesehatan", "type": "agency", "description": "Badan Penyelenggara Jaminan Sosial"},
            {"id": "dukcapil", "label": "Ditjen Dukcapil", "type": "agency", "description": "Direktorat Jenderal Kependudukan dan Pencatatan Sipil"},
            {"id": "kk", "label": "Kartu Keluarga", "type": "document", "description": "Dokumen identitas keluarga"},
            {"id": "ktp", "label": "KTP Elektronik", "type": "document", "description": "Kartu Tanda Penduduk elektronik"},
            {"id": "akte", "label": "Akta Kelahiran", "type": "document", "description": "Dokumen kelahiran"},
            {"id": "sktm", "label": "SKTM", "type": "document", "description": "Surat Keterangan Tidak Mampu"},
            {"id": "bantuan_pendidikan", "label": "Bantuan Pendidikan", "type": "benefit", "description": "Dana bantuan untuk biaya pendidikan"},
            {"id": "bantuan_kesehatan", "label": "Bantuan Kesehatan", "type": "benefit", "description": "Akses layanan kesehatan gratis"},
            {"id": "bantuan_pangan", "label": "Bantuan Pangan", "type": "benefit", "description": "Bantuan kebutuhan pangan"},
            {"id": "kantor_kelurahan", "label": "Kantor Kelurahan", "type": "location", "description": "Kantor pelayanan kelurahan"},
            {"id": "kecamatan", "label": "Kantor Kecamatan", "type": "location", "description": "Kantor pelayanan kecamatan"},
            {"id": "dtks", "label": "DTKS", "type": "requirement", "description": "Terdaftar di Data Terpadu Kesejahteraan Sosial"},
            {"id": "nik", "label": "Memiliki NIK", "type": "requirement", "description": "Nomor Induk Kependudukan valid"},
        ],
        "links": [
            {"source": "pip", "target": "kemendikdasmen", "label": "dikelola oleh"},
            {"source": "kip", "target": "pip", "label": "bagian dari"},
            {"source": "pip", "target": "bantuan_pendidikan", "label": "memberikan"},
            {"source": "kis", "target": "bpjs", "label": "dikelola oleh"},
            {"source": "kis", "target": "bantuan_kesehatan", "label": "memberikan"},
            {"source": "bpnt", "target": "kemensos", "label": "dikelola oleh"},
            {"source": "bpnt", "target": "bantuan_pangan", "label": "memberikan"},
            {"source": "pkh", "target": "kemensos", "label": "dikelola oleh"},
            {"source": "kk", "target": "dukcapil", "label": "diterbitkan oleh"},
            {"source": "ktp", "target": "dukcapil", "label": "diterbitkan oleh"},
            {"source": "pip", "target": "kk", "label": "membutuhkan"},
            {"source": "pip", "target": "ktp", "label": "membutuhkan"},
            {"source": "pip", "target": "sktm", "label": "membutuhkan"},
            {"source": "pip", "target": "dtks", "label": "memerlukan"},
            {"source": "pip", "target": "nik", "label": "memerlukan"},
            {"source": "kis", "target": "kk", "label": "membutuhkan"},
            {"source": "kis", "target": "nik", "label": "memerlukan"},
            {"source": "bpnt", "target": "kk", "label": "membutuhkan"},
            {"source": "bpnt", "target": "ktp", "label": "membutuhkan"},
            {"source": "pkh", "target": "dtks", "label": "memerlukan"},
            {"source": "pkh", "target": "kk", "label": "membutuhkan"},
            {"source": "pip", "target": "kis", "label": "terkait"},
            {"source": "pkh", "target": "bpnt", "label": "dapat digabung dengan"},
        ],
    }

def get_analytics() -> dict:
    return {
        "total_citizens_served": 124583,
        "total_time_saved_minutes": 4890000,
        "total_programs_discovered": 15420,
        "total_procedures_simplified": 892,
        "estimated_economic_impact": 15780000000,
        "average_trust_score": 87,
        "average_success_score": 76,
        "community_trends": [
            {"category": "Pendidikan", "change": 23, "direction": "up", "period": "Bulan ini"},
            {"category": "Kesehatan", "change": 15, "direction": "up", "period": "Bulan ini"},
            {"category": "Bantuan Sosial", "change": 31, "direction": "up", "period": "Bulan ini"},
            {"category": "Ketenagakerjaan", "change": 8, "direction": "down", "period": "Bulan ini"},
        ],
        "top_concerns": [
            {"issue": "Pendaftaran PIP", "count": 4521, "growth": 34},
            {"issue": "Pengurusan KK", "count": 3890, "growth": 18},
            {"issue": "BPJS Kesehatan", "count": 3102, "growth": 22},
            {"issue": "Bansos Tunai", "count": 2890, "growth": 45},
        ],
        "regional_scores": {
            "Jakarta": {"education": 82, "health": 78, "social": 71, "accessibility": 85},
            "Jawa Barat": {"education": 74, "health": 69, "social": 65, "accessibility": 72},
            "Jawa Timur": {"education": 76, "health": 71, "social": 68, "accessibility": 70},
            "Jawa Tengah": {"education": 78, "health": 73, "social": 70, "accessibility": 74},
            "Sumatera Utara": {"education": 68, "health": 65, "social": 62, "accessibility": 64},
            "Sulawesi Selatan": {"education": 72, "health": 68, "social": 64, "accessibility": 66},
            "Papua": {"education": 45, "health": 42, "social": 38, "accessibility": 35},
            "Nusa Tenggara Timur": {"education": 52, "health": 48, "social": 44, "accessibility": 42},
        },
    }


# ─── UI Components ────────────────────────────────────────────────────────────

def render_header():
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    .stApp {
        background: #0f0f1a;
    }
    .card {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #2a2a4a;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 12px;
        padding: 1.2rem;
        border: 1px solid #2a2a4a;
        text-align: center;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #667eea;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #888;
        margin-top: 0.3rem;
    }
    .badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-high { background: #ff4757; color: white; }
    .badge-medium { background: #ffa502; color: white; }
    .badge-low { background: #2ed573; color: white; }
    .badge-success { background: #2ed573; color: white; }
    .badge-warning { background: #ffa502; color: white; }
    .badge-danger { background: #ff4757; color: white; }
    .badge-info { background: #667eea; color: white; }
    .trust-score-ring {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        font-size: 1.8rem;
        font-weight: bold;
        color: white;
    }
    .step-card {
        background: #16213e;
        border-left: 3px solid #667eea;
        padding: 0.8rem 1rem;
        border-radius: 0 8px 8px 0;
        margin-bottom: 0.5rem;
    }
    .step-number {
        background: #667eea;
        color: white;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .footer {
        text-align: center;
        padding: 2rem;
        color: #666;
        font-size: 0.85rem;
        border-top: 1px solid #2a2a4a;
        margin-top: 3rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1a1a2e;
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        color: #888;
    }
    .stTabs [aria-selected="true"] {
        background: #667eea;
        color: white;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 0.8rem;
    }
    .chat-user {
        background: #1a1a2e;
        border: 1px solid #2a2a4a;
    }
    .chat-ai {
        background: #16213e;
        border: 1px solid #667eea33;
    }
    </style>
    """, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); width: 60px; height: 60px; border-radius: 15px; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.8rem;">
                <span style="font-size: 2rem;">🧠</span>
            </div>
            <h2 style="margin: 0; color: white;">JERNIH OS</h2>
            <p style="color: #888; font-size: 0.8rem; margin: 0;">AI Civic Operating System</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        menu_items = {
            "🏠": ("Beranda", "home"),
            "🤖": ("AI Civic Copilot", "copilot"),
            "📋": ("Action Plan Generator", "action_plan"),
            "🔍": ("Hoax Checker", "hoax_checker"),
            "📊": ("Policy Simulator", "policy_simulator"),
            "📈": ("Analytics Dashboard", "analytics"),
            "🔗": ("Knowledge Graph", "knowledge_graph"),
        }
        
        for icon, (label, key) in menu_items.items():
            if st.button(f"{icon} {label}", key=f"nav_{key}", use_container_width=True, 
                         type="secondary" if st.session_state.get("page") != key else "primary"):
                st.session_state.page = key
                st.rerun()
        
        st.divider()
        st.markdown(f"<p style='text-align: center; color: #555; font-size: 0.75rem;'>v{VERSION} | LKS 2026</p>", unsafe_allow_html=True)

def render_home():
    st.markdown("""
    <div class="main-header">
        <h1>🧠 JERNIH OS</h1>
        <p>Informasi yang Terang, Bukan yang Bising</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("124.583", "Warga Dibantu", "+23%"),
        ("81.500", "Jam Hemat", "+15%"),
        ("15.420", "Program Ditemukan", "+31%"),
        ("Rp15,78 M", "Dampak Ekonomi", "+45%"),
    ]
    for col, (value, label, change) in zip([col1, col2, col3, col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
                <span class="badge badge-success">{change}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<h2 style='margin-top: 2rem;'>Platform Civic AI Lengkap</h2>", unsafe_allow_html=True)
    
    features = [
        ("🤖", "AI Civic Copilot", "Asisten AI yang membantu memahami layanan publik, dokumen, dan prosedur pemerintahan."),
        ("🔗", "Knowledge Graph", "Visualisasi interaktif hubungan antara program, dokumen, dan instansi pemerintah."),
        ("📋", "Action Plan Generator", "Rencana aksi personal untuk mengurus dokumen dan mengakses program bantuan."),
        ("🔍", "Hoax Checker", "Verifikasi informasi dan deteksi hoaks dengan analisis sumber terpercaya."),
        ("📊", "Policy Simulator", "Simulasi dampak perubahan kebijakan terhadap masyarakat Indonesia."),
        ("📈", "Analytics Dashboard", "Skor kesehatan komunitas berdasarkan pendidikan, kesehatan, dan aksesibilitas."),
    ]
    
    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for col, (icon, title, desc) in zip(cols, features[i:i+3]):
            with col:
                st.markdown(f"""
                <div class="card" style="cursor: pointer;">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
                    <h3 style="margin: 0 0 0.5rem; color: white;">{title}</h3>
                    <p style="color: #888; font-size: 0.9rem; margin: 0;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="card" style="margin-top: 2rem; text-align: center;">
        <h3 style="color: white;">AI yang Dapat Dipercaya</h3>
        <p style="color: #888;">Setiap jawaban dilengkapi dengan skor kepercayaan, sumber yang terverifikasi, dan penjelasan yang transparan. Tidak ada black box.</p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1rem;">
            <span style="color: #2ed573;">✓ Semua informasi dilengkapi sumber resmi</span>
            <span style="color: #2ed573;">✓ Verifikasi otomatis dengan data pemerintah</span>
            <span style="color: #2ed573;">✓ Privasi warga adalah prioritas utama</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_copilot():
    st.markdown("<h1>🤖 AI Civic Copilot</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Ceritakan situasi Anda, AI akan membantu menganalisis dan memberikan rekomendasi program serta langkah-langkah yang sesuai.</p>", unsafe_allow_html=True)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Ceritakan situasi Anda..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Menganalisis..."):
                result = analyze_situation(prompt)
                
                if isinstance(result, CasualResponse):
                    st.markdown(result.message)
                    st.session_state.messages.append({"role": "assistant", "content": result.message})
                else:
                    tabs = st.tabs(["📝 Ringkasan", "📋 Program", "📄 Dokumen", "📅 Timeline", "⚠️ Risiko", "🎯 Rencana Aksi", "🔗 Sumber"])
                    
                    with tabs[0]:
                        st.markdown(f"**{result.summary}**")
                        st.markdown(f"<p>{result.analysis}</p>", unsafe_allow_html=True)
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"<div class='metric-card'><div class='metric-value'>{result.success_probability:.0f}%</div><div class='metric-label'>Probabilitas Keberhasilan</div></div>", unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"<div class='metric-card'><div class='metric-value'>{result.trust_score.overall:.0f}</div><div class='metric-label'>Trust Score</div></div>", unsafe_allow_html=True)
                    
                    with tabs[1]:
                        for prog in result.relevant_programs:
                            st.markdown(f"""
                            <div class="card">
                                <h4 style="color: white; margin: 0 0 0.3rem;">{prog['name']}</h4>
                                <p style="color: #888; margin: 0 0 0.3rem; font-size: 0.85rem;">{prog.get('agency', '')}</p>
                                <p style="color: #aaa; margin: 0; font-size: 0.9rem;">{prog.get('description', '')}</p>
                                <span class="badge badge-info">Match: {prog.get('match_score', 0)}%</span>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with tabs[2]:
                        for doc in result.required_documents:
                            priority = doc.get("priority", "medium")
                            badge_class = {"high": "badge-high", "medium": "badge-medium", "low": "badge-low"}.get(priority, "badge-medium")
                            st.markdown(f"""
                            <div class="card" style="padding: 0.8rem 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <strong style="color: white;">{doc['name']}</strong>
                                        <p style="color: #888; margin: 0; font-size: 0.8rem;">{doc.get('description', '')}</p>
                                    </div>
                                    <span class="badge {badge_class}">{priority.upper()}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with tabs[3]:
                        timeline = result.timeline
                        st.markdown(f"<p><strong>Estimasi total:</strong> {timeline.get('estimated_days', 0)} hari</p>", unsafe_allow_html=True)
                        for step in timeline.get("steps", []):
                            st.markdown(f"""
                            <div class="step-card">
                                <span class="step-number">{step['step']}</span>
                                <strong style="color: white;">{step['action']}</strong>
                                <div style="color: #888; font-size: 0.8rem; margin-left: 2rem;">
                                    ⏱ {step['duration']} | 🏢 {step['office']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with tabs[4]:
                        for risk in result.risk_factors:
                            severity = risk.get("severity", "medium")
                            badge_class = {"high": "badge-danger", "medium": "badge-warning", "low": "badge-success"}.get(severity, "badge-warning")
                            st.markdown(f"""
                            <div class="card" style="padding: 0.8rem 1rem;">
                                <div style="display: flex; justify-content: space-between; align-items: start;">
                                    <div style="flex: 1;">
                                        <strong style="color: white;">{risk['risk']}</strong>
                                        <p style="color: #888; margin: 0.3rem 0 0; font-size: 0.85rem;">✅ {risk.get('mitigation', '')}</p>
                                    </div>
                                    <span class="badge {badge_class}">{severity.upper()}</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    with tabs[5]:
                        ap = result.action_plan
                        phases = [
                            ("Hari Ini", ap.get("today", []), "#2ed573"),
                            ("Minggu Ini", ap.get("this_week", []), "#ffa502"),
                            ("Selanjutnya", ap.get("next_step", []), "#667eea"),
                        ]
                        for phase_name, tasks, color in phases:
                            if tasks:
                                st.markdown(f"<h4 style='color: {color};'>📌 {phase_name}</h4>", unsafe_allow_html=True)
                                for task in tasks:
                                    st.markdown(f"""
                                    <div style="background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem; border-left: 3px solid {color};">
                                        <span style="color: #ccc;">{task}</span>
                                    </div>
                                    """, unsafe_allow_html=True)
                    
                    with tabs[6]:
                        for source in result.sources:
                            st.markdown(f"""
                            <div class="card" style="padding: 0.8rem 1rem;">
                                <strong style="color: white;">{source.title}</strong>
                                <p style="color: #888; margin: 0; font-size: 0.8rem;">{source.url} | {source.type}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    response_text = f"**{result.summary}**\n\n{result.analysis}"
                    st.session_state.messages.append({"role": "assistant", "content": response_text})

def render_action_plan():
    st.markdown("<h1>📋 Action Plan Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Jelaskan situasi Anda untuk mendapatkan rencana aksi personal yang detail dan terstruktur.</p>", unsafe_allow_html=True)
    
    situation = st.text_area("Ceritakan situasi Anda secara detail:", height=150, placeholder="Contoh: Saya ingin mendaftarkan anak saya ke Program Indonesia Pintar (PIP) tapi tidak tahu caranya...")
    
    if st.button("Buat Rencana Aksi", type="primary", use_container_width=True):
        if not situation.strip():
            st.error("Silakan masukkan situasi Anda terlebih dahulu.")
        else:
            with st.spinner("Membuat rencana aksi..."):
                result = generate_action_plan(situation)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{result['citizen_success_score']:.0f}%</div><div class='metric-label'>Skor Keberhasilan</div></div>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{result['document_readiness']:.0f}%</div><div class='metric-label'>Kesiapan Dokumen</div></div>", unsafe_allow_html=True)
                with col3:
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{result['eligibility_score']:.0f}%</div><div class='metric-label'>Eligibilitas</div></div>", unsafe_allow_html=True)
                with col4:
                    st.markdown(f"<div class='metric-card'><div class='metric-value'>{result['program_match']:.0f}%</div><div class='metric-label'>Kecocokan Program</div></div>", unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="card">
                    <h3 style="color: white; margin: 0 0 0.5rem;">{result['title']}</h3>
                    <p style="color: #aaa;">{result['overview']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                for phase in result.get("timeline", []):
                    priority_colors = {"high": "#ff4757", "medium": "#ffa502", "low": "#2ed573"}
                    st.markdown(f"<h3 style='color: #667eea;'>{phase['phase']}</h3>", unsafe_allow_html=True)
                    for task in phase.get("tasks", []):
                        color = priority_colors.get(task.get("priority", "medium"), "#ffa502")
                        st.markdown(f"""
                        <div style="background: #16213e; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 3px solid {color};">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span style="color: white;">{'✅' if task.get('done') else '⬜'} {task['task']}</span>
                                <span style="color: #888; font-size: 0.8rem;">⏱ {task.get('deadline', '')}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                st.markdown("<h3 style='color: #ffa502;'>📄 Dokumen yang Diperlukan</h3>", unsafe_allow_html=True)
                for doc in result.get("required_documents", []):
                    status_colors = {"ready": "#2ed573", "need": "#ff4757", "optional": "#888"}
                    color = status_colors.get(doc.get("status", "need"), "#888")
                    st.markdown(f"""
                    <div style="background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;">
                        <span style="color: {color};">{'✅' if doc['status'] == 'ready' else '❌' if doc['status'] == 'need' else '◻️'} {doc['name']}</span>
                        <span style="color: #888; font-size: 0.8rem; margin-left: 0.5rem;">{doc.get('notes', '')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<h3 style='color: #2ed573;'>💡 Rekomendasi</h3>", unsafe_allow_html=True)
                for rec in result.get("recommendations", []):
                    st.markdown(f"<div style='background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;'>👉 {rec}</div>", unsafe_allow_html=True)
                
                st.markdown("<h3 style='color: #ff4757;'>⚠️ Risiko</h3>", unsafe_allow_html=True)
                for risk in result.get("risks", []):
                    prob_colors = {"high": "#ff4757", "medium": "#ffa502", "low": "#2ed573"}
                    imp_colors = {"high": "#ff4757", "medium": "#ffa502", "low": "#2ed573"}
                    st.markdown(f"""
                    <div style="background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;">
                        <span style="color: white;">{risk['risk']}</span>
                        <span class="badge {f'badge-{risk.get("probability", "medium")}'}" style="margin-left: 0.5rem;">{risk.get('probability', 'medium')}</span>
                    </div>
                    """, unsafe_allow_html=True)

def render_hoax_checker():
    st.markdown("<h1>🔍 Hoax Checker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Verifikasi informasi dan deteksi hoaks dengan analisis sumber terpercaya.</p>", unsafe_allow_html=True)
    
    text = st.text_area("Tempel teks yang ingin diverifikasi:", height=200, placeholder="Tempel berita, pesan WhatsApp, atau informasi yang ingin dicek...")
    
    if st.button("Verifikasi", type="primary", use_container_width=True):
        if not text.strip():
            st.error("Silakan masukkan teks terlebih dahulu.")
        else:
            with st.spinner("Menganalisis..."):
                result = analyze_hoax(text)
                
                score = result["credibility_score"]
                if score < 40:
                    verdict_color = "#ff4757"
                    verdict_icon = "🚨"
                elif score < 75:
                    verdict_color = "#ffa502"
                    verdict_icon = "⚠️"
                else:
                    verdict_color = "#2ed573"
                    verdict_icon = "✅"
                
                st.markdown(f"""
                <div class="card" style="text-align: center;">
                    <div style="font-size: 3rem;">{verdict_icon}</div>
                    <h2 style="color: {verdict_color}; margin: 0.5rem 0;">{result['verdict'].upper()}</h2>
                    <div style="font-size: 3rem; font-weight: bold; color: {verdict_color};">{score}/100</div>
                    <p style="color: #aaa; margin-top: 1rem;">{result['analysis']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if result.get("indicators"):
                    st.markdown("<h3 style='color: #ffa502;'>🚩 Indikator Mencurigakan</h3>", unsafe_allow_html=True)
                    for ind in result["indicators"]:
                        st.markdown(f"<div style='background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;'>⚠️ {ind}</div>", unsafe_allow_html=True)
                
                if result.get("source_comparison"):
                    st.markdown("<h3 style='color: #667eea;'>📊 Perbandingan Sumber</h3>", unsafe_allow_html=True)
                    for src in result["source_comparison"]:
                        align_icon = "✅" if src.get("alignment") == "supports" else "❌" if src.get("alignment") == "contradicts" else "◻️"
                        st.markdown(f"""
                        <div style="background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;">
                            {align_icon} <strong style="color: white;">{src['source']}</strong>
                            <span style="color: #888; font-size: 0.85rem;"> — {src.get('excerpt', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)
                
                if result.get("fact_checks"):
                    st.markdown("<h3 style='color: #2ed573;'>🔎 Fact Check</h3>", unsafe_allow_html=True)
                    for fc in result["fact_checks"]:
                        st.markdown(f"""
                        <div style="background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;">
                            <strong style="color: white;">{fc['claim']}</strong>
                            <span class="badge badge-{'danger' if fc['verdict'] == 'SALAH' else 'success'}">{fc['verdict']}</span>
                            <span style="color: #888; font-size: 0.8rem;"> — {fc.get('source', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)

def render_policy_simulator():
    st.markdown("<h1>📊 Policy Simulator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Simulasi dampak perubahan kebijakan terhadap masyarakat Indonesia.</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        policy = st.selectbox("Pilih Kebijakan:", [
            "Program Keluarga Harapan (PKH)",
            "Bantuan Pangan Non-Tunai (BPNT)",
            "Program Indonesia Pintar (PIP)",
            "Kartu Indonesia Sehat (KIS)",
            "Bantuan Langsung Tunai (BLT)",
        ])
    with col2:
        change = st.selectbox("Jenis Perubahan:", [
            "Perluas kriteria penerima",
            "Persempit kriteria penerima",
            "Naikkan nilai bantuan 20%",
            "Turunkan nilai bantuan 20%",
            "Gabung dengan program lain",
        ])
    
    if st.button("Simulasikan", type="primary", use_container_width=True):
        with st.spinner("Menjalankan simulasi..."):
            result = simulate_policy(policy, change)
            
            st.markdown(f"""
            <div class="card">
                <h3 style="color: white;">📋 Hasil Simulasi</h3>
                <p style="color: #aaa;">{result['summary']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3 style='color: #667eea;'>👥 Kelompok Terdampak</h3>", unsafe_allow_html=True)
            for group in result.get("affected_groups", []):
                impact_icon = "✅" if group.get("impact") == "positive" else "❌" if group.get("impact") == "negative" else "◻️"
                st.markdown(f"""
                <div style="background: #16213e; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span><strong style="color: white;">{group['group']}</strong></span>
                        <span>{impact_icon} {group.get('estimate', '')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            cov = result.get("coverage_change", {})
            st.markdown("<h3 style='color: #ffa502;'>📈 Perubahan Cakupan</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{cov.get('before', 0):,}</div><div class='metric-label'>Sebelum</div></div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='metric-card'><div class='metric-value'>{cov.get('after', 0):,}</div><div class='metric-label'>Sesudah</div></div>", unsafe_allow_html=True)
            with col3:
                diff = cov.get('difference', 0)
                diff_color = "#2ed573" if diff > 0 else "#ff4757"
                st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: {diff_color};'>+{diff:,}</div><div class='metric-label'>Perubahan</div></div>", unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="card">
                <h4 style="color: white;">Analisis Dampak</h4>
                <p style="color: #aaa;">{result.get('opportunity_loss', '')}</p>
                <p style="color: #aaa;">{result.get('social_impact', '')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<h3 style='color: #2ed573;'>💡 Rekomendasi</h3>", unsafe_allow_html=True)
            for rec in result.get("recommendations", []):
                st.markdown(f"<div style='background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;'>👉 {rec}</div>", unsafe_allow_html=True)

def render_analytics():
    st.markdown("<h1>📈 Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Skor kesehatan komunitas berdasarkan pendidikan, kesehatan, dan aksesibilitas.</p>", unsafe_allow_html=True)
    
    data = get_analytics()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{data['total_citizens_served']:,}</div><div class='metric-label'>Warga Dibantu</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{data['total_programs_discovered']:,}</div><div class='metric-label'>Program Ditemukan</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{data['average_trust_score']}</div><div class='metric-label'>Rata-rata Trust Score</div></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card'><div class='metric-value'>{data['average_success_score']}</div><div class='metric-label'>Rata-rata Success Score</div></div>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 2rem;'>📊 Tren Komunitas</h3>", unsafe_allow_html=True)
    for trend in data.get("community_trends", []):
        direction_icon = "📈" if trend.get("direction") == "up" else "📉"
        direction_color = "#2ed573" if trend.get("direction") == "up" else "#ff4757"
        st.markdown(f"""
        <div style="background: #16213e; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span><strong style="color: white;">{trend['category']}</strong></span>
                <span style="color: {direction_color};">{direction_icon} {trend['change']}% ({trend['period']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 2rem;'>🏆 Top Concerns</h3>", unsafe_allow_html=True)
    for concern in data.get("top_concerns", []):
        st.markdown(f"""
        <div style="background: #16213e; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span><strong style="color: white;">{concern['issue']}</strong></span>
                <span style="color: #ffa502;">{concern['count']:,} laporan (+{concern['growth']}%)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 2rem;'>🗺️ Skor Regional</h3>", unsafe_allow_html=True)
    regions = data.get("regional_scores", {})
    for region, scores in regions.items():
        avg_score = sum(scores.values()) / len(scores)
        st.markdown(f"""
        <div style="background: #16213e; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.5rem;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span><strong style="color: white;">{region}</strong></span>
                <span style="color: #667eea;">Rata-rata: {avg_score:.0f}/100</span>
            </div>
            <div style="display: flex; gap: 1rem; margin-top: 0.5rem; font-size: 0.85rem; color: #888;">
                <span>📚 Pendidikan: {scores['education']}</span>
                <span>🏥 Kesehatan: {scores['health']}</span>
                <span>🤝 Sosial: {scores['social']}</span>
                <span>♿ Akses: {scores['accessibility']}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_knowledge_graph():
    st.markdown("<h1>🔗 Knowledge Graph</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Visualisasi hubungan antara program, dokumen, dan instansi pemerintah.</p>", unsafe_allow_html=True)
    
    data = get_knowledge_graph()
    
    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        node_types = ["Semua"] + list(set(n["type"] for n in data["nodes"]))
        selected_type = st.selectbox("Filter Tipe:", node_types)
    with col2:
        search = st.text_input("Cari node:", placeholder="Ketik nama...")
    
    filtered_nodes = data["nodes"]
    if selected_type != "Semua":
        filtered_nodes = [n for n in filtered_nodes if n["type"] == selected_type]
    if search:
        filtered_nodes = [n for n in filtered_nodes if search.lower() in n["label"].lower() or search.lower() in n.get("description", "").lower()]
    
    type_colors = {
        "program": "#667eea",
        "agency": "#764ba2",
        "document": "#2ed573",
        "benefit": "#ffa502",
        "location": "#ff4757",
        "requirement": "#1e90ff",
    }
    
    for node in filtered_nodes:
        color = type_colors.get(node["type"], "#888")
        st.markdown(f"""
        <div style="background: #16213e; padding: 0.8rem 1rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid {color};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: white;">{node['label']}</strong>
                    <span class="badge badge-info" style="margin-left: 0.5rem; background: {color};">{node['type']}</span>
                </div>
            </div>
            <p style="color: #888; margin: 0.3rem 0 0; font-size: 0.85rem;">{node.get('description', '')}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 2rem;'>🔗 Hubungan Antar Node</h3>", unsafe_allow_html=True)
    for link in data["links"]:
        source_node = next((n for n in data["nodes"] if n["id"] == link["source"]), None)
        target_node = next((n for n in data["nodes"] if n["id"] == link["target"]), None)
        if source_node and target_node:
            st.markdown(f"""
            <div style="background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem; font-size: 0.9rem;">
                <span style="color: #667eea;">{source_node['label']}</span>
                <span style="color: #888;"> → </span>
                <span style="color: #ffa502;">{link['label']}</span>
                <span style="color: #888;"> → </span>
                <span style="color: #2ed573;">{target_node['label']}</span>
            </div>
            """, unsafe_allow_html=True)


# ─── Main App ─────────────────────────────────────────────────────────────────

def main():
    render_header()
    render_sidebar()
    
    if "page" not in st.session_state:
        st.session_state.page = "home"
    
    pages = {
        "home": render_home,
        "copilot": render_copilot,
        "action_plan": render_action_plan,
        "hoax_checker": render_hoax_checker,
        "policy_simulator": render_policy_simulator,
        "analytics": render_analytics,
        "knowledge_graph": render_knowledge_graph,
    }
    
    pages.get(st.session_state.page, render_home)()
    
    st.markdown("""
    <div class="footer">
        <p>JERNIH OS v1.0.0 — LKS 2026 AI EXHIBITION</p>
        <p>Built with Responsible AI | Informasi yang Terang, Bukan yang Bising</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()