from typing import Optional


class RuleBasedSummaryGenerator:
    def __init__(self):
        pass

    def generate_summary(self, content: str, max_length: int = 200) -> str:
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


class SummaryGenerator:
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        self.rule_based = RuleBasedSummaryGenerator()
        self.llm_service = None
        
        if use_llm:
            from .llm_service import LLMSummaryService
            self.llm_service = LLMSummaryService()

    def generate(self, content: str, max_length: int = 200) -> str:
        if self.use_llm and self.llm_service is not None:
            try:
                return self.llm_service.generate_summary(content, max_length)
            except Exception as e:
                print(f"LLM摘要生成失败，使用规则式摘要: {str(e)}")
                return self.rule_based.generate_summary(content, max_length)
        
        return self.rule_based.generate_summary(content, max_length)