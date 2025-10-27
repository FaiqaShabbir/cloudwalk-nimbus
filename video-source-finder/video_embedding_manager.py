import os
import json
import shutil
import time
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from video_finder_config import VideoFinderConfig
from youtube_transcript_manager import YouTubeTranscriptManager
from video_search_api import VideoSearchAPI

class VideoEmbeddingManager:
    """Manages video transcript embeddings and similarity search"""
    
    def __init__(self):
        self.config = VideoFinderConfig()
        self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            length_function=len,
        )
        
        # Initialize ChromaDB
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
                    print("Successfully connected to existing database.")
                except Exception as e_connect:
                    print(f"Could not connect to existing database: {str(e_connect)}")
                    # If connection failed, try to delete and recreate
                    try:
                        if os.path.exists(self.config.CHROMA_PERSIST_DIRECTORY):
                            try:
                                print("Attempting to delete database...")
                                shutil.rmtree(self.config.CHROMA_PERSIST_DIRECTORY)
                                print("Database deleted successfully.")
                                # Create new database
                                self.client = chromadb.PersistentClient(
                                    path=self.config.CHROMA_PERSIST_DIRECTORY,
                                    settings=Settings(anonymized_telemetry=False)
                                )
                                print("New database created successfully.")
                            except PermissionError as pe:
                                print(f"Could not delete database (locked): {str(pe)}")
                                print("Using existing database in compatibility mode...")
                                self.client = chromadb.PersistentClient(
                                    path=self.config.CHROMA_PERSIST_DIRECTORY
                                )
                                print("Connected to existing database.")
                        else:
                            # No database exists, create new one
                            self.client = chromadb.PersistentClient(
                                path=self.config.CHROMA_PERSIST_DIRECTORY,
                                settings=Settings(anonymized_telemetry=False)
                            )
                            print("New database created.")
                    except Exception as e2:
                        print(f"Failed to recreate database: {str(e2)}")
                        print("Final fallback: trying existing database...")
                        self.client = chromadb.PersistentClient(
                            path=self.config.CHROMA_PERSIST_DIRECTORY
                        )
                        print("Connected to existing database.")
            else:
                print(f"Unexpected ChromaDB error: {str(e)}")
                raise
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.config.COLLECTION_NAME)
        except:
            self.collection = self.client.create_collection(
                name=self.config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
        
        # Initialize other components
        self.transcript_manager = YouTubeTranscriptManager()
        self.search_api = VideoSearchAPI()
    
    def add_video_transcript(self, video_id: str) -> bool:
        """Add a video's transcript to the embedding database"""
        try:
            # Get transcript
            transcript_data = self.transcript_manager.get_video_transcript(video_id)
            if not transcript_data:
                return False
            
            # Check if video already exists
            existing = self.collection.get(where={"video_id": video_id})
            if existing['ids']:
                print(f"Video {video_id} already exists in database")
                return True
            
            # Chunk the transcript
            chunks = self.transcript_manager.chunk_transcript(transcript_data)
            
            # Prepare data for embedding
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [f"{video_id}_{i}" for i in range(len(chunks))]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(texts).tolist()
            
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(chunks)} chunks for video {video_id}")
            return True
            
        except Exception as e:
            print(f"Error adding video {video_id}: {str(e)}")
            return False
    
    def search_similar_content(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for similar content in the database"""
        if top_k is None:
            top_k = self.config.TOP_K_RESULTS
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # Search in collection
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    confidence = 1 - distance  # Convert distance to confidence
                    
                    if confidence >= self.config.SIMILARITY_THRESHOLD:
                        formatted_results.append({
                            'video_id': metadata['video_id'],
                            'timestamp': metadata['timestamp'],
                            'text': doc,
                            'confidence': confidence,
                            'chunk_id': metadata['chunk_id']
                        })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching similar content: {str(e)}")
            return []
    
    def find_video_source(self, text_snippet: str) -> Optional[Dict]:
        """Find the video source for a given text snippet"""
        try:
            # Search for similar content
            results = self.search_similar_content(text_snippet, top_k=3)
            
            if not results:
                return None
            
            # Get the best match
            best_match = results[0]
            
            # Extract timestamp information
            timestamp_start = best_match['timestamp']
            
            # Calculate end timestamp (approximate)
            timestamp_end = self._calculate_end_timestamp(
                best_match['text'], 
                timestamp_start
            )
            
            return {
                "video_id": best_match['video_id'],
                "timestamp_start": timestamp_start,
                "timestamp_end": timestamp_end,
                "confidence": best_match['confidence'],
                "transcript_snippet": best_match['text']
            }
            
        except Exception as e:
            print(f"Error finding video source: {str(e)}")
            return None
    
    def _calculate_end_timestamp(self, text: str, start_timestamp: str) -> str:
        """Calculate end timestamp based on text length"""
        try:
            # Convert start timestamp to seconds
            start_seconds = self._timestamp_to_seconds(start_timestamp)
            
            # Estimate duration based on text length (rough estimate: 150 words per minute)
            word_count = len(text.split())
            estimated_duration = (word_count / 150) * 60  # seconds
            
            # Add some buffer
            end_seconds = start_seconds + estimated_duration + 10
            
            return self._seconds_to_timestamp(end_seconds)
            
        except Exception as e:
            print(f"Error calculating end timestamp: {str(e)}")
            return start_timestamp
    
    def _timestamp_to_seconds(self, timestamp: str) -> float:
        """Convert HH:MM:SS to seconds"""
        try:
            parts = timestamp.split(':')
            if len(parts) == 3:
                hours, minutes, seconds = map(int, parts)
                return hours * 3600 + minutes * 60 + seconds
            elif len(parts) == 2:
                minutes, seconds = map(int, parts)
                return minutes * 60 + seconds
            else:
                return float(parts[0])
        except:
            return 0.0
    
    def _seconds_to_timestamp(self, seconds: float) -> str:
        """Convert seconds to HH:MM:SS format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def discover_and_index_videos(self, search_query: str, max_videos: int = 5) -> List[str]:
        """Discover videos related to a query and index them"""
        try:
            # Search for videos
            videos = self.search_api.search_youtube_videos(search_query, max_videos)
            
            indexed_videos = []
            for video in videos:
                video_id = video['video_id']
                success = self.add_video_transcript(video_id)
                if success:
                    indexed_videos.append(video_id)
            
            return indexed_videos
            
        except Exception as e:
            print(f"Error discovering and indexing videos: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the database"""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.config.COLLECTION_NAME,
                'embedding_model': self.config.EMBEDDING_MODEL
            }
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
            return {}
