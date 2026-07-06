import streamlit as st
import sys
from pathlib import Path

root_path = Path(__file__).parent.parent
if str(root_path) not in sys.path:
    sys.path.append(str(root_path))

import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Tentang - JERNIH OS", page_icon="🧠", layout="wide", initial_sidebar_state="expanded")

from src.ui_components import inject_css
inject_css()

TODAY = datetime.now().strftime("%d %B %Y")

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');
.glow-text {{ font-family: 'Playfair Display', serif; font-style: italic; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3.5rem; font-weight: 700; text-align: center; margin: 0; }}
.glow-sub {{ font-family: 'Inter', sans-serif; text-align: center; color: rgba(255,255,255,0.6); font-size: 1.1rem; margin-top: 0.3rem; font-weight: 300; letter-spacing: 0.05em; }}
.feature-card {{ background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02)); border: 1px solid rgba(255,255,255,0.08); border-radius: 20px; padding: 1.5rem; transition: all 0.3s ease; height: 100%; }}
.feature-card:hover {{ transform: translateY(-6px); border-color: rgba(102,126,234,0.3); box-shadow: 0 12px 40px rgba(102,126,234,0.15); }}
.feature-icon {{ font-size: 2rem; margin-bottom: 0.5rem; display: block; }}
.feature-title {{ color: #E5E7EB; font-size: 1rem; font-weight: 600; margin: 0 0 0.3rem 0; }}
.feature-desc {{ color: rgba(255,255,255,0.5); font-size: 0.8rem; line-height: 1.5; margin: 0; }}
.stat-box {{ background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06); border-radius: 16px; padding: 1.2rem; text-align: center; }}
.stat-number {{ font-size: 2rem; font-weight: 700; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
.stat-label {{ color: rgba(255,255,255,0.5); font-size: 0.75rem; margin-top: 0.2rem; }}
.arch-node {{ display: inline-block; padding: 0.5rem 1.2rem; border-radius: 30px; font-size: 0.8rem; font-weight: 500; margin: 0.2rem; }}
.step-container {{ position: relative; padding-left: 2rem; margin: 0.8rem 0; }}
.step-line {{ position: absolute; left: 0.5rem; top: 0.3rem; bottom: 0.3rem; width: 2px; background: linear-gradient(180deg, #667eea, #764ba2); border-radius: 1px; }}
.step-dot {{ position: absolute; left: 0.2rem; top: 0.3rem; width: 1.1rem; height: 1.1rem; border-radius: 50%; background: linear-gradient(135deg, #667eea, #764ba2); display: flex; align-items: center; justify-content: center; font-size: 0.5rem; color: white; font-weight: 700; }}
.step-content {{ color: rgba(255,255,255,0.75); font-size: 0.85rem; }}
.step-title {{ color: #E5E7EB; font-weight: 600; font-size: 0.95rem; }}
.tech-pill {{ display: inline-block; padding: 0.3rem 0.9rem; border-radius: 20px; font-size: 0.75rem; background: rgba(102,126,234,0.12); border: 1px solid rgba(102,126,234,0.2); color: rgba(255,255,255,0.8); margin: 0.15rem; }}
</style>
""", unsafe_allow_html=True)

# ── Hero ──
col_h1, col_h2, col_h3 = st.columns([1, 2, 1])
with col_h2:
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0 0.5rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🧠</div>
        <p class="glow-text">JERNIH.</p>
        <p class="glow-sub">Informasi yang Terang, Bukan yang Bising</p>
        <p style="color: rgba(255,255,255,0.25); font-size: 0.75rem; margin-top: 0.3rem;">AI Civic Operating System — LKS 2026 AI Exhibition</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 3D Architecture Graph ──
st.markdown("<h3 style='color: #E5E7EB; text-align: center; font-weight: 500;'>🌐 Arsitektur Multi-AI JERNIH</h3>", unsafe_allow_html=True)

nodes = [
    "User", "Web Search", "RAG DB", "Groq\nLlama 3.1", "Gemini\nAPI",
    "OpenRouter\nNemotron", "Smart\nScanner", "Hoax\nChecker", "Action\nPlan", "Policy\nSim",
    "Predictive\nMap", "Knowledge\nGraph"
]
colors = ["#667eea", "#2ed573", "#ffa502", "#764ba2", "#1e90ff",
          "#ff4757", "#a78bfa", "#2ed573", "#ffa502", "#1e90ff",
          "#ff4757", "#764ba2"]
sizes = [20, 14, 14, 18, 18, 18, 14, 14, 14, 14, 14, 14]

edges = [
    (0, 1), (0, 2), (0, 3), (0, 4), (0, 5),
    (3, 6), (3, 7), (3, 8), (3, 9), (4, 6), (5, 7),
    (8, 2), (7, 2), (6, 10), (8, 11), (9, 11), (10, 11),
]
edge_labels = [
    "bertanya", "cari web", "cari data", "AI utama", "cadangan", "cadangan",
    "OCR", "verifikasi", "rencana", "simulasi", "Gemini", "Nemotron",
    "RAG", "RAG", "peta", "graf", "graf", "peta"
]

pos = {}
pos[0] = np.array([0, 2, 0])
pos[1] = np.array([-2, 1, 0.5])
pos[2] = np.array([2, 1, -0.5])
pos[3] = np.array([-1, 0, 1])
pos[4] = np.array([1, 0, -1])
pos[5] = np.array([0, -0.5, 0])
pos[6] = np.array([-2.5, -1, 0.8])
pos[7] = np.array([-0.5, -1.5, 1.5])
pos[8] = np.array([0.5, -1.5, -1.5])
pos[9] = np.array([2.5, -1, -0.8])
pos[10] = np.array([-1.5, -2.5, 0])
pos[11] = np.array([1.5, -2.5, 0])

edge_traces = []
for idx, (s, t) in enumerate(edges):
    x0, y0, z0 = pos[s]
    x1, y1, z1 = pos[t]
    edge_traces.append(go.Scatter3d(
        x=[x0, x1, None], y=[y0, y1, None], z=[z0, z1, None],
        mode="lines", line=dict(width=2, color="rgba(102,126,234,0.35)"),
        hoverinfo="text", text=f"{edge_labels[idx]}" if idx < len(edge_labels) else "",
        showlegend=False,
    ))

node_trace = go.Scatter3d(
    x=[pos[i][0] for i in range(len(nodes))],
    y=[pos[i][1] for i in range(len(nodes))],
    z=[pos[i][2] for i in range(len(nodes))],
    mode="markers+text",
    text=nodes,
    textposition="middle center",
    hoverinfo="text",
    marker=dict(size=sizes, color=colors, line=dict(width=1, color="rgba(255,255,255,0.2)")),
    textfont=dict(size=9, color="#E5E7EB"),
    showlegend=False,
)

fig = go.Figure(data=[*edge_traces, node_trace])
fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False, range=[-3.5, 3.5]),
        yaxis=dict(visible=False, range=[-3.5, 3.5]),
        zaxis=dict(visible=False, range=[-2.5, 2.5]),
        bgcolor="rgba(0,0,0,0)",
        camera=dict(eye=dict(x=1.5, y=-1.5, z=1.2)),
    ),
    margin=dict(l=0, r=0, t=0, b=0),
    paper_bgcolor="rgba(0,0,0,0)",
    height=400,
    hovermode="closest",
)
fig.update_layout(dragmode="turntable")
config = {"displayModeBar": False, "responsive": True}
st.plotly_chart(fig, use_container_width=True, config=config)

st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.3); font-size: 0.7rem; margin-top: 0;'>🔄 Seret untuk memutar arsitektur 3D</p>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Stats ──
st.markdown("<h3 style='color: #E5E7EB; text-align: center; font-weight: 500;'>📊 Dampak JERNIH</h3>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("<div class='stat-box'><div class='stat-number'>8</div><div class='stat-label'>Fitur AI Terintegrasi</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown("<div class='stat-box'><div class='stat-number'>3</div><div class='stat-label'>Provider AI (Groq/Gemini/OR)</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown("<div class='stat-box'><div class='stat-number'>100%</div><div class='stat-label'>Gratis, Tanpa API Berbayar</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown("<div class='stat-box'><div class='stat-number'>24/7</div><div class='stat-label'>Live di Streamlit Cloud</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Fitur ──
st.markdown("<h3 style='color: #E5E7EB; text-align: center; font-weight: 500;'>🚀 Fitur Unggulan</h3>", unsafe_allow_html=True)

features = [
    ("🤖", "AI Civic Copilot", "Chatbot cerdas dengan Groq Llama 3.1 + fallback Gemini & OpenRouter. Jawab pertanyaan layanan publik, cek fakta, dan bantu warga."),
    ("🔍", "Hoax Checker", "Analisis berita dengan AI. Auto-fetch URL + perbandingan sumber + score gauge + claims breakdown + rekomendasi."),
    ("📋", "Action Plan Generator", "Buat rencana aksi langkah demi langkah untuk masalah warga. Format tabel + timeline + prioritas."),
    ("📊", "Policy Simulator", "Simulasi dampak kebijakan publik berdasarkan anggaran, target, dan durasi."),
    ("📸", "Smart Scanner", "OCR Tesseract + Gemini Vision untuk scan KTP/dokumen. Download hasil sebagai PDF/TXT/DOC."),
    ("🗺️", "Predictive Map", "Peta 3D interaktif prediksi wilayah rawan banjir, hoax, dan prioritas bansos. Data 8 kota Indonesia."),
    ("🧠", "Knowledge Graph", "Visualisasi interaktif hubungan antara isu, kebijakan, dan dampak menggunakan NetworkX + Plotly."),
    ("🌐", "Web Search + Data 2026", "Data pemimpin dunia terkini (Trump, Prabowo, dll) + jawaban tanggal real-time via Python datetime."),
]

for i in range(0, len(features), 3):
    cols = st.columns(3)
    for j in range(3):
        if i + j < len(features):
            icon, title, desc = features[i + j]
            with cols[j]:
                st.markdown(f"""
                <div class="feature-card">
                    <span class="feature-icon">{icon}</span>
                    <p class="feature-title">{title}</p>
                    <p class="feature-desc">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Alur ──
st.markdown("<h3 style='color: #E5E7EB; text-align: center; font-weight: 500;'>⚡ Cara Kerja JERNIH</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.4); font-size: 0.8rem; margin-bottom: 1.5rem;'>Bagaimana AI JERNIH memproses pertanyaan Anda</p>", unsafe_allow_html=True)

steps = [
    ("1", "Input", "Anda mengetik pertanyaan atau upload gambar"),
    ("2", "Cari Konteks", "Web search (DuckDuckGo) + RAG database + data terkini 2026"),
    ("3", "AI Processing", "Prioritas: Groq Llama 3.1 → Gemini API → OpenRouter Nemotron"),
    ("4", "Caching", "Respons disimpan di cache biar query sama gak perlu panggil API ulang"),
    ("5", "Output", "Jawaban ditampilkan dengan confidence score + sumber"),
]

for num, title, desc in steps:
    st.markdown(f"""
    <div class="step-container">
        <div class="step-line"></div>
        <div class="step-dot">{num}</div>
        <div class="step-content">
            <span class="step-title">{title}</span>
            <br>{desc}
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tech Stack ──
st.markdown("<h3 style='color: #E5E7EB; text-align: center; font-weight: 500;'>🛠️ Teknologi</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.4); font-size: 0.8rem; margin-bottom: 1rem;'>Stack yang digunakan JERNIH</p>", unsafe_allow_html=True)

techs = [
    "Streamlit", "Python", "Groq API", "Gemini API", "OpenRouter",
    "DuckDuckGo", "LangChain", "ChromaDB", "Tesseract OCR",
    "Pillow", "Plotly", "NetworkX", "PyDeck", "httpx", "BeautifulSoup",
    "FPDF2", "Google Generative AI", "Pytesseract",
]

cols = st.columns(6)
for i, tech in enumerate(techs):
    with cols[i % 6]:
        st.markdown(f"<span class='tech-pill'>{tech}</span>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# ── Footer ──
st.markdown("""
<div style="text-align: center; padding: 2rem; border-top: 1px solid rgba(255,255,255,0.06);">
    <p style="color: rgba(255,255,255,0.2); font-size: 0.75rem; font-family: 'Playfair Display', serif; font-style: italic; margin: 0;">JERNIH.</p>
    <p style="color: rgba(255,255,255,0.15); font-size: 0.65rem; margin: 0.3rem 0 0 0;">AI Civic Operating System — LKS 2026 AI Exhibition</p>
    <p style="color: rgba(255,255,255,0.1); font-size: 0.6rem; margin: 0.2rem 0 0 0;">v2.0.0 | Dibangun dengan ❤️ untuk Indonesia</p>
</div>
""", unsafe_allow_html=True)
