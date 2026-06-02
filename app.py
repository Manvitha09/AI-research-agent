import streamlit as st
import time
from agent import run_agent
from report import save_report

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

* { font-family: 'Syne', sans-serif; }
code, pre, .stCode { font-family: 'JetBrains Mono', monospace !important; }

/* Background */
.stApp {
    background: #0a0a0f;
    color: #e8e8f0;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* Hero section */
.hero {
    text-align: center;
    padding: 3rem 0 2rem 0;
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #a78bfa, #60a5fa, #34d399);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.5rem;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #6b7280;
    font-weight: 400;
    letter-spacing: 0.05em;
}

/* Input area */
.stTextInput > div > div > input {
    background: #13131a !important;
    border: 1px solid #2a2a3a !important;
    border-radius: 12px !important;
    color: #e8e8f0 !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #a78bfa !important;
    box-shadow: 0 0 0 2px rgba(167,139,250,0.15) !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #2563eb) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2rem !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    letter-spacing: 0.03em !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(124,58,237,0.4) !important;
}

/* Status steps */
.step-card {
    background: #13131a;
    border: 1px solid #2a2a3a;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 0.95rem;
    color: #9ca3af;
}
.step-card.active {
    border-color: #a78bfa;
    color: #e8e8f0;
    background: #1a1a2e;
}
.step-card.done {
    border-color: #34d399;
    color: #34d399;
    background: #0d1f18;
}

/* Report container */
.report-container {
    background: #13131a;
    border: 1px solid #2a2a3a;
    border-radius: 16px;
    padding: 2rem;
    margin-top: 1.5rem;
}

/* Metrics row */
.metric-row {
    display: flex;
    gap: 1rem;
    margin: 1rem 0;
}
.metric-card {
    background: #13131a;
    border: 1px solid #2a2a3a;
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    flex: 1;
    text-align: center;
}
.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #a78bfa;
}
.metric-label {
    font-size: 0.75rem;
    color: #6b7280;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* Tip cards */
.tip {
    background: #13131a;
    border-left: 3px solid #a78bfa;
    border-radius: 0 8px 8px 0;
    padding: 0.75rem 1rem;
    margin: 0.4rem 0;
    font-size: 0.88rem;
    color: #9ca3af;
}

/* Markdown report styling */
.stMarkdown h1, .stMarkdown h2 {
    color: #a78bfa !important;
    font-family: 'Syne', sans-serif !important;
}
.stMarkdown h3 { color: #60a5fa !important; }
.stMarkdown p { color: #d1d5db !important; line-height: 1.7 !important; }
.stMarkdown li { color: #d1d5db !important; }
.stMarkdown table {
    border-collapse: collapse !important;
    width: 100% !important;
}
.stMarkdown th {
    background: #1e1e2e !important;
    color: #a78bfa !important;
    padding: 0.5rem 1rem !important;
    border: 1px solid #2a2a3a !important;
}
.stMarkdown td {
    padding: 0.5rem 1rem !important;
    border: 1px solid #2a2a3a !important;
    color: #d1d5db !important;
}

/* Download button */
.stDownloadButton > button {
    background: #13131a !important;
    border: 1px solid #34d399 !important;
    color: #34d399 !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: #0d1f18 !important;
    transform: translateY(-1px) !important;
}

/* Divider */
hr { border-color: #2a2a3a !important; margin: 2rem 0 !important; }
</style>
""", unsafe_allow_html=True)


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">AI Research Agent</div>
    <div class="hero-subtitle">Enter any topic. Get a structured research report in seconds.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ── Layout ────────────────────────────────────────────────────────────────────
left, right = st.columns([2, 1])

with left:
    topic = st.text_input(
        "",
        placeholder='Try: "Kafka vs RabbitMQ" or "how does kubernetes work"',
        label_visibility="collapsed",
    )
    run_btn = st.button("🔬 Run Research Agent", use_container_width=True)

with right:
    st.markdown("""
    <div class="tip">💡 Add <b>"vs"</b> for comparison reports with tables</div>
    <div class="tip">📁 Reports auto-saved to <b>reports/</b> folder</div>
    <div class="tip">⚡ Powered by <b>Groq LLaMA 3</b> + <b>Tavily</b></div>
    """, unsafe_allow_html=True)


# ── Agent Run ─────────────────────────────────────────────────────────────────
if run_btn and topic.strip():
    st.markdown("---")

    # Status indicators
    status_placeholder = st.empty()

    def show_status(step: int, message: str):
        steps = [
            ("🧠", "Planning sub-questions"),
            ("🔍", "Searching the web"),
            ("📝", "Synthesizing report"),
        ]
        html = ""
        for i, (icon, label) in enumerate(steps):
            if i < step:
                css = "done"
                icon = "✅"
            elif i == step:
                css = "active"
            else:
                css = ""
            html += f'<div class="step-card {css}">{icon} {label}</div>'
        status_placeholder.markdown(html, unsafe_allow_html=True)

    # Monkey-patch agent to show live status updates in UI
    show_status(0, "Planning")
    start_time = time.time()

    try:
        with st.spinner(""):
            report = run_agent(topic.strip())

        duration = round(time.time() - start_time)
        word_count = len(report.split())

        # Done status
        show_status(3, "Done")

        # Metrics
        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <div class="metric-value">{duration}s</div>
                <div class="metric-label">Total Time</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{word_count}</div>
                <div class="metric-label">Words</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{"⚖️ Compare" if " vs " in topic.lower() else "📄 Research"}</div>
                <div class="metric-label">Report Type</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Report
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(report)
        st.markdown('</div>', unsafe_allow_html=True)

        # Save + download
        filename = save_report(topic, report)
        st.download_button(
            label="⬇️ Download Report as Markdown",
            data=report,
            file_name=filename.split("/")[-1],
            mime="text/markdown",
        )

    except Exception as e:
        status_placeholder.empty()
        st.error(f"**Error:** {e}")
        st.info("If you hit a rate limit, wait 1-2 minutes and try again.")

elif run_btn and not topic.strip():
    st.warning("Please enter a research topic first.")


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#374151; font-size:0.8rem; padding-bottom:1rem;">
    Built with Groq LLaMA 3 · Tavily Search · Streamlit &nbsp;·&nbsp; 
    <a href="https://github.com" style="color:#6b7280;">GitHub</a>
</div>
""", unsafe_allow_html=True)