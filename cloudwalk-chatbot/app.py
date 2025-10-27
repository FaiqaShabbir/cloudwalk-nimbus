import streamlit as st
from chatbot import CloudWalkRAGChatbot
import time

# Page configuration
st.set_page_config(
    page_title="CloudWalk Assistant",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #ff6b6b;
    }
    .assistant-message {
        background-color: #e8f4fd;
        border-left-color: #1f77b4;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #0d5aa7;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "chatbot" not in st.session_state:
    st.session_state.chatbot = CloudWalkRAGChatbot()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "initialized" not in st.session_state:
    st.session_state.initialized = False

# Sidebar
with st.sidebar:
    st.title("☁️ CloudWalk Assistant")
    st.markdown("---")
    
    st.markdown("### Quick Questions")
    quick_questions = [
        "What is CloudWalk?",
        "Tell me about InfinitePay",
        "What are CloudWalk's core values?",
        "How does CloudWalk's technology work?",
        "What is CloudWalk's mission?"
    ]
    
    for question in quick_questions:
        if st.button(question, key=f"quick_{question}"):
            st.session_state.messages.append({"role": "user", "content": question})
            with st.spinner("Thinking..."):
                response = st.session_state.chatbot.chat(question)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This chatbot uses **Retrieval-Augmented Generation (RAG)** 
    to provide accurate information about CloudWalk's:
    - Products and services
    - Mission and values
    - Technology and security
    - Company information
    """)

# Main content
st.markdown('<h1 class="main-header">☁️ CloudWalk Assistant</h1>', unsafe_allow_html=True)

# Display welcome message if no messages yet
if not st.session_state.messages:
    welcome_msg = st.session_state.chatbot.get_welcome_message()
    st.markdown(welcome_msg)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about CloudWalk..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chatbot.chat(prompt)
        st.markdown(response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Powered by CloudWalk | Built with Streamlit and RAG Technology
    </div>
    """,
    unsafe_allow_html=True
)
