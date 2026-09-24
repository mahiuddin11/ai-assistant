from tool_sdk import BaseTool, ToolManifest, ToolResult
from tool_registry import ToolRegistry


class DummyEchoTool(BaseTool):
    @property
    def manifest(self) -> ToolManifest:
        return ToolManifest(
            name="echo",
            description="Echoes back whatever text is given (for testing the Tool SDK).",
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
        )

    def execute(self, **kwargs) -> ToolResult:
        text = kwargs.get("text", "")
        return ToolResult(success=True, output=f"Echo: {text}")


registry = ToolRegistry()
registry.register(DummyEchoTool())

print("Registered tools:", registry.list_manifests())

result = registry.get("echo").execute(text="Hello Tool SDK")
print("Execution result:", result)