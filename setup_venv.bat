# CloudWalk Chatbot Virtual Environment Setup

# Create virtual environment for CloudWalk Chatbot
python -m venv cloudwalk-chatbot/venv

# Activate virtual environment (Windows)
cloudwalk-chatbot\venv\Scripts\activate

# Install dependencies for CloudWalk Chatbot
cd cloudwalk-chatbot
pip install -r requirements.txt

# Go back to root directory
cd ..

# Create virtual environment for Video Source Finder
python -m venv video-source-finder/venv

# Activate virtual environment for Video Source Finder (Windows)
video-source-finder\venv\Scripts\activate

# Install dependencies for Video Source Finder
cd video-source-finder
pip install -r video_finder_requirements.txt

# Go back to root directory
cd ..

echo "Both virtual environments created successfully!"
echo "To activate CloudWalk Chatbot: cloudwalk-chatbot\venv\Scripts\activate"
echo "To activate Video Source Finder: video-source-finder\venv\Scripts\activate"