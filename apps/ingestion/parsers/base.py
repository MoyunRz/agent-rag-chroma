from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ParsedSection:
    """解析后的文本段."""
    text: str
    page: int | None = None
    heading_level: int = 0
    heading: str = ''


@dataclass
class ParsedDocument:
    """解析器统一输出格式."""
    title: str
    sections: list[ParsedSection] = field(default_factory=list)
    raw_text: str = ''


class BaseParser(ABC):
    """文档解析器基类."""

    @abstractmethod
    def parse(self, file_path: str) -> ParsedDocument:
        ...
