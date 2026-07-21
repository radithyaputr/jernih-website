import streamlit as st

CSS = """
<style>
.main-header {
    background: #111118;
    padding: 1.25rem;
    border-radius: 10px;
    margin-bottom: 1.5rem;
    text-align: center;
    border: 1px solid #2a2a35;
}
.main-header h1 { color: #e8e8ed; margin: 0; font-size: 2rem; font-weight: 600; }
.main-header p { color: #5a5a66; margin: 0.3rem 0 0 0; font-size: 0.9rem; }
.stApp { background: #0a0a0f; }
.card {
    background: #111118; border-radius: 10px; padding: 1.25rem;
    border: 1px solid #2a2a35; margin-bottom: 1rem;
}
.glass-card {
    background: #111118;
    border: 1px solid #2a2a35;
    border-radius: 10px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.metric-card {
    background: #111118;
    border-radius: 10px; padding: 1rem;
    border: 1px solid #2a2a35; text-align: center;
}
.metric-value { font-size: 1.6rem; font-weight: 600; color: #e8e8ed; }
.metric-label { font-size: 0.75rem; color: #5a5a66; margin-top: 0.2rem; }
.badge {
    display: inline-block; padding: 0.15rem 0.5rem; border-radius: 6px;
    font-size: 0.7rem; font-weight: 500;
}
.badge-high, .badge-danger { background: rgba(248,113,113,0.12); color: #f87171; }
.badge-medium, .badge-warning { background: rgba(251,191,36,0.12); color: #fbbf24; }
.badge-low, .badge-success { background: rgba(52,211,153,0.12); color: #34d399; }
.badge-info { background: rgba(91,141,239,0.12); color: #5b8def; }
.step-card {
    background: #111118; border-left: 3px solid #5b8def;
    padding: 0.7rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.5rem;
}
.step-number {
    background: #5b8def; color: white; width: 22px; height: 22px;
    border-radius: 50%; display: inline-flex; align-items: center;
    justify-content: center; font-size: 0.7rem; font-weight: 600; margin-right: 0.5rem;
}
.footer {
    text-align: center; padding: 1.5rem; color: #3a3a48;
    font-size: 0.75rem; border-top: 1px solid #1a1a24; margin-top: 2rem;
}
.chat-message { padding: 0.8rem; border-radius: 8px; margin-bottom: 0.6rem; }
.chat-user { background: #1a1a24; border: 1px solid #2a2a35; }
.chat-ai { background: #111118; border: 1px solid #2a2a35; }
.agent-badge {
    display: inline-flex; align-items: center; gap: 0.25rem;
    padding: 0.15rem 0.5rem; border-radius: 6px;
    font-size: 0.65rem; font-weight: 500; margin-left: 0.4rem;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.fade-in { animation: fadeIn 0.3s ease forwards; }
</style>
"""

AGENT_COLORS = {
    "civic": "#5b8def",
    "policy": "#a78bfa",
    "fact_check": "#f87171",
    "decision": "#34d399",
    "climate": "#38bdf8",
    "legal": "#fbbf24",
    "emergency": "#f87171",
    "unknown": "#5a5a66",
}

AGENT_ICONS = {
    "civic": "🤖",
    "policy": "📜",
    "fact_check": "🔍",
    "decision": "🎯",
    "climate": "🌱",
    "legal": "⚖️",
    "emergency": "🚨",
    "unknown": "❓",
}

AGENT_LABELS = {
    "civic": "Civic Advisor",
    "policy": "Policy Expert",
    "fact_check": "Fact Checker",
    "decision": "Decision Engine",
    "climate": "Climate Expert",
    "legal": "Legal Assistant",
    "emergency": "Emergency Assistant",
    "unknown": "General",
}

def inject_css():
    st.markdown(CSS, unsafe_allow_html=True)

def metric_card(value: str, label: str, change: str = None):
    change_html = f'<span class="badge badge-success">{change}</span>' if change else ""
    st.markdown(f"""
    <div class="metric-card fade-in">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)

def render_card(title: str, body: str, icon: str = None):
    icon_html = f'<div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>' if icon else ""
    st.markdown(f"""
    <div class="glass-card fade-in">
        {icon_html}
        <h3 style="margin: 0 0 0.5rem; color: white;">{title}</h3>
        <p style="color: #aaa; font-size: 0.9rem; margin: 0;">{body}</p>
    </div>
    """, unsafe_allow_html=True)

def render_step(step_num: int, action: str, duration: str, office: str):
    st.markdown(f"""
    <div class="step-card fade-in">
        <span class="step-number">{step_num}</span>
        <strong style="color: white;">{action}</strong>
        <div style="color: #888; font-size: 0.8rem; margin-left: 2rem;">
            ⏱ {duration} | 🏢 {office}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_agent_badge(agent_type: str):
    color = AGENT_COLORS.get(agent_type, "#888")
    icon = AGENT_ICONS.get(agent_type, "❓")
    label = AGENT_LABELS.get(agent_type, "General")
    st.markdown(f'<span class="agent-badge" style="background: {color}22; color: {color}; border: 1px solid {color}44;">{icon} {label}</span>', unsafe_allow_html=True)

def confidence_bar(score: float, label: str = "Confidence"):
    color = "#34d399" if score >= 80 else "#fbbf24" if score >= 50 else "#f87171"
    st.markdown(f"""
    <div style="margin-bottom: 0.6rem;">
        <div style="display: flex; justify-content: space-between; font-size: 0.75rem; color: #5a5a66; margin-bottom: 0.15rem;">
            <span>{label}</span>
            <span>{score:.0f}%</span>
        </div>
        <div style="background: #1a1a24; border-radius: 6px; height: 6px; overflow: hidden;">
            <div style="background: {color}; width: {score}%; height: 100%; border-radius: 6px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def trust_score_ring(score: float):
    color = "#34d399" if score >= 85 else "#fbbf24" if score >= 65 else "#f87171"
    st.markdown(f"""
    <div style="text-align: center;">
        <div style="width: 90px; height: 90px; border-radius: 50%; background: conic-gradient({color} {score}%, #1a1a24 {score}%); display: flex; align-items: center; justify-content: center; margin: 0 auto;">
            <div style="width: 72px; height: 72px; border-radius: 50%; background: #111118; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1.3rem; font-weight: 600; color: #e8e8ed;">{score:.0f}</span>
            </div>
        </div>
        <div style="color: #3a3a48; font-size: 0.7rem; margin-top: 0.2rem;">Trust Score</div>
    </div>
    """, unsafe_allow_html=True)

def agent_indicator(agent_type: str = "civic"):
    icon = AGENT_ICONS.get(agent_type, "🤖")
    label = AGENT_LABELS.get(agent_type, "AI Assistant")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.8rem; padding: 0.5rem 0.8rem; background: #111118; border-radius: 8px; border: 1px solid #2a2a35;">
        <span style="font-size: 1.1rem;">{icon}</span>
        <span style="color: #5b8def; font-size: 0.8rem; font-weight: 500;">{label}</span>
        <span style="color: #3a3a48; font-size: 0.7rem;">· AI Assistant</span>
    </div>
    """, unsafe_allow_html=True)

def footer():
    from src.config import VERSION
    st.markdown(f"""
    <div class="footer">
        <p>JERNIH OS v{VERSION} — LKS 2026 AI EXHIBITION</p>
        <p>Built with Responsible AI | Informasi yang Terang, Bukan yang Bising</p>
    </div>
    """, unsafe_allow_html=True)
