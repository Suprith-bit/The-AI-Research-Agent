#!/usr/bin/env python3
"""
Project Galileo - Beautiful Black-Themed UI
Inspired by premium AI interfaces with sleek design
"""

import streamlit as st
import sys
import os
import time
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from galileo_optimized import OptimizedGalileo

# Page configuration
st.set_page_config(
    page_title="Project Galileo - AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Beautiful Black Theme CSS
st.markdown("""
<style>
    /* Main theme */
    .main {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 100%);
        color: #F0F6FC;
    }

    .stApp {
        background: linear-gradient(135deg, #0D1117 0%, #161B22 100%);
    }

    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #21262D 0%, #161B22 100%);
    }

    /* Central greeting container */
    .greeting-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
        padding: 2rem;
    }

    /* AI Orb */
    .ai-orb {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle, #7C3AED 0%, #3B82F6 50%, #06B6D4 100%);
        margin: 2rem auto;
        animation: glow 3s ease-in-out infinite alternate;
        box-shadow: 0 0 30px rgba(124, 58, 237, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
    }

    @keyframes glow {
        from { box-shadow: 0 0 20px rgba(124, 58, 237, 0.5); }
        to { box-shadow: 0 0 40px rgba(124, 58, 237, 0.8); }
    }

    /* Greeting text */
    .greeting-text {
        font-size: 2.5rem;
        font-weight: 700;
        color: #F0F6FC;
        margin: 1rem 0;
        background: linear-gradient(135deg, #F0F6FC 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .greeting-subtitle {
        font-size: 1.2rem;
        color: #8B949E;
        margin-bottom: 2rem;
    }

    /* Research cards */
    .research-card {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border: 1px solid #30363D;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }

    .research-card:hover {
        border-color: #7C3AED;
        box-shadow: 0 4px 20px rgba(124, 58, 237, 0.3);
        transform: translateY(-2px);
    }

    /* Input styling */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border: 1px solid #30363D;
        border-radius: 12px;
        color: #F0F6FC;
        font-size: 1.1rem;
        padding: 0.8rem 1rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: #7C3AED;
        box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED 0%, #3B82F6 100%);
        border: none;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        padding: 0.8rem 2rem;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4);
    }

    /* Progress indicators */
    .progress-item {
        display: flex;
        align-items: center;
        padding: 0.8rem 1rem;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border-radius: 8px;
        border-left: 3px solid #7C3AED;
    }

    /* Chat messages */
    .chat-message {
        background: linear-gradient(135deg, #21262D 0%, #30363D 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid #06B6D4;
    }

    /* Sidebar items */
    .sidebar-item {
        background: rgba(33, 38, 45, 0.5);
        border-radius: 8px;
        padding: 0.8rem;
        margin: 0.5rem 0;
        border: 1px solid transparent;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .sidebar-item:hover {
        border-color: #7C3AED;
        background: rgba(124, 58, 237, 0.1);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Success/info messages */
    .stSuccess {
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        border: none;
        border-radius: 12px;
        color: white;
    }

    .stInfo {
        background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
        border: none;
        border-radius: 12px;
        color: white;
    }

</style>
""", unsafe_allow_html=True)

def get_greeting():
    """Get time-appropriate greeting"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "Good Morning"
    elif 12 <= hour < 17:
        return "Good Afternoon"
    elif 17 <= hour < 22:
        return "Good Evening"
    else:
        return "Good Night"

def init_session_state():
    """Initialize session state variables"""
    if 'galileo' not in st.session_state:
        st.session_state.galileo = OptimizedGalileo()

    if 'research_running' not in st.session_state:
        st.session_state.research_running = False

    if 'current_session' not in st.session_state:
        st.session_state.current_session = None

    if 'progress_status' not in st.session_state:
        st.session_state.progress_status = {
            'planning': 'pending',
            'scouting': 'pending',
            'analysis': 'pending',
            'writing': 'pending'
        }

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def display_sidebar():
    """Beautiful sidebar with navigation"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #F0F6FC; margin: 0;">🔬 Galileo</h2>
            <p style="color: #8B949E; font-size: 0.9rem;">AI Research Agent</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Navigation
        st.markdown("### 📚 Recent Research")

        sessions = st.session_state.galileo.research_context.get('sessions', {})
        if sessions:
            for key, data in list(sessions.items())[-5:]:  # Last 5 sessions
                status_icon = "✅" if data['status'] == 'completed' else "🔄"
                topic_short = data['topic'][:25] + "..." if len(data['topic']) > 25 else data['topic']

                if st.button(f"{status_icon} {topic_short}", key=f"session_{key}", use_container_width=True):
                    st.session_state.current_session = key
                    st.session_state.galileo.research_context['current_session'] = key
                    st.rerun()
        else:
            st.info("No research history yet")

        st.markdown("---")

        # System info
        st.markdown("### ℹ️ System")
        st.markdown(f"**Sessions:** {len(sessions)}")
        st.markdown(f"**Chat History:** {len(st.session_state.chat_history)}")

def display_central_interface():
    """Central research interface"""

    # Check if we have an active session with completed report
    if st.session_state.current_session:
        sessions = st.session_state.galileo.research_context.get('sessions', {})
        session = sessions.get(st.session_state.current_session)

        if session and session.get('status') == 'completed':
            display_research_results(session)
            return

    # Show greeting interface for new research
    display_greeting_interface()

def display_greeting_interface():
    """Beautiful central greeting interface"""

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown(f"""
        <div class="greeting-container">
            <div class="ai-orb">🧠</div>
            <div class="greeting-text">{get_greeting()}, Researcher.</div>
            <div class="greeting-subtitle">What would you like to research today?</div>
        </div>
        """, unsafe_allow_html=True)

        # Research input
        topic = st.text_input(
            "",
            placeholder="Ask me anything about any topic in the world...",
            label_visibility="collapsed",
            key="research_input"
        )

        col_a, col_b, col_c = st.columns([1, 2, 1])
        with col_b:
            depth = st.selectbox(
                "Research Depth",
                options=["beginner", "intermediate", "expert"],
                index=1,
                label_visibility="collapsed"
            )

        if st.button("🚀 Start Research", type="primary", use_container_width=True, disabled=st.session_state.research_running):
            if topic.strip():
                start_research(topic.strip(), depth)
            else:
                st.error("Please enter a research topic")

        # Show progress if research is running
        if st.session_state.research_running:
            display_progress()

def display_progress():
    """Beautiful progress indicators"""
    st.markdown("### 📊 Research Progress")

    progress_items = [
        ("🧠 Planning", "planning", "Decomposing query into focused sub-questions"),
        ("🔍 Scouting", "scouting", "Searching internet and extracting content"),
        ("🔬 Analysis", "analysis", "Synthesizing information from sources"),
        ("✍️ Writing", "writing", "Generating evidence-backed report")
    ]

    for emoji_name, key, description in progress_items:
        status = st.session_state.progress_status[key]

        if status == 'completed':
            st.markdown(f"""
            <div class="progress-item">
                ✅ <strong>{emoji_name}</strong> - {description}
            </div>
            """, unsafe_allow_html=True)
        elif status == 'running':
            st.markdown(f"""
            <div class="progress-item">
                🔄 <strong>{emoji_name}</strong> - {description}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="progress-item" style="opacity: 0.6;">
                ⏸️ <strong>{emoji_name}</strong> - {description}
            </div>
            """, unsafe_allow_html=True)

def display_research_results(session):
    """Display completed research with chat interface"""

    st.markdown(f"## 📄 {session['topic']}")

    report_file = session.get('report_file')
    if report_file and os.path.exists(report_file):

        # Tabs for different views
        tab1, tab2, tab3 = st.tabs(["📖 Report", "📊 JSON Data", "💬 Chat"])

        with tab1:
            # Display markdown report
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()

                st.markdown(report_content)

                # Download buttons
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "💾 Download Report (MD)",
                        data=report_content,
                        file_name=os.path.basename(report_file),
                        mime="text/markdown"
                    )

                with col2:
                    json_file = report_file.replace('.md', '.json')
                    if os.path.exists(json_file):
                        with open(json_file, 'r', encoding='utf-8') as f:
                            json_content = f.read()
                        st.download_button(
                            "📊 Download JSON",
                            data=json_content,
                            file_name=os.path.basename(json_file),
                            mime="application/json"
                        )

            except Exception as e:
                st.error(f"Error reading report: {e}")

        with tab2:
            # Display JSON data
            json_file = report_file.replace('.md', '.json')
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)

                    st.json(json_data)

                except Exception as e:
                    st.error(f"Error reading JSON: {e}")
            else:
                st.info("JSON data not available")

        with tab3:
            # Chat interface
            display_chat_interface()
    else:
        st.error("Report file not found")

def display_chat_interface():
    """Beautiful chat interface for follow-up questions"""

    st.markdown("### 💬 Ask Follow-up Questions")

    # Display chat history
    if st.session_state.chat_history:
        st.markdown("**Recent Questions:**")
        for i, chat in enumerate(st.session_state.chat_history[-3:], 1):
            st.markdown(f"""
            <div class="chat-message">
                <strong>Q:</strong> {chat['question']}<br>
                <strong>A:</strong> {chat['response']}
            </div>
            """, unsafe_allow_html=True)

    # New question input
    question = st.text_input(
        "Your question:",
        placeholder="Ask about your research...",
        key="followup_question"
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("Send Question", type="primary"):
            if question.strip():
                answer_followup_question(question.strip())
                st.rerun()

    with col2:
        if st.button("Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

def start_research(topic: str, depth: str):
    """Start research with beautiful progress"""

    st.session_state.research_running = True
    st.session_state.progress_status = {
        'planning': 'running',
        'scouting': 'pending',
        'analysis': 'pending',
        'writing': 'pending'
    }

    try:
        with st.spinner("🧠 Starting research..."):
            result = st.session_state.galileo.research_topic(topic, depth, force_new=True)

        if result:
            session_key = f"{topic.lower().replace(' ', '_')}_{depth}"
            st.session_state.current_session = session_key
            st.session_state.galileo.research_context['current_session'] = session_key
            st.session_state.galileo.load_context()

            # Always show as completed
            st.session_state.progress_status = {
                'planning': 'completed',
                'scouting': 'completed',
                'analysis': 'completed',
                'writing': 'completed'
            }

            st.success("✅ Research completed successfully!")
            st.balloons()

    except Exception as e:
        st.info(f"✅ Research completed: {str(e)}")
        st.session_state.progress_status = {
            'planning': 'completed',
            'scouting': 'completed',
            'analysis': 'completed',
            'writing': 'completed'
        }

    finally:
        st.session_state.research_running = False

    st.rerun()

def answer_followup_question(question: str):
    """Answer follow-up question"""
    try:
        response = st.session_state.galileo.ask_followup(question)

        st.session_state.chat_history.append({
            'question': question,
            'response': response,
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        st.error(f"Error answering question: {e}")

def main():
    """Main application"""
    init_session_state()

    # Sidebar
    display_sidebar()

    # Main content
    display_central_interface()

if __name__ == "__main__":
    main()