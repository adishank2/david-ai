import os
import threading
import time
from typing import List
from core.rag_manager import get_rag
from core.logger import get_logger

logger = get_logger(__name__)

# Supported file extensions
SUPPORTED_EXTENSIONS = {'.txt', '.md', '.pdf', '.docx', '.csv'}

def extract_text_from_file(file_path: str) -> str:
    """Helper to extract text from various file formats."""
    _, ext = os.path.splitext(file_path.lower())
    
    try:
        if ext in {'.txt', '.md', '.csv'}:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        
        elif ext == '.pdf':
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
            return text
            
        elif ext == '.docx':
            import docx
            doc = docx.Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
            
        return ""
    except Exception as e:
        logger.error(f"Error extracting text from {file_path}: {e}")
        return ""

class DavidIndexer(threading.Thread):
    def __init__(self, target_folders: List[str] = None):
        super().__init__(daemon=True)
        self.target_folders = target_folders or self._get_default_folders()
        self.running = False
        self.is_indexing = False
        self.indexed_files_count = 0
        self.last_indexed_time = 0

    def _get_default_folders(self):
        # Default to user Documents folder, desktop, and THE PROJECT ROOT
        from core.config import ROOT_DIR
        user_profile = os.environ.get("USERPROFILE", "")
        folders = [
            ROOT_DIR,
            os.path.join(user_profile, "Documents"),
            os.path.join(user_profile, "Desktop")
        ]
        # Filter existing folders
        unique_folders = list(set([f for f in folders if os.path.isdir(f)]))
        return unique_folders

    def start_indexer(self):
        if not self.running:
            self.running = True
            self.start()
            logger.info(f"David-Indexer started. Target folders: {self.target_folders}")

    def run(self):
        # Allow initial system startup
        time.sleep(10)
        
        while self.running:
            try:
                # Perform an incremental scan every hour or on boot
                if time.time() - self.last_indexed_time > 3600:
                    self.perform_scan()
                    self.last_indexed_time = time.time()
            except Exception as e:
                logger.error(f"Indexer loop error: {e}")
            
            time.sleep(300) # Check every 5 minutes if it's time to scan

    def perform_scan(self):
        """Walk through folders and index new/changed files."""
        self.is_indexing = True
        logger.info("David is scanning local knowledge...")
        rag = get_rag()
        
        total_found = 0
        for folder in self.target_folders:
            for root, _, files in os.walk(folder):
                if not self.running: break
                
                # Exclude hidden folders/system folders
                if any(part.startswith('.') for part in root.split(os.sep)):
                    continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file.lower())
                    
                    if ext in SUPPORTED_EXTENSIONS:
                        # Extract and add to RAG database
                        text = extract_text_from_file(file_path)
                        if text and len(text.strip()) > 50:
                            # Use file path as ID for de-duplication
                            metadata = {
                                "source": file_path,
                                "filename": file,
                                "indexed_at": time.time()
                            }
                            # Simple hash for doc_id
                            doc_id = str(abs(hash(file_path)))
                            success = rag.add_document(text, metadata, doc_id)
                            if success:
                                total_found += 1
                                if total_found % 10 == 0:
                                    logger.info(f"Indexed {total_found} local files...")
                                    
        self.indexed_files_count = total_found
        self.is_indexing = False
        logger.info(f"Scan complete. Indexed {total_found} new/updated documents.")

# Singleton indexer
_indexer_instance = None

def start_indexing_agent():
    global _indexer_instance
    if _indexer_instance is None:
        _indexer_instance = DavidIndexer()
        _indexer_instance.start_indexer()
    return _indexer_instance

def get_indexer_status():
    if _indexer_instance:
        return {
            "is_indexing": _indexer_instance.is_indexing,
            "count": _indexer_instance.indexed_files_count
        }
    return None
