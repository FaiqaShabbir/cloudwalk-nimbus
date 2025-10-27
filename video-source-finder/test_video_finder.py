# Test script for Video Source Finder

import os
from video_source_finder import VideoSourceFinder

def test_video_finder():
    """Test the Video Source Finder with sample text snippets"""
    
    # Initialize video finder
    print("Initializing Video Source Finder...")
    video_finder = VideoSourceFinder()
    
    # Test text snippets
    test_snippets = [
        "Hello everyone, welcome to my channel",
        "In today's video, I'm going to show you how to",
        "Don't forget to like and subscribe if you enjoyed this video",
        "Let me know in the comments below what you think",
        "Thanks for watching, see you in the next video"
    ]
    
    print("\n" + "="*60)
    print("TESTING VIDEO SOURCE FINDER")
    print("="*60)
    
    for i, snippet in enumerate(test_snippets, 1):
        print(f"\nTest {i}: '{snippet}'")
        print("-" * 50)
        
        try:
            result = video_finder.find_video_source(snippet)
            
            if result:
                print(f"✅ Video found!")
                print(f"   Video ID: {result['video_id']}")
                print(f"   Start Time: {result['timestamp_start']}")
                print(f"   End Time: {result['timestamp_end']}")
                print(f"   Confidence: {result['confidence']:.2%}")
                print(f"   Transcript: {result['transcript_snippet'][:100]}...")
            else:
                print("❌ No video source found")
                
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 50)
    
    # Test database stats
    print("\n" + "="*60)
    print("DATABASE STATISTICS")
    print("="*60)
    
    stats = video_finder.get_database_stats()
    if stats:
        print(f"Total chunks indexed: {stats.get('total_chunks', 0)}")
        print(f"Collection name: {stats.get('collection_name', 'N/A')}")
        print(f"Embedding model: {stats.get('embedding_model', 'N/A')}")
    else:
        print("No database statistics available")
    
    print("\n" + "="*60)
    print("TESTING COMPLETED")
    print("="*60)

def test_manual_video_addition():
    """Test adding a specific video to the database"""
    print("\n" + "="*60)
    print("TESTING MANUAL VIDEO ADDITION")
    print("="*60)
    
    video_finder = VideoSourceFinder()
    
    # Test with a popular video (Rick Roll - for testing purposes)
    test_video_id = "dQw4w9WgXcQ"
    
    print(f"Adding video {test_video_id} to database...")
    success = video_finder.add_video_to_database(test_video_id)
    
    if success:
        print(f"✅ Video {test_video_id} added successfully!")
        
        # Test searching in the added video
        test_snippet = "Never gonna give you up"
        print(f"\nSearching for '{test_snippet}' in the added video...")
        
        result = video_finder.find_video_source(test_snippet)
        if result:
            print(f"✅ Found in video {result['video_id']} at {result['timestamp_start']}")
        else:
            print("❌ Text snippet not found in the video")
    else:
        print(f"❌ Failed to add video {test_video_id}")

if __name__ == "__main__":
    # Run basic tests
    test_video_finder()
    
    # Run manual video addition test
    test_manual_video_addition()
