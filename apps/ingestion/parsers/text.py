from .base import BaseParser, ParsedDocument, ParsedSection


class TextParser(BaseParser):
    """纯文本解析器 (.txt)."""

    def parse(self, file_path: str) -> ParsedDocument:
        with open(file_path, encoding='utf-8') as f:
            text = f.read()
        title = file_path.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
        return ParsedDocument(
            title=title,
            sections=[ParsedSection(text=text)],
            raw_text=text,
        )
