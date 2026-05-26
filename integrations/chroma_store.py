"""Chroma 向量库适配."""
from django.conf import settings

import chromadb


def get_client() -> chromadb.PersistentClient:
    cfg = settings.CHROMA_CONFIG
    return chromadb.PersistentClient(path=cfg['persist_dir'])


def get_collection(name: str):
    client = get_client()
    return client.get_or_create_collection(name=name)


def ensure_collection(tenant_id: str, kb_id: str):
    """按 kb_{tenant}_{kb} 命名取得 collection."""
    name = f'kb_{tenant_id}_{kb_id}'
    return get_collection(name)
