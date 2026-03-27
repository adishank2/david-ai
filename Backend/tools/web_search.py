from duckduckgo_search import DDGS
from core.logger import get_logger
from ai.llm import ask_llm
import re

logger = get_logger(__name__)

class WebSearchTool:
    """Web search integration for real-time information."""
    
    def __init__(self):
        """Initialize web search tool."""
        self.ddgs = DDGS()
    
    def search(self, query: str, max_results: int = 5) -> list:
        """
        Search the web using DuckDuckGo.
        
        Args:
            query: Search query
            max_results: Maximum number of results
            
        Returns:
            list: Search results with title, snippet, and URL
        """
        try:
            logger.info(f"Searching web for: {query}")
            
            results = []
            for result in self.ddgs.text(query, max_results=max_results):
                results.append({
                    "title": result.get("title", ""),
                    "snippet": result.get("body", ""),
                    "url": result.get("href", "")
                })
            
            logger.debug(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return []
    
    def search_and_summarize(self, query: str) -> str:
        """
        Search the web and summarize results using LLM.
        
        Args:
            query: Search query
            
        Returns:
            str: Summarized answer with sources
        """
        try:
            results = self.search(query, max_results=3)
            
            if not results:
                return "I couldn't find any information about that."
            
            # Build context from search results
            context = f"User question: {query}\n\nSearch results:\n\n"
            
            for i, result in enumerate(results, 1):
                context += f"{i}. {result['title']}\n"
                context += f"   {result['snippet']}\n"
                context += f"   Source: {result['url']}\n\n"
            
            # Ask LLM to summarize
            prompt = f"""{context}

Based on the search results above, provide a concise and accurate answer to the user's question.
Include relevant details and cite sources when appropriate.
Keep the response conversational and helpful."""

            summary = ask_llm(prompt)
            
            return summary
            
        except Exception as e:
            logger.error(f"Search and summarize failed: {e}")
            return "I encountered an error while searching for that information."
    
    def is_search_query(self, text: str) -> bool:
        """
        Determine if user input is a search query.
        
        Args:
            text: User input
            
        Returns:
            bool: True if likely a search query
        """
        search_indicators = [
            r'\bwhat\s+is\b',
            r'\bwho\s+is\b',
            r'\bwhen\s+is\b',
            r'\bwhere\s+is\b',
            r'\bhow\s+to\b',
            r'\bwhy\s+is\b',
            r'\btell\s+me\s+about\b',
            r'\bsearch\s+for\b',
            r'\blook\s+up\b',
            r'\bfind\s+information\b',
            r'\bweather\b',
            r'\bnews\b',
            r'\bcurrent\b',
            r'\blatest\b',
        ]
        
        text_lower = text.lower()
        
        for pattern in search_indicators:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def extract_search_query(self, text: str) -> str:
        """
        Extract clean search query from user input.
        
        Args:
            text: User input
            
        Returns:
            str: Cleaned search query
        """
        # Remove common prefixes
        prefixes = [
            "search for ",
            "look up ",
            "find ",
            "tell me about ",
            "what is ",
            "who is ",
            "when is ",
            "where is ",
            "how to ",
            "why is ",
        ]
        
        query = text.lower()
        
        for prefix in prefixes:
            if query.startswith(prefix):
                query = query[len(prefix):]
                break
        
        return query.strip()
