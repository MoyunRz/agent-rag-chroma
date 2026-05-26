from django.conf import settings

from .base import BaseChunker, Chunk


class SemanticChunker(BaseChunker):
    """按段落切分，保证每段不超过 chunk_size 字符."""

    def __init__(self):
        cfg = settings.RAG_CONFIG
        self.chunk_size = cfg['chunk_size']
        self.chunk_overlap = cfg['chunk_overlap']

    def chunk(self, text: str, page: int | None = None, heading_path: str = '') -> list[Chunk]:
        paragraphs = text.split('\n')
        chunks = []
        buf = ''
        idx = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                buf += '\n'
                continue

            if len(buf) + len(para) > self.chunk_size and buf.strip():
                chunks.append(Chunk(
                    text=buf.strip(),
                    page=page,
                    heading_path=heading_path,
                    chunk_index=idx,
                ))
                idx += 1
                # overlap: retain last N chars
                overlap_text = buf[-self.chunk_overlap:] if self.chunk_overlap > 0 else ''
                buf = overlap_text + para + '\n'
            else:
                buf += para + '\n'

        if buf.strip():
            chunks.append(Chunk(
                text=buf.strip(),
                page=page,
                heading_path=heading_path,
                chunk_index=idx,
            ))
            idx += 1

        return chunks
