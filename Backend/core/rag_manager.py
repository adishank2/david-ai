import os
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter
from core.logger import get_logger

logger = get_logger(__name__)

# Configurable paths
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "rag_db")
os.makedirs(DB_DIR, exist_ok=True)

class RAGManager:
    def __init__(self, collection_name="david_knowledge"):
        self.client = chromadb.PersistentClient(path=DB_DIR)
        
        # Using Chroma's default embedding function (sentence-transformers/all-MiniLM-L6-v2)
        # This is ~80MB and runs locally on CPU/GPU
        self.embedding_func = embedding_functions.DefaultEmbeddingFunction()
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_func,
            metadata={"description": "David AI Personal Knowledge Base"}
        )
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(f"RAG Manager initialized. Collection: {collection_name}")

    def add_document(self, content: str, metadata: dict, doc_id: str):
        """Chunk and add a document to the vector store."""
        try:
            chunks = self.text_splitter.split_text(content)
            ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [metadata for _ in range(len(chunks))]
            
            self.collection.add(
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )
            logger.debug(f"Added document {doc_id} to RAG in {len(chunks)} chunks.")
            return True
        except Exception as e:
            logger.error(f"Failed to add document to RAG: {e}")
            return False

    def query(self, query_text: str, n_results=5):
        """Search for relevant chunks."""
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Combine documents into a context block
            context = ""
            if results and results['documents']:
                for doc_list in results['documents']:
                    for doc in doc_list:
                        context += f"{doc}\n---\n"
            
            return context.strip()
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return ""

    def get_stats(self):
        """Return basic collection stats."""
        try:
            return {"count": self.collection.count()}
        except Exception:
            return {"count": 0}

    def clear_database(self):
        """Clear all knowledge from the database."""
        try:
            self.client.delete_collection(self.collection.name)
            self.collection = self.client.get_or_create_collection(name=self.collection.name)
            logger.info("RAG Knowledge base cleared.")
            return True
        except Exception as e:
            logger.error(f"Failed to clear RAG database: {e}")
            return False

# Singleton instance
_rag_instance = None

def get_rag():
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = RAGManager()
    return _rag_instance
