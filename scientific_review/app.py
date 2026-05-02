# scientific-review/scientific_review/app.py
# streamlit app

from dataclasses import dataclass
from textwrap import dedent
from typing import Any, Mapping

import requests
import streamlit as st


@dataclass(frozen=True)
class AppConfig:
    page_title: str = "SciReview • Multi-Agent AI"
    page_icon: str = "🔬"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    default_api_url: str = "http://localhost:8000/review/multiagent"
    request_timeout_s: int = 180


CONFIG = AppConfig()

# page config
st.set_page_config(
    page_title=CONFIG.page_title,
    page_icon=CONFIG.page_icon,
    layout=CONFIG.layout,
    initial_sidebar_state=CONFIG.initial_sidebar_state,
)

# custom css + animations
@st.cache_data(show_spinner=False)
def _styles_html() -> str:
    return dedent(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap');

            .stApp {
                background: linear-gradient(180deg, #0a0b0f 0%, #11131a 100%);
            }

            .main-header {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 3.1rem;
                font-weight: 600;
                background: linear-gradient(90deg, #7a81d1, #00e0ff);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                animation: glow 4s ease-in-out infinite alternate;
            }

            @keyframes glow {
                from { filter: drop-shadow(0 0 8px rgba(122, 129, 209, 0.6)); }
                to   { filter: drop-shadow(0 0 20px rgba(0, 224, 255, 0.8)); }
            }

            .glass {
                background: rgba(255, 255, 255, 0.06);
                backdrop-filter: blur(22px);
                border-radius: 22px;
                border: 1px solid rgba(255,255,255,0.1);
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
            }

            .metric-card {
                background: rgba(255,255,255,0.05);
                border-radius: 18px;
                padding: 24px 16px;
                text-align: center;
                transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .metric-card:hover {
                transform: translateY(-8px) scale(1.03);
                box-shadow: 0 20px 40px rgba(122, 129, 209, 0.25);
            }

            .score-big {
                font-size: 3.6rem;
                font-weight: 600;
                line-height: 1;
                color: #00e0ff;
            }

            .criterion {
                background: rgba(255,255,255,0.04);
                border-radius: 16px;
                padding: 20px;
                margin-bottom: 14px;
                border-left: 6px solid #7a81d1;
                transition: all 0.3s ease;
            }

            .criterion:hover {
                border-left-color: #00e0ff;
            }

            .stButton > button {
                background: linear-gradient(135deg, #5d63ff, #00d4ff);
                color: white;
                border-radius: 18px;
                padding: 16px 32px;
                font-weight: 600;
                font-size: 1.1rem;
                border: none;
                box-shadow: 0 8px 25px rgba(93, 99, 255, 0.4);
                transition: all 0.3s ease;
            }

            .stButton > button:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 30px rgba(93, 99, 255, 0.5);
            }

            .review-box {
                background: rgba(255,255,255,0.03);
                border-radius: 20px;
                padding: 32px;
                line-height: 1.8;
                font-size: 1.08rem;
                border: 1px solid rgba(122,129,209,0.2);
            }

            .fade-in {
                animation: fadeInUp 0.8s ease forwards;
            }

            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(30px); }
                to   { opacity: 1; transform: translateY(0); }
            }

            .footer {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                text-align: center;
                padding: 20px;
                background: rgba(10, 11, 15, 0.95);
                backdrop-filter: blur(12px);
                border-top: 1px solid rgba(255,255,255,0.08);
                font-size: 0.85rem;
                opacity: 0.6;
                z-index: 100;
            }
        </style>
        """
    ).strip()


def load_styles() -> None:
    st.markdown(_styles_html(), unsafe_allow_html=True)

# sidebar
def sidebar() -> str:
    with st.sidebar:
        st.markdown("### ⚙️ System Configuration")
        api_url = st.text_input(
            "Backend Endpoint",
            value=CONFIG.default_api_url,
            help="FastAPI endpoint"
        )
        
        st.divider()
        st.markdown("**Active Mode**")
        st.success("**Multi-Agent Review**")
        st.caption("4 SLM Agents • LangGraph Orchestration")
        
        st.divider()
        st.markdown("**Agents**")
        agents = (
            "Novelty Agent",
            "Scientificity Agent",
            "Readability Agent",
            "Complexity Agent",
            "Raw Review Agent",
            "Final Review Agent",
        )
        for agent in agents:
            st.markdown(f"• {agent}")
            
    return api_url

# header
def header() -> None:
    st.markdown('<h1 class="main-header fade-in">SciReview</h1>', unsafe_allow_html=True)
    st.markdown(
        dedent(
            """
            <p style="font-size:1.35rem; opacity:0.9; margin-top:-12px;" class="fade-in">
                Multi-Agent AI System for Scientific Paper Evaluation
            </p>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

# upload
def upload_section() -> str | None:
    st.markdown("### 📄 Upload Your Paper")
    uploaded_file = st.file_uploader(
        "Supported formats: .txt, .md",
        type=["txt", "md"],
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        text = uploaded_file.read().decode("utf-8")
        st.success(f"✅ **{uploaded_file.name}** loaded • {len(text):,} characters")
        
        with st.expander("📜 Paper Preview"):
            st.text_area("", text[:1800] + "..." if len(text) > 1800 else text, height=300, label_visibility="collapsed")
        return text
    return None

# results
def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def show_results(data: Mapping[str, Any]) -> None:
    scores = _safe_dict(data.get("scores"))
    final_score = scores.get("final_score", data.get("score", "—"))
    final_review = data.get("final_review") or data.get("review", "")
    reasons = _safe_dict(data.get("reasons"))
    verdict = str(data.get("verdict", "revise")).upper()

    st.markdown('<div class="fade-in"><h3>📊 Analysis Results</h3></div>', unsafe_allow_html=True)
    
    # score + verdict
    c1, c2 = st.columns([2, 3])
    with c1:
        st.markdown(f"""
        <div class="glass metric-card fade-in">
            <div class="score-big">{final_score}</div>
            <div style="font-size:1.15rem; opacity:0.85;">Overall Score</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        color = {"ACCEPT": "#00e0ff", "REVISE": "#ffb400", "REJECT": "#ff4d4d"}.get(verdict, "#7a81d1")
        st.markdown(f"""
        <div class="glass" style="padding:28px; text-align:center; border-radius:20px;">
            <span style="font-size:1.8rem; font-weight:600; color:{color};">{verdict}</span>
        </div>
        """, unsafe_allow_html=True)

    # criteria
    st.markdown("#### Evaluation Criteria")
    cols = st.columns(4)
    criteria = ["novelty", "scientificity", "readability", "complexity"]
    
    for i, crit in enumerate(criteria):
        val = scores.get(crit, 0)
        with cols[i]:
            st.markdown(f"""
            <div class="glass metric-card fade-in">
                <div style="font-size:2rem; font-weight:600;">{val}</div>
                <div style="font-size:1rem; opacity:0.75;">{crit.title()}</div>
            </div>
            """, unsafe_allow_html=True)

    # tabs
    tab1, tab2, tab3 = st.tabs(["📝 Full Review", "🔍 Agent Reasoning", "📋 Raw Outputs"])
    
    with tab1:
        st.markdown(f'<div class="review-box fade-in">{final_review}</div>', unsafe_allow_html=True)
    
    with tab2:
        for k, v in reasons.items():
            st.markdown(f"""
            <div class="criterion fade-in">
                <strong>{k.replace("_", " ").title()}</strong><br>
                {v}
            </div>
            """, unsafe_allow_html=True)
    
    with tab3:
        st.json(_safe_dict(data.get("agents_outputs")))


# main
def main() -> None:
    load_styles()
    api_url = sidebar()
    header()
    
    text = upload_section()
    
    if text:
        if st.button("🚀 Run Multi-Agent Analysis", use_container_width=True, type="primary"):
            with st.spinner("Running 6 specialized AI agents..."):
                try:
                    res = requests.post(
                        api_url,
                        json={"text": text},
                        timeout=CONFIG.request_timeout_s,
                    )
                    res.raise_for_status()
                    data = res.json() if res.content else {}
                    show_results(data)
                except requests.exceptions.Timeout:
                    st.error("Request timed out. Check backend availability and try again.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Backend request failed: {e}")
                except ValueError as e:
                    st.error(f"Invalid JSON response from backend: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")

    st.markdown(
        dedent(
            """
            <div class="footer">
                SciReview • Multi-Agent Scientific Review System • 2026
            </div>
            """
        ).strip(),
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
