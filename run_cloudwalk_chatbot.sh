#!/bin/bash
# CloudWalk Chatbot Setup Script for Linux/Mac

# Activate CloudWalk Chatbot virtual environment
source cloudwalk-chatbot/venv/bin/activate

# Navigate to CloudWalk Chatbot directory
cd cloudwalk-chatbot

# Run the Streamlit application
streamlit run app.py

# Instructions:
# 1. Make sure you have set up your .env file with OPENAI_API_KEY
# 2. The app will open at http://localhost:8501
# 3. To stop the app, press Ctrl+C
