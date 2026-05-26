"""本地 Embedding 客户端（sentence-transformers）."""
import logging

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

# 中文友好的轻量模型
_DEFAULT_MODEL = 'BAAI/bge-small-zh-v1.5'


class EmbeddingClient:
    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or _DEFAULT_MODEL
        logger.info('加载 embedding 模型: %s', self.model_name)
        self.model = SentenceTransformer(self.model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        """批量文本 → 向量."""
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
