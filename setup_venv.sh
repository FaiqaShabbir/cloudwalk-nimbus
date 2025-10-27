#!/bin/bash
# CloudWalk Chatbot Virtual Environment Setup for Linux/Mac

# Create virtual environment for CloudWalk Chatbot
python3 -m venv cloudwalk-chatbot/venv

# Activate virtual environment for CloudWalk Chatbot
source cloudwalk-chatbot/venv/bin/activate

# Install dependencies for CloudWalk Chatbot
cd cloudwalk-chatbot
pip install -r requirements.txt

# Go back to root directory
cd ..

# Create virtual environment for Video Source Finder
python3 -m venv video-source-finder/venv

# Activate virtual environment for Video Source Finder
source video-source-finder/venv/bin/activate

# Install dependencies for Video Source Finder
cd video-source-finder
pip install -r video_finder_requirements.txt

# Go back to root directory
cd ..

echo "Both virtual environments created successfully!"
echo "To activate CloudWalk Chatbot: source cloudwalk-chatbot/venv/bin/activate"
echo "To activate Video Source Finder: source video-source-finder/venv/bin/activate"