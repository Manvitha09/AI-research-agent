import os
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY not set in .env file")
        _client = TavilyClient(api_key=api_key)
    return _client


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web for a query and return a list of results.
    Each result has: title, url, content (snippet).
    """
    client = get_client()
    # In tools.py, update search_web()
    response = client.search(
    query=query,
    search_depth="advanced",
    max_results=5,
    include_domains=[
        "github.com", "stackoverflow.com", "dev.to",
        "docs.python.org", "developer.mozilla.org",
        "news.ycombinator.com", "medium.com"
    ]
)
    results = []
    for r in response.get("results", []):
        results.append({
            "title": r.get("title", ""),
            "url": r.get("url", ""),
            "content": r.get("content", ""),
        })
    return results