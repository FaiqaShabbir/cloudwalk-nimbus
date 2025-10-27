import os
import json
import re
import time
import random
from typing import List, Dict, Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from video_finder_config import VideoFinderConfig

class YouTubeTranscriptManager:
    """Manages YouTube transcript extraction and processing"""
    
    def __init__(self):
        self.config = VideoFinderConfig()
        self.formatter = TextFormatter()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def get_video_transcript(self, video_id: str, languages: List[str] = None) -> Optional[Dict]:
        """Extract transcript from a YouTube video with IP blocking workarounds"""
        if languages is None:
            languages = self.config.SUPPORTED_LANGUAGES
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = random.uniform(2, 5) * (attempt + 1)
                    print(f"Waiting {delay:.1f} seconds before retry {attempt + 1}...")
                    time.sleep(delay)
                
                print(f"Attempt {attempt + 1}/{max_retries} to get transcript for video {video_id}")
                
                # Create instance of YouTubeTranscriptApi
                ytt_api = YouTubeTranscriptApi()
                
                # Try to get transcript in preferred languages
                transcript_list = ytt_api.list(video_id)
                
                # Try to find transcript in preferred languages
                transcript = None
                for lang in languages:
                    try:
                        transcript = transcript_list.find_transcript([lang])
                        break
                    except:
                        continue
                
                # If no preferred language found, try to get any available transcript
                if transcript is None:
                    try:
                        # Get all available transcripts
                        available_transcripts = list(transcript_list)
                        if available_transcripts:
                            transcript = available_transcripts[0]
                    except:
                        pass
                
                # If still no transcript found, try manual transcript
                if transcript is None:
                    try:
                        transcript = transcript_list.find_manually_created_transcripts(['en'])[0]
                    except:
                        pass
                
                if transcript is None:
                    print(f"No transcript available for video {video_id}")
                    return None
                
                # Fetch the actual transcript
                transcript_data = transcript.fetch()
                
                # Format transcript with timestamps
                formatted_transcript = self._format_transcript_with_timestamps(transcript_data)
                
                print(f"Successfully extracted transcript for video {video_id}")
                return {
                    'video_id': video_id,
                    'transcript': formatted_transcript,
                    'raw_transcript': transcript_data,
                    'language': transcript.language_code,
                    'duration': self._calculate_duration(transcript_data)
                }
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"Attempt {attempt + 1} failed for video {video_id}: {str(e)}")
                
                if "blocked" in error_msg or "ip" in error_msg:
                    print("IP blocking detected, will retry...")
                    if attempt == max_retries - 1:
                        print("Max retries reached for transcript extraction")
                        return None
                    continue
                elif "not found" in error_msg or "disabled" in error_msg:
                    print("Transcript not available for this video")
                    return None
                else:
                    print(f"Unexpected error: {str(e)}")
                    if attempt == max_retries - 1:
                        print("Max retries reached, giving up")
                        return None
                    continue
        
        return None
    
    def _format_transcript_with_timestamps(self, transcript_data) -> str:
        """Format transcript with timestamps for better search"""
        formatted_lines = []
        
        for entry in transcript_data:
            # Handle both dictionary and object formats
            if hasattr(entry, 'start'):
                start_time = self._format_timestamp(entry.start)
                text = entry.text.strip()
            else:
                start_time = self._format_timestamp(entry['start'])
                text = entry['text'].strip()
            formatted_lines.append(f"[{start_time}] {text}")
        
        return "\n".join(formatted_lines)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _calculate_duration(self, transcript_data) -> float:
        """Calculate total duration of the transcript"""
        if not transcript_data:
            return 0.0
        
        last_entry = transcript_data[-1]
        # Handle both dictionary and object formats
        if hasattr(last_entry, 'start') and hasattr(last_entry, 'duration'):
            return last_entry.start + last_entry.duration
        else:
            return last_entry['start'] + last_entry['duration']
    
    def chunk_transcript(self, transcript_data: Dict) -> List[Document]:
        """Split transcript into searchable chunks"""
        transcript_text = transcript_data['transcript']
        video_id = transcript_data['video_id']
        
        # Split into chunks
        chunks = self.text_splitter.split_text(transcript_text)
        
        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            # Extract timestamp from chunk if available
            timestamp_match = re.search(r'\[(\d{2}:\d{2}:\d{2})\]', chunk)
            timestamp = timestamp_match.group(1) if timestamp_match else "00:00:00"
            
            doc = Document(
                page_content=chunk,
                metadata={
                    "video_id": video_id,
                    "chunk_id": i,
                    "timestamp": timestamp,
                    "language": transcript_data.get('language', 'en'),
                    "duration": transcript_data.get('duration', 0)
                }
            )
            documents.append(doc)
        
        return documents
    
    def search_transcript_chunks(self, query: str, video_id: str, top_k: int = 5) -> List[Dict]:
        """Search for specific text within a video's transcript"""
        transcript_data = self.get_video_transcript(video_id)
        if not transcript_data:
            return []
        
        chunks = self.chunk_transcript(transcript_data)
        
        # Simple text search for now (can be enhanced with embeddings)
        query_lower = query.lower()
        matches = []
        
        for chunk in chunks:
            if query_lower in chunk.page_content.lower():
                # Extract timestamp from chunk
                timestamp_match = re.search(r'\[(\d{2}:\d{2}:\d{2})\]', chunk.page_content)
                timestamp = timestamp_match.group(1) if timestamp_match else "00:00:00"
                
                matches.append({
                    'video_id': video_id,
                    'timestamp': timestamp,
                    'text': chunk.page_content,
                    'confidence': 0.8  # Simple confidence score
                })
        
        return matches[:top_k]
    
    def add_video_transcript(self, video_id: str) -> bool:
        """Add a video transcript to the database"""
        try:
            transcript_data = self.get_video_transcript(video_id)
            if transcript_data:
                # Here you would add the transcript to a database
                # For now, we'll just return True to indicate success
                print(f"Transcript for video {video_id} processed successfully")
                return True
            return False
        except Exception as e:
            print(f"Error adding video transcript {video_id}: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the video database"""
        return {
            'total_chunks': 0,  # Would be actual count from database
            'collection_name': 'youtube_transcripts',
            'embedding_model': 'sentence-transformers/all-MiniLM-L6-v2',
            'note': 'Transcript search enabled - using text matching'
        }
