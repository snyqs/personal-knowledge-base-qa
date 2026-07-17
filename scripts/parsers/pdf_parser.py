import pdfplumber
import re
from typing import List, Optional


class PDFParser:
    def __init__(self):
        pass

    def parse(self, file_path: str) -> str:
        md_content = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    md_content.append(f"## 第{page_num}页")
                    
                    text = page.extract_text()
                    if text:
                        cleaned_text = self._clean_text(text)
                        md_content.append(cleaned_text)
                    
                    tables = page.extract_tables()
                    for table_idx, table in enumerate(tables, 1):
                        md_table = self._table_to_markdown(table)
                        md_content.append(f"\n### 表格{table_idx}\n")
                        md_content.append(md_table)
                    
                    md_content.append("\n---\n")
            
            return "\n".join(md_content)
        except Exception as e:
            raise RuntimeError(f"PDF解析失败: {str(e)}")

    def _clean_text(self, text: str) -> str:
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
        return '\n'.join(cleaned_lines)

    def _table_to_markdown(self, table: List[List[str]]) -> str:
        if not table or not table[0]:
            return ""
        
        md_lines = []
        header = [str(cell).strip() if cell else "" for cell in table[0]]
        md_lines.append(f"| {' | '.join(header)} |")
        
        separator = ["---"] * len(header)
        md_lines.append(f"| {' | '.join(separator)} |")
        
        for row in table[1:]:
            row_cells = [str(cell).strip() if cell else "" for cell in row]
            md_lines.append(f"| {' | '.join(row_cells)} |")
        
        return '\n'.join(md_lines)