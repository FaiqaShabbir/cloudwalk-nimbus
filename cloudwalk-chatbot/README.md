# CloudWalk Chatbot

A Retrieval-Augmented Generation (RAG) powered chatbot that explains CloudWalk's products, mission, and brand values. Built with Streamlit, LangChain, and OpenAI.

## Features

- **RAG Technology**: Uses retrieval-augmented generation to provide accurate, up-to-date information
- **Interactive Chat Interface**: Clean, user-friendly Streamlit interface
- **Comprehensive Knowledge Base**: Covers CloudWalk's products, mission, values, and technology
- **Quick Questions**: Pre-defined questions for easy access to common information
- **Real-time Responses**: Fast, contextual answers using OpenAI's language models

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd cloudwalk-chatbot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open your browser and navigate to the Streamlit app (usually `http://localhost:8501`)
2. Use the chat interface to ask questions about CloudWalk
3. Try the quick questions in the sidebar for common queries
4. The chatbot will provide detailed, contextual responses based on the knowledge base

## Sample Conversations

### Conversation 1: Company Overview

**User**: What is CloudWalk?

**Chatbot**: CloudWalk is a Brazilian financial technology (fintech) company founded in 2013 that specializes in providing innovative payment solutions and financial services. The company is headquartered in São Paulo, Brazil, and has become one of the leading fintech companies in Latin America.

CloudWalk's mission is to democratize financial services by making them more accessible, transparent, and efficient for businesses of all sizes. The company aims to transform the financial landscape by providing cutting-edge technology solutions that simplify payment processing and financial management.

Our flagship product, **InfinitePay**, is a comprehensive payment processing solution designed for businesses, offering low-cost processing, multiple payment methods, real-time processing, and advanced analytics.

### Conversation 2: Product Information

**User**: Tell me about InfinitePay and its features

**Chatbot**: InfinitePay is CloudWalk's flagship payment processing solution designed for businesses. Here are its key features:

**Core Features:**
- **Low-cost payment processing**: Competitive transaction fees to help businesses save money
- **Multiple payment methods**: Supports credit cards, debit cards, PIX, boleto, and more
- **Real-time processing**: Instant payment confirmation for better customer experience
- **Advanced analytics**: Detailed reporting and insights to help businesses understand their transactions
- **Easy integration**: Simple API and SDK for developers to integrate quickly
- **Security**: PCI DSS compliant with advanced fraud protection
- **Multi-channel support**: Works for online, mobile, and in-person payments

**Additional Benefits:**
- Comprehensive point-of-sale solution with inventory management
- Customer relationship management tools
- Financial reporting capabilities
- Integration with CloudWalk's broader ecosystem

InfinitePay is designed to make payment processing simple, secure, and cost-effective for businesses of all sizes.

### Conversation 3: Mission and Values

**User**: What are CloudWalk's core values and mission?

**Chatbot**: CloudWalk's mission is to **democratize financial services** by making them more accessible, transparent, and efficient for businesses of all sizes. We aim to transform the financial landscape by providing cutting-edge technology solutions that simplify payment processing and financial management.

**Our Core Values:**

1. **Innovation**: We continuously develop cutting-edge technology solutions to stay ahead of the curve
2. **Transparency**: We provide clear, honest communication and pricing with no hidden fees
3. **Accessibility**: We make financial services available to businesses of all sizes, from startups to enterprises
4. **Customer-Centric**: We put customer needs at the center of all our decisions
5. **Reliability**: We ensure secure, stable, and dependable services that businesses can count on
6. **Simplicity**: We make complex financial processes simple and intuitive

**Our Vision**: To become the leading financial technology platform in Latin America, empowering businesses to grow through innovative payment solutions and financial services.

These values drive everything we do, from product development to customer service, ensuring that we always put our customers first while maintaining the highest standards of innovation and reliability.

## Technical Architecture

### RAG Implementation
- **Vector Database**: ChromaDB for storing document embeddings
- **Embedding Model**: Sentence Transformers (all-MiniLM-L6-v2)
- **Language Model**: OpenAI GPT-3.5-turbo
- **Text Processing**: LangChain for document splitting and processing

### Components
- `config.py`: Configuration settings and API keys
- `knowledge_base_manager.py`: Manages the vector database and document retrieval
- `chatbot.py`: Core chatbot logic with RAG implementation
- `app.py`: Streamlit web interface
- `knowledge_base.md`: Comprehensive CloudWalk information

## Customization

### Adding New Information
1. Update `knowledge_base.md` with new information
2. Restart the application to reinitialize the knowledge base
3. The new information will be automatically indexed and available for queries

### Modifying Responses
1. Edit the system prompt in `chatbot.py`
2. Adjust the configuration in `config.py`
3. Restart the application to apply changes

## Requirements

- Python 3.8+
- OpenAI API key
- Internet connection for API calls

## License

This project is for educational and demonstration purposes. Please ensure you have the necessary permissions to use CloudWalk's information in your applications.

## Support

For questions about this chatbot implementation, please refer to the code documentation or create an issue in the repository.
