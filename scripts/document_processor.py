import os
import sys
import unicodedata
from typing import Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from parsers import PDFParser, DOCXParser, PPTXParser, XLSXParser


def normalize_filename(filename: str) -> str:
    filename = unicodedata.normalize('NFKC', filename)
    filename = filename.replace('\\', '_').replace('/', '_').replace(':', '_')
    filename = filename.replace('*', '_').replace('?', '_').replace('"', '_')
    filename = filename.replace('<', '_').replace('>', '_').replace('|', '_')
    return filename


class DocumentProcessor:
    def __init__(self, user_data_path: str = "user_data"):
        self.user_data_path = user_data_path
        self.parsers = {
            '.pdf': PDFParser(),
            '.docx': DOCXParser(),
            '.pptx': PPTXParser(),
            '.xlsx': XLSXParser(),
        }
        self._ensure_directories()

    def _ensure_directories(self):
        for ext in self.parsers.keys():
            dir_name = ext[1:]
            dir_path = os.path.join(self.user_data_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)

    def process_file(self, file_path: str) -> Optional[str]:
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext not in self.parsers:
            raise ValueError(f"不支持的文件格式: {ext}")
        
        parser = self.parsers[ext]
        md_content = parser.parse(file_path)
        
        filename = os.path.basename(file_path)
        filename = normalize_filename(filename)
        md_filename = f"{os.path.splitext(filename)[0]}.md"
        dir_name = ext[1:]
        save_path = os.path.join(self.user_data_path, dir_name, md_filename)
        
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return save_path

    def get_supported_extensions(self) -> list:
        return list(self.parsers.keys())

    def is_supported(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.parsers