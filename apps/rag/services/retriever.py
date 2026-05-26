"""RAG 检索器：query → embedding → Chroma 搜索."""
from dataclasses import dataclass

from django.conf import settings

from integrations.chroma_store import ensure_collection
from integrations.embedding_client import EmbeddingClient


@dataclass
class RetrievedChunk:
    text: str
    doc_id: str
    title: str
    page: int
    heading_path: str
    score: float
    chroma_id: str


def retrieve(kb_id: int, query: str, tenant_id: str = 'demo', top_k: int | None = None) -> list[RetrievedChunk]:
    """检索知识库中与 query 最相关的 chunk."""
    if top_k is None:
        top_k = settings.RAG_CONFIG['default_top_k']

    # 1. query embedding (本地模型)
    embed = EmbeddingClient()
    embeddings = embed.embed([query])
    query_vector = embeddings[0]

    # 2. Chroma 检索
    collection = ensure_collection(tenant_id=tenant_id, kb_id=str(kb_id))
    results = collection.query(
        query_embeddings=[query_vector],
        n_results=top_k,
        include=['documents', 'metadatas', 'distances'],
    )

    # 3. 组装结果
    chunks = []
    if results['ids'] and results['ids'][0]:
        for i, cid in enumerate(results['ids'][0]):
            meta = results['metadatas'][0][i] if results['metadatas'] else {}
            text = results['documents'][0][i] if results['documents'] else ''
            distance = results['distances'][0][i] if results['distances'] else 0
            # Chroma returns cosine distance, convert to similarity score
            score = 1 - distance if distance else 0

            chunks.append(RetrievedChunk(
                text=text,
                doc_id=meta.get('doc_id', ''),
                title=meta.get('title', ''),
                page=meta.get('page', 0),
                heading_path=meta.get('heading_path', ''),
                score=round(score, 4),
                chroma_id=cid,
            ))

    return chunks
