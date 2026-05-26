"""答案生成器：LLM 调用 + 引用整理 + trace."""
import uuid
from dataclasses import dataclass, field
from typing import Any

from integrations.minimax_client import MiniMaxClient

from .prompt_builder import build_messages
from .retriever import RetrievedChunk


@dataclass
class RAGResponse:
    answer: str
    citations: list[dict]
    trace_id: str
    chunks_used: list[RetrievedChunk] = field(repr=False)


def generate(question: str, chunks: list[RetrievedChunk]) -> RAGResponse:
    """基于检索到的 chunks 生成回答."""
    trace_id = uuid.uuid4().hex[:12]
    messages = build_messages(question, chunks)

    mini = MiniMaxClient()
    answer = mini.chat(messages)

    citations = _extract_citations(chunks)

    return RAGResponse(
        answer=answer,
        citations=citations,
        trace_id=trace_id,
        chunks_used=chunks,
    )


def _extract_citations(chunks: list[RetrievedChunk]) -> list[dict[str, Any]]:
    """从检索结果提取引用列表."""
    return [
        {
            'index': i + 1,
            'doc_id': c.doc_id,
            'title': c.title,
            'page': c.page,
            'heading': c.heading_path,
            'text_snippet': c.text[:200],
            'score': c.score,
        }
        for i, c in enumerate(chunks)
    ]
