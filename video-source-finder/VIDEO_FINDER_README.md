# Video Source Finder - Complete Documentation

## Overview

The Video Source Finder is a sophisticated system that finds the original video source for any text snippet using Retrieval-Augmented Generation (RAG) technology. It searches through YouTube videos to locate where specific text was spoken, providing timestamps and confidence scores.

## Features

- **YouTube Transcript Extraction**: Automatically extracts transcripts from YouTube videos
- **Semantic Search**: Uses embeddings to find semantically similar content
- **Multiple Search APIs**: Integrates with Serper and Tavily for video discovery
- **Real-time Processing**: Fast search and retrieval of video sources
- **Confidence Scoring**: Provides confidence scores for search results
- **Web Interface**: User-friendly Streamlit application

## Project Structure

```
video-source-finder/
├── video_finder_config.py          # Configuration settings
├── youtube_transcript_manager.py   # YouTube transcript handling
├── video_search_api.py            # Video search APIs (Serper, Tavily)
├── video_embedding_manager.py     # Embedding and vector database management
├── video_source_finder.py         # Main finder class
├── video_finder_app.py            # Streamlit web application
├── test_video_finder.py           # Test script
├── video_finder_requirements.txt  # Python dependencies
└── .env.video_finder              # Environment variables template
```

## Installation

1. **Set up virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r video_finder_requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.video_finder .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   SERPER_API_KEY=your_serper_api_key_here
   TAVILY_API_KEY=your_tavily_api_key_here
   ```

## Usage

### Web Interface

Run the Streamlit application:
```bash
streamlit run video_finder_app.py
```

Open your browser to `http://localhost:8501` and:
1. Enter a text snippet in the text area
2. Click "Find Video Source"
3. View the results with video ID, timestamps, and confidence score

### Programmatic Usage

```python
from video_source_finder import VideoSourceFinder

# Initialize the finder
finder = VideoSourceFinder()

# Find video source for a text snippet
result = finder.find_video_source("Hello everyone, welcome to my channel")

if result:
    print(f"Video ID: {result['video_id']}")
    print(f"Start Time: {result['timestamp_start']}")
    print(f"End Time: {result['timestamp_end']}")
    print(f"Confidence: {result['confidence']}")
```

### Manual Video Addition

```python
# Add a specific video to the database
success = finder.add_video_to_database("dQw4w9WgXcQ")
```

## API Response Format

The system returns results in the following JSON format:

```json
{
    "video_id": "dQw4w9WgXcQ",
    "timestamp_start": "00:00:15",
    "timestamp_end": "00:00:25",
    "confidence": 0.85,
    "transcript_snippet": "[00:00:15] Hello everyone, welcome to my channel..."
}
```

## Configuration

Key configuration options in `video_finder_config.py`:

- **Embedding Model**: `all-MiniLM-L6-v2` (can be changed)
- **Similarity Threshold**: `0.7` (minimum confidence for results)
- **Chunk Size**: `500` characters (for transcript processing)
- **Top K Results**: `5` (number of results to return)
- **Supported Languages**: `['en', 'pt', 'es']` (transcript languages)

## How It Works

1. **Text Input**: User provides a text snippet
2. **Embedding Generation**: Text is converted to vector embeddings
3. **Database Search**: Similar content is found in the vector database
4. **Video Discovery**: If not found, new videos are discovered via search APIs
5. **Transcript Extraction**: YouTube transcripts are extracted and indexed
6. **Result Generation**: Best match is returned with timestamps and confidence

## Testing

Run the test script to verify functionality:

```bash
python test_video_finder.py
```

This will test:
- Basic text snippet searches
- Manual video addition
- Database statistics
- Error handling

## Limitations

- **API Rate Limits**: YouTube and search APIs have rate limits
- **Transcript Availability**: Not all videos have transcripts
- **Language Support**: Limited to configured languages
- **Accuracy**: Depends on transcript quality and embedding similarity

## Troubleshooting

### Common Issues

1. **"No video source found"**:
   - Try more specific or unique text snippets
   - Check if videos have transcripts available
   - Verify API keys are correctly set

2. **"Error extracting transcript"**:
   - Video might not have transcripts
   - Check video ID format
   - Verify internet connection

3. **Low confidence scores**:
   - Text snippet might be too generic
   - Try more specific phrases
   - Check if video is properly indexed

### Debug Mode

Enable debug logging by setting environment variable:
```bash
export DEBUG=1
```

## Future Enhancements

- **Multi-language Support**: Expand language detection and processing
- **Video Categories**: Organize videos by topic/category
- **Batch Processing**: Process multiple text snippets at once
- **API Rate Limiting**: Implement intelligent rate limiting
- **Caching**: Add caching for frequently searched content
- **Advanced Search**: Implement fuzzy matching and typo tolerance

## License

This project is for educational and demonstration purposes. Please ensure compliance with YouTube's Terms of Service and API usage policies.
