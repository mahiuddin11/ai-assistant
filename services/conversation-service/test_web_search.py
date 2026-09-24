from web_search_tool import WebSearchTool

tool = WebSearchTool()
print("Manifest:", tool.manifest.model_dump())

result = tool.execute(query="latest news about AI agents")
print("Success:", result.success)
print("Output:", result.output[:500])