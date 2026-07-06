import streamlit as st
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import os
import base64
import io
import time
from datetime import datetime

from src.config import OPENROUTER_URL, SITE_URL, SITE_TITLE

# Get API keys
try:
    OPENROUTER_KEY = os.environ.get("OPENAI_API_KEY", "") or st.secrets["OPENAI_API_KEY"]
except Exception:
    OPENROUTER_KEY = ""

try:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") or st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = ""

st.set_page_config(
    page_title="Smart Scanner - JERNIH OS",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.ui_components import inject_css

inject_css()

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

try:
    from fpdf import FPDF
    HAS_FPDF = True
except ImportError:
    HAS_FPDF = False

import subprocess

import shutil

TESSERACT_PATH = shutil.which("tesseract") or "/usr/bin/tesseract"
TESSERACT_AVAILABLE = bool(shutil.which("tesseract")) or os.path.exists("/usr/bin/tesseract")


# ── OCR: Local Tesseract first, then OpenRouter fallback ──

def encode_image(uploaded_file) -> str:
    return base64.b64encode(uploaded_file.getvalue()).decode("utf-8")


def ocr_local(image_bytes: bytes) -> str | None:
    if not TESSERACT_AVAILABLE:
        return None
    try:
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        img = Image.open(io.BytesIO(image_bytes))
        text = pytesseract.image_to_string(img, lang="eng+ind")
        text = text.strip()
        return text if text else None
    except Exception:
        return None


def ocr_via_gemini_vision(image_bytes: bytes) -> str | None:
    if not GEMINI_API_KEY:
        return None
    for attempt in range(2):
        try:
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            img = Image.open(io.BytesIO(image_bytes))
            model = genai.GenerativeModel("gemini-2.0-flash")
            resp = model.generate_content(
                ["Extract ALL text from this image exactly as written. Return ONLY the raw text with no extra words.", img],
            )
            if resp and resp.text and resp.text.strip():
                return resp.text.strip()
            return None
        except Exception:
            if attempt == 0:
                import time; time.sleep(3)
                continue
            return None
    return None


def run_ocr(uploaded_file) -> tuple[str, bool]:
    image_bytes = uploaded_file.getvalue()

    # 1. Local OCR (Tesseract)
    text = ocr_local(image_bytes)
    if text:
        return text, True

    # 2. Gemini Vision OCR (works on cloud, uses Gemini API)
    text = ocr_via_gemini_vision(image_bytes)
    if text:
        return text, True

    # 3. OpenRouter API for vision
    if OPENROUTER_KEY:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        mime = uploaded_file.type or "image/jpeg"
        data_url = f"data:{mime};base64,{b64}"

        models = [
            "openai/gpt-4o-mini:free",
            "meta-llama/llama-3.2-11b-vision-instruct:free",
            "google/gemini-2.0-flash-exp:free",
        ]
        for model in models:
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=OPENROUTER_KEY,
                    base_url="https://openrouter.ai/api/v1",
                    default_headers={"HTTP-Referer": SITE_URL, "X-Title": SITE_TITLE},
                )
                resp = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": [
                        {"type": "text", "text": "Extract ALL text from this image exactly as written. Return ONLY the raw text."},
                        {"type": "image_url", "image_url": {"url": data_url}},
                    ]}],
                    max_tokens=2048, temperature=0.0, timeout=25,
                )
                raw = resp.choices[0].message.content
                if raw and raw.strip():
                    return raw.strip(), True
            except Exception:
                continue

    return (
        "Gambar ini tidak bisa di-scan otomatis.\n"
        "Ketik manual teks yang ada di gambar ke kolom di bawah.",
        False
    )


# ── PDF Generation ──

def generate_pdf(text: str, filename: str = "scan_result") -> bytes:
    if HAS_FPDF:
        return generate_pdf_fpdf(text, filename)
    return generate_pdf_simple(text)


def _clean_text_for_pdf(text: str) -> str:
    replacements = {
        "\u201d": '"', "\u201c": '"', "\u2018": "'", "\u2019": "'",
        "\u2013": "-", "\u2014": "-", "\u2026": "...", "\u00a0": " ",
        "\u2022": "-", "\u25cf": "*", "\u25e6": "*", "\u2713": "v",
        "\u2714": "v", "\u2716": "x", "\u2718": "x",
        "\ufe0f": "", "\u20b9": "Rp", "\u20a8": "Rp",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    result = []
    for ch in text:
        try:
            ch.encode("latin-1")
            result.append(ch)
        except UnicodeEncodeError:
            result.append("?")
    return "".join(result)


def generate_pdf_fpdf(text: str, filename: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 8, "Smart Scanner - JERNIH OS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 7)
    pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Source: {filename}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    pdf.set_font("Helvetica", "", 9)
    cleaned = _clean_text_for_pdf(text)
    pdf.multi_cell(w=0, h=4.5, text=cleaned)
    out = pdf.output()
    if isinstance(out, bytearray):
        out = bytes(out)
    return out


def generate_pdf_simple(text: str) -> bytes:
    safe = text.encode("ascii", "replace").decode("ascii")
    body = "\n".join(line for line in safe.split("\n"))
    pdf_content = f"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Contents 4 0 R/Resources<</Font<</F1 5 0 R>>>>>>endobj
4 0 obj<</Length 6 0 R>>stream
BT /F1 11 Tf 50 750 Td 14 TL
({body}) Tj
ET
endstream
endobj
5 0 obj<</Type/Font/Subtype/Type1/BaseFont/Courier>>endobj
6 0 obj
{len(body)+10}
endobj
xref
0 7
...
trailer<</Size 7/Root 1 0 R>>
startxref
XXX
%%EOF"""
    return pdf_content.encode("latin-1", "replace")


# ── UI ──

def render_page():
    st.markdown("""
    <div class="main-header fade-in">
        <h1>📸 Smart Scanner</h1>
        <p>AI-Powered Picture-to-Text OCR — Extract, Copy & Download</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(
        "<p style='color: #888;'>Upload gambar untuk mengekstrak semua teks secara otomatis. Hasil bisa disalin atau diunduh sebagai PDF.</p>",
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Upload Gambar (JPG, PNG, JPEG, BMP, WEBP)",
        type=["jpg", "png", "jpeg", "bmp", "webp"],
    )

    if uploaded_file is None:
        with st.container():
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown("""
                <div style="text-align: center; padding: 3rem 1rem; color: rgba(255,255,255,0.3);">
                    <div style="font-size: 4rem; margin-bottom: 1rem;">📄</div>
                    <p style="font-size: 1.1rem;">Upload gambar untuk memulai</p>
                    <p style="font-size: 0.85rem;">Dukung format JPG, PNG, JPEG, BMP, WEBP</p>
                </div>
                """, unsafe_allow_html=True)
        return

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h3 style='color: #667eea;'>📷 Gambar Asli</h3>", unsafe_allow_html=True)
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

    with col2:
        st.markdown("<h3 style='color: #2ed573;'>📝 Hasil Ekstraksi Teks</h3>", unsafe_allow_html=True)

        scan_btn = st.button("🔍 Scan Text dari Gambar", type="primary", use_container_width=True)

        if "ocr_text" not in st.session_state:
            st.session_state.ocr_text = ""
        if "ocr_is_ai" not in st.session_state:
            st.session_state.ocr_is_ai = False
        if "ocr_done" not in st.session_state:
            st.session_state.ocr_done = False

        if scan_btn:
            with st.spinner("🧠 AI Vision sedang mengekstrak teks..."):
                time.sleep(0.5)
                extracted_text, is_ai = run_ocr(uploaded_file)
                st.session_state.ocr_text = extracted_text
                st.session_state.ocr_is_ai = is_ai
                st.session_state.ocr_done = True

            if is_ai:
                st.success("✅ Teks berhasil diekstrak oleh AI Vision!")
            else:
                st.info("ℹ️ Teks tidak bisa diekstrak otomatis. Silakan edit manual.")

        if st.session_state.ocr_done:
            edited_text = st.text_area(
                "Edit teks jika perlu:",
                value=st.session_state.ocr_text,
                height=300,
                key="text_editor",
            )
            st.session_state.ocr_text = edited_text

            word_count = len(edited_text.split()) if edited_text else 0
            char_count = len(edited_text) if edited_text else 0

            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Kata", word_count)
            with col_m2:
                st.metric("Karakter", char_count)
            with col_m3:
                source_label = "AI Vision" if st.session_state.ocr_is_ai else "Manual"
                st.metric("Sumber", source_label)

            st.markdown("<div style='margin: 0.5rem 0;'>", unsafe_allow_html=True)

            with st.expander("📋 Teks Hasil Scan (bisa dicopy dari sini)", expanded=True):
                st.code(edited_text if edited_text else "(kosong)", language="text")

            st.markdown("</div>", unsafe_allow_html=True)

            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

            with btn_col1:
                if edited_text:
                    st.download_button(
                        label="📋 Salin sebagai TXT",
                        data=edited_text.encode("utf-8"),
                        file_name=f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        use_container_width=True,
                    )

            with btn_col2:
                if edited_text and HAS_FPDF:
                    try:
                        pdf_bytes = generate_pdf(edited_text, uploaded_file.name)
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception as pdf_err:
                        st.warning(f"Gagal generate PDF: {pdf_err}")

            with btn_col3:
                if edited_text:
                    st.download_button(
                        label="📄 Download DOC",
                        data=f"<html><body><pre>{edited_text}</pre></body></html>".encode("utf-8"),
                        file_name=f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        use_container_width=True,
                    )

            with btn_col4:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.ocr_text = ""
                    st.session_state.ocr_done = False
                    st.rerun()


if __name__ == "__main__":
    render_page()
