import os
import sys
from typing import List, Dict, Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from document_processor import DocumentProcessor
from index_manager import IndexManager
from summary_generator import SummaryGenerator
from llm_service import LLMSummaryService


class KnowledgeBase:
    def __init__(self, user_data_path: str = "user_data", use_llm_summary: bool = False):
        self.user_data_path = user_data_path
        self.processor = DocumentProcessor(user_data_path)
        self.index_manager = IndexManager(user_data_path)
        self.summary_generator = SummaryGenerator(use_llm=use_llm_summary)
        self.llm_service = LLMSummaryService()

    def add_document(self, file_path: str) -> Dict:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        md_path = self.processor.process_file(file_path)
        
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = self.summary_generator.generate(content)
        
        file_name = os.path.basename(file_path)
        file_type = os.path.splitext(file_name)[1][1:]
        relative_path = os.path.relpath(md_path, self.user_data_path).replace('\\', '/')
        
        self.index_manager.add_entry(file_type, file_name, relative_path, summary)
        
        return {
            'file_name': file_name,
            'file_type': file_type,
            'md_path': md_path,
            'summary': summary
        }

    def add_documents_from_dir(self, dir_path: str) -> List[Dict]:
        results = []
        
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in self.processor.get_supported_extensions():
                    try:
                        result = self.add_document(file_path)
                        results.append(result)
                        print(f"处理成功: {file}")
                    except Exception as e:
                        print(f"处理失败 {file}: {str(e)}")
                        results.append({'file_name': file, 'error': str(e)})
        
        return results

    def remove_document(self, file_path: str) -> bool:
        ext = os.path.splitext(file_path)[1][1:]
        md_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}.md"
        relative_path = f"{ext}/{md_filename}"
        
        self.index_manager.remove_entry(relative_path)
        
        full_md_path = os.path.join(self.user_data_path, relative_path)
        if os.path.exists(full_md_path):
            os.remove(full_md_path)
            return True
        
        return False

    def search(self, query: str) -> List[Dict]:
        return self.index_manager.search_entries(query)

    def get_all_documents(self) -> List[Dict]:
        return self.index_manager.get_all_entries()

    def rebuild_index(self):
        self.index_manager.rebuild_index()

    def update_summary(self, file_path: str) -> Optional[str]:
        if file_path.startswith('/'):
            file_path = file_path[1:]
        
        if '/' in file_path:
            parts = file_path.split('/')
            if len(parts) >= 2:
                relative_path = file_path
            else:
                ext = os.path.splitext(file_path)[1][1:]
                md_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}.md"
                relative_path = f"{ext}/{md_filename}"
        else:
            ext = os.path.splitext(file_path)[1][1:]
            md_filename = f"{os.path.splitext(os.path.basename(file_path))[0]}.md"
            relative_path = f"{ext}/{md_filename}"
        
        full_md_path = os.path.join(self.user_data_path, relative_path)
        if not os.path.exists(full_md_path):
            return None
        
        with open(full_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = self.summary_generator.generate(content)
        self.index_manager.update_entry(relative_path, summary)
        
        return summary

    def _search_by_keywords(self, keywords: list) -> list:
        matched_files = []
        keyword_set = set([k.lower() for k in keywords if k.strip()])
        
        if not keyword_set:
            return matched_files
        
        valid_extensions = {'pdf', 'docx', 'pptx', 'xlsx'}
        
        for ext in valid_extensions:
            ext_dir = os.path.join(self.user_data_path, ext)
            if not os.path.exists(ext_dir):
                continue
            
            for file in os.listdir(ext_dir):
                if file.endswith('.md'):
                    file_path = os.path.join(ext_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                        
                        match_count = 0
                        for kw in keyword_set:
                            if kw in content:
                                match_count += content.count(kw)
                        
                        if match_count > 0:
                            original_filename = os.path.splitext(file)[0]
                            file_path_in_index = f"{ext}/{original_filename}.{ext}"
                            matched_files.append((file_path_in_index, match_count))
                    except Exception as e:
                        print(f"读取文件失败 {file_path}: {str(e)}")
        
        matched_files.sort(key=lambda x: x[1], reverse=True)
        
        return [f[0] for f in matched_files[:5]]
    
    def _extract_context_around_keywords(self, content: str, keywords: list, window_size: int = 500) -> str:
        if not keywords:
            return content[:3000]
        
        keyword_lower = [k.lower() for k in keywords if k.strip()]
        content_lower = content.lower()
        
        relevant_positions = []
        for kw in keyword_lower:
            start = 0
            while True:
                pos = content_lower.find(kw, start)
                if pos == -1:
                    break
                relevant_positions.append(pos)
                start = pos + len(kw)
        
        if not relevant_positions:
            return content[:3000]
        
        relevant_positions.sort()
        
        segments = []
        used_ranges = []
        
        for pos in relevant_positions:
            start = max(0, pos - window_size)
            end = min(len(content), pos + window_size)
            
            overlap = False
            for us_start, us_end in used_ranges:
                if not (end < us_start or start > us_end):
                    overlap = True
                    break
            
            if not overlap:
                segments.append((start, end))
                used_ranges.append((start, end))
        
        segments.sort(key=lambda x: x[0])
        
        merged_segments = []
        for seg in segments:
            if not merged_segments:
                merged_segments.append(seg)
            else:
                last_start, last_end = merged_segments[-1]
                if seg[0] <= last_end:
                    merged_segments[-1] = (last_start, max(last_end, seg[1]))
                else:
                    merged_segments.append(seg)
        
        result_parts = []
        for start, end in merged_segments:
            result_parts.append(content[start:end])
        
        return '\n\n'.join(result_parts)[:5000]

    def smart_ask(self, question: str) -> Dict:
        index_path = os.path.join(self.user_data_path, "index.md")
        if not os.path.exists(index_path):
            return {
                "status": "error",
                "answer": "知识库索引文件不存在",
                "sources": [],
                "context": ""
            }
        
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        selected_files = self.llm_service.select_relevant_files(index_content, question)
        
        if not selected_files:
            llm_keywords = self.llm_service.extract_keywords(question, index_content)
            print(f"LLM文件选择失败，使用LLM关键词检索: {llm_keywords}")
            
            if llm_keywords:
                selected_files = self._search_by_keywords(llm_keywords)
                print(f"LLM关键词检索结果: {selected_files}")
            
            if not selected_files:
                rule_keywords = self.llm_service._rule_based_keywords(question)
                print(f"LLM关键词检索失败，使用规则式关键词检索: {rule_keywords}")
                
                if rule_keywords:
                    selected_files = self._search_by_keywords(rule_keywords)
                    print(f"规则式关键词检索结果: {selected_files}")
        
        if not selected_files:
            return {
                "status": "success",
                "answer": "抱歉，在知识库中未找到相关内容。",
                "sources": [],
                "context": ""
            }
        
        context_parts = []
        sources = []
        all_keywords = self.llm_service._rule_based_keywords(question)
        
        for file_path in selected_files:
            md_path = os.path.join(self.user_data_path, file_path.replace('.pdf', '.md').replace('.docx', '.md').replace('.pptx', '.md').replace('.xlsx', '.md'))
            
            if os.path.exists(md_path):
                with open(md_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                context_segment = self._extract_context_around_keywords(content, all_keywords)
                context_parts.append(f"【{file_path}】\n{context_segment}")
                sources.append({
                    "file_name": os.path.basename(file_path),
                    "file_path": file_path
                })
            else:
                print(f"文件不存在: {md_path}")
        
        if not context_parts:
            print(f"未找到任何有效文件，尝试规则式关键词回退")
            rule_keywords = self.llm_service._rule_based_keywords(question)
            fallback_files = self._search_by_keywords(rule_keywords)
            print(f"规则式关键词回退检索结果: {fallback_files}")
            
            for file_path in fallback_files:
                md_path = os.path.join(self.user_data_path, file_path.replace('.pdf', '.md').replace('.docx', '.md').replace('.pptx', '.md').replace('.xlsx', '.md'))
                
                if os.path.exists(md_path):
                    with open(md_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    context_segment = self._extract_context_around_keywords(content, rule_keywords)
                    context_parts.append(f"【{file_path}】\n{context_segment}")
                    sources.append({
                        "file_name": os.path.basename(file_path),
                        "file_path": file_path
                    })
        
        if not context_parts:
            return {
                "status": "success",
                "answer": "抱歉，在知识库中未找到相关内容。",
                "sources": [],
                "context": ""
            }
        
        context = "\n\n---\n\n".join(context_parts)
        answer = self.llm_service.generate_answer(question, context)
        
        return {
            "status": "success",
            "answer": answer,
            "sources": sources,
            "context": context[:2000]
        }