#!/bin/bash
# Video Source Finder Setup Script for Linux/Mac

# Activate Video Source Finder virtual environment
source video-source-finder/venv/bin/activate

# Navigate to Video Source Finder directory
cd video-source-finder

# Run the Streamlit application
streamlit run video_finder_app.py

# Instructions:
# 1. Make sure you have set up your .env file with API keys
# 2. The app will open at http://localhost:8501
# 3. To stop the app, press Ctrl+C
