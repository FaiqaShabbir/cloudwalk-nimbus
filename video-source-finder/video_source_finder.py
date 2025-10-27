import os
import json
import time
import random
from typing import Dict, Optional, List
from video_search_api import VideoSearchAPI
from searchapi_transcript_manager import SearchAPITranscriptManager
from youtube_transcript_manager import YouTubeTranscriptManager
from video_finder_config import VideoFinderConfig

class VideoSourceFinder:
    """Main class for finding video sources from text snippets"""
    
    def __init__(self):
        self.config = VideoFinderConfig()
        self.search_api = VideoSearchAPI()
        
        # Try SearchAPI first, fallback to YouTube API
        if self.config.SEARCHAPI_API_KEY:
            print("Using SearchAPI for transcript extraction (bypasses IP blocking)")
            self.transcript_manager = SearchAPITranscriptManager()
        else:
            print("SearchAPI key not found, using YouTube transcript API with retry mechanism")
            self.transcript_manager = YouTubeTranscriptManager()
        
        self.retry_count = 0
        self.max_retries = 3
    
    def find_video_source(self, text_snippet: str) -> Optional[Dict]:
        """
        Find the video source for a given text snippet using SearchAPI or YouTube transcript API
        
        Args:
            text_snippet: The text to search for
            
        Returns:
            Dict with video_id, timestamp_start, timestamp_end, confidence, and transcript_snippet
            or None if not found
        """
        try:
            # FIRST: Search existing database for exact matches across ALL indexed videos
            print("Searching indexed transcripts for exact matches...")
            all_matches = self.transcript_manager.search_transcript_chunks(
                text_snippet, video_id=None, top_k=10  # Search across all videos
            )
            
            if all_matches:
                # Sort by confidence (highest first)
                all_matches.sort(key=lambda x: x['confidence'], reverse=True)
                best_match = all_matches[0]
                print(f"Found {len(all_matches)} potential matches in database")
                print(f"Top 3 matches:")
                for i, match in enumerate(all_matches[:3]):
                    print(f"  {i+1}. Video {match['video_id']} - Confidence: {match['confidence']:.2%}")
                print(f"Using best match with confidence: {best_match['confidence']:.2%}")
                
                # Only return if confidence is high enough
                if best_match['confidence'] >= 0.6:
                    return {
                        "video_id": best_match['video_id'],
                        "timestamp_start": best_match['timestamp'],
                        "timestamp_end": self._calculate_end_timestamp(
                            best_match['text'], best_match['timestamp']
                        ),
                        "confidence": best_match['confidence'],
                        "transcript_snippet": best_match['text'],
                        "title": f"Video {best_match['video_id']}",
                        "url": f'https://www.youtube.com/watch?v={best_match["video_id"]}',
                        "note": f"Exact transcript match from indexed database",
                        "method": "Exact Transcript Match"
                    }
                else:
                    print(f"Best match confidence {best_match['confidence']:.2%} is too low, searching for new videos...")
            
            # Extract keywords from the text snippet for search
            keywords = self._extract_keywords(text_snippet)
            search_query = " ".join(keywords[:5])  # Use top 5 keywords
            
            print(f"Searching for videos related to: {search_query}")
            
            # Search for videos using the API
            videos = self.search_api.search_youtube_videos(search_query, max_results=15)
            
            if not videos:
                return None
            
            # Try to find exact timestamp matches using transcript API
            best_result = None
            best_confidence = 0
            video_count = 0
            
            print(f"Checking {len(videos)} videos for exact matches...")
            for video in videos:
                video_id = video['video_id']
                video_count += 1
                print(f"Checking video {video_count}/{len(videos)}: {video_id}")
                
                # Try transcript API (SearchAPI or YouTube API with retry mechanism)
                transcript_result = self._get_transcript_with_retry(video_id, text_snippet)
                
                # Track the best match across all videos
                if transcript_result and transcript_result['confidence'] > best_confidence:
                    best_result = transcript_result
                    best_confidence = transcript_result['confidence']
                    print(f"New best match found! Confidence: {best_confidence:.2%}")
                
                # Add delay between video checks to avoid rate limiting
                time.sleep(random.uniform(0.5, 1.5))
            
            if best_result:
                print(f"Best overall match: Video {best_result['video_id']} with confidence {best_result['confidence']:.2%}")
                return best_result
            
            # If no transcript matches found, use content analysis fallback
            print("No transcript matches found, using content analysis fallback")
            best_match = self._find_best_video_match(text_snippet, videos)
            
            if best_match:
                return best_match
            
            # Final fallback to first video with intelligent estimation
            first_video = videos[0]
            estimated_timestamps = self._estimate_timestamps_from_content(text_snippet, first_video)
            
            return {
                "video_id": first_video['video_id'],
                "timestamp_start": estimated_timestamps['start'],
                "timestamp_end": estimated_timestamps['end'], 
                "confidence": 0.4,  # Lower confidence for fallback
                "transcript_snippet": f"Content-matched location: '{text_snippet[:100]}...'",
                "title": first_video.get('title', ''),
                "url": first_video.get('url', f'https://www.youtube.com/watch?v={first_video["video_id"]}'),
                "note": "Using content analysis fallback - transcript API unavailable",
                "method": "Content-based video matching (fallback)"
            }
            
        except Exception as e:
            print(f"Error finding video source: {str(e)}")
            return None
    
    def _get_transcript_with_retry(self, video_id: str, text_snippet: str) -> Optional[Dict]:
        """Get transcript with retry mechanism (SearchAPI or YouTube API)"""
        # Check if we have SearchAPI (no retry needed, it handles IP blocking)
        if hasattr(self.transcript_manager, 'config') and self.transcript_manager.config.SEARCHAPI_API_KEY:
            return self._get_transcript_searchapi(video_id, text_snippet)
        else:
            return self._get_transcript_youtube_api(video_id, text_snippet)
    
    def _get_transcript_searchapi(self, video_id: str, text_snippet: str) -> Optional[Dict]:
        """Get transcript using SearchAPI (bypasses IP blocking)"""
        try:
            print(f"Using SearchAPI for video {video_id}")
            
            # First, try to get transcript and add to database
            transcript_data = self.transcript_manager.get_video_transcript(video_id)
            if not transcript_data:
                print(f"No transcript available for video {video_id}")
                return None
            
            # Add to database for future searches
            self.transcript_manager.add_video_transcript(video_id)
            
            # Search for matches in the transcript
            matches = self.transcript_manager.search_transcript_chunks(
                text_snippet, video_id, top_k=3
            )
            
            if matches:
                best_match = matches[0]
                print(f"Found SearchAPI transcript match for video {video_id}")
                return {
                    "video_id": video_id,
                    "timestamp_start": best_match['timestamp'],
                    "timestamp_end": self._calculate_end_timestamp(
                        best_match['text'], best_match['timestamp']
                    ),
                    "confidence": best_match['confidence'],
                    "transcript_snippet": best_match['text'],
                    "title": f"Video {video_id}",
                    "url": f'https://www.youtube.com/watch?v={video_id}',
                    "note": "Exact transcript match via SearchAPI",
                    "method": "SearchAPI YouTube Transcripts"
                }
            else:
                print(f"No transcript matches found for video {video_id}")
                return None
                
        except Exception as e:
            print(f"SearchAPI error for video {video_id}: {str(e)}")
            return None
    
    def _get_transcript_youtube_api(self, video_id: str, text_snippet: str) -> Optional[Dict]:
        """Get transcript using YouTube API with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                print(f"Attempt {attempt + 1}/{self.max_retries} for video {video_id}")
                
                # Add random delay to avoid rate limiting
                if attempt > 0:
                    delay = random.uniform(2, 5) * (attempt + 1)  # Exponential backoff
                    print(f"Waiting {delay:.1f} seconds before retry...")
                    time.sleep(delay)
                
                # Try to get transcript and search for matches
                matches = self.transcript_manager.search_transcript_chunks(
                    text_snippet, video_id, top_k=3
                )
                
                if matches:
                    # Find the best match
                    best_match = matches[0]
                    print(f"Found transcript match for video {video_id}")
                    return {
                        "video_id": video_id,
                        "timestamp_start": best_match['timestamp'],
                        "timestamp_end": self._calculate_end_timestamp(
                            best_match['text'], best_match['timestamp']
                        ),
                        "confidence": best_match['confidence'],
                        "transcript_snippet": best_match['text'],
                        "title": f"Video {video_id}",
                        "url": f'https://www.youtube.com/watch?v={video_id}',
                        "note": f"Exact transcript match (attempt {attempt + 1})",
                        "method": "YouTube Transcript API"
                    }
                else:
                    print(f"No transcript matches found for video {video_id}")
                    return None
                    
            except Exception as e:
                error_msg = str(e).lower()
                print(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if "blocked" in error_msg or "ip" in error_msg:
                    print("IP blocking detected, will retry with delay...")
                    continue
                elif "not found" in error_msg or "disabled" in error_msg:
                    print("Transcript not available for this video")
                    return None
                else:
                    print(f"Unexpected error: {str(e)}")
                    if attempt == self.max_retries - 1:
                        print("Max retries reached, giving up on transcript API")
                        return None
                    continue
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for search"""
        import re
        
        # Simple keyword extraction (can be enhanced with NLP libraries)
        # Remove common words and extract meaningful terms
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Clean and split text
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [word for word in words if len(word) > 2 and word not in stop_words]
        
        # Remove duplicates and return
        return list(set(keywords))
    
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
    
    def _find_best_video_match(self, text_snippet: str, videos: List[Dict]) -> Optional[Dict]:
        """Find the best video match using advanced content analysis"""
        try:
            snippet_lower = text_snippet.lower()
            snippet_words = set(snippet_lower.split())
            
            best_match = None
            best_score = 0
            
            for video in videos:
                score = 0
                title = video.get('title', '').lower()
                description = video.get('description', '').lower()
                
                # Calculate content similarity score
                title_words = set(title.split())
                desc_words = set(description.split())
                
                # Title matching (higher weight)
                title_matches = len(snippet_words.intersection(title_words))
                score += title_matches * 3
                
                # Description matching
                desc_matches = len(snippet_words.intersection(desc_words))
                score += desc_matches * 2
                
                # Keyword density analysis
                snippet_keywords = self._extract_keywords(text_snippet)
                for keyword in snippet_keywords:
                    if keyword in title:
                        score += 2
                    if keyword in description:
                        score += 1
                
                # Content type analysis
                content_type_score = self._analyze_content_type(text_snippet, title, description)
                score += content_type_score
                
                if score > best_score:
                    best_score = score
                    best_match = video
            
            if best_match and best_score > 2:  # Minimum threshold
                estimated_timestamps = self._estimate_timestamps_from_content(text_snippet, best_match)
                return {
                    "video_id": best_match['video_id'],
                    "timestamp_start": estimated_timestamps['start'],
                    "timestamp_end": estimated_timestamps['end'],
                    "confidence": min(0.9, 0.5 + (best_score * 0.05)),  # Dynamic confidence
                    "transcript_snippet": f"Content-matched: '{text_snippet[:100]}...'",
                    "title": best_match.get('title', ''),
                    "url": best_match.get('url', f'https://www.youtube.com/watch?v={best_match["video_id"]}'),
                    "note": f"Advanced content analysis (score: {best_score:.1f})",
                    "method": "Content-based matching"
                }
            
            return None
            
        except Exception as e:
            print(f"Error in content analysis: {str(e)}")
            return None
    
    def _analyze_content_type(self, text_snippet: str, title: str, description: str) -> float:
        """Analyze content type to improve timestamp estimation"""
        snippet_lower = text_snippet.lower()
        title_lower = title.lower()
        desc_lower = description.lower()
        
        score = 0
        
        # Educational content indicators
        if any(word in snippet_lower for word in ['learn', 'teach', 'tutorial', 'guide', 'how to']):
            if any(word in title_lower for word in ['tutorial', 'guide', 'learn', 'how to']):
                score += 3
        
        # Speaking/presentation indicators
        if any(word in snippet_lower for word in ['speaking', 'presentation', 'speech', 'talk']):
            if any(word in title_lower for word in ['speaking', 'presentation', 'speech', 'talk']):
                score += 3
        
        # Habit/improvement indicators
        if any(word in snippet_lower for word in ['habit', 'improve', 'better', 'tips']):
            if any(word in title_lower for word in ['habit', 'improve', 'tips', 'better']):
                score += 2
        
        return score
    
    def _estimate_timestamps_from_content(self, text_snippet: str, video: Dict) -> Dict:
        """Estimate timestamps based on advanced content analysis"""
        try:
            snippet_lower = text_snippet.lower()
            snippet_length = len(text_snippet.split())
            title = video.get('title', '').lower()
            
            # Advanced position estimation based on content analysis
            if any(word in snippet_lower for word in ['introduction', 'welcome', 'hello', 'hi', 'start']):
                start_seconds = 15  # Very beginning
            elif any(word in snippet_lower for word in ['conclusion', 'summary', 'thanks', 'goodbye', 'end']):
                start_seconds = 300  # Near end
            elif any(word in snippet_lower for word in ['example', 'demonstration', 'tutorial', 'practice']):
                start_seconds = 120  # Middle section
            elif any(word in snippet_lower for word in ['habit', 'tip', 'advice', 'technique']):
                # For habit/tip content, estimate based on video structure
                if 'habit' in snippet_lower:
                    # Habits are often listed, estimate position based on content
                    habit_number = self._extract_habit_number(text_snippet)
                    if habit_number:
                        start_seconds = 30 + (habit_number * 45)  # 45 seconds per habit
                    else:
                        start_seconds = 90  # Default for habits
                else:
                    start_seconds = 60  # Tips usually early
            else:
                # Default intelligent estimation
                start_seconds = 60  # 1 minute in
            
            # Calculate duration based on content complexity
            if snippet_length <= 5:
                estimated_duration = 20  # Short snippets
            elif snippet_length <= 15:
                estimated_duration = 45  # Medium snippets
            else:
                estimated_duration = 60  # Longer snippets
            
            return {
                'start': self._seconds_to_timestamp(start_seconds),
                'end': self._seconds_to_timestamp(start_seconds + estimated_duration)
            }
            
        except Exception as e:
            print(f"Error estimating timestamps: {str(e)}")
            return {
                'start': '00:01:00',  # Default 1 minute
                'end': '00:01:30'     # Default 30 seconds duration
            }
    
    def _extract_habit_number(self, text_snippet: str) -> Optional[int]:
        """Extract habit number from text snippet"""
        import re
        
        # Look for patterns like "9 Habits", "Habit 3", "First habit", etc.
        patterns = [
            r'(\d+)\s*habits?',
            r'habit\s*(\d+)',
            r'(\d+)(?:st|nd|rd|th)\s*habit',
            r'first\s*habit',
            r'second\s*habit',
            r'third\s*habit'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text_snippet.lower())
            if match:
                if 'first' in pattern:
                    return 1
                elif 'second' in pattern:
                    return 2
                elif 'third' in pattern:
                    return 3
                else:
                    return int(match.group(1))
        
        return None
    
    def add_video_to_database(self, video_id: str) -> bool:
        """Add a specific video to the database using transcript API"""
        try:
            print(f"Adding video {video_id} to database using transcript API...")
            return self.transcript_manager.add_video_transcript(video_id)
        except Exception as e:
            print(f"Error adding video {video_id}: {str(e)}")
            return False
    
    def get_database_stats(self) -> Dict:
        """Get statistics about the video database"""
        try:
            return self.transcript_manager.get_database_stats()
        except Exception as e:
            print(f"Error getting database stats: {str(e)}")
            return {
                'total_chunks': 0,
                'collection_name': 'error_state',
                'embedding_model': 'unavailable',
                'note': f'Error: {str(e)}'
            }
    
    def search_videos_by_query(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for videos by query"""
        return self.search_api.search_youtube_videos(query, max_results)
