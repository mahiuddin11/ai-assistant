from tool_sdk import BaseTool


class ToolRegistry:
    """
    রানটাইমে উপলব্ধ সব টুল ট্র্যাক রাখে। Orchestrator/Agent এখান থেকে
    নাম দিয়ে টুল খুঁজে execute করতে পারবে।
    """

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:
        name = tool.manifest.name
        self._tools[name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_manifests(self) -> list[dict]:
        return [tool.manifest.model_dump() for tool in self._tools.values()]