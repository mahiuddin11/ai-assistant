import sys
import os
import requests
import structlog
from tavily import TavilyClient

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "config-loader"))
from config_loader import get_secret  # noqa: E402

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "packages", "tool-sdk"))
from tool_sdk import BaseTool, ToolManifest, ToolResult  # noqa: E402

logger = structlog.get_logger()

TAVILY_API_KEY = get_secret("TAVILY_API_KEY", vault_path="conversation-service", default=None)
SERPER_API_KEY = get_secret("SERPER_API_KEY", vault_path="conversation-service", default=None)


def _search_tavily(query: str) -> str | None:
    """Tavily দিয়ে সার্চ করে। ব্যর্থ হলে None রিটার্ন করে (exception raise করে না)।"""
    if not TAVILY_API_KEY:
        return None
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        response = client.search(query=query, max_results=3)
        results = response.get("results", [])
        if not results:
            return None
        return "\n\n".join(
            f"- {r['title']}: {r['content'][:200]}... (source: {r['url']})"
            for r in results
        )
    except Exception as e:
        logger.warning("tavily_search_failed", query=query, error=str(e))
        return None


def _search_serper(query: str) -> str | None:
    """Serper.dev দিয়ে সার্চ করে (fallback)। ব্যর্থ হলে None রিটার্ন করে।"""
    if not SERPER_API_KEY:
        return None
    try:
        response = requests.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
            json={"q": query, "num": 3},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        results = data.get("organic", [])
        if not results:
            return None
        return "\n\n".join(
            f"- {r.get('title', '')}: {r.get('snippet', '')[:200]}... (source: {r.get('link', '')})"
            for r in results
        )
    except Exception as e:
        logger.warning("serper_search_failed", query=query, error=str(e))
        return None


class WebSearchTool(BaseTool):
    @property
    def manifest(self) -> ToolManifest:
        return ToolManifest(
            name="web_search",
            description="Searches the web for current information and returns a summary of top results.",
            input_schema={
                "type": "object",
                "properties": {"query": {"type": "string", "description": "The search query"}},
                "required": ["query"],
            },
        )

    def execute(self, **kwargs) -> ToolResult:
        query = kwargs.get("query", "").strip()

        if not query:
            return ToolResult(success=False, output="", error="No search query provided")

        # প্রথমে Tavily ট্রাই করা
        result = _search_tavily(query)
        if result is not None:
            logger.info("web_search_success", provider="tavily", query=query)
            return ToolResult(success=True, output=result)

        logger.warning("tavily_failed_falling_back_to_serper", query=query)

        # তারপর Serper.dev fallback
        result = _search_serper(query)
        if result is not None:
            logger.info("web_search_success", provider="serper", query=query)
            return ToolResult(success=True, output=result)

        # দুটোই ব্যর্থ হলে
        logger.error("all_search_providers_failed", query=query)
        return ToolResult(
            success=False,
            output="",
            error="Search service is temporarily unavailable. Please try again shortly.",
        )