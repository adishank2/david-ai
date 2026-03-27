"""Browser automation plugin for David AI Assistant."""

from plugins.base import BasePlugin
from typing import Dict, List
import webbrowser
from core.logger import get_logger

logger = get_logger(__name__)

class BrowserPlugin(BasePlugin):
    """Control browser and perform web searches."""
    
    def get_intents(self) -> List[str]:
        return ["open_website", "search_google", "search_youtube", "close_browser"]
    
    def get_description(self) -> str:
        return "Browser automation: open websites, search Google/YouTube"
    
    def get_prompt_examples(self) -> str:
        return """open_website:
{
  "intent": "open_website",
  "url": "https://example.com"
}

search_google:
{
  "intent": "search_google",
  "query": "Python tutorials"
}

search_youtube:
{
  "intent": "search_youtube",
  "query": "machine learning basics"
}

close_browser:
{
  "intent": "close_browser"
}"""
    
    def execute(self, intent: Dict) -> str:
        """Execute browser operation."""
        intent_type = intent.get("intent")
        
        try:
            if intent_type == "open_website":
                url = intent.get("url", "")
                if not url:
                    return "Please provide a URL."
                
                # Add https:// if not present
                if not url.startswith("http"):
                    url = "https://" + url
                
                webbrowser.open(url)
                logger.info(f"Opened website: {url}")
                # Extract domain for cleaner response
                domain = url.replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
                return f"Opening {domain}"
            
            elif intent_type == "search_google":
                query = intent.get("query", "")
                if not query:
                    return "Please provide a search query."
                
                search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                logger.info(f"Google search: {query}")
                return f"Searching Google for {query}"
            
            elif intent_type == "search_youtube":
                query = intent.get("query", "")
                if not query:
                    return "Please provide a search query."
                
                search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
                webbrowser.open(search_url)
                logger.info(f"YouTube search: {query}")
                return f"Searching YouTube for {query}"
            
            elif intent_type == "close_browser":
                # This requires process control
                import psutil
                browser_processes = ["chrome.exe", "firefox.exe", "msedge.exe"]
                
                killed = False
                for proc in psutil.process_iter(['name']):
                    try:
                        if proc.info['name'].lower() in browser_processes:
                            proc.kill()
                            killed = True
                            logger.info(f"Closed browser: {proc.info['name']}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                if killed:
                    return "Closed browser windows."
                else:
                    return "No browser windows found."
            
            else:
                return "Unknown browser command."
                
        except Exception as e:
            logger.error(f"Browser plugin error: {e}")
            return "Sorry, I couldn't perform the browser operation."
