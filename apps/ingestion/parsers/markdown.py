import re

from .base import BaseParser, ParsedDocument, ParsedSection

HEADING_RE = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)


class MarkdownParser(BaseParser):
    """Markdown 解析器 (.md)."""

    def parse(self, file_path: str) -> ParsedDocument:
        with open(file_path, encoding='utf-8') as f:
            text = f.read()

        title = file_path.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
        sections = self._split_sections(text)
        return ParsedDocument(title=title, sections=sections, raw_text=text)

    def _split_sections(self, text: str) -> list[ParsedSection]:
        """按标题边界切分，保留标题内容和层级."""
        matches = list(HEADING_RE.finditer(text))
        if not matches:
            return [ParsedSection(text=text)]

        sections = []
        for i, m in enumerate(matches):
            start = m.end() + 1
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start:end].strip()
            sections.append(ParsedSection(
                text=f'{m.group(0)}\n{body}',
                heading_level=len(m.group(1)),
                heading=m.group(2),
            ))
        return sections
