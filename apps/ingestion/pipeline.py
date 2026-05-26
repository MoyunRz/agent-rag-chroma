"""文档入库流水线：解析 → 分块 → 向量化 → Chroma → DB."""
import hashlib
import logging
import mimetypes

from django.conf import settings
from django.utils import timezone

from apps.ingestion.models import ChunkRecord, Document, DocumentVersion
from apps.ingestion.parsers import get_parser
from apps.ingestion.chunkers import SemanticChunker
from integrations.chroma_store import ensure_collection
from integrations.embedding_client import EmbeddingClient

logger = logging.getLogger(__name__)


def compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def ingest_document(kb_id: int, file_path: str, tenant_id: str = 'demo') -> Document:
    """
    入库单个文档：
    1. 检测文件类型 → 解析
    2. 文本清洗 + 分块
    3. 向量化 (MiniMax Embedding)
    4. 写入 Chroma + Django DB
    """
    # ── 0. 检测 mime type ─────────────────────────
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        ext = file_path.rsplit('.', 1)[-1].lower()
        mime_map = {
            'txt': 'text/plain', 'md': 'text/markdown',
            'pdf': 'application/pdf', 'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'doc': 'application/msword',
        }
        mime_type = mime_map.get(ext, 'text/plain')

    # ── 1. 解析 ──────────────────────────────────
    parser = get_parser(mime_type)
    parsed = parser.parse(file_path)
    content_hash = compute_hash(parsed.raw_text)

    # ── 2. 去重检查 ──────────────────────────────
    from apps.knowledge.models import KnowledgeBase
    kb = KnowledgeBase.objects.get(id=kb_id)
    existing = Document.objects.filter(kb=kb, title=parsed.title).first()
    if existing:
        last_ver = existing.versions.filter(content_hash=content_hash, status=DocumentVersion.Status.DONE).first()
        if last_ver:
            logger.info('文档 %s 内容未变化，跳过入库', parsed.title)
            return existing

    doc = Document.objects.create(
        kb=kb, title=parsed.title, source_uri=file_path,
        mime_type=mime_type, file_path=file_path,
    )
    version_number = (existing.versions.count() if existing else 0) + 1
    version = DocumentVersion.objects.create(
        document=doc, version_number=version_number,
        content_hash=content_hash, status=DocumentVersion.Status.PROCESSING,
    )

    try:
        # ── 3. 分块 ──────────────────────────────
        chunker = SemanticChunker()
        all_chunks = []
        for section in parsed.sections:
            heading = section.heading or parsed.title
            chunks = chunker.chunk(section.text, page=section.page, heading_path=heading)
            # Assign global chunk_index
            for c in chunks:
                c.chunk_index = len(all_chunks)
            all_chunks.extend(chunks)

        logger.info('文档 %s → %d 个 chunk', parsed.title, len(all_chunks))

        # ── 4. 本地 Embedding ─────────────────
        embed = EmbeddingClient()
        texts = [c.text for c in all_chunks]
        embeddings = embed.embed(texts)

        # ── 5. Chroma 写入 ───────────────────────
        collection = ensure_collection(tenant_id=tenant_id, kb_id=str(kb_id))
        chroma_ids = []
        metas = []
        for c in all_chunks:
            cid = f'{tenant_id}:{kb_id}:{doc.id}:{version.id}:{c.chunk_index}'
            chroma_ids.append(cid)
            metas.append({
                'tenant_id': tenant_id,
                'kb_id': str(kb_id),
                'doc_id': str(doc.id),
                'version_id': str(version.id),
                'source_uri': file_path,
                'title': parsed.title,
                'mime_type': mime_type,
                'page': c.page if c.page else 0,
                'heading_path': c.heading_path,
                'chunk_index': c.chunk_index,
                'content_hash': compute_hash(c.text),
            })

        collection.upsert(
            ids=chroma_ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metas,
        )

        # ── 6. DB 写入 ───────────────────────────
        for c, cid in zip(all_chunks, chroma_ids):
            ChunkRecord.objects.create(
                version=version,
                chunk_index=c.chunk_index,
                text=c.text,
                page=c.page,
                heading_path=c.heading_path,
                content_hash=compute_hash(c.text),
                chroma_id=cid,
            )

        version.status = DocumentVersion.Status.DONE
        version.chunks_count = len(all_chunks)
        version.save()

        logger.info('文档 %s 入库完成: %d chunks', parsed.title, len(all_chunks))

    except Exception as e:
        version.status = DocumentVersion.Status.FAILED
        version.error_message = str(e)
        version.save()
        logger.exception('文档 %s 入库失败', parsed.title)
        raise

    return doc
