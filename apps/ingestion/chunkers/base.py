from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class Chunk:
    text: str
    page: int | None = None
    heading_path: str = ''
    chunk_index: int = 0


class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str, page: int | None = None, heading_path: str = '') -> list[Chunk]:
        ...
