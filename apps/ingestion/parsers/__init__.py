from .base import BaseParser, ParsedDocument, ParsedSection
from .text import TextParser
from .markdown import MarkdownParser
from .pdf import PDFParser
from .docx import DocxParser

PARSER_MAP = {
    'text/plain': TextParser,
    'text/markdown': MarkdownParser,
    'application/pdf': PDFParser,
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DocxParser,
    'application/msword': DocxParser,
}


def get_parser(mime_type: str) -> BaseParser:
    cls = PARSER_MAP.get(mime_type)
    if cls is None:
        raise ValueError(f'不支持的文档类型: {mime_type}')
    return cls()
