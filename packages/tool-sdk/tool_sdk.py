"""
Tool SDK v1 — manifest-based tool interface।
প্রতিটা টুল (Web Search, ভবিষ্যতে File Ops, ইত্যাদি) এই abstract class থেকে inherit করবে,
যাতে Orchestrator/Agent একই ইন্টারফেসে সব টুল কল করতে পারে।
"""

from abc import ABC, abstractmethod
from pydantic import BaseModel


class ToolManifest(BaseModel):
    """প্রতিটা টুলের self-description — নাম, বিবরণ, ইনপুট স্কিমা।"""
    name: str
    description: str
    input_schema: dict  # JSON-schema স্টাইল, LLM function-calling-এর সাথে সামঞ্জস্যপূর্ণ


class ToolResult(BaseModel):
    """প্রতিটা টুল কলের ফলাফল — সফল/ব্যর্থ দুটোই এক ফরম্যাটে।"""
    success: bool
    output: str
    error: str | None = None


class BaseTool(ABC):
    """
    সব টুলের বেস ক্লাস। নতুন টুল বানাতে এই ক্লাস inherit করে
    manifest প্রপার্টি ও execute() মেথড implement করতে হবে।
    """

    @property
    @abstractmethod
    def manifest(self) -> ToolManifest:
        """এই টুলের self-description রিটার্ন করে।"""
        ...

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        টুলটা চালায়। এই মেথড কখনো raw exception raise করবে না —
        ব্যর্থ হলেও ToolResult(success=False, error=...) রিটার্ন করবে,
        যাতে caller-কে সবসময় একটা predictable structure দেওয়া যায়।
        """
        ...