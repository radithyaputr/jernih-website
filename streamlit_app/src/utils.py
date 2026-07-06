import streamlit as st
from datetime import datetime


CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;0,800;1,600;1,700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* ── Animated Gradient Background ── */
    .stApp {
        background: #0E1117;
    }
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: linear-gradient(135deg, #0E1117 0%, #1a0a2e 25%, #0d1b2a 50%, #0a1f1a 75%, #0E1117 100%);
        background-size: 400% 400%;
        animation: gradientShift 25s ease infinite;
        z-index: -2;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        25% { background-position: 50% 0%; }
        50% { background-position: 100% 50%; }
        75% { background-position: 50% 100%; }
        100% { background-position: 0% 50%; }
    }

    /* ── Floating Orbs ── */
    .orb {
        position: fixed;
        border-radius: 50%;
        filter: blur(80px);
        opacity: 0.25;
        pointer-events: none;
        z-index: -1;
    }
    .orb-1 {
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(102,126,234,0.4), transparent);
        top: -100px; left: -100px;
        animation: floatOrb1 20s ease-in-out infinite;
    }
    .orb-2 {
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(118,75,162,0.3), transparent);
        bottom: -80px; right: -80px;
        animation: floatOrb2 25s ease-in-out infinite;
    }
    .orb-3 {
        width: 350px; height: 350px;
        background: radial-gradient(circle, rgba(46,213,115,0.15), transparent);
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        animation: floatOrb3 30s ease-in-out infinite;
    }
    @keyframes floatOrb1 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(80px, 60px) scale(1.1); }
        66% { transform: translate(-40px, 100px) scale(0.9); }
    }
    @keyframes floatOrb2 {
        0%, 100% { transform: translate(0, 0) scale(1); }
        33% { transform: translate(-60px, -40px) scale(1.15); }
        66% { transform: translate(50px, -80px) scale(0.85); }
    }
    @keyframes floatOrb3 {
        0%, 100% { transform: translate(-50%, -50%) scale(1); }
        50% { transform: translate(-50%, -50%) scale(1.2); }
    }

    /* ── Base Typography ── */
    * { font-family: 'Inter', sans-serif; }

    /* ── Glassmorphism Card ── */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(255, 255, 255, 0.15);
        box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5);
    }

    /* ── Main Header ── */
    .main-header {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
    }
    .main-header h1 {
        font-family: 'Playfair Display', serif;
        font-size: 4rem;
        font-weight: 800;
        font-style: italic;
        background: linear-gradient(135deg, #e8d5ff 0%, #a78bfa 30%, #667eea 60%, #5ce1e6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0;
        letter-spacing: -0.02em;
        text-shadow: 0 0 60px rgba(102,126,234,0.3);
    }
    .main-header .tagline {
        font-family: 'Inter', sans-serif;
        color: rgba(255,255,255,0.5);
        font-size: 0.95rem;
        font-weight: 300;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin: 0.5rem 0 0 0;
    }
    .main-header .tagline em {
        font-style: italic;
        color: rgba(255,255,255,0.6);
    }

    /* ── AI Active Badge (pulse) ── */
    .badge-ai {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(46, 213, 115, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(46, 213, 115, 0.3);
        color: #2ed573;
        padding: 0.4rem 1rem;
        border-radius: 24px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.8rem;
        position: relative;
    }
    .badge-ai::before {
        content: '';
        position: absolute;
        inset: -2px;
        border-radius: 26px;
        background: rgba(46, 213, 115, 0.1);
        animation: pulseGlow 3s ease-in-out infinite;
        z-index: -1;
    }
    @keyframes pulseGlow {
        0%, 100% { opacity: 0.4; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.05); }
    }

    /* ── KPI Cards ── */
    .kpi-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem 1rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 12px 48px rgba(102, 126, 234, 0.15);
        transform: translateY(-4px);
    }
    .kpi-card .kpi-icon { font-size: 2rem; margin-bottom: 0.5rem; }
    .kpi-card .kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0.2rem 0;
        line-height: 1.2;
    }
    .kpi-card .kpi-label {
        color: rgba(255,255,255,0.5);
        font-size: 0.8rem;
        margin: 0;
        font-weight: 400;
        letter-spacing: 0.02em;
    }
    .kpi-card .kpi-trend {
        color: #2ed573;
        font-size: 0.8rem;
        margin-top: 0.3rem;
        font-weight: 600;
    }
    .kpi-card .kpi-updated {
        color: rgba(255,255,255,0.25);
        font-size: 0.6rem;
        margin-top: 0.5rem;
    }

    /* ── Source Inline ── */
    .source-inline {
        background: rgba(102, 126, 234, 0.06);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(102, 126, 234, 0.15);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin: 1rem 0;
    }
    .source-inline .source-header {
        color: #2ed573;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .source-inline ul {
        margin: 0;
        padding-left: 1.2rem;
        color: #D1D5DB;
    }
    .source-inline li { margin-bottom: 0.25rem; font-size: 0.85rem; }
    .source-inline li a { color: #a78bfa; text-decoration: none; }
    .source-inline li a:hover { text-decoration: underline; }

    /* ── Confidence Bar ── */
    .confidence-bar {
        background: rgba(255,255,255,0.06);
        border-radius: 10px;
        height: 8px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 10px;
        transition: width 0.6s ease;
    }

    /* ── Status Badge ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.35rem 0.9rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        backdrop-filter: blur(10px);
    }
    .status-true {
        background: rgba(46,213,115,0.12);
        color: #2ed573;
        border: 1px solid rgba(46,213,115,0.25);
    }
    .status-misleading {
        background: rgba(255,165,2,0.12);
        color: #ffa502;
        border: 1px solid rgba(255,165,2,0.25);
    }
    .status-hoax {
        background: rgba(255,71,87,0.12);
        color: #ff4757;
        border: 1px solid rgba(255,71,87,0.25);
    }

    /* ── Section Title ── */
    .section-title {
        color: #E5E7EB;
        font-size: 1.1rem;
        font-weight: 600;
        margin: 1.5rem 0 0.8rem 0;
    }

    /* ── Input Fields (glass) ── */
    .stTextArea textarea, .stTextInput input, .stSelectbox select, .stSlider div[data-baseweb] {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #E5E7EB !important;
        border-radius: 16px !important;
        transition: all 0.3s ease !important;
    }
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 0 20px rgba(102, 126, 234, 0.1) !important;
    }

    /* ── Chat Input ── */
    div[data-testid="stChatInput"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 0.3rem;
    }
    div[data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        color: #E5E7EB !important;
    }

    /* ── Chat Messages ── */
    div[data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }

    /* ── Buttons (Glass) ── */
    .stButton > button {
        border-radius: 14px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        color: #D1D5DB !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        border-color: rgba(102, 126, 234, 0.4) !important;
        background: rgba(255, 255, 255, 0.07) !important;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15) !important;
        color: #FFFFFF !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, rgba(102,126,234,0.3), rgba(118,75,162,0.3)) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        backdrop-filter: blur(10px) !important;
        box-shadow: 0 4px 24px rgba(102, 126, 234, 0.2) !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, rgba(102,126,234,0.5), rgba(118,75,162,0.5)) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 8px 40px rgba(102, 126, 234, 0.3) !important;
        transform: translateY(-2px) !important;
    }

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: rgba(15, 15, 25, 0.85);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border-right: 1px solid rgba(255, 255, 255, 0.06);
    }
    section[data-testid="stSidebar"] .stButton > button {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        justify-content: flex-start !important;
        border-radius: 12px !important;
        padding: 0.5rem 1rem !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(255,255,255,0.05) !important;
        border: none !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: rgba(102,126,234,0.15) !important;
        border: none !important;
        box-shadow: none !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: rgba(102,126,234,0.25) !important;
    }

    /* ── Selectbox ── */
    div[data-baseweb="select"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
    }

    /* ── Expander ── */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.03) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
    }

    /* ── Feedback ── */
    .feedback-btn {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 10px;
        padding: 0.3rem 0.8rem;
        color: rgba(255,255,255,0.5);
        cursor: pointer;
        font-size: 0.8rem;
        transition: all 0.2s ease;
    }
    .feedback-btn:hover {
        border-color: rgba(102,126,234,0.4);
        color: #FFFFFF;
        background: rgba(102,126,234,0.1);
    }

    /* ── Animations ── */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(12px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .fade-in {
        animation: fadeIn 0.5s ease forwards;
    }

    /* ── Hoax Checker - Score Gauge ── */
    .gauge-container {
        display: flex; justify-content: center; align-items: center;
        position: relative; width: 160px; height: 160px; margin: 0 auto;
    }
    .gauge-svg { transform: rotate(-90deg); }
    .gauge-bg { fill: none; stroke: rgba(255,255,255,0.06); stroke-width: 8; }
    .gauge-fill { fill: none; stroke-width: 8; stroke-linecap: round; transition: stroke-dashoffset 1.2s ease; }
    .gauge-center {
        position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
        text-align: center;
    }
    .gauge-center .score { font-size: 2.2rem; font-weight: 800; color: #fff; line-height: 1; }
    .gauge-center .label { font-size: 0.65rem; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 0.05em; }

    /* ── Verdict Card ── */
    .verdict-card {
        border-radius: 20px; padding: 1.5rem;
        backdrop-filter: blur(20px);
        position: relative; overflow: hidden;
        animation: fadeIn 0.6s ease;
    }
    .verdict-card::before {
        content: ''; position: absolute; inset: 0;
        border-radius: 20px; padding: 2px;
        -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
        -webkit-mask-composite: xor; mask-composite: exclude;
        pointer-events: none;
    }
    .verdict-true {
        background: rgba(46,213,115,0.08);
    }
    .verdict-true::before { background: linear-gradient(135deg, #2ed573, #7bed9f); }
    .verdict-misleading {
        background: rgba(255,165,2,0.08);
    }
    .verdict-misleading::before { background: linear-gradient(135deg, #ffa502, #ffbe76); }
    .verdict-hoax {
        background: rgba(255,71,87,0.08);
    }
    .verdict-hoax::before { background: linear-gradient(135deg, #ff4757, #ff6b81); }

    .verdict-icon { font-size: 1.8rem; }
    .verdict-label { font-size: 1.4rem; font-weight: 700; }
    .verdict-sub { font-size: 0.8rem; opacity: 0.6; margin-top: 0.3rem; }
    .verdict-true .verdict-label { color: #2ed573; }
    .verdict-misleading .verdict-label { color: #ffa502; }
    .verdict-hoax .verdict-label { color: #ff4757; }

    /* ── Indicator Tag ── */
    .indicator-tag {
        display: inline-block;
        background: rgba(255,71,87,0.08);
        border: 1px solid rgba(255,71,87,0.2);
        color: #ff6b81;
        padding: 0.25rem 0.7rem;
        border-radius: 8px;
        font-size: 0.75rem;
        margin: 0.2rem;
        white-space: nowrap;
    }
    .indicator-tag-safe {
        background: rgba(46,213,115,0.08);
        border-color: rgba(46,213,115,0.2);
        color: #7bed9f;
    }

    /* ── Source Alignment Badge ── */
    .alignment-support { color: #2ed573; }
    .alignment-contradict { color: #ff4757; }
    .alignment-neutral { color: #ffa502; }

    /* ── Risk Badge ── */
    .risk-badge {
        display: inline-flex; align-items: center; gap: 0.3rem;
        padding: 0.25rem 0.7rem; border-radius: 20px;
        font-size: 0.75rem; font-weight: 600;
    }
    .risk-high { background: rgba(255,71,87,0.12); color: #ff4757; border: 1px solid rgba(255,71,87,0.2); }
    .risk-medium { background: rgba(255,165,2,0.12); color: #ffa502; border: 1px solid rgba(255,165,2,0.2); }
    .risk-low { background: rgba(46,213,115,0.12); color: #2ed573; border: 1px solid rgba(46,213,115,0.2); }

    /* ── Section Header ── */
    .hoax-section {
        margin: 1.2rem 0 0.6rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid rgba(255,255,255,0.06);
        color: #E5E7EB; font-size: 1rem; font-weight: 600;
    }

    /* ── Animated Verification Pulse ── */
    @keyframes verifyPulse {
        0% { box-shadow: 0 0 0 0 rgba(102,126,234,0.4); }
        70% { box-shadow: 0 0 0 12px rgba(102,126,234,0); }
        100% { box-shadow: 0 0 0 0 rgba(102,126,234,0); }
    }
    .verify-animation {
        animation: verifyPulse 1.5s ease-out;
    }

    /* ── Responsive ── */
    @media (max-width: 768px) {
        .main-header h1 { font-size: 2.5rem; }
        .kpi-card .kpi-value { font-size: 1.4rem; }
        .orb-1, .orb-2, .orb-3 { display: none; }
    }
</style>
"""


def inject_css():
    st.markdown("""
    <div class="orb orb-1"></div>
    <div class="orb orb-2"></div>
    <div class="orb orb-3"></div>
    """, unsafe_allow_html=True)
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
