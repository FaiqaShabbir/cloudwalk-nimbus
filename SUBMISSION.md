# Project Submission

This repository contains two challenge implementations for the CloudWalk Nimbus challenge:

## 1. Find the Video Source 🎥

**Goal**: Given a snippet of text (from a book, paper, article, or transcript), find the original video where it was spoken.

**Input**: Text snippet (plain text)
**Output**: 
```json
{
  "video_id": "yt123",
  "timestamp_start": "00:14:05",
  "timestamp_end": "00:14:38",
  "confidence": 0.85,
  "transcript_snippet": "..."
}
```

**Technology Stack**:

- YouTube transcript extraction (SearchAPI + YouTube Transcript API)
- Vector embeddings (Sentence Transformers)
- Semantic search (ChromaDB)
- Search APIs (Serper, Tavily)
- Streamlit web interface

**Key Features**:

- Searches ALL indexed videos for exact matches first
- Falls back to discovering new videos if needed
- Returns highest confidence matches
- Real-time video indexing and transcript processing
- Multiple search API integration for redundancy

## 2. CloudWalk Chatbot 📱

**Goal**: Build a chatbot that explains what CloudWalk is, its products (like InfinitePay), mission, and brand values.

**Input**: User questions via chat interface
**Output**: Natural language answers (with Markdown formatting support)

**Technology Stack**:

- Retrieval-Augmented Generation (RAG)
- OpenAI GPT-3.5-turbo
- ChromaDB for vector storage
- LangChain for document processing
- Streamlit web interface
- Static knowledge base (knowledge_base.md)

**Key Features**:

- Comprehensive knowledge base about CloudWalk
- RAG technology for accurate, contextual responses
- Pre-defined quick questions for common queries
- Support for InfinitePay and other CloudWalk products
- Company mission and values information

## Sample Conversations (CloudWalk Chatbot)

See `cloudwalk-chatbot/README.md` for detailed sample conversations including:
1. Company Overview - "What is CloudWalk?"
2. Product Information - "Tell me about InfinitePay and its features"
3. Mission and Values - "What are CloudWalk's core values and mission?"

## Setup Instructions

### Prerequisites

- Python 3.8+
- API Keys (see environment setup below)

### Quick Start

**Windows**:
```bash
# Setup virtual environments (one-time)
setup_venv.bat

# Run CloudWalk Chatbot
run_cloudwalk_chatbot.bat

# Run Video Source Finder
run_video_finder.bat
```

**Linux/Mac**:
```bash
# Setup virtual environments (one-time)
chmod +x setup_venv.sh
./setup_venv.sh

# Run CloudWalk Chatbot
chmod +x run_cloudwalk_chatbot.sh
./run_cloudwalk_chatbot.sh

# Run Video Source Finder
chmod +x run_video_finder.sh
./run_video_finder.sh
```

### Environment Setup

1. **CloudWalk Chatbot**: 
   - Copy `cloudwalk-chatbot/env_template.txt` to `.env`
   - Add your `OPENAI_API_KEY`

2. **Video Source Finder**:
   - Copy `video-source-finder/env_template.txt` to `.env`
   - Add your API keys:
     - `OPENAI_API_KEY` (required)
     - `SERPER_API_KEY` (optional, recommended)
     - `TAVILY_API_KEY` (optional, recommended)
     - `SEARCHAPI_API_KEY` (optional, for YouTube transcripts)

### Testing

**CloudWalk Chatbot**:
```bash
cd cloudwalk-chatbot
python test_chatbot.py
```

**Video Source Finder**:
```bash
cd video-source-finder
python test_video_finder.py
```

## File Structure

```
Nimbus Level 1/
├── README.md                    # Main overview and quick start
├── SUBMISSION.md                # This file - implementation details
├── setup_venv.bat/sh            # One-time setup script
├── run_cloudwalk_chatbot.bat/sh # Run CloudWalk Chatbot
├── run_video_finder.bat/sh      # Run Video Source Finder
├── .gitignore                   # Protects sensitive data
│
├── cloudwalk-chatbot/           # Challenge 2: Chatbot project
│   ├── app.py                   # Streamlit interface
│   ├── chatbot.py               # RAG chatbot implementation
│   ├── knowledge_base_manager.py # Vector DB management
│   ├── knowledge_base.md         # CloudWalk information
│   ├── config.py                 # Configuration
│   ├── requirements.txt          # Dependencies
│   ├── test_chatbot.py           # Test script
│   ├── README.md                 # Documentation + 3 sample conversations
│   ├── env_template.txt          # Environment variables template
│   └── chroma_db/               # Vector database (included)
│
└── video-source-finder/         # Challenge 1: Video finder project
    ├── video_finder_app.py       # Streamlit interface
    ├── video_source_finder.py    # Main finder logic
    ├── searchapi_transcript_manager.py # Transcript processing
    ├── video_search_api.py       # Search APIs (Serper, Tavily)
    ├── video_embedding_manager.py # Embedding management
    ├── youtube_transcript_manager.py # YouTube transcript handling
    ├── video_finder_config.py    # Configuration
    ├── video_finder_requirements.txt # Dependencies
    ├── test_video_finder.py      # Test script
    ├── VIDEO_FINDER_README.md    # Documentation
    ├── env_template.txt          # Environment variables template
    └── video_chroma_db/         # Vector database (included)
```

## Implementation Details

### Video Source Finder

- **Database**: Searches across all indexed videos for exact transcript matches
- **Confidence**: Returns only matches with confidence ≥ 60%
- **Fallback**: Discovers and indexes new videos when needed
- **APIs**: Primary (Serper), Fallback (Tavily), Direct (YouTube)
- **Output Format**: JSON with video_id, timestamps, confidence, and transcript snippet

### CloudWalk Chatbot

- **RAG**: Uses retrieval-augmented generation for accurate responses
- **Knowledge Base**: Comprehensive markdown file with CloudWalk information
- **Sample Conversations**: 3 detailed examples included in README
- **Features**: Quick questions, chat history, contextual responses
