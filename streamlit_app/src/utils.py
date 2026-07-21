import streamlit as st
from datetime import datetime


CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Inter:wght@300;400;500;600;700&display=swap');

    .stApp { background: #0a0a0f; }

    /* ── Base Typography ── */
    * { font-family: 'Inter', sans-serif; }

    /* ── Glassmorphism Card ── */
    .glass-card {
        background: #111118;
        border: 1px solid #2a2a35;
        border-radius: 10px;
        padding: 1.25rem;
        transition: border-color 0.2s;
    }
    .glass-card:hover { border-color: #3a3a48; }

    /* ── Main Header ── */
    .main-header {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
    }
    .main-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 3.5rem;
        font-weight: 700;
        font-style: italic;
        color: #e8e8ed;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .main-header .tagline {
        color: #5a5a66;
        font-size: 0.85rem;
        font-weight: 400;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 0.4rem 0 0 0;
    }
    .main-header .tagline em {
        font-style: italic;
        color: #6a6a76;
    }

    /* ── AI Active Badge (pulse) ── */
    .badge-ai {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(52, 211, 153, 0.06);
        border: 1px solid rgba(52, 211, 153, 0.15);
        color: #34d399;
        padding: 0.3rem 0.8rem;
        border-radius: 6px;
        font-size: 0.7rem;
        font-weight: 500;
        margin-top: 0.6rem;
    }

    /* ── KPI Cards ── */
    .kpi-card {
        background: #111118;
        border: 1px solid #2a2a35;
        border-radius: 10px;
        padding: 1.25rem 1rem;
        text-align: center;
        transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: #3a3a48; }
    .kpi-card .kpi-icon { font-size: 1.5rem; margin-bottom: 0.4rem; }
    .kpi-card .kpi-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #e8e8ed;
        margin: 0.15rem 0;
        line-height: 1.2;
    }
    .kpi-card .kpi-label {
        color: #5a5a66;
        font-size: 0.75rem;
        margin: 0;
    }
    .kpi-card .kpi-trend {
        color: #34d399;
        font-size: 0.75rem;
        margin-top: 0.25rem;
        font-weight: 500;
    }
    .kpi-card .kpi-updated {
        color: #3a3a48;
        font-size: 0.55rem;
        margin-top: 0.4rem;
    }

    /* ── Source Inline ── */
    .source-inline {
        background: #111118;
        border: 1px solid #2a2a35;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin: 0.8rem 0;
    }
    .source-inline .source-header {
        color: #34d399;
        font-size: 0.8rem;
        font-weight: 500;
        margin-bottom: 0.4rem;
    }
    .source-inline ul { margin: 0; padding-left: 1.1rem; }
    .source-inline li { margin-bottom: 0.2rem; font-size: 0.8rem; color: #9494a0; }

    /* ── Confidence Bar ── */
    .confidence-bar {
        background: #1a1a24;
        border-radius: 6px;
        height: 6px;
        overflow: hidden;
        margin: 0.4rem 0;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.25rem 0.7rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-true { background: rgba(52,211,153,0.08); color: #34d399; border: 1px solid rgba(52,211,153,0.2); }
    .status-misleading { background: rgba(251,191,36,0.08); color: #fbbf24; border: 1px solid rgba(251,191,36,0.2); }
    .status-hoax { background: rgba(248,113,113,0.08); color: #f87171; border: 1px solid rgba(248,113,113,0.2); }

    /* ── Section Title ── */
    .section-title {
        color: #E5E7EB;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 0.8rem 0;
    }

    /* ── Input Fields (glass) ── */
    .stTextArea textarea, .stTextInput input, .stSelectbox select, .stSlider div[data-baseweb] {
        background: #111118 !important;
        border: 1px solid #2a2a35 !important;
        color: #e8e8ed !important;
        border-radius: 8px !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #5b8def !important;
    }

    div[data-testid="stChatInput"] {
        background: #111118;
        border: 1px solid #2a2a35;
        border-radius: 10px;
        padding: 0.25rem;
    }
    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        color: #e8e8ed !important;
    }

    div[data-testid="stChatMessage"] {
        background: #111118;
        border: 1px solid #2a2a35;
        border-radius: 10px;
        padding: 0.7rem 0.9rem;
        margin-bottom: 0.5rem;
    }

    .stButton > button {
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 0.85rem !important;
        background: #111118 !important;
        border: 1px solid #2a2a35 !important;
        color: #9494a0 !important;
    }
    .stButton > button:hover {
        border-color: #3a3a48 !important;
        background: #1a1a24 !important;
        color: #e8e8ed !important;
    }
    .stButton > button[kind="primary"] {
        background: #5b8def !important;
        border: 1px solid #5b8def !important;
        color: #fff !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: #7aa5ff !important;
        border-color: #7aa5ff !important;
    }

    section[data-testid="stSidebar"] {
        background: #0a0a0f;
        border-right: 1px solid #2a2a35;
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        justify-content: flex-start !important;
        border-radius: 6px !important;
        padding: 0.4rem 0.8rem !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.04) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(91, 141, 239, 0.12) !important;
    }

    div[data-baseweb="select"] {
        background: #111118 !important;
        border: 1px solid #2a2a35 !important;
        border-radius: 8px !important;
    }

    .streamlit-expanderHeader {
        background: #111118 !important;
        border-radius: 8px !important;
        border: 1px solid #2a2a35 !important;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in { animation: fadeIn 0.3s ease forwards; }

    .gauge-container {
        display: flex; justify-content: center; align-items: center;
        position: relative; width: 140px; height: 140px; margin: 0 auto;
    }
    .gauge-svg { transform: rotate(-90deg); }
    .gauge-bg { fill: none; stroke: #1a1a24; stroke-width: 6; }
    .gauge-fill { fill: none; stroke-width: 6; stroke-linecap: round; transition: stroke-dashoffset 1s ease; }
    .gauge-center {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        text-align: center;
    }
    .gauge-center .score { font-size: 1.8rem; font-weight: 700; color: #e8e8ed; line-height: 1; }
    .gauge-center .label { font-size: 0.6rem; color: #5a5a66; text-transform: uppercase; letter-spacing: 0.05em; }

    .verdict-card {
        border-radius: 10px; padding: 1.25rem;
        background: #111118;
        border: 1px solid #2a2a35;
    }
    .verdict-true { border-left: 3px solid #34d399; }
    .verdict-misleading { border-left: 3px solid #fbbf24; }
    .verdict-hoax { border-left: 3px solid #f87171; }

    .verdict-icon { font-size: 1.5rem; }
    .verdict-label { font-size: 1.1rem; font-weight: 600; }
    .verdict-sub { font-size: 0.75rem; opacity: 0.5; margin-top: 0.2rem; }
    .verdict-true .verdict-label { color: #34d399; }
    .verdict-misleading .verdict-label { color: #fbbf24; }
    .verdict-hoax .verdict-label { color: #f87171; }

    .indicator-tag {
        display: inline-block;
        background: rgba(248,113,113,0.06);
        border: 1px solid rgba(248,113,113,0.15);
        color: #f87171;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-size: 0.7rem;
        margin: 0.15rem;
    }
    .indicator-tag-safe {
        background: rgba(52,211,153,0.06);
        border-color: rgba(52,211,153,0.15);
        color: #34d399;
    }

    .alignment-support { color: #34d399; }
    .alignment-contradict { color: #f87171; }
    .alignment-neutral { color: #fbbf24; }

    .risk-badge {
        display: inline-flex; align-items: center; gap: 0.25rem;
        padding: 0.2rem 0.6rem; border-radius: 6px;
        font-size: 0.7rem; font-weight: 500;
    }
    .risk-high { background: rgba(248,113,113,0.08); color: #f87171; border: 1px solid rgba(248,113,113,0.15); }
    .risk-medium { background: rgba(251,191,36,0.08); color: #fbbf24; border: 1px solid rgba(251,191,36,0.15); }
    .risk-low { background: rgba(52,211,153,0.08); color: #34d399; border: 1px solid rgba(52,211,153,0.15); }

    .hoax-section {
        margin: 1rem 0 0.5rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 1px solid #2a2a35;
        color: #e8e8ed; font-size: 0.9rem; font-weight: 500;
    }

    @keyframes verifyPulse {
        0% { box-shadow: 0 0 0 0 rgba(91,141,239,0.3); }
        70% { box-shadow: 0 0 0 8px rgba(91,141,239,0); }
        100% { box-shadow: 0 0 0 0 rgba(91,141,239,0); }
    }
    .verify-animation { animation: verifyPulse 1.2s ease-out; }

    @media (max-width: 768px) {
        .main-header h1 { font-size: 2rem; }
        .kpi-card .kpi-value { font-size: 1.25rem; }
    }
</style>
"""


def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>JERNIH.</h1>
        <p class="tagline"><em>Informasi yang Terang</em>, Bukan yang Bising</p>
        <div class="badge-ai">⚡ AI Active</div>
    </div>
    """, unsafe_allow_html=True)


def render_kpi_card(icon: str, value: str, label: str, trend: str):
    now = datetime.now().strftime("%d %b %Y, %H:%M")
    st.markdown(f"""
    <div class="kpi-card fade-in">
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-trend">↑ {trend}</div>
        <div class="kpi-updated">Last updated: {now}</div>
    </div>
    """, unsafe_allow_html=True)


def render_sources_inline(sources: list, label: str = "sumber terkait"):
    if not sources:
        return
    st.markdown(f"""
    <div class="source-inline">
        <div class="source-header">🔍 JERNIH menemukan {len(sources)} {label}:</div>
        <ul>
            {''.join(f'<li>[{i+1}] {s.title}</li>' for i, s in enumerate(sources))}
        </ul>
    </div>
    """, unsafe_allow_html=True)


def render_sources_expander(sources: list, source_texts: list[str] = None):
    if not sources:
        return
    with st.expander("📚 Lihat Cuplikan Teks Sumber (Detail)"):
        for i, src in enumerate(sources):
            st.markdown(f"**[{i+1}] {src.title}**")
            if source_texts and i < len(source_texts):
                st.markdown(f"<blockquote style='color: rgba(255,255,255,0.5); font-size: 0.85rem;'>{source_texts[i][:300]}...</blockquote>", unsafe_allow_html=True)
            if src.url:
                st.markdown(f"🔗 [{src.url}]({src.url})")
            st.markdown("---")


def render_confidence_bar(score: float):
    score = min(max(score, 0), 100)
    color = "#2ed573" if score >= 70 else "#ffa502" if score >= 40 else "#ff4757"
    st.markdown(f"""
    <div style="margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: rgba(255,255,255,0.5); margin-bottom: 0.2rem;">
            <span>Confidence Score</span>
            <span>{score:.0f}%</span>
        </div>
        <div class="confidence-bar">
            <div class="confidence-bar-fill" style="width: {score}%; background: {color};"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_feedback_buttons(msg_key: str):
    col1, col2 = st.columns([1, 10])
    with col1:
        if st.button("👍", key=f"fb_up_{msg_key}", help="Membantu"):
            st.toast("👍 Terima kasih atas feedback Anda!", icon="✅")
    with col2:
        if st.button("👎", key=f"fb_down_{msg_key}", help="Tidak Membantu"):
            st.toast("📝 Terima kasih, kami akan terus belajar!", icon="📝")


def render_status_badge(status: str):
    status_map = {
        "benar": ("✅ Benar", "status-true"),
        "true": ("✅ Benar", "status-true"),
        "fakta": ("✅ Fakta", "status-true"),
        "menyesatkan": ("⚠️ Menyesatkan", "status-misleading"),
        "misleading": ("⚠️ Menyesatkan", "status-misleading"),
        "hoaks": ("❌ Hoaks", "status-hoax"),
        "hoax": ("❌ Hoaks", "status-hoax"),
        "salah": ("❌ Hoaks", "status-hoax"),
    }
    label, cls = status_map.get(status.lower(), ("⚪ Tidak Diketahui", ""))
    st.markdown(f'<span class="status-badge {cls}">{label}</span>', unsafe_allow_html=True)


def get_lang() -> str:
    return st.session_state.get("language", "id")


def t(id_text: str, en_text: str) -> str:
    return id_text if get_lang() == "id" else en_text
