import os
import re
from typing import List, Dict, Optional


class IndexManager:
    def __init__(self, user_data_path: str = "user_data", index_file: str = "index.md"):
        self.user_data_path = user_data_path
        self.index_file = os.path.join(user_data_path, index_file)
        self._ensure_index_file()

    def _ensure_index_file(self):
        if not os.path.exists(self.index_file):
            with open(self.index_file, 'w', encoding='utf-8') as f:
                f.write("# 私人知识库索引\n\n")

    def add_entry(self, file_type: str, file_name: str, file_path: str, summary: str):
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        section_header = f"## {file_type}/"
        entry_line = f"- [{file_name}]({file_path}) - {summary}"
        
        if section_header not in content:
            content += f"\n{section_header}\n"
        
        if f"]({file_path})" in content:
            self.update_entry(file_path, summary)
            return
        
        lines = content.split('\n')
        new_lines = []
        section_found = False
        for line in lines:
            new_lines.append(line)
            if line.strip() == section_header:
                section_found = True
                continue
            if section_found and line.startswith('- ['):
                new_lines.insert(len(new_lines) - 1, entry_line)
                section_found = False
                continue
        
        if section_found:
            new_lines.append(entry_line)
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))

    def remove_entry(self, file_path: str):
        with open(self.index_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if file_path not in line:
                new_lines.append(line)
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

    def update_entry(self, file_path: str, new_summary: str):
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        pattern = rf"- \[([^\]]+)\]\({re.escape(file_path)}\) - .+"
        new_entry = rf"- [\1]({file_path}) - {new_summary}"
        content = re.sub(pattern, new_entry, content)
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def get_all_entries(self) -> List[Dict]:
        entries = []
        current_type = ""
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('## '):
                current_type = line[3:].rstrip('/')
            elif line.startswith('- ['):
                match = re.match(r"- \[([^\]]+)\]\(([^)]*(?:\([^)]*\)[^)]*)*)\) - (.+)", line)
                if match:
                    entries.append({
                        'type': current_type,
                        'file_name': match.group(1),
                        'file_path': match.group(2),
                        'summary': match.group(3)
                    })
        
        return entries

    def search_entries(self, query: str) -> List[Dict]:
        entries = self.get_all_entries()
        results = []
        query_lower = query.lower()
        
        query_words = [w for w in query_lower.split() if len(w) >= 2]
        
        for entry in entries:
            content = f"{entry['file_name'].lower()} {entry['summary'].lower()}"
            
            if query_lower in content:
                results.append(entry)
            elif query_words:
                matched_count = sum(1 for word in query_words if word in content)
                if matched_count >= len(query_words) * 0.5:
                    results.append(entry)
        
        return results

    def get_entry_by_path(self, file_path: str) -> Optional[Dict]:
        entries = self.get_all_entries()
        for entry in entries:
            if entry['file_path'] == file_path:
                return entry
        return None

    def rebuild_index(self):
        extensions = {'pdf', 'docx', 'pptx', 'xlsx'}
        entries = []
        
        for ext in extensions:
            dir_path = os.path.join(self.user_data_path, ext)
            if not os.path.exists(dir_path):
                continue
            
            for md_file in os.listdir(dir_path):
                if md_file.endswith('.md'):
                    file_name = md_file[:-3]
                    file_path = f"{ext}/{md_file}"
                    entries.append({
                        'type': ext,
                        'file_name': file_name,
                        'file_path': file_path,
                        'summary': '待生成摘要'
                    })
        
        with open(self.index_file, 'w', encoding='utf-8') as f:
            f.write("# 私人知识库索引\n\n")
            
            for ext in sorted(extensions):
                ext_entries = [e for e in entries if e['type'] == ext]
                if ext_entries:
                    f.write(f"## {ext}/\n")
                    for entry in ext_entries:
                        f.write(f"- [{entry['file_name']}]({entry['file_path']}) - {entry['summary']}\n")
                    f.write("\n")