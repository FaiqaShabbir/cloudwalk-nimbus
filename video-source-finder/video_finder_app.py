import streamlit as st
import json
from video_source_finder import VideoSourceFinder
import time

# Page configuration
st.set_page_config(
    page_title="Video Source Finder",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #4ecdc4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #4ecdc4;
        background-color: #2d3748;
        color: #e2e8f0;
    }
    .video-info {
        background-color: #4a5568;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        color: #e2e8f0;
    }
    .timestamp {
        font-family: monospace;
        background-color: #4a5568;
        color: #e2e8f0;
        padding: 0.25rem 0.5rem;
        border-radius: 0.25rem;
        display: inline-block;
    }
    .confidence-bar {
        background-color: #4a5568;
        border-radius: 0.25rem;
        height: 0.5rem;
        margin: 0.5rem 0;
    }
    .confidence-fill {
        background-color: #4ecdc4;
        height: 100%;
        border-radius: 0.25rem;
        transition: width 0.3s ease;
    }
    
    /* Fix white text visibility in inputs */
    .stTextInput > div > div > input {
        color: #e2e8f0 !important;
        background-color: #2d3748 !important;
    }
    
    .stTextArea > div > div > textarea {
        color: #e2e8f0 !important;
        background-color: #2d3748 !important;
    }
    
    .stSelectbox > div > div > select {
        color: #e2e8f0 !important;
        background-color: #2d3748 !important;
    }
    
    .stButton > button {
        background-color: #ff6b6b;
        color: white;
        border-radius: 0.5rem;
        border: none;
        padding: 0.5rem 1rem;
    }
    .stButton > button:hover {
        background-color: #ff5252;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "video_finder" not in st.session_state:
    st.session_state.video_finder = VideoSourceFinder()

if "search_history" not in st.session_state:
    st.session_state.search_history = []

# Sidebar
with st.sidebar:
    st.title("🎥 Video Source Finder")
    st.markdown("---")
    
    st.markdown("### Database Stats")
    stats = st.session_state.video_finder.get_database_stats()
    if stats:
        st.metric("Indexed Chunks", stats.get('total_chunks', 0))
        st.text(f"Model: {stats.get('embedding_model', 'N/A')}")
    
    st.markdown("---")
    
    st.markdown("### Add Video Manually")
    video_id_input = st.text_input("YouTube Video ID", placeholder="dQw4w9WgXcQ")
    if st.button("Add Video to Database"):
        if video_id_input:
            with st.spinner("Adding video..."):
                success = st.session_state.video_finder.add_video_to_database(video_id_input)
                if success:
                    st.success(f"Video {video_id_input} added successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to add video {video_id_input}")
    
    st.markdown("---")
    
    st.markdown("### Search History")
    if st.session_state.search_history:
        for i, search in enumerate(st.session_state.search_history[-5:]):
            if st.button(f"📝 {search['text'][:50]}...", key=f"history_{i}"):
                # Store the search text for display
                st.session_state.current_search_text = search['text']
                st.rerun()
    
    # Display current search text if set
    if "current_search_text" in st.session_state and st.session_state.current_search_text:
        st.info(f"Selected: {st.session_state.current_search_text}")
        if st.button("Clear Selection", key="clear_selection"):
            st.session_state.current_search_text = ""
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### About")
    st.markdown("""
    This tool finds the original video source 
    for text snippets using:
    - YouTube transcript extraction
    - Semantic search with embeddings
    - Multiple search APIs (Serper, Tavily)
    """)

# Main content
st.markdown('<h1 class="main-header">🎥 Video Source Finder</h1>', unsafe_allow_html=True)

st.markdown("""
**Find the original video where a text snippet was spoken!**

Enter any text snippet below, and we'll search through YouTube videos to find where it was originally spoken, 
complete with timestamps and confidence scores.
""")

# Text input
text_snippet = st.text_area(
    "Enter the text snippet you want to find:",
    placeholder="Enter any text snippet here...",
    height=100,
    key="text_input"
)

# Search button
if st.button("🔍 Find Video Source", type="primary"):
    if text_snippet.strip():
        with st.spinner("Searching for video source..."):
            result = st.session_state.video_finder.find_video_source(text_snippet)
            
            
            # Add to search history
            st.session_state.search_history.append({
                'text': text_snippet,
                'result': result,
                'timestamp': time.time()
            })
            
            if result:
                st.markdown("### ✅ Video Source Found!")
                
                # Display result in a nice format
                with st.container():
                    st.markdown(f"""
                    <div class="result-box">
                        <h4>📹 Video Information</h4>
                        <div class="video-info">
                            <strong>Video ID:</strong> {result['video_id']}<br>
                            <strong>Title:</strong> {result.get('title', 'N/A')}<br>
                            <strong>YouTube URL:</strong> <a href="{result['url']}" target="_blank">{result['url']}</a><br>
                            <strong>Start Time:</strong> <span class="timestamp">{result['timestamp_start']}</span><br>
                            <strong>End Time:</strong> <span class="timestamp">{result['timestamp_end']}</span><br>
                            <strong>Confidence:</strong> {result['confidence']:.2%}
                        </div>
                        
                        <div class="confidence-bar">
                            <div class="confidence-fill" style="width: {result['confidence']*100:.1f}%"></div>
                        </div>
                        
                        <h4>📝 Transcript Snippet</h4>
                        <p style="background-color: #f9f9f9; padding: 1rem; border-radius: 0.25rem; font-style: italic;">
                            "{result['transcript_snippet']}"
                        </p>
                        
                        {f'''
                        <div style="background-color: #d1ecf1; border: 1px solid #bee5eb; padding: 1rem; border-radius: 0.25rem; margin-top: 1rem;">
                            <h5 style="color: #0c5460; margin: 0 0 0.5rem 0;">🔍 Analysis Method</h5>
                            <p style="color: #0c5460; margin: 0; font-size: 0.9rem;">
                                <strong>Method:</strong> {result.get('method', 'Content-based matching')}
                            </p>
                            <p style="color: #0c5460; margin: 0.5rem 0 0 0; font-size: 0.8rem;">
                                <strong>Note:</strong> {result.get('note', '')}
                            </p>
                        </div>
                        ''' if result.get('method') else ''}
                        
                        {f'''
                        <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 1rem; border-radius: 0.25rem; margin-top: 1rem;">
                            <h5 style="color: #856404; margin: 0 0 0.5rem 0;">⚠️ Limitation Notice</h5>
                            <p style="color: #856404; margin: 0; font-size: 0.9rem;">
                                {result.get('limitation', '')}
                            </p>
                        </div>
                        ''' if result.get('limitation') else ''}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display JSON output
                st.markdown("### 📋 JSON Output")
                st.code(json.dumps({
                    "video_id": result['video_id'],
                    "timestamp_start": result['timestamp_start'],
                    "timestamp_end": result['timestamp_end'],
                    "confidence": result['confidence'],
                    "transcript_snippet": result['transcript_snippet']
                }, indent=2), language="json")
                
            else:
                st.error("❌ No video source found for this text snippet.")
                st.markdown("""
                **Suggestions:**
                - Try a more specific or unique text snippet
                - Check if the text might be from a video that's not indexed yet
                - Try adding specific video IDs manually in the sidebar
                """)
    else:
        st.warning("Please enter a text snippet to search for.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Powered by YouTube Transcripts | Built with Streamlit and RAG Technology
    </div>
    """,
    unsafe_allow_html=True
)
