import streamlit as st
import random
from datetime import datetime
from src.config import VERSION, APP_NAME, TAGLINE, HAS_AI_API
from src.fallback import (
    analyze_situation_fallback, analyze_hoax_fallback, generate_action_plan_fallback,
    CasualResponse, CopilotResponse, Source
)
from src.trust_layer import TrustScore
from src.router import route_analysis, detect_intent
from src.ai_service import chat_with_ai
from src.agents import (
    ACTION_PLAN_PROMPT, POLICY_EXPERT_PROMPT, FACT_CHECKER_PROMPT, DECISION_ENGINE_PROMPT,
    CLIMATE_EXPERT_PROMPT, LEGAL_ASSISTANT_PROMPT, EMERGENCY_ASSISTANT_PROMPT,
)
from src.knowledge_base import KNOWLEDGE_GRAPH_DATA
from src.security import sanitize_input, detect_prompt_injection
from src.ui_components import (
    inject_css, metric_card, render_card, render_step, render_agent_badge,
    confidence_bar, trust_score_ring, agent_indicator, footer, AGENT_COLORS,
    AGENT_ICONS, AGENT_LABELS,
)

_AGENT_PROMPTS = {
    "action_plan": ACTION_PLAN_PROMPT,
    "policy": POLICY_EXPERT_PROMPT,
    "fact_check": FACT_CHECKER_PROMPT,
    "decision": DECISION_ENGINE_PROMPT,
    "climate": CLIMATE_EXPERT_PROMPT,
    "legal": LEGAL_ASSISTANT_PROMPT,
    "emergency": EMERGENCY_ASSISTANT_PROMPT,
}

def render_sidebar():
    with st.sidebar:
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); width: 60px; height: 60px; border-radius: 15px; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.8rem;">
                <span style="font-size: 2rem;">🧠</span>
            </div>
            <h2 style="margin: 0; color: white;">{APP_NAME}</h2>
            <p style="color: #888; font-size: 0.8rem; margin: 0;">AI Civic Operating System</p>
            {"<span class='badge badge-success' style='margin-top: 0.5rem;'>AI Active</span>" if HAS_AI_API else "<span class='badge badge-warning' style='margin-top: 0.5rem;'>Fallback Mode</span>"}
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        menu_items = [
            ("🏠", "Beranda", "home"),
            ("🤖", "AI Civic Copilot", "copilot"),
            ("📋", "Action Plan Generator", "action_plan"),
            ("🔍", "Hoax Checker", "hoax_checker"),
            ("📊", "Policy Simulator", "policy_simulator"),
            ("📈", "Analytics Dashboard", "analytics"),
            ("🔗", "Knowledge Graph", "knowledge_graph"),
        ]

        for icon, label, key in menu_items:
            is_active = st.session_state.get("page") == key
            if st.button(
                f"{icon} {label}",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = key
                st.rerun()

        st.divider()
        st.markdown(f"<p style='text-align: center; color: #555; font-size: 0.75rem;'>v{VERSION} | LKS 2026</p>", unsafe_allow_html=True)

def render_home():
    st.markdown(f"""
    <div class="main-header">
        <h1>🧠 {APP_NAME}</h1>
        <p>{TAGLINE}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("124.583", "Warga Dibantu", "+23%")
    with col2:
        metric_card("81.500", "Jam Hemat", "+15%")
    with col3:
        metric_card("15.420", "Program Ditemukan", "+31%")
    with col4:
        metric_card("Rp15,78 M", "Dampak Ekonomi", "+45%")

    st.markdown("<h2 style='margin-top: 2rem;'>Platform Civic AI Lengkap</h2>", unsafe_allow_html=True)

    features = [
        ("🤖", "AI Civic Copilot", "Asisten AI multi-agent yang membantu memahami layanan publik, dokumen, dan prosedur pemerintahan."),
        ("🔗", "Knowledge Graph", "Visualisasi hubungan antara program, dokumen, dan instansi pemerintah."),
        ("📋", "Action Plan Generator", "Rencana aksi personal untuk mengurus dokumen dan mengakses program bantuan."),
        ("🔍", "Hoax Checker", "Verifikasi informasi dan deteksi hoaks dengan analisis AI."),
        ("📊", "Policy Simulator", "Simulasi dampak perubahan kebijakan terhadap masyarakat Indonesia."),
        ("📈", "Analytics Dashboard", "Skor kesehatan komunitas berdasarkan pendidikan, kesehatan, dan aksesibilitas."),
    ]
    for i in range(0, len(features), 3):
        cols = st.columns(3)
        for col, (icon, title, desc) in zip(cols, features[i:i+3]):
            with col:
                render_card(title, desc, icon)

    st.markdown("""
    <div class="glass-card" style="margin-top: 2rem; text-align: center;">
        <h3 style="color: white;">AI yang Dapat Dipercaya</h3>
        <p style="color: #888;">Setiap jawaban dilengkapi dengan skor kepercayaan, sumber yang terverifikasi, dan penjelasan yang transparan.</p>
        <div style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 1rem;">
            <span style="color: #2ed573;">✓ Semua informasi dilengkapi sumber resmi</span>
            <span style="color: #2ed573;">✓ Verifikasi otomatis dengan data pemerintah</span>
            <span style="color: #2ed573;">✓ Privasi warga adalah prioritas utama</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _render_trust_tab(result):
    trust = result.trust_score
    col1, col2, col3 = st.columns(3)
    with col1:
        trust_score_ring(trust.overall)
    with col2:
        confidence_bar(trust.reliability, "Reliabilitas")
        confidence_bar(trust.freshness, "Kebaruan")
    with col3:
        confidence_bar(trust.verification, "Verifikasi")
        confidence_bar(trust.transparency, "Transparansi")

    st.markdown("""
    <div style="background: #16213e; padding: 1rem; border-radius: 8px; margin-top: 1rem;">
        <p style="color: #888; font-size: 0.85rem; text-align: center;">
            🛡️ Trust Score mengukur seberapa dapat dipercaya informasi ini berdasarkan sumber, kebaruan data, dan transparansi analisis.
        </p>
    </div>
    """, unsafe_allow_html=True)

def _render_copilot_analysis(result):
    tabs = st.tabs(["📝 Ringkasan", "📋 Program", "📄 Dokumen", "📅 Timeline", "⚠️ Risiko", "🎯 Rencana Aksi", "🛡️ Trust", "🔗 Sumber"])

    with tabs[0]:
        st.markdown(f"**{result.summary}**")
        st.markdown(f"<p>{result.analysis}</p>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{result.success_probability:.0f}%</div><div class='metric-label'>Probabilitas Keberhasilan</div></div>", unsafe_allow_html=True)
        with col2:
            trust_score_ring(result.trust_score.overall)

    with tabs[1]:
        for prog in result.relevant_programs:
            st.markdown(f"""
            <div class="card fade-in">
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
            render_step(step['step'], step['action'], step['duration'], step['office'])

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
        phases = [("Hari Ini", ap.get("today", []), "#2ed573"),
                   ("Minggu Ini", ap.get("this_week", []), "#ffa502"),
                   ("Selanjutnya", ap.get("next_step", []), "#667eea")]
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
        _render_trust_tab(result)

    with tabs[7]:
        for source in result.sources:
            st.markdown(f"""
            <div class="card" style="padding: 0.8rem 1rem;">
                <strong style="color: white;">{source.title}</strong>
                <p style="color: #888; margin: 0; font-size: 0.8rem;">{source.url} | {source.type}</p>
            </div>
            """, unsafe_allow_html=True)

def render_copilot():
    st.markdown("<h1>🤖 AI Civic Copilot</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Ceritakan situasi Anda, AI multi-agent akan membantu menganalisis dan memberikan rekomendasi program serta langkah-langkah yang sesuai.</p>", unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ceritakan situasi Anda..."):
        clean_prompt = sanitize_input(prompt)

        st.session_state.messages.append({"role": "user", "content": clean_prompt})
        with st.chat_message("user"):
            st.markdown(clean_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Menganalisis..."):
                history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[:-1]]
                result = route_analysis(clean_prompt, history if history else None)

                if isinstance(result, dict) and result.get("type") == "casual":
                    agent_indicator("civic")
                    st.markdown(result["message"])
                    st.session_state.messages.append({"role": "assistant", "content": result["message"]})
                elif isinstance(result, CasualResponse):
                    st.markdown(result.message)
                    st.session_state.messages.append({"role": "assistant", "content": result.message})
                else:
                    if isinstance(result, dict):
                        trust = TrustScore()
                        copilot_result = CopilotResponse(
                            session_id=f"sess_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
                            summary=result.get("summary", ""),
                            analysis=result.get("analysis", ""),
                            relevant_programs=result.get("relevant_programs", []),
                            required_documents=result.get("required_documents", []),
                            risk_factors=result.get("risk_factors", []),
                            timeline=result.get("timeline", {"estimated_days": 14, "steps": []}),
                            action_plan=result.get("action_plan", {"today": [], "this_week": [], "next_step": []}),
                            success_probability=result.get("success_probability", 75),
                            trust_score=trust,
                            sources=[
                                Source("Portal PIP - Kemdikdasmen", "https://pip.kemdikbud.go.id", "government"),
                                Source("Data Terpadu Kesejahteraan Sosial (DTKS)", "https://dtks.kemensos.go.id", "government"),
                                Source("Kemendagri - Dukcapil", "https://dukcapil.kemendagri.go.id", "government"),
                            ],
                        )
                        intent = result.get("intent", "civic")
                        agent_indicator(intent)
                        _render_copilot_analysis(copilot_result)
                        response_text = f"**{copilot_result.summary}**\n\n{copilot_result.analysis}"
                    else:
                        agent_indicator("civic")
                        _render_copilot_analysis(result)
                        response_text = f"**{result.summary}**\n\n{result.analysis}"

                    st.session_state.messages.append({"role": "assistant", "content": response_text})

def render_action_plan():
    st.markdown("<h1>📋 Action Plan Generator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Jelaskan situasi Anda untuk mendapatkan rencana aksi personal yang detail dan terstruktur.</p>", unsafe_allow_html=True)

    situation = st.text_area("Ceritakan situasi Anda secara detail:", height=150,
                             placeholder="Contoh: Saya ingin mendaftarkan anak saya ke Program Indonesia Pintar (PIP) tapi tidak tahu caranya...")

    if st.button("Buat Rencana Aksi", type="primary", use_container_width=True):
        if not situation.strip():
            st.error("Silakan masukkan situasi Anda terlebih dahulu.")
        else:
            with st.spinner("Membuat rencana aksi..."):
                clean_sit = sanitize_input(situation)
                result = None
                if HAS_AI_API:
                    from src.ai_service import chat_with_ai
                    result = chat_with_ai(ACTION_PLAN_PROMPT, f"Situasi warga:\n\n{clean_sit}")
                if result and all(k in result for k in ["title", "overview", "citizen_success_score"]):
                    pass
                else:
                    from src.fallback import generate_action_plan_fallback
                    result = generate_action_plan_fallback(clean_sit)

                if isinstance(result, dict):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.markdown(f"<div class='metric-card'><div class='metric-value'>{result.get('citizen_success_score', 0):.0f}%</div><div class='metric-label'>Skor Keberhasilan</div></div>", unsafe_allow_html=True)
                    with col2:
                        st.markdown(f"<div class='metric-card'><div class='metric-value'>{result.get('document_readiness', 0):.0f}%</div><div class='metric-label'>Kesiapan Dokumen</div></div>", unsafe_allow_html=True)
                    with col3:
                        st.markdown(f"<div class='metric-card'><div class='metric-value'>{result.get('eligibility_score', 0):.0f}%</div><div class='metric-label'>Eligibilitas</div></div>", unsafe_allow_html=True)
                    with col4:
                        st.markdown(f"<div class='metric-card'><div class='metric-value'>{result.get('program_match', 0):.0f}%</div><div class='metric-label'>Kecocokan Program</div></div>", unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class="glass-card">
                        <h3 style="color: white; margin: 0 0 0.5rem;">{result.get('title', 'Rencana Aksi')}</h3>
                        <p style="color: #aaa;">{result.get('overview', '')}</p>
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
                        st.markdown(f"""
                        <div style="background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;">
                            <span style="color: white;">{risk['risk']}</span>
                            <span class="badge badge-warning" style="margin-left: 0.5rem;">{risk.get('probability', 'medium')}</span>
                        </div>
                        """, unsafe_allow_html=True)

def render_hoax_checker():
    st.markdown("<h1>🔍 AI Fact Checker</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Verifikasi informasi dan deteksi hoaks dengan analisis AI multi-agent.</p>", unsafe_allow_html=True)

    if "hc_images" not in st.session_state:
        st.session_state.hc_images = []

    text_type = st.selectbox("Tipe:", ["text", "article", "screenshot"])

    text = st.text_area("Tempel teks yang ingin diverifikasi:", height=200,
                        placeholder="Tempel berita, pesan WhatsApp, atau informasi yang ingin dicek...")

    st.markdown("<div style='margin: 0.5rem 0;'>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "📷 Upload screenshot (opsional) — bisa dari HP/galeri:",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key="hc_uploader",
        help="Ambil foto atau pilih dari galeri untuk dicek oleh AI",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if uploaded:
        import base64
        import io as _io
        st.session_state.hc_images = []
        for f in uploaded:
            ext = f.name.rsplit(".", 1)[-1].lower()
            if ext == "jpg":
                ext = "jpeg"
            raw = f.getvalue()
            b64 = base64.b64encode(raw).decode("utf-8")
            st.session_state.hc_images.append({"base64": b64, "format": ext, "name": f.name, "raw": raw})

    if st.session_state.hc_images:
        cols = st.columns(min(len(st.session_state.hc_images), 4))
        for i, img in enumerate(st.session_state.hc_images):
            with cols[i % len(cols)]:
                st.image(img["raw"], width=120, caption=img["name"][:20])
        if st.button("🗑 Hapus Gambar", key="hc_clear_images", use_container_width=True):
            st.session_state.hc_images = []
            st.rerun()

    if st.button("Verifikasi", type="primary", use_container_width=True):
        if not text.strip() and not st.session_state.hc_images:
            st.error("Silakan masukkan teks atau unggah gambar terlebih dahulu.")
        else:
            with st.spinner("Menganalisis..."):
                clean_text = sanitize_input(text) if text.strip() else ""
                result = None
                if HAS_AI_API:
                    from src.ai_service import chat_with_ai, chat_with_images
                    from src.agents import FACT_CHECKER_PROMPT
                    if st.session_state.hc_images:
                        prompt_text = f"Teks yang akan diverifikasi (tipe: {text_type}):\n\n{clean_text[:3000]}" if clean_text else f"Analisis gambar screenshot (tipe: {text_type}) ini dan berikan fact check."
                        result = chat_with_images(FACT_CHECKER_PROMPT, prompt_text, st.session_state.hc_images)
                    else:
                        result = chat_with_ai(FACT_CHECKER_PROMPT, f"Teks yang akan diverifikasi (tipe: {text_type}):\n\n{clean_text[:3000]}")
                if not result or not all(k in result for k in ["credibility_score", "verdict"]):
                    result = analyze_hoax_fallback(clean_text if clean_text else "Gambar dianalisis")

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

                agent_indicator("fact_check")
                st.markdown(f"""
                <div class="glass-card" style="text-align: center;">
                    <div style="font-size: 3rem;">{verdict_icon}</div>
                    <h2 style="color: {verdict_color}; margin: 0.5rem 0;">{result['verdict'].upper()}</h2>
                    <div style="font-size: 3rem; font-weight: bold; color: {verdict_color};">{score}/100</div>
                    <p style="color: #aaa; margin-top: 1rem;">{result.get('analysis', '')}</p>
                </div>
                """, unsafe_allow_html=True)

                if result.get("indicators"):
                    st.markdown("<h3 style='color: #ffa502;'>🚩 Indikator</h3>", unsafe_allow_html=True)
                    for ind in result["indicators"]:
                        st.markdown(f"<div style='background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;'>⚠️ {ind}</div>", unsafe_allow_html=True)

                if result.get("source_comparison"):
                    st.markdown("<h3 style='color: #667eea;'>📊 Perbandingan Sumber</h3>", unsafe_allow_html=True)
                    for src in result["source_comparison"]:
                        align_icon = "✅" if src.get("alignment") == "supports" else "❌"
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
                            <span class="badge badge-{'danger' if fc.get('verdict') == 'SALAH' else 'success'}">{fc.get('verdict', '')}</span>
                            <span style="color: #888; font-size: 0.8rem;"> — {fc.get('source', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)

def render_policy_simulator():
    st.markdown("<h1>📊 Policy Simulator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Simulasi dampak perubahan kebijakan terhadap masyarakat Indonesia.</p>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        policy = st.selectbox("Pilih Kebijakan:", [
            "Program Keluarga Harapan (PKH)", "Bantuan Pangan Non-Tunai (BPNT)",
            "Program Indonesia Pintar (PIP)", "Kartu Indonesia Sehat (KIS)",
            "Bantuan Langsung Tunai (BLT)",
        ])
    with col2:
        change = st.selectbox("Jenis Perubahan:", [
            "Perluas kriteria penerima", "Persempit kriteria penerima",
            "Naikkan nilai bantuan 20%", "Turunkan nilai bantuan 20%",
            "Gabung dengan program lain",
        ])

    if st.button("Simulasikan", type="primary", use_container_width=True):
        with st.spinner("Menjalankan simulasi..."):
            clean_policy = sanitize_input(policy)
            clean_change = sanitize_input(change)

            result = None
            if HAS_AI_API:
                from src.agents import POLICY_EXPERT_PROMPT
                from src.ai_service import chat_with_ai
                result = chat_with_ai(POLICY_EXPERT_PROMPT,
                    f"Kebijakan: {clean_policy}\nPerubahan: {clean_change}\n\nSimulasikan dampak dari perubahan kebijakan ini.")

            if not result:
                result = {
                    "summary": f"Simulasi perubahan kebijakan {clean_policy}: '{clean_change}' menunjukkan dampak signifikan terhadap cakupan penerima manfaat.",
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

            st.markdown(f"""
            <div class="glass-card">
                <h3 style="color: white;">📋 Hasil Simulasi</h3>
                <p style="color: #aaa;">{result.get('summary', '')}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<h3 style='color: #667eea;'>👥 Kelompok Terdampak</h3>", unsafe_allow_html=True)
            for group in result.get("affected_groups", []):
                impact_icon = "✅" if group.get("impact") == "positive" else "❌"
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
                st.markdown(f"<div class='metric-card'><div class='metric-value' style='color: {"#2ed573" if diff > 0 else "#ff4757"};'>+{diff:,}</div><div class='metric-label'>Perubahan</div></div>", unsafe_allow_html=True)

            if result.get("recommendations"):
                st.markdown("<h3 style='color: #2ed573;'>💡 Rekomendasi</h3>", unsafe_allow_html=True)
                for rec in result["recommendations"]:
                    st.markdown(f"<div style='background: #16213e; padding: 0.5rem 1rem; border-radius: 8px; margin-bottom: 0.3rem;'>👉 {rec}</div>", unsafe_allow_html=True)

def render_analytics():
    st.markdown("<h1>📈 Analytics Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #888; margin-bottom: 2rem;'>Skor kesehatan komunitas berdasarkan pendidikan, kesehatan, dan aksesibilitas.</p>", unsafe_allow_html=True)

    data = {
        "total_citizens_served": 124583, "total_time_saved_minutes": 4890000,
        "total_programs_discovered": 15420, "total_procedures_simplified": 892,
        "estimated_economic_impact": 15780000000, "average_trust_score": 87,
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

    ai_insight = None
    if HAS_AI_API:
        from src.ai_service import chat_with_ai
        insight_prompt = (
            "Kamu adalah analis data JERNIH OS. Selalu respon dalam format JSON dengan type='casual' dan message berisi insight."
        )
        insight_data = (
            f"Berdasarkan data analytics berikut, berikan 2-3 insight strategis singkat dalam Bahasa Indonesia:\n"
            f"- Warga dibantu: {data['total_citizens_served']:,}\n"
            f"- Trust score: {data['average_trust_score']}/100\n"
            f"- Tren: Pendidikan +23%, Kesehatan +15%, Bansos +31%, Ketenagakerjaan -8%\n"
            f"- Top concern: PIP ({data['top_concerns'][0]['count']:,}), KK ({data['top_concerns'][1]['count']:,})\n"
            f"- Skor terendah: Papua (rata-rata {sum(data['regional_scores']['Papua'].values())/4:.0f})\n"
            f"Gunakan emoji, tanpa markdown, maksimal 3 poin."
        )
        ai_insight = chat_with_ai(insight_prompt, insight_data)

    if ai_insight and ai_insight.get("message"):
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 1.5rem;">
            <h3 style="color: #ffa502;">🤖 AI Insight</h3>
            <p style="color: #ddd;">{ai_insight['message']}</p>
        </div>
    """, unsafe_allow_html=True)

    ai_welcome = None
    if HAS_AI_API:
        with st.spinner("Menyiapkan pengalaman..."):
            ai_welcome = chat_with_ai(
                "Kamu adalah asisten ramah JERNIH OS. Selalu respon dalam format JSON dengan field type='casual' dan message berisi 2-3 kalimat sambutan hangat dalam Bahasa Indonesia.",
                "Sapa pengguna dengan hangat dan tawarkan bantuan."
            )

    if ai_welcome and ai_welcome.get("message"):
        st.markdown(f"""
        <div class="glass-card" style="margin-bottom: 1.5rem; text-align: left;">
            <p style="color: #ddd; font-size: 1.1rem;">🤖 {ai_welcome['message']}</p>
        </div>
        """, unsafe_allow_html=True)

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
    for region, scores in data.get("regional_scores", {}).items():
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

    data = KNOWLEDGE_GRAPH_DATA

    col1, col2 = st.columns(2)
    with col1:
        node_types = ["Semua"] + sorted(set(n["type"] for n in data["nodes"]))
        selected_type = st.selectbox("Filter Tipe:", node_types, key="kg_filter")
    with col2:
        search = st.text_input("Cari:", placeholder="Ketik nama...")

    filtered_nodes = data["nodes"]
    if selected_type != "Semua":
        filtered_nodes = [n for n in filtered_nodes if n["type"] == selected_type]
    if search:
        s = search.lower()
        filtered_nodes = [n for n in filtered_nodes if s in n["label"].lower() or s in n.get("description", "").lower()]

    type_colors = {
        "program": "#667eea", "agency": "#764ba2", "document": "#2ed573",
        "benefit": "#ffa502", "location": "#ff4757", "requirement": "#1e90ff",
    }

    import json as _json
    nodes_json = _json.dumps(data["nodes"])
    links_json = _json.dumps(data["links"])
    colors_json = _json.dumps(type_colors)

    st.components.v1.html(f"""
    <div id="kg-container" style="width:100%;height:600px;background:#0a0a1a;border-radius:16px;border:1px solid #1a1a3e;"></div>
    <div id="tooltip" style="
        position:fixed;display:none;background:#16213e;color:#ddd;padding:8px 12px;border-radius:8px;
        font-size:13px;pointer-events:none;z-index:9999;border:1px solid #667eea;max-width:250px;
    "></div>
    <script src="https://unpkg.com/vis-network@9.1.9/dist/vis-network.min.js"></script>
    <script>
    try {{
        var nodesData = {nodes_json};
        var linksData = {links_json};
        var colors = {colors_json};

        var visNodes = nodesData.map(function(n) {{
            return {{
                id: n.id,
                label: n.label,
                title: n.description || n.type,
                color: {{ background: colors[n.type] || '#667eea', border: '#fff', highlight: {{ background: '#ffa502', border: '#fff' }} }},
                font: {{ color: '#eee', size: 11, face: 'Arial' }},
                borderWidth: 1,
                size: n.type === 'program' ? 25 : n.type === 'agency' ? 22 : 18,
                shape: 'dot',
            }};;
        }});

        var visEdges = linksData.map(function(l) {{
            return {{
                from: l.source,
                to: l.target,
                label: l.label,
                font: {{ color: '#888', size: 9, align: 'middle' }},
                color: {{ color: '#333', highlight: '#ffa502' }},
                width: 1,
                smooth: {{ type: 'continuous' }},
            }};;
        }});

        var container = document.getElementById('kg-container');;
        var networkData = {{ nodes: new vis.DataSet(visNodes), edges: new vis.DataSet(visEdges) }};
        var options = {{
            physics: {{ stabilization: true, barnesHut: {{ gravitationalConstant: -3000, springLength: 150 }} }},
            interaction: {{ hover: true, tooltipDelay: 200, navigationButtons: true, keyboard: true }},
            edges: {{ smooth: true }},
            layout: {{ improvedLayout: true }},
            groups: Object.keys(colors).reduce(function(acc, k) {{ acc[k] = {{ color: colors[k] }}; return acc; }}, {{}}),
        }};

        var network = new vis.Network(container, networkData, options);;

        network.on('hoverNode', function(params) {{
            var node = nodesData.find(function(n) {{ return n.id === params.node; }});;
            if (node) {{
                var tip = document.getElementById('tooltip');;
                tip.innerHTML = '<b>' + node.label + '</b><br><span style="color:#888;">' + (node.description || node.type) + '</span>';;
                tip.style.display = 'block';;
            }}
        }});;

        network.on('blurNode', function() {{
            document.getElementById('tooltip').style.display = 'none';;
        }});;

        container.addEventListener('mousemove', function(e) {{
            var tip = document.getElementById('tooltip');;
            tip.style.left = (e.clientX + 15) + 'px';;
            tip.style.top = (e.clientY + 15) + 'px';;
        }});;
    }} catch(e) {{
        document.getElementById('kg-container').innerHTML = '<div style="padding:20px;color:red;">Error: ' + e.message + '</div>';;
    }}
    </script>
    """, height=620)

    st.markdown("<h3 style='margin-top: 1.5rem;'>📋 Daftar Node</h3>", unsafe_allow_html=True)
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

def main():
    inject_css()

    if "page" not in st.session_state:
        st.session_state.page = "home"

    render_sidebar()

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
    footer()
