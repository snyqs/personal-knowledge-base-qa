import pandas as pd
from typing import List


class XLSXParser:
    def __init__(self):
        pass

    def parse(self, file_path: str) -> str:
        md_content = []
        try:
            xls = pd.ExcelFile(file_path, engine='openpyxl')
            
            for sheet_name in xls.sheet_names:
                md_content.append(f"## 工作表: {sheet_name}")
                
                df = pd.read_excel(xls, sheet_name=sheet_name, engine='openpyxl')
                
                md_table = self._dataframe_to_markdown(df)
                md_content.append(md_table)
                md_content.append("\n---\n")
            
            return "\n".join(md_content)
        except Exception as e:
            raise RuntimeError(f"XLSX解析失败: {str(e)}")

    def _dataframe_to_markdown(self, df: pd.DataFrame) -> str:
        md_lines = []
        
        headers = df.columns.tolist()
        md_lines.append(f"| {' | '.join(str(h) for h in headers)} |")
        md_lines.append(f"| {' | '.join(['---'] * len(headers))} |")
        
        for _, row in df.iterrows():
            cells = []
            for val in row:
                if pd.isna(val):
                    cells.append("")
                else:
                    cells.append(str(val).replace('\n', ' '))
            md_lines.append(f"| {' | '.join(cells)} |")
        
        return '\n'.join(md_lines)