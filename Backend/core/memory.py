import os
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Any
import ollama
from core.logger import get_logger
from core.config import BASE_DIR, MODEL_NAME

logger = get_logger(__name__)

MEMORY_FILE  = os.path.join(BASE_DIR, "long_term_memory.json")
SAVE_EVERY_N = 5   # Only write to disk every N new memories (performance)


class MemoryManager:
    """
    Long-term memory using vector embeddings via Ollama.
    Retrieves semantically similar memories for context injection.
    """

    def __init__(self):
        self.memories: List[Dict[str, Any]] = []
        self._dirty: int = 0   # count of unsaved additions
        self.load_memory()

    # ── Persistence ──────────────────────────────────────────
    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    self.memories = json.load(f)
                logger.info(f"Loaded {len(self.memories)} long-term memories")
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
                self.memories = []

    def save_memory(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memories, f, indent=2)
            self._dirty = 0
            logger.debug("Saved long-term memory")
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")

    def _maybe_save(self):
        """Save only after accumulating N new memories to reduce disk I/O."""
        self._dirty += 1
        if self._dirty >= SAVE_EVERY_N:
            self.save_memory()

    # ── Embeddings ───────────────────────────────────────────
    def _get_embedding(self, text: str) -> List[float]:
        try:
            response = ollama.embeddings(model=MODEL_NAME, prompt=text)
            return response.get("embedding", [])
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return []

    # ── Public API ───────────────────────────────────────────
    def add_memory(self, text: str, source: str = "user"):
        if not text:
            return

        # Deduplicate: skip if exact text already stored
        if any(m["text"] == text for m in self.memories):
            return

        vector = self._get_embedding(text)
        if not vector:
            return

        self.memories.append({
            "text":      text,
            "vector":    vector,
            "timestamp": datetime.now().isoformat(),
            "source":    source,
        })
        self._maybe_save()
        logger.info(f"Learned: {text[:60]}")

    def search_memory(self, query: str, limit: int = 3, threshold: float = 0.5) -> List[str]:
        if not self.memories:
            return []

        query_vec = self._get_embedding(query)
        if not query_vec:
            return []

        q = np.array(query_vec)
        norm_q = np.linalg.norm(q)
        if norm_q == 0:
            return []

        scored = []
        for mem in self.memories:
            v = np.array(mem["vector"])
            norm_v = np.linalg.norm(v)
            if norm_v == 0:
                continue
            sim = float(np.dot(q, v) / (norm_q * norm_v))
            if sim >= threshold:
                scored.append((sim, mem["text"]))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in scored[:limit]]

    def extract_and_store_fact(self, user_input: str):
        """Heuristically detect facts worth remembering."""
        triggers = [
            "i am", "my name is", "i like", "i love",
            "i hate", "i work", "remember that",
        ]
        if any(t in user_input.lower() for t in triggers):
            self.add_memory(user_input)

    def detect_and_store_correction(self, user_input: str, previous_response: str) -> bool:
        """
        Detect if user is correcting David and store the correction.
        
        Returns:
            True if a correction was detected and stored.
        """
        correction_triggers = [
            "no,", "no ", "that's wrong", "thats wrong", "that is wrong",
            "actually,", "actually ", "not correct", "incorrect",
            "you're wrong", "you are wrong", "wrong answer",
            "no david", "nahi", "galat", "galat hai",
            "the correct answer", "the right answer",
            "i meant", "i said", "what i meant",
        ]
        
        text_lower = user_input.lower().strip()
        
        is_correction = any(text_lower.startswith(t) or t in text_lower 
                           for t in correction_triggers)
        
        if is_correction:
            # Store correction with context
            correction_text = (
                f"CORRECTION: User said '{user_input}' "
                f"(correcting David's response: '{previous_response[:100]}')"
            )
            self.add_memory(correction_text, source="correction")
            logger.info(f"Learned correction: {user_input[:80]}")
            return True
        
        return False

    def search_memory(self, query: str, limit: int = 3, threshold: float = 0.5) -> List[str]:
        if not self.memories:
            return []

        query_vec = self._get_embedding(query)
        if not query_vec:
            return []

        q = np.array(query_vec)
        norm_q = np.linalg.norm(q)
        if norm_q == 0:
            return []

        corrections = []
        regular = []
        
        for mem in self.memories:
            v = np.array(mem["vector"])
            norm_v = np.linalg.norm(v)
            if norm_v == 0:
                continue
            sim = float(np.dot(q, v) / (norm_q * norm_v))
            if sim >= threshold:
                if mem.get("source") == "correction":
                    corrections.append((sim + 0.15, mem["text"]))  # Boost corrections
                else:
                    regular.append((sim, mem["text"]))

        # Prioritize corrections, then regular memories
        all_results = sorted(corrections + regular, key=lambda x: x[0], reverse=True)
        return [t for _, t in all_results[:limit]]

    def flush(self):
        """Force-save any pending dirty memories (call on shutdown)."""
        if self._dirty > 0:
            self.save_memory()
