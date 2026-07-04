import os
os.environ["STREAMLIT_SERVER_FILE_WATCHER_TYPE"] = "none"

import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="JERNIH - Informasi yang Terang",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

from src.utils import (
    inject_css, render_header, render_kpi_card,
    render_sources_inline, render_sources_expander,
    render_confidence_bar, render_feedback_buttons,
    render_status_badge, get_lang, t,
)
from src.rag_engine import query_rag, initialize_vector_store
from src.agents import CivicAgent, HoaxAgent, ActionPlanAgent, PolicyAgent
from src.models import RAGResult, Source


def init_session():
    if "page" not in st.session_state:
        st.session_state.page = "home"
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "language" not in st.session_state:
        st.session_state.language = "id"


def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1.2rem 0 0.5rem 0;">
            <div style="background: linear-gradient(135deg, #667eea, #764ba2); width: 52px; height: 52px; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 0 auto 0.6rem;">
                <span style="font-size: 1.6rem;">🧠</span>
            </div>
            <h2 style="margin: 0; color: #FFFFFF; font-family: 'Playfair Display', serif; font-style: italic; font-weight: 700; font-size: 1.6rem;">JERNIH.</h2>
            <p style="color: rgba(255,255,255,0.4); font-size: 0.7rem; margin: 0.2rem 0 0 0; letter-spacing: 0.1em; text-transform: uppercase;">Informasi yang Terang</p>
        </div>
        """, unsafe_allow_html=True)

        st.divider()

        menu_items = [
            ("🏠", t("Beranda", "Home"), "home"),
            ("🤖", t("AI Civic Copilot", "AI Civic Copilot"), "copilot"),
            ("🔍", t("Hoax Checker", "Hoax Checker"), "hoax"),
            ("📋", t("Action Plan Generator", "Action Plan Generator"), "action"),
            ("📊", t("Policy Simulator", "Policy Simulator"), "policy"),
            ("🧠", t("Knowledge Graph", "Knowledge Graph"), "graph"),
        ]

        for icon, label, key in menu_items:
            is_active = st.session_state.page == key
            if st.button(
                f"{icon} {label}",
                key=f"nav_{key}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = key
                st.rerun()

        st.divider()

        lang = get_lang()
        new_lang = "en" if lang == "id" else "id"
        lang_label = "🌐 English" if lang == "id" else "🌐 Indonesia"
        if st.button(lang_label, key="lang_toggle", use_container_width=True):
            st.session_state.language = new_lang
            st.rerun()

        st.markdown(f"<p style='text-align: center; color: rgba(255,255,255,0.2); font-size: 0.7rem; margin-top: 2rem;'>v2.0.0 | LKS 2026</p>", unsafe_allow_html=True)


def render_home():
    render_header()

    st.markdown(f"<p style='color: #9CA3AF; text-align: center; margin-bottom: 2rem; font-size: 0.9rem;'>{t('Ringkasan dampak JERNIH untuk masyarakat.', 'JERNIH impact summary for the community.')}</p>", unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card("👥", "124.583", t("Warga Dibantu", "Citizens Helped"), "+23%")
    with col2:
        render_kpi_card("⏱️", "81.500", t("Jam Hemat", "Hours Saved"), "+15%")
    with col3:
        render_kpi_card("📋", "15.420", t("Program Ditemukan", "Programs Found"), "+31%")
    with col4:
        render_kpi_card("💰", "Rp15,78M", t("Dampak Ekonomi", "Economic Impact"), "+45%")

    st.markdown(f"<h3 style='color: #E5E7EB; margin-top: 2rem; margin-bottom: 1rem;'>{t('Akses Cepat', 'Quick Access')}</h3>", unsafe_allow_html=True)

    col1, col2, col3, col4, col5 = st.columns(5)
    quick_actions = [
        ("col1", "🤖", t("AI Civic\nCopilot", "AI Civic\nCopilot"), "copilot"),
        ("col2", "📋", t("Action Plan\nGenerator", "Action Plan\nGenerator"), "action"),
        ("col3", "🔍", t("Hoax\nChecker", "Hoax\nChecker"), "hoax"),
        ("col4", "📊", t("Policy\nSimulator", "Policy\nSimulator"), "policy"),
        ("col5", "🧠", t("Knowledge\nGraph", "Knowledge\nGraph"), "graph"),
    ]
    cols = [col1, col2, col3, col4, col5]
    for col_obj, icon, label, page_key in quick_actions:
        with cols[quick_actions.index((col_obj, icon, label, page_key))]:
            if st.button(f"{icon}\n{label}", key=f"qa_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()

    st.markdown(f"""
    <div class="glass-card" style="margin-top: 2rem; text-align: center;">
        <h4 style="color: rgba(255,255,255,0.9); margin: 0 0 0.5rem 0; font-weight: 600;">{t('🤖 AI yang Transparan & Bertanggung Jawab', '🤖 Transparent & Responsible AI')}</h4>
        <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">
            {t('Setiap jawaban AI JERNIH dilengkapi dengan sumber yang terverifikasi, confidence score, dan penjelasan yang transparan.', 'Every JERNIH AI answer comes with verified sources, confidence scores, and transparent explanations.')}
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_copilot():
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #FFFFFF; font-size: 2rem; margin: 0;">🤖 AI Civic Copilot</h1>
        <p style="color: #9CA3AF; margin: 0.3rem 0 0 0;">{t('Tanya apa pun tentang layanan publik, program pemerintah, atau informasi kewarganegaraan.', 'Ask anything about public services, government programs, or civic information.')}</p>
    </div>
    """, unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                render_sources_inline(msg["sources"])
                if msg.get("confidence"):
                    render_confidence_bar(msg["confidence"])
                render_sources_expander(msg["sources"], msg.get("source_texts"))
                render_feedback_buttons(msg.get("msg_key", ""))

    if prompt := st.chat_input(t("Tanyakan sesuatu...", "Ask something...")):
        prompt = prompt.strip()
        if not prompt:
            st.warning(t("Silakan masukkan pertanyaan.", "Please enter a question."))
            st.stop()

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner(t("Mencari informasi...", "Searching for information...")):
                rag = query_rag(prompt)
                agent = CivicAgent()
                response = agent.ask(prompt, rag, lang=get_lang())

                st.markdown(response.answer)

                render_sources_inline(response.sources)

                if response.confidence:
                    render_confidence_bar(response.confidence)

                render_sources_expander(response.sources, response.source_texts)

                msg_key = f"copilot_{len(st.session_state.messages)}"
                render_feedback_buttons(msg_key)

            st.session_state.messages.append({
                "role": "assistant",
                "content": response.answer,
                "sources": response.sources,
                "confidence": response.confidence,
                "source_texts": response.source_texts,
                "msg_key": msg_key,
            })


def render_hoax():
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #FFFFFF; font-size: 2rem; margin: 0;">🔍 {t('Hoax Checker', 'Hoax Checker')}</h1>
        <p style="color: #9CA3AF; margin: 0.3rem 0 0 0;">{t('Verifikasi kebenaran informasi atau berita dengan AI berbasis data.', 'Verify the truth of information or news with data-driven AI.')}</p>
    </div>
    """, unsafe_allow_html=True)

    claim = st.text_area(
        t("Masukkan klaim/berita yang ingin dicek:", "Enter the claim/news to check:"),
        height=150,
        placeholder=t("Contoh: Pemerintah akan memberikan bantuan Rp10 juta untuk semua warga...", "Example: The government will provide Rp10 million assistance to all citizens..."),
    )

    if st.button(t("🔍 Verifikasi", "🔍 Verify"), type="primary", use_container_width=True):
        claim = claim.strip()
        if not claim:
            st.warning(t("Silakan masukkan klaim terlebih dahulu.", "Please enter a claim first."))
        else:
            with st.spinner(t("Menganalisis klaim...", "Analyzing claim...")):
                rag = query_rag(claim)
                agent = HoaxAgent()
                result = agent.check(claim, rag, lang=get_lang())

                status = result.get("status", "menyesatkan")
                explanation = result.get("explanation", "")
                confidence = result.get("confidence", 50)
                sources = result.get("sources", [])

                st.markdown("<div style='margin: 1rem 0;'>", unsafe_allow_html=True)
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
                    render_status_badge(status)
                    st.markdown("</div>", unsafe_allow_html=True)
                with col2:
                    render_confidence_bar(confidence)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="glass-card" style="padding: 1rem; margin: 1rem 0;">
                    <p style="color: rgba(255,255,255,0.8); margin: 0; line-height: 1.6;">{explanation}</p>
                </div>
                """, unsafe_allow_html=True)

                source_objs = [Source(title=s) for s in sources]
                render_sources_inline(source_objs, label=t("sumber rujukan untuk verifikasi ini", "reference sources for this verification"))
                render_sources_expander(source_objs, [rag.context] if rag.context else [])

                st.success(t("✅ Verifikasi selesai! JERNIH selalu transparan dengan sumber data.", "✅ Verification complete! JERNIH is always transparent with data sources."))


def render_action():
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #FFFFFF; font-size: 2rem; margin: 0;">📋 {t('Action Plan Generator', 'Action Plan Generator')}</h1>
        <p style="color: #9CA3AF; margin: 0.3rem 0 0 0;">{t('Dapatkan rencana aksi langkah demi langkah untuk menyelesaikan masalah Anda.', 'Get a step-by-step action plan to solve your problem.')}</p>
    </div>
    """, unsafe_allow_html=True)

    problem = st.text_area(
        t("Ceritakan masalah/keluhan Anda:", "Describe your problem/complaint:"),
        height=150,
        placeholder=t("Contoh: Banjir di daerah saya setiap tahun terjadi dan kami butuh bantuan...", "Example: Flooding in my area happens every year and we need help..."),
    )

    if st.button(t("📋 Buat Rencana Aksi", "📋 Generate Action Plan"), type="primary", use_container_width=True):
        problem = problem.strip()
        if not problem:
            st.warning(t("Silakan masukkan masalah Anda terlebih dahulu.", "Please enter your problem first."))
        else:
            with st.spinner(t("Membuat rencana aksi...", "Generating action plan...")):
                rag = query_rag(problem)
                agent = ActionPlanAgent()
                result = agent.generate(problem, rag, lang=get_lang())

                st.markdown(f"""
                <div class="glass-card" style="padding: 1.5rem; margin: 1rem 0;">
                    <div style="white-space: pre-wrap; color: rgba(255,255,255,0.8); line-height: 1.7;">{result}</div>
                </div>
                """, unsafe_allow_html=True)

                if rag.sources:
                    render_sources_inline(rag.sources, label=t("sumber kebijakan yang mendasari rencana ini", "policy sources underlying this plan"))
                    render_sources_expander(rag.sources, [rag.context] if rag.context else [])

                st.success(t("✅ Rencana aksi siap! JERNIH selalu mendasari rekomendasi dengan sumber resmi.", "✅ Action plan ready! JERNIH always bases recommendations on official sources."))


def render_policy():
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #FFFFFF; font-size: 2rem; margin: 0;">📊 {t('Policy Simulator', 'Policy Simulator')}</h1>
        <p style="color: #9CA3AF; margin: 0.3rem 0 0 0;">{t('Simulasikan dampak kebijakan publik pada aspek ekonomi, sosial, dan lingkungan.', 'Simulate public policy impacts on economic, social, and environmental aspects.')}</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        budget = st.number_input(
            t("Anggaran (Rp)", "Budget (Rp)"),
            min_value=100_000,
            max_value=1_000_000_000_000,
            value=1_000_000_000,
            step=100_000_000,
            format="%d",
        )
    with col2:
        target_options = [
            t("Pendidikan", "Education"),
            t("Kesehatan", "Health"),
            t("Bantuan Sosial", "Social Assistance"),
            t("Infrastruktur", "Infrastructure"),
            t("Lingkungan", "Environment"),
            t("UMKM", "SMEs"),
        ]
        target = st.selectbox(t("Target Kebijakan", "Policy Target"), target_options)
    with col3:
        duration = st.slider(t("Durasi (bulan)", "Duration (months)"), min_value=1, max_value=60, value=12)

    if st.button(t("📊 Jalankan Simulasi", "📊 Run Simulation"), type="primary", use_container_width=True):
        with st.spinner(t("Menjalankan simulasi...", "Running simulation...")):
            agent = PolicyAgent()
            result = agent.simulate(budget, target, duration, lang=get_lang())

            st.markdown(f"""
            <div class="glass-card" style="padding: 1.5rem; margin: 1rem 0;">
                <h3 style="color: rgba(255,255,255,0.9); margin: 0 0 1rem 0;">📈 {t('Hasil Simulasi', 'Simulation Result')}</h3>
                <div style="white-space: pre-wrap; color: rgba(255,255,255,0.8); line-height: 1.7;">{result}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="glass-card" style="padding: 1rem; margin-top: 1rem;">
                <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">
                    📊 {t('Simulasi dibuat berdasarkan data yang tersedia di database JERNIH.', 'Simulation is based on data available in the JERNIH database.')}
                </p>
            </div>
            """, unsafe_allow_html=True)


def render_graph():
    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <h1 style="color: #FFFFFF; font-size: 2rem; margin: 0;">🧠 {t('Knowledge Graph', 'Knowledge Graph')}</h1>
        <p style="color: #9CA3AF; margin: 0.3rem 0 0 0;">{t('Visualisasi hubungan antara isu, kebijakan, dan dampak.', 'Visualization of relationships between issues, policies, and impacts.')}</p>
    </div>
    """, unsafe_allow_html=True)

    try:
        import networkx as nx
        import plotly.graph_objects as go

        G = nx.Graph()

        edges = [
            ("Hoaks", "Verifikasi AI", "dicek oleh"),
            ("Verifikasi AI", "Informasi Akurat", "menghasilkan"),
            ("Informasi Akurat", "Partisipasi Masyarakat", "mendorong"),
            ("Partisipasi Masyarakat", "Kebijakan Tepat Sasaran", "mewujudkan"),
            ("Kebijakan Tepat Sasaran", "Kesejahteraan Warga", "meningkatkan"),
            ("Informasi Akurat", "Kepercayaan Publik", "membangun"),
            ("Kepercayaan Publik", "Kesejahteraan Warga", "mendukung"),
            ("Hoaks", "Misinformasi", "menyebabkan"),
            ("Misinformasi", "Kebijakan Salah Sasaran", "mengakibatkan"),
            ("Kebijakan Salah Sasaran", "Kesejahteraan Warga", "menghambat"),
            ("Verifikasi AI", "Sumber Resmi", "berbasis"),
            ("Sumber Resmi", "Kepercayaan Publik", "meningkatkan"),
            ("AI Civic Copilot", "Verifikasi AI", "melakukan"),
            ("AI Civic Copilot", "Informasi Akurat", "menyediakan"),
            ("Knowledge Graph", "AI Civic Copilot", "mendukung"),
        ]

        for source, target, label in edges:
            G.add_edge(source, target, label=label)

        pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)

        edge_traces = []
        for source, target, data in G.edges(data=True):
            x0, y0 = pos[source]
            x1, y1 = pos[target]
            label = data.get("label", "")

            edge_traces.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(width=1.5, color="rgba(102,126,234,0.4)"),
                hoverinfo="text",
                text=f"{source} → {target}: {label}",
            ))

            mid_x = (x0 + x1) / 2
            mid_y = (y0 + y1) / 2
            edge_traces.append(go.Scatter(
                x=[mid_x],
                y=[mid_y],
                mode="text",
                text=[label],
                textposition="middle center",
                textfont=dict(size=9, color="rgba(156,163,175,0.7)"),
                hoverinfo="none",
            ))

        node_x = []
        node_y = []
        node_labels = []
        node_colors = []
        color_map = {
            "Hoaks": "#ff4757",
            "Misinformasi": "#ff6348",
            "Kebijakan Salah Sasaran": "#ffa502",
            "Kebijakan Tepat Sasaran": "#2ed573",
            "Kesejahteraan Warga": "#2ed573",
            "Informasi Akurat": "#667eea",
            "Verifikasi AI": "#764ba2",
            "Partisipasi Masyarakat": "#1e90ff",
            "Kepercayaan Publik": "#1e90ff",
            "Sumber Resmi": "#2ed573",
            "AI Civic Copilot": "#667eea",
            "Knowledge Graph": "#764ba2",
        }

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            node_labels.append(node)
            node_colors.append(color_map.get(node, "#667eea"))

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=node_labels,
            textposition="top center",
            hoverinfo="text",
            marker=dict(
                size=28,
                color=node_colors,
                line=dict(width=2, color="rgba(255,255,255,0.3)"),
            ),
            textfont=dict(size=11, color="#E5E7EB"),
        )

        fig = go.Figure(
            data=[*edge_traces, node_trace],
            layout=go.Layout(
                title=dict(
                    text=t("Hubungan Isu → Kebijakan → Dampak", "Issue → Policy → Impact Relationships"),
                    font=dict(size=16, color="#E5E7EB"),
                ),
                showlegend=False,
                hovermode="closest",
                margin=dict(b=20, l=20, r=20, t=40),
                paper_bgcolor="#0E1117",
                plot_bgcolor="#0E1117",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                height=600,
            ),
        )

        config = {"displayModeBar": False, "responsive": True}
        st.plotly_chart(fig, use_container_width=True, config=config)

        st.markdown(f"""
        <div class="glass-card" style="padding: 1rem; margin-top: 1rem;">
            <p style="color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0;">
                🧠 {t('Grafik ini menunjukkan bagaimana JERNIH menghubungkan berbagai elemen dalam ekosistem informasi publik.', 'This graph shows how JERNIH connects various elements in the public information ecosystem.')}
            </p>
        </div>
        """, unsafe_allow_html=True)

    except ImportError:
        st.warning(t(
            "Library NetworkX atau Plotly tidak tersedia. Install dengan: pip install networkx plotly",
            "NetworkX or Plotly library not available. Install with: pip install networkx plotly",
        ))
        st.info(t(
            "Knowledge Graph membutuhkan networkx dan plotly untuk visualisasi interaktif.",
            "Knowledge Graph requires networkx and plotly for interactive visualization.",
        ))


def main():
    inject_css()
    init_session()

    with st.sidebar:
        render_sidebar()

    pages = {
        "home": render_home,
        "copilot": render_copilot,
        "hoax": render_hoax,
        "action": render_action,
        "policy": render_policy,
        "graph": render_graph,
    }

    pages.get(st.session_state.page, render_home)()

    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; color: rgba(255,255,255,0.25); font-size: 0.75rem; border-top: 1px solid rgba(255,255,255,0.06); margin-top: 3rem;">
        <p style="margin: 0; font-family: 'Playfair Display', serif; font-style: italic;">JERNIH.</p>
        <p style="margin: 0.3rem 0 0 0; letter-spacing: 0.05em;">{t('Informasi yang Terang, Bukan yang Bising', 'Clear Information, Not Noise')}</p>
        <p style="margin: 0.3rem 0 0 0; font-size: 0.65rem;">v2.0.0 — LKS 2026 AI Exhibition</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
