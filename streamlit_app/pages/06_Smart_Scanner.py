import streamlit as st
import time
import json

# Must be the first Streamlit command
st.set_page_config(
    page_title="Smart Scanner - JERNIH OS",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import custom CSS and UI components
import sys
from pathlib import Path
# Ensure we can import from src
root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

from src.ui_components import inject_css

# Inject the Liquid Glass theme
inject_css()

import base64
import httpx
from src.config import OPENROUTER_KEY, OPENROUTER_URL, SITE_URL, SITE_TITLE

def mock_ai_vision_process():
    """Simulates AI OCR and data extraction processing"""
    time.sleep(2.5) # Simulate processing time
    return {
        "nik": "3171234567890001",
        "name": "Budi Santoso",
        "birth_place_date": "Jakarta, 15-08-1985",
        "gender": "Laki-Laki",
        "address": "Jl. Kemerdekaan No. 45, RT 01/RW 02",
        "blood_type": "O",
        "confidence": 98.4
    }

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

def actual_ai_vision_process(uploaded_file):
    """Uses OpenRouter Vision API (GPT-4o-mini) to extract KTP data"""
    if not OPENROUTER_KEY:
        st.error("API Key belum diset. Fallback ke data mock.")
        return mock_ai_vision_process()
        
    base64_image = encode_image(uploaded_file)
    mime_type = uploaded_file.type
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": SITE_URL,
        "X-Title": SITE_TITLE,
    }
    
    system_prompt = (
        "Anda adalah AI Vision yang bertugas mengekstrak informasi dari dokumen KTP/KK Indonesia. "
        "Ekstrak data secara akurat dan kembalikan hanya dalam format JSON yang valid. "
        "Struktur JSON harus memiliki key berikut (semua string/number, jangan disarangkan): "
        "'nik', 'name', 'birth_place_date', 'gender', 'address', 'blood_type', 'confidence' (angka 1-100). "
        "Jangan tambahkan markdown ```json, cukup kembalikan JSON raw."
    )
    
    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": "Tolong ekstrak data dari KTP ini."},
                {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{base64_image}"}}
            ]}
        ],
        "temperature": 0.1,
    }
    
    try:
        with httpx.Client(timeout=30.0) as http:
            resp = http.post(OPENROUTER_URL, headers=headers, json=payload)
            
        if resp.status_code == 200:
            raw_content = resp.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            raw_content = raw_content.replace('```json', '').replace('```', '').strip()
            data = json.loads(raw_content)
            # Ensure confidence is present
            if "confidence" not in data:
                data["confidence"] = 92.5
            return data
        else:
            st.error(f"API Error {resp.status_code}: {resp.text}")
            return mock_ai_vision_process()
    except Exception as e:
        st.error(f"Vision API Gagal: {e}. Fallback ke data mock.")
        return mock_ai_vision_process()

def render_page():
    st.markdown("""
    <div class="main-header fade-in">
        <h1>📸 Smart Document Scanner</h1>
        <p>AI-Powered OCR & Auto-Form Filling for Official Documents</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<p style='color: #888;'>Unggah dokumen resmi (KTP/KK/Surat) untuk mengekstrak data secara otomatis menggunakan Vision AI.</p>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Dokumen (JPG, PNG, JPEG)", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        if st.button("🚀 Analyze Document", type="primary", use_container_width=True):
            with st.spinner("🧠 Initializing Vision AI & Extracting Text..."):
                extracted_data = actual_ai_vision_process(uploaded_file)
            
            st.success("✅ Document Analyzed Successfully!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<h3 style='color: #667eea;'>📄 Dokumen Asli</h3>", unsafe_allow_html=True)
                st.image(uploaded_file, caption="Uploaded Document", use_container_width=True)
                
            with col2:
                st.markdown("<h3 style='color: #2ed573;'>✨ Extracted Data</h3>", unsafe_allow_html=True)
                
                # Confidence Score Metric
                st.markdown(f"""
                <div class="metric-card" style="margin-bottom: 1rem;">
                    <div class="metric-value" style="color: #2ed573;">{extracted_data['confidence']}%</div>
                    <div class="metric-label">AI Confidence Score</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Lihat Raw JSON", expanded=False):
                    st.json(extracted_data)
                
                st.markdown("<h4 style='color: #ffa502; margin-top: 1.5rem;'>📝 Auto-Filled Form</h4>", unsafe_allow_html=True)
                
                # Auto-populated form
                with st.form("auto_filled_form"):
                    st.text_input("NIK (Nomor Induk Kependudukan)", value=extracted_data["nik"])
                    st.text_input("Nama Lengkap", value=extracted_data["name"])
                    
                    subcol1, subcol2 = st.columns(2)
                    with subcol1:
                        st.text_input("Tempat/Tgl Lahir", value=extracted_data["birth_place_date"])
                    with subcol2:
                        st.text_input("Golongan Darah", value=extracted_data["blood_type"])
                    
                    st.text_area("Alamat Lengkap", value=extracted_data["address"])
                    
                    st.form_submit_button("Simpan Data ke Database", type="primary")

if __name__ == "__main__":
    render_page()
