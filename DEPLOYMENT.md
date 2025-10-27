# Deployment Instructions

## 🌐 Live URLs

**Note**: These are localhost URLs as the applications run on your machine. For production deployment, you would use platforms like Heroku, Streamlit Cloud, or AWS.

### Development URLs

- **CloudWalk Chatbot**: `http://localhost:8501`
- **Video Source Finder**: `http://localhost:8501` (or different port if CloudWalk is running)

### Production Deployment Options

#### Option 1: Streamlit Cloud (Recommended for Quick Deployment)
1. Push code to GitHub
2. Go to https://share.streamlit.io/
3. Connect your GitHub repository
4. Deploy both apps separately
5. Configure environment variables in Streamlit Cloud settings

#### Option 2: Heroku
```bash
# Add Procfile for each app
# cloudwalk-chatbot/Procfile:
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0

# Deploy
heroku create cloudwalk-chatbot-app
git push heroku main
```

#### Option 3: Local Network Access
To access from other devices on your network:
```bash
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```
Then access via: `http://YOUR_IP_ADDRESS:8501`

## Architecture

Both applications use a client-server architecture:
- **Frontend**: Streamlit web interface
- **Backend**: Python with OpenAI API, ChromaDB, and other APIs
- **Database**: ChromaDB (persistent local storage)
- **APIs**: OpenAI, Serper, Tavily, SearchAPI

## Security Considerations for Production

1. **API Keys**: Use environment variables (never hardcode)
2. **Database**: Secure ChromaDB access if deployed
3. **Rate Limiting**: Implement rate limiting for API calls
4. **Error Handling**: Comprehensive error messages
5. **Logging**: Secure logging without exposing sensitive data

## Current Deployment Status

- **Environment**: Local development
- **Database**: Local ChromaDB
- **APIs**: Production APIs (OpenAI, Serper, Tavily)
- **Access**: Localhost only

## Deployment Checklist

- [ ] Add API keys to deployment platform
- [ ] Configure database persistence
- [ ] Set up proper error logging
- [ ] Add rate limiting
- [ ] Test API connections
- [ ] Verify database security
- [ ] Set up monitoring
- [ ] Configure CORS if needed

