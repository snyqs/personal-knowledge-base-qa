import os
import json
import urllib.request
import urllib.error
from typing import Optional


class LLMSummaryService:
    def __init__(self, use_ollama: bool = True, model_name: str = "qwen2:7b", base_url: str = "http://localhost:11434"):
        self.use_ollama = use_ollama
        self.model_name = model_name
        self.base_url = base_url
        self._ollama_available = False
        self._check_ollama()

    def _check_ollama(self):
        try:
            urllib.request.urlopen(f"{self.base_url}/api/tags", timeout=5)
            self._ollama_available = True
            print(f"Ollama服务可用，模型: {self.model_name}")
        except urllib.error.URLError:
            self._ollama_available = False
            print("Ollama服务不可用，将使用规则式摘要")

    def generate_summary(self, content: str, max_length: int = 200) -> str:
        if not self.use_ollama or not self._ollama_available:
            return self._rule_based_summary(content, max_length)
        
        prompt = f"""请用简洁的中文概括以下文档内容，字数控制在100-200字之间：

{content[:5000]}

摘要："""
        
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": max_length
            }
        }
        
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(data).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                response = json.loads(resp.read().decode('utf-8'))
                summary = response.get('response', '').strip()
            
            return summary[:max_length]
        except Exception as e:
            print(f"Ollama调用失败，使用规则式摘要: {str(e)}")
            return self._rule_based_summary(content, max_length)

    def _rule_based_summary(self, content: str, max_length: int = 200) -> str:
        content = content.strip()
        if not content:
            return "无内容"
        
        sentences = content.split('\n')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return "无内容"
        
        first_lines = []
        for sentence in sentences[:5]:
            if len(sentence) > 50:
                first_lines.append(sentence[:50] + "...")
            else:
                first_lines.append(sentence)
        
        summary = " ".join(first_lines)
        
        if len(summary) > max_length:
            summary = summary[:max_length] + "..."
        
        return summary

    def is_model_loaded(self) -> bool:
        return self._ollama_available

    def select_relevant_files(self, index_content: str, question: str) -> list:
        if not self.use_ollama or not self._ollama_available:
            return []
        
        prompt = f"""你是一个智能文档检索助手。请分析用户的问题，从以下文档索引中选择最相关的文档文件路径。

文档索引内容：
{index_content[:8000]}

用户问题：{question}

请严格按照JSON格式返回，不要包含任何其他文本：
{{"file_paths": ["文件路径1", "文件路径2", ...]}}

注意：
1. 文件路径是索引中的相对路径，如 "pdf/xxx.pdf" 或 "docx/xxx.docx"
2. 只返回最相关的2-5个文件
3. 如果没有相关文件，返回空数组 []"""
        
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "max_tokens": 200
            }
        }
        
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(data).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                response = json.loads(resp.read().decode('utf-8'))
                result = response.get('response', '').strip()
            
            result = result.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(result)
            
            if isinstance(parsed, dict):
                return parsed.get('file_paths', [])
            elif isinstance(parsed, list):
                return parsed
            else:
                return []
        except Exception as e:
            print(f"LLM文件选择失败: {str(e)}")
            return []

    def extract_keywords(self, question: str, index_content: str) -> list:
        if not self.use_ollama or not self._ollama_available:
            return []
        
        prompt = f"""你是一个关键词提取助手。请分析用户的问题，从以下文档索引中提取3个最相关的关键词或数据。
如果索引中没有明显相关的内容，请根据问题本身提取3个核心关键词。

文档索引内容：
{index_content[:5000]}

用户问题：{question}

请严格按照JSON格式返回，不要包含任何其他文本：
{{"keywords": ["关键词1", "关键词2", "关键词3"]}}

注意：
1. 关键词应该是名词或短语，能够帮助检索文档内容
2. 如果无法提取，请返回空数组 []"""
        
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "max_tokens": 100
            }
        }
        
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(data).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=60) as resp:
                response = json.loads(resp.read().decode('utf-8'))
                result = response.get('response', '').strip()
            
            result = result.replace('```json', '').replace('```', '').strip()
            parsed = json.loads(result)
            
            if isinstance(parsed, dict):
                return parsed.get('keywords', [])
            elif isinstance(parsed, list):
                return parsed[:3]
            else:
                return []
        except Exception as e:
            print(f"LLM关键词提取失败: {str(e)}")
            return []

    def generate_answer(self, question: str, context: str) -> str:
        if not self.use_ollama or not self._ollama_available:
            return f"根据检索到的内容，关于'{question}'的信息如下：\n{context[:500]}"
        
        prompt = f"""你是一个智能问答助手。请根据提供的文档内容，回答用户的问题。

用户问题：{question}

相关文档内容：
{context[:10000]}

请用简洁、准确的中文回答用户的问题，不要编造信息。如果文档中没有相关内容，请明确说明。"""
        
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "max_tokens": 500
            }
        }
        
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(data).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=120) as resp:
                response = json.loads(resp.read().decode('utf-8'))
                answer = response.get('response', '').strip()
            
            return answer
        except Exception as e:
            print(f"LLM回答生成失败: {str(e)}")
            return f"根据检索到的内容，关于'{question}'的信息如下：\n{context[:500]}"