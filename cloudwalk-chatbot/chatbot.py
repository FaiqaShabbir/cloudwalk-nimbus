import os
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from knowledge_base_manager import KnowledgeBase
from config import Config

class CloudWalkRAGChatbot:
    def __init__(self):
        self.config = Config()
        self.knowledge_base = KnowledgeBase()
        self.client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        
        # Initialize the knowledge base
        self.knowledge_base.initialize_knowledge_base()
        
        # System prompt for the chatbot
        self.system_prompt = """You are a helpful assistant for CloudWalk, a Brazilian fintech company. 
        Your role is to provide accurate information about CloudWalk's products, services, mission, and values.
        
        Guidelines:
        - Always be helpful, friendly, and professional
        - Use the provided context to answer questions accurately
        - If you don't know something, say so rather than guessing
        - Focus on CloudWalk's products like InfinitePay, their mission, and values
        - Provide specific details when available
        - Use markdown formatting when appropriate for better readability
        """
    
    def retrieve_relevant_context(self, query):
        """Retrieve relevant context from the knowledge base"""
        results = self.knowledge_base.search_similar_documents(query)
        
        if not results['documents'] or not results['documents'][0]:
            return ""
        
        # Combine the retrieved documents
        context = "\n\n".join(results['documents'][0])
        return context
    
    def generate_response(self, user_query, context):
        """Generate a response using OpenAI's API"""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Context: {context}\n\nUser Question: {user_query}"}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.CHAT_MODEL,
                messages=messages,
                max_tokens=self.config.MAX_TOKENS,
                temperature=self.config.TEMPERATURE
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}"
    
    def chat(self, user_query):
        """Main chat function that combines retrieval and generation"""
        # Retrieve relevant context
        context = self.retrieve_relevant_context(user_query)
        
        # Generate response
        response = self.generate_response(user_query, context)
        
        return response
    
    def get_welcome_message(self):
        """Get a welcome message for the chatbot"""
        return """👋 Welcome to the CloudWalk Assistant!

I'm here to help you learn about CloudWalk, our innovative fintech solutions, and how we're transforming the financial landscape in Brazil and Latin America.

You can ask me about:
- **What CloudWalk is** and our company overview
- **Our products** like InfinitePay and CloudWalk POS
- **Our mission** and core values
- **Our technology** and security features
- **How to get started** with our services

What would you like to know about CloudWalk?"""
