import requests
import time
from core.config import OLLAMA_URL, MODEL_NAME
from core.logger import get_logger
from core.cache import get_cache

logger = get_logger(__name__)


def check_ollama_connection() -> bool:
    """Check if Ollama server is running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def ask_llm(prompt: str, system: str = "", max_retries: int = 2, use_cache: bool = True, temperature: float = 0.7, num_predict: int = 250, use_rag: bool = True) -> str:
    """
    Query the Ollama LLM with optional RAG context.

    Args:
        prompt:      The user prompt / request text.
        system:      Optional system prompt. If empty, no system role is used.
        max_retries: Number of retry attempts on transient failures.
        use_cache:   Whether to cache responses.
        use_rag:     Whether to use local file knowledge.

    Returns:
        LLM response string.
    """
    # ── RAG Integration ──
    if use_rag:
        try:
            from core.rag_manager import get_rag
            rag = get_rag()
            
            # Simple heuristic: only query RAG for longer queries that don't look like internal system cmds
            if len(prompt) > 8 and not prompt.startswith("{"):
                context = rag.query(prompt)
                if context:
                    logger.debug("Local context found in RAG database. Appending to prompt.")
                    # Provide context to the model in a way it understands it is from local files
                    prompt_with_context = (
                        "Below is some relevant information found in your local system files that can help answer the query.\n"
                        "### LOCAL CONTEXT:\n"
                        f"{context}\n\n"
                        f"### USER QUERY:\n{prompt}\n\n"
                        "Instruction: Use the provided LOCAL CONTEXT to answer the user query accurately. If the context doesn't contain the answer, reply normally."
                    )
                    prompt = prompt_with_context
        except Exception as e:
            logger.error(f"RAG lookup failed: {e}")

    cache_key = (system + "|||" + prompt) if system else prompt
    if use_cache:
        cache = get_cache()
        cached = cache.get(cache_key)
        if cached:
            logger.debug("Using cached LLM response")
            return cached

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": num_predict,
            "num_ctx": 4096,
            "temperature": temperature
        }
    }
    
    # Add system prompt if provided
    if system:
        payload["system"] = system

    for attempt in range(max_retries + 1):
        try:
            logger.debug(f"LLM request attempt {attempt + 1}/{max_retries + 1}")
            r = requests.post(OLLAMA_URL, json=payload, timeout=30)
            r.raise_for_status()

            data = r.json()
            response = data.get("response", "").strip()

            if not response:
                logger.warning("LLM returned empty response")
                return "I'm not sure how to respond to that."

            # Strip accidental markdown code fences from JSON responses
            if "```" in response:
                import re
                match = re.search(r"```(?:\w+)?\n?(.*?)```", response, re.DOTALL)
                if match:
                    response = match.group(1).strip()

            if use_cache:
                cache.set(cache_key, response)

            return response

        except requests.exceptions.Timeout:
            logger.error(f"LLM timeout (attempt {attempt + 1})")
            if attempt < max_retries:
                time.sleep(1)
                continue
            raise Exception("LLM server is not responding. Is Ollama running?")

        except requests.exceptions.ConnectionError:
            logger.error(f"Cannot connect to LLM (attempt {attempt + 1})")
            if attempt < max_retries:
                time.sleep(1)
                continue
            raise Exception("Cannot connect to Ollama. Run: ollama serve")

        except requests.exceptions.HTTPError as e:
            logger.error(f"LLM HTTP error: {e}")
            raise Exception(f"LLM server error: {e}")

        except Exception as e:
            logger.error(f"Unexpected LLM error: {e}")
            if attempt < max_retries:
                time.sleep(1)
                continue
            raise Exception(f"LLM error: {e}")

    raise Exception("Failed to get LLM response after all retries")
