import os
import json
import re
import requests
from typing import List, Dict, Optional
from tavily import TavilyClient
from video_finder_config import VideoFinderConfig

class VideoSearchAPI:
    """Handles video search using various APIs"""
    
    def __init__(self):
        self.config = VideoFinderConfig()
        self.tavily_client = None
        
        # Initialize Tavily if API key is available
        if self.config.TAVILY_API_KEY:
            self.tavily_client = TavilyClient(api_key=self.config.TAVILY_API_KEY)
    
    def search_youtube_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for YouTube videos using Serper API or Tavily as primary method"""
        videos = []
        
        # Use Serper API as primary search method
        if self.config.SERPER_API_KEY:
            try:
                print(f"Searching with Serper API for: {query}")
                search_url = "https://google.serper.dev/youtube"
                headers = {
                    "X-API-KEY": self.config.SERPER_API_KEY,
                    "Content-Type": "application/json"
                }
                payload = {
                    "q": query,
                    "num": max_results
                }
                
                response = requests.post(search_url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    results = response.json()
                    
                    # Extract videos from Serper response
                    organic_videos = results.get('organic', [])
                    
                    for video in organic_videos:
                        video_id = video.get('videoId', '')
                        if video_id:
                            videos.append({
                                'video_id': video_id,
                                'title': video.get('title', ''),
                                'description': video.get('description', ''),
                                'url': f'https://www.youtube.com/watch?v={video_id}',
                                'source': 'serper'
                            })
                    
                    if videos:
                        print(f"Serper found {len(videos)} videos")
                        return videos
                else:
                    print(f"Serper API returned status code: {response.status_code}")
                    
            except Exception as e:
                print(f"Error with Serper API: {str(e)}")
        else:
            print("Serper API key not available")
        
        # Fallback to Tavily if Serper fails
        if self.tavily_client:
            try:
                print(f"Trying Tavily API as fallback for: {query}")
                tavily_results = self.tavily_client.search(
                    query=f"{query} site:youtube.com",
                    search_depth="basic",
                    max_results=max_results
                )
                
                if tavily_results and 'results' in tavily_results:
                    for result in tavily_results['results']:
                        url = result.get('url', '')
                        if 'youtube.com/watch' in url:
                            video_id = self._extract_video_id(url)
                            if video_id:
                                videos.append({
                                    'video_id': video_id,
                                    'title': result.get('title', ''),
                                    'description': result.get('content', ''),
                                    'url': url,
                                    'source': 'tavily'
                                })
                
                if videos:
                    print(f"Tavily found {len(videos)} videos")
                    return videos
                    
            except Exception as e:
                print(f"Tavily search failed: {str(e)}")
        
        # Final fallback to direct YouTube search
        return self._fallback_youtube_search(query, max_results)
    
    def search_with_tavily(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search for videos using Tavily API"""
        if not self.tavily_client:
            return []
        
        try:
            search_params = {
                "query": f"{query} youtube video",
                "search_depth": "basic",
                "max_results": max_results,
                "include_domains": ["youtube.com"]
            }
            
            results = self.tavily_client.search(**search_params)
            
            videos = []
            for result in results.get('results', []):
                if 'youtube.com/watch' in result.get('url', ''):
                    video_id = self._extract_video_id(result['url'])
                    if video_id:
                        videos.append({
                            'video_id': video_id,
                            'title': result.get('title', ''),
                            'description': result.get('content', ''),
                            'url': result.get('url', ''),
                            'source': 'tavily'
                        })
            
            return videos
            
        except Exception as e:
            print(f"Error with Tavily search: {str(e)}")
            return []
    
    def _fallback_youtube_search(self, query: str, max_results: int) -> List[Dict]:
        """Fallback search method using requests"""
        try:
            print(f"Using fallback search for: {query}")
            
            # Simple search using YouTube's search endpoint
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Fallback search failed with status code: {response.status_code}")
                return []
            
            # Extract video IDs from the response (simplified)
            video_ids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', response.text)
            
            if not video_ids:
                print("No video IDs found in fallback search")
                return []
            
            videos = []
            for video_id in video_ids[:max_results]:
                videos.append({
                    'video_id': video_id,
                    'title': f'Video {video_id}',
                    'description': '',
                    'url': f'https://www.youtube.com/watch?v={video_id}',
                    'source': 'fallback'
                })
            
            print(f"Fallback search found {len(videos)} videos")
            return videos
            
        except Exception as e:
            print(f"Error with fallback search: {str(e)}")
            return []
    
    def _extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """Get basic metadata for a video"""
        try:
            # This is a simplified version - in production, you'd use YouTube API
            return {
                'video_id': video_id,
                'url': f'https://www.youtube.com/watch?v={video_id}',
                'title': f'Video {video_id}',
                'description': 'Video description not available'
            }
        except Exception as e:
            print(f"Error getting metadata for video {video_id}: {str(e)}")
            return None
