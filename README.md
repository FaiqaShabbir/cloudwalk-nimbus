# CloudWalk Nimbus Challenge Submission 🚀

This repository contains my implementation of **two CloudWalk Nimbus challenges**:
1. **Find the Video Source** 🎥
2. **CloudWalk Chatbot** 📱

## 📋 Challenges Overview

### Challenge 1: Find the Video Source
**Goal**: Given a snippet of text, find the original video where it was spoken with timestamps.

**Implementation**:
- Searches ALL indexed YouTube videos for exact transcript matches
- Uses semantic search with embeddings (ChromaDB + Sentence Transformers)
- Multiple search APIs (Serper, Tavily) for video discovery
- Returns best match with confidence scoring
- Real-time indexing of new videos

### Challenge 2: CloudWalk Chatbot
**Goal**: Build a RAG-powered chatbot that explains CloudWalk's products, mission, and values.

**Implementation**:
- Retrieval-Augmented Generation with OpenAI
- Comprehensive knowledge base about CloudWalk and InfinitePay
- Interactive Streamlit chat interface
- Pre-defined quick questions
- Sample conversations included (see README in cloudwalk-chatbot/)

## 🎯 Key Features

This repository contains two main projects, each with its own virtual environment and dependencies:

## 1. CloudWalk Chatbot 📱
A RAG-powered chatbot that explains CloudWalk's products, mission, and brand values.

**Location**: `cloudwalk-chatbot/`

**Features**:
- Interactive chat interface with Streamlit
- Comprehensive knowledge base about CloudWalk
- RAG technology for accurate responses
- Information about InfinitePay, mission, and values

**Quick Start**:
```bash
# Windows
run_cloudwalk_chatbot.bat

# Linux/Mac
chmod +x run_cloudwalk_chatbot.sh
./run_cloudwalk_chatbot.sh
```

## 2. Video Source Finder 🎥
A system that finds the original video source for any text snippet using YouTube transcripts and embeddings.

**Location**: `video-source-finder/`

**Features**:
- YouTube transcript extraction
- Semantic search with embeddings
- Multiple search APIs (Serper, Tavily)
- Real-time video source detection
- Web interface for easy usage

**Quick Start**:
```bash
# Windows
run_video_finder.bat

# Linux/Mac
chmod +x run_video_finder.sh
./run_video_finder.sh
```

## Setup Instructions

### Initial Setup (One-time)

**Windows**:
```bash
setup_venv.bat
```

**Linux/Mac**:
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

This will create separate virtual environments for both projects and install all dependencies.

### Environment Variables Setup

1. **CloudWalk Chatbot**:
   ```bash
   cd cloudwalk-chatbot
   cp env_template.txt .env
   # Edit .env and add your OPENAI_API_KEY
   ```

2. **Video Source Finder**:
   ```bash
   cd video-source-finder
   cp env_template.txt .env
   # Edit .env and add your API keys (OPENAI_API_KEY, SERPER_API_KEY, TAVILY_API_KEY)
   ```

## Environment Variables Required

### CloudWalk Chatbot
- `OPENAI_API_KEY`: Your OpenAI API key

### Video Source Finder
- `OPENAI_API_KEY`: Your OpenAI API key
- `SERPER_API_KEY`: Your Serper API key (optional)
- `TAVILY_API_KEY`: Your Tavily API key (optional)

## Running the Applications

### CloudWalk Chatbot
```bash
# Windows
run_cloudwalk_chatbot.bat

# Linux/Mac
./run_cloudwalk_chatbot.sh
```
Access at: `http://localhost:8501`

### Video Source Finder
```bash
# Windows
run_video_finder.bat

# Linux/Mac
./run_video_finder.sh
```
Access at: `http://localhost:8501` (will use different port if CloudWalk is running)

## Testing

### Test CloudWalk Chatbot
```bash
cd cloudwalk-chatbot
cloudwalk-chatbot\venv\Scripts\activate  # Windows
# or source cloudwalk-chatbot/venv/bin/activate  # Linux/Mac
python test_chatbot.py
```

### Test Video Source Finder
```bash
cd video-source-finder
video-source-finder\venv\Scripts\activate  # Windows
# or source video-source-finder/venv/bin/activate  # Linux/Mac
python test_video_finder.py
```

## Project Structure

```
├── cloudwalk-chatbot/           # CloudWalk Chatbot project
│   ├── venv/                   # Virtual environment
│   ├── app.py                  # Streamlit interface
│   ├── chatbot.py             # Core chatbot logic
│   ├── config.py              # Configuration
│   ├── knowledge_base_manager.py  # Vector database
│   ├── knowledge_base.md       # CloudWalk information
│   ├── requirements.txt        # Dependencies
│   ├── README.md              # Documentation
│   ├── test_chatbot.py        # Test script
│   └── env_template.txt       # Environment variables template
├── video-source-finder/        # Video Source Finder project
│   ├── venv/                  # Virtual environment
│   ├── video_finder_config.py      # Configuration
│   ├── youtube_transcript_manager.py  # YouTube transcript handling
│   ├── video_search_api.py         # Search APIs
│   ├── video_embedding_manager.py  # Embedding management
│   ├── video_source_finder.py     # Main finder class
│   ├── video_finder_app.py        # Streamlit interface
│   ├── test_video_finder.py       # Test script
│   ├── video_finder_requirements.txt  # Dependencies
│   ├── VIDEO_FINDER_README.md     # Documentation
│   └── env_template.txt           # Environment variables template
├── setup_venv.bat             # Windows setup script
├── setup_venv.sh              # Linux/Mac setup script
├── run_cloudwalk_chatbot.bat  # Windows run script for CloudWalk
├── run_cloudwalk_chatbot.sh   # Linux/Mac run script for CloudWalk
├── run_video_finder.bat       # Windows run script for Video Finder
├── run_video_finder.sh        # Linux/Mac run script for Video Finder
└── README.md                  # This file
```

## Features Comparison

| Feature | CloudWalk Chatbot | Video Source Finder |
|---------|------------------|-------------------|
| **Technology** | RAG with static knowledge | RAG with dynamic video discovery |
| **Data Source** | Markdown knowledge base | YouTube transcripts |
| **Search Type** | Company information | Video content matching |
| **Output** | Natural language responses | Video ID + timestamps |
| **APIs Used** | OpenAI only | OpenAI + Serper + Tavily |
| **Real-time** | Static responses | Dynamic video discovery |

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure all required API keys are set in `.env` files
2. **Port Conflicts**: Use different ports if running both applications
3. **Dependencies**: Make sure all packages are installed correctly
4. **YouTube Access**: Some videos may not have transcripts available

### Getting Help

- Check the individual README files for detailed documentation
- Run test scripts to verify functionality
- Check console output for error messages
- Ensure internet connection for API calls

## 📝 Sample Conversations

The CloudWalk Chatbot includes 3 detailed sample conversations demonstrating:
1. Company Overview ("What is CloudWalk?")
2. Product Information ("Tell me about InfinitePay")
3. Mission and Values ("What are CloudWalk's core values?")

See `cloudwalk-chatbot/README.md` for full conversations.

## 🛠️ Technology Stack

### Video Source Finder
- **Python** 3.8+
- **Streamlit** - Web interface
- **ChromaDB** - Vector database
- **Sentence Transformers** - Embeddings
- **Serper API** - Video search
- **Tavily API** - Alternative search
- **SearchAPI** - YouTube transcripts
- **LangChain** - Document processing

### CloudWalk Chatbot
- **Python** 3.8+
- **Streamlit** - Web interface
- **OpenAI** - Language model
- **ChromaDB** - Vector database
- **LangChain** - RAG implementation
- **Sentence Transformers** - Embeddings

## 📊 Project Statistics

- **Total Files**: ~50+ Python files
- **Lines of Code**: ~5,000+ lines
- **Documentation**: 4 README files + submission docs
- **Test Coverage**: Test scripts for both projects
- **Dependencies**: 30+ packages

## 🚀 Future Enhancements

- Production deployment on Streamlit Cloud/Heroku
- Multi-language support expansion
- Advanced caching mechanisms
- Batch processing capabilities
- Real-time collaboration features

## 📧 Submission

**Email**: nimbus@cloudwalk.io  
**Repository**: `cloudwalk-nimbus-submission`  
**Status**: Ready for review ✅

## 👤 Author

This project was completed for the CloudWalk Nimbus Challenge.

## License

Both projects are for educational and demonstration purposes. Please ensure compliance with:
- YouTube's Terms of Service
- OpenAI's API usage policies
- Respect for intellectual property rights
