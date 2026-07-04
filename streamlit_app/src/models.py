from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Source:
    title: str
    url: str = ""
    source_type: str = "government"


@dataclass
class RAGResult:
    context: str
    sources: list[Source] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class ChatMessage:
    role: str
    content: str


@dataclass
class CopilotResponse:
    answer: str
    sources: list[Source] = field(default_factory=list)
    confidence: float = 0.0
    source_texts: list[str] = field(default_factory=list)
