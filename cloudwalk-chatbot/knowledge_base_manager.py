import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import markdown
from config import Config

class KnowledgeBase:
    def __init__(self):
        self.config = Config()
        self.embedding_model = SentenceTransformer(self.config.EMBEDDING_MODEL)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=self.config.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(self.config.COLLECTION_NAME)
        except:
            self.collection = self.client.create_collection(
                name=self.config.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"}
            )
    
    def load_knowledge_from_file(self, file_path):
        """Load knowledge from a markdown file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Convert markdown to text
        html = markdown.markdown(content)
        
        # Split into chunks
        chunks = self.text_splitter.split_text(content)
        
        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={"source": file_path, "chunk_id": i}
            )
            documents.append(doc)
        
        return documents
    
    def add_documents_to_vectorstore(self, documents):
        """Add documents to the vector store"""
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(texts).tolist()
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    def search_similar_documents(self, query, n_results=None):
        """Search for similar documents"""
        if n_results is None:
            n_results = self.config.TOP_K_RESULTS
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query]).tolist()
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        return results
    
    def initialize_knowledge_base(self):
        """Initialize the knowledge base with CloudWalk information"""
        if self.collection.count() == 0:
            print("Initializing knowledge base...")
            documents = self.load_knowledge_from_file("knowledge_base.md")
            self.add_documents_to_vectorstore(documents)
            print(f"Added {len(documents)} documents to knowledge base")
        else:
            print(f"Knowledge base already contains {self.collection.count()} documents")
