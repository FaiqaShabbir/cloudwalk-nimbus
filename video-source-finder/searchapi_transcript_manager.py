import os
import json
import re
import time
import random
import shutil
import requests
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from video_finder_config import VideoFinderConfig

class SearchAPITranscriptManager:
    """Manages YouTube transcript extraction using SearchAPI to bypass IP blocking"""
    
    def __init__(self):
        self.config = VideoFinderConfig()
        
        # Initialize ChromaDB client with proper error handling
        # Check if database already exists to avoid settings conflicts
        db_exists = os.path.exists(self.config.CHROMA_PERSIST_DIRECTORY)
        
        try:
            if db_exists:
                # If database exists, connect without settings to avoid conflicts
                self.client = chromadb.PersistentClient(
                    path=self.config.CHROMA_PERSIST_DIRECTORY
                )
            else:
                # If database doesn't exist, create with settings
                self.client = chromadb.PersistentClient(
                    path=self.config.CHROMA_PERSIST_DIRECTORY,
                    settings=Settings(anonymized_telemetry=False)
                )
            
            self.collection = self.client.get_or_create_collection(
                name=self.config.COLLECTION_NAME
            )
        except (ValueError, Exception) as e:
            # Handle schema mismatch or other database issues
            error_str = str(e).lower()
            if ("already exists" in error_str or "different settings" in error_str or 
                "no such column" in error_str or "operationalerror" in error_str):
                print("Warning: Database schema mismatch detected. Attempting to recreate database...")
                
                # Try to close any existing client first
                try:
                    if hasattr(self, 'client') and self.client:
                        del self.client
                except:
                    pass
                
                # Try to use existing database without settings first (most reliable)
                print("Attempting to connect with existing database without settings...")
                try:
                    self.client = chromadb.PersistentClient(
                        path=self.config.CHROMA_PERSIST_DIRECTORY
                    )
                    self.collection = self.client.get_or_create_collection(
                        name=self.config.COLLECTION_NAME
                    )
                    print("Successfully connected to existing database.")
                    return
                except Exception as e_connect:
                    print(f"Could not connect to existing database: {str(e_connect)}")
                    # If connection failed, try to delete and recreate
                    print("Attempting to delete and recreate database...")
                    try:
                        if os.path.exists(self.config.CHROMA_PERSIST_DIRECTORY):
                            try:
                                shutil.rmtree(self.config.CHROMA_PERSIST_DIRECTORY)
                                print("Database deleted successfully.")
                            except PermissionError as pe:
                                print(f"Could not delete database (locked by another process): {str(pe)}")
                                print("Using existing database with compatibility mode...")
                                # Try one more time without settings
                                self.client = chromadb.PersistentClient(
                                    path=self.config.CHROMA_PERSIST_DIRECTORY
                                )
                                self.collection = self.client.get_or_create_collection(
                                    name=self.config.COLLECTION_NAME
                                )
                                print("Connected to existing database.")
                                return
                        print("Creating new database...")
                        self.client = chromadb.PersistentClient(
                            path=self.config.CHROMA_PERSIST_DIRECTORY,
                            settings=Settings(anonymized_telemetry=False)
                        )
                        self.collection = self.client.get_or_create_collection(
                            name=self.config.COLLECTION_NAME
                        )
                        print("New database created successfully.")
                    except Exception as e2:
                        print(f"Failed to recreate database: {str(e2)}")
                        print("Falling back to existing database without settings...")
                        try:
                            self.client = chromadb.PersistentClient(
                                path=self.config.CHROMA_PERSIST_DIRECTORY
                            )
                            self.collection = self.client.get_or_create_collection(
                                name=self.config.COLLECTION_NAME
                            )
                            print("Successfully using existing database.")
                            return
                        except Exception as e3:
                            print(f"Final fallback also failed: {str(e3)}")
                            raise
            else:
                print(f"Unexpected ChromaDB error: {str(e)}")
                raise
        
        self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
        )
    
    def get_video_transcript(self, video_id: str, languages: List[str] = None) -> Optional[Dict]:
        """Extract transcript from a YouTube video using SearchAPI"""
        if languages is None:
            languages = self.config.SUPPORTED_LANGUAGES
        
        if not self.config.SEARCHAPI_API_KEY:
            print("SearchAPI API key not configured")
            return None
        
        max_retries = self.config.SEARCHAPI_RETRY_ATTEMPTS
        for attempt in range(max_retries):
            try:
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = random.uniform(1, 3) * (attempt + 1)
                    print(f"Waiting {delay:.1f} seconds before retry {attempt + 1}...")
                    time.sleep(delay)
                
                print(f"Attempt {attempt + 1}/{max_retries} to get transcript for video {video_id} using SearchAPI")
                
                # Try each language preference
                for lang in languages:
                    transcript_data = self._fetch_transcript_from_searchapi(video_id, lang)
                    if transcript_data:
                        print(f"Successfully extracted transcript for video {video_id} in language {lang}")
                        return {
                            'video_id': video_id,
                            'transcript': self._format_transcript_with_timestamps(transcript_data),
                            'raw_transcript': transcript_data,
                            'language': lang,
                            'duration': self._calculate_duration(transcript_data),
                            'source': 'searchapi'
                        }
                
                print(f"No transcript available for video {video_id} in any preferred language")
                return None
                
            except Exception as e:
                error_msg = str(e).lower()
                print(f"Attempt {attempt + 1} failed for video {video_id}: {str(e)}")
                
                if "rate limit" in error_msg or "quota" in error_msg:
                    print("Rate limit detected, will retry...")
                    if attempt == max_retries - 1:
                        print("Max retries reached for SearchAPI")
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
    
    def _fetch_transcript_from_searchapi(self, video_id: str, lang: str = 'en') -> Optional[List[Dict]]:
        """Fetch transcript from SearchAPI"""
        try:
            url = self.config.SEARCHAPI_BASE_URL
            params = {
                'engine': 'youtube_transcripts',
                'video_id': video_id,
                'lang': lang,
                'api_key': self.config.SEARCHAPI_API_KEY
            }
            
            print(f"Fetching transcript from SearchAPI for video {video_id} in {lang}")
            response = requests.get(url, params=params, timeout=self.config.SEARCHAPI_TIMEOUT)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if transcript is available
                if 'transcripts' in data and data['transcripts']:
                    return data['transcripts']
                elif 'available_languages' in data:
                    print(f"Language {lang} not available. Available languages: {[lang_info['lang'] for lang_info in data['available_languages']]}")
                    return None
                else:
                    print(f"No transcript data in response for video {video_id}")
                    return None
            else:
                print(f"SearchAPI request failed with status code: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error fetching transcript: {str(e)}")
            return None
        except Exception as e:
            print(f"Error parsing SearchAPI response: {str(e)}")
            return None
    
    def _format_transcript_with_timestamps(self, transcript_data: List[Dict]) -> str:
        """Format transcript with timestamps for better search"""
        formatted_lines = []
        
        for entry in transcript_data:
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
    
    def _calculate_duration(self, transcript_data: List[Dict]) -> float:
        """Calculate total duration from transcript data"""
        if not transcript_data:
            return 0.0
        
        last_entry = transcript_data[-1]
        return last_entry['start'] + last_entry['duration']
    
    def search_transcript_chunks(self, query: str, video_id: str = None, top_k: int = 3) -> List[Dict]:
        """Search for transcript chunks using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Search in collection
            if video_id:
                # Filter by video_id if provided
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where={"video_id": video_id}
                )
            else:
                # Search all videos
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k
                )
            
            if not results['documents'] or not results['documents'][0]:
                return []
            
            # Format results
            matches = []
            for i, (doc, distance, metadata) in enumerate(zip(
                results['documents'][0],
                results['distances'][0],
                results['metadatas'][0]
            )):
                # Convert distance to similarity score (higher is better)
                similarity_score = 1 - distance
                
                matches.append({
                    'text': doc,
                    'timestamp': metadata.get('timestamp', '00:00:00'),
                    'video_id': metadata.get('video_id', ''),
                    'confidence': similarity_score,
                    'metadata': metadata
                })
            
            return matches
            
        except Exception as e:
            print(f"Error searching transcript chunks: {str(e)}")
            return []
    
    def add_video_transcript(self, video_id: str) -> bool:
        """Add a video transcript to the database using SearchAPI"""
        try:
            transcript_data = self.get_video_transcript(video_id)
            if not transcript_data:
                print(f"No transcript available for video {video_id}")
                return False
            
            # Process transcript into chunks
            chunks = self._process_transcript_into_chunks(transcript_data)
            
            if not chunks:
                print(f"No chunks created for video {video_id}")
                return False
            
            # Add chunks to database
            documents = [chunk['text'] for chunk in chunks]
            embeddings = self.embedding_model.encode(documents).tolist()
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [f"{video_id}_{i}" for i in range(len(chunks))]
            
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Successfully added {len(chunks)} chunks for video {video_id}")
            return True
            
        except Exception as e:
            print(f"Error adding video transcript {video_id}: {str(e)}")
            return False
    
    def _process_transcript_into_chunks(self, transcript_data: Dict) -> List[Dict]:
        """Process transcript data into searchable chunks"""
        try:
            raw_transcript = transcript_data['raw_transcript']
            video_id = transcript_data['video_id']
            
            chunks = []
            
            # Group transcript entries into meaningful chunks
            current_chunk = []
            current_start_time = 0
            
            for i, entry in enumerate(raw_transcript):
                current_chunk.append(entry)
                
                # Create chunk every 3-5 entries or when there's a natural break
                if len(current_chunk) >= 3 or i == len(raw_transcript) - 1:
                    # Combine text from chunk
                    chunk_text = " ".join([entry['text'] for entry in current_chunk])
                    
                    # Calculate timing
                    start_time = current_chunk[0]['start']
                    end_time = current_chunk[-1]['start'] + current_chunk[-1]['duration']
                    
                    chunks.append({
                        'text': chunk_text,
                        'metadata': {
                            'video_id': video_id,
                            'timestamp': self._format_timestamp(start_time),
                            'start_time': start_time,
                            'end_time': end_time,
                            'duration': end_time - start_time,
                            'chunk_size': len(current_chunk)
                        }
                    })
                    
                    # Reset for next chunk
                    current_chunk = []
            
            return chunks
            
        except Exception as e:
            print(f"Error processing transcript into chunks: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the video database"""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.config.COLLECTION_NAME,
                'embedding_model': self.config.EMBEDDING_MODEL,
                'note': 'Using SearchAPI for transcript extraction - bypasses IP blocking'
            }
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
            return {
                'total_chunks': 0,
                'collection_name': 'error_state',
                'embedding_model': 'unavailable',
                'note': f'Error: {str(e)}'
            }
