import streamlit as st

CSS = """
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    text-align: center;
}
.main-header h1 { color: white; margin: 0; font-size: 2.5rem; }
.main-header p { color: rgba(255,255,255,0.85); margin: 0.5rem 0 0 0; font-size: 1.1rem; }
.stApp { background: #0f0f1a; }
.card {
    background: #1a1a2e; border-radius: 12px; padding: 1.5rem;
    border: 1px solid #2a2a4a; margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.card:hover { border-color: #667eea; box-shadow: 0 4px 20px rgba(102,126,234,0.15); }
.glass-card {
    background: rgba(26, 26, 46, 0.8);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}
.glass-card:hover {
    border-color: rgba(102, 126, 234, 0.5);
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
}
.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border-radius: 12px; padding: 1.2rem;
    border: 1px solid #2a2a4a; text-align: center;
}
.metric-value { font-size: 1.8rem; font-weight: bold; color: #667eea; }
.metric-label { font-size: 0.85rem; color: #888; margin-top: 0.3rem; }
.badge {
    display: inline-block; padding: 0.2rem 0.6rem; border-radius: 6px;
    font-size: 0.75rem; font-weight: 600;
}
.badge-high, .badge-danger { background: #ff4757; color: white; }
.badge-medium, .badge-warning { background: #ffa502; color: white; }
.badge-low, .badge-success { background: #2ed573; color: white; }
.badge-info { background: #667eea; color: white; }
.step-card {
    background: #16213e; border-left: 3px solid #667eea;
    padding: 0.8rem 1rem; border-radius: 0 8px 8px 0; margin-bottom: 0.5rem;
}
.step-number {
    background: #667eea; color: white; width: 24px; height: 24px;
    border-radius: 50%; display: inline-flex; align-items: center;
    justify-content: center; font-size: 0.75rem; font-weight: bold; margin-right: 0.5rem;
}
.footer {
    text-align: center; padding: 2rem; color: #666;
    font-size: 0.85rem; border-top: 1px solid #2a2a4a; margin-top: 3rem;
}
.chat-message { padding: 1rem; border-radius: 12px; margin-bottom: 0.8rem; }
.chat-user { background: #1a1a2e; border: 1px solid #2a2a4a; }
.chat-ai { background: #16213e; border: 1px solid #667eea33; }
.agent-badge {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.2rem 0.6rem; border-radius: 20px;
    font-size: 0.7rem; font-weight: 600; margin-left: 0.5rem;
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.fade-in { animation: fadeIn 0.4s ease forwards; }
@keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.pulse { animation: pulse 2s ease infinite; }
</style>
"""

AGENT_COLORS = {
    "civic": "#667eea",
    "policy": "#764ba2",
    "fact_check": "#ff4757",
    "decision": "#2ed573",
    "climate": "#1e90ff",
    "legal": "#ffa502",
    "emergency": "#ff4757",
    "unknown": "#888",
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
    color = "#2ed573" if score >= 80 else "#ffa502" if score >= 50 else "#ff4757"
    st.markdown(f"""
    <div style="margin-bottom: 0.8rem;">
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #888; margin-bottom: 0.2rem;">
            <span>{label}</span>
            <span>{score:.0f}%</span>
        </div>
        <div style="background: #2a2a4a; border-radius: 8px; height: 8px; overflow: hidden;">
            <div style="background: {color}; width: {score}%; height: 100%; border-radius: 8px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def trust_score_ring(score: float):
    color = "#2ed573" if score >= 85 else "#ffa502" if score >= 65 else "#ff4757"
    st.markdown(f"""
    <div style="text-align: center;">
        <div style="width: 100px; height: 100px; border-radius: 50%; background: conic-gradient({color} {score}%, #2a2a4a {score}%); display: flex; align-items: center; justify-content: center; margin: 0 auto;">
            <div style="width: 80px; height: 80px; border-radius: 50%; background: #1a1a2e; display: flex; align-items: center; justify-content: center;">
                <span style="font-size: 1.5rem; font-weight: bold; color: white;">{score:.0f}</span>
            </div>
        </div>
        <div style="color: #888; font-size: 0.75rem; margin-top: 0.3rem;">Trust Score</div>
    </div>
    """, unsafe_allow_html=True)

def agent_indicator(agent_type: str = "civic"):
    icon = AGENT_ICONS.get(agent_type, "🤖")
    label = AGENT_LABELS.get(agent_type, "AI Assistant")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; padding: 0.5rem 1rem; background: rgba(102,126,234,0.1); border-radius: 8px; border: 1px solid rgba(102,126,234,0.2);">
        <span style="font-size: 1.2rem;">{icon}</span>
        <span style="color: #667eea; font-size: 0.85rem; font-weight: 600;">{label}</span>
        <span style="color: #888; font-size: 0.75rem;">· AI Assistant</span>
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
