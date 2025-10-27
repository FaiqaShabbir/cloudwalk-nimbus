# Test script for CloudWalk Chatbot

import os
from chatbot import CloudWalkRAGChatbot

def test_chatbot():
    """Test the CloudWalk chatbot with sample questions"""
    
    # Initialize chatbot
    print("Initializing CloudWalk Chatbot...")
    chatbot = CloudWalkRAGChatbot()
    
    # Test questions
    test_questions = [
        "What is CloudWalk?",
        "Tell me about InfinitePay",
        "What are CloudWalk's core values?",
        "What is CloudWalk's mission?",
        "How does CloudWalk's technology work?",
        "What payment methods does InfinitePay support?"
    ]
    
    print("\n" + "="*50)
    print("TESTING CLOUDWALK CHATBOT")
    print("="*50)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nTest {i}: {question}")
        print("-" * 40)
        
        try:
            response = chatbot.chat(question)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {str(e)}")
        
        print("-" * 40)
    
    print("\n" + "="*50)
    print("TESTING COMPLETED")
    print("="*50)

if __name__ == "__main__":
    test_chatbot()
