from .base import BaseParser, ParsedDocument, ParsedSection


class PDFParser(BaseParser):
    """PDF 解析器（需要 pypdf 或 pdfplumber）."""

    def parse(self, file_path: str) -> ParsedDocument:
        try:
            import pdfplumber
        except ImportError:
            try:
                from pypdf import PdfReader
                return self._parse_pypdf(file_path)
            except ImportError:
                raise ImportError('PDF 解析需要安装 pypdf 或 pdfplumber: pip install pypdf')

        return self._parse_pdfplumber(file_path)

    def _parse_pdfplumber(self, file_path: str) -> ParsedDocument:
        import pdfplumber
        sections = []
        with pdfplumber.open(file_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    sections.append(ParsedSection(text=text, page=i + 1))
        title = file_path.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
        raw = '\n\n'.join(s.text for s in sections)
        return ParsedDocument(title=title, sections=sections, raw_text=raw)

    def _parse_pypdf(self, file_path: str) -> ParsedDocument:
        from pypdf import PdfReader
        sections = []
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                sections.append(ParsedSection(text=text, page=i + 1))
        title = file_path.rsplit('/', 1)[-1].rsplit('\\', 1)[-1]
        raw = '\n\n'.join(s.text for s in sections)
        return ParsedDocument(title=title, sections=sections, raw_text=raw)
