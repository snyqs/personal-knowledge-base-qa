# 私人知识库智能问答系统

## 概述

本技能提供端侧私人知识库智能问答功能，支持PDF、DOCX、PPTX、XLSX等多种文档格式的上传、解析和智能问答。用户可以通过Web界面上传文档，系统自动解析为Markdown格式并建立索引，然后通过智能问答功能检索相关内容并生成回答。

## 功能特性

- **文档上传**：支持PDF、DOCX、PPTX、XLSX格式文档上传
- **文档解析**：自动将文档解析为Markdown格式，按文件类型分类存储
- **AI摘要**：使用Ollama+qwen2:7b模型生成文档摘要
- **智能问答**：通过LLM驱动的文档检索和问答功能
- **索引管理**：三层索引结构（路径、文件名、内容概括）

## 技术栈

- Python 3.11
- FastAPI
- PyTorch + CUDA
- Ollama + qwen2:7b
- pdfplumber、python-docx、python-pptx、pandas

## 目录结构

```
<skill-root>/
├── SKILL.md                    # 技能定义文件
├── scripts/                    # 核心脚本包
│   ├── __init__.py
│   ├── main.py                 # FastAPI Web应用入口
│   ├── document_processor.py   # 文档处理管道
│   ├── index_manager.py        # 索引管理
│   ├── knowledge_base.py       # 知识库管理
│   ├── llm_service.py          # LLM服务
│   ├── summary_generator.py    # 摘要生成
│   ├── parsers/                # 文档解析器
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── pptx_parser.py
│   │   └── xlsx_parser.py
│   ├── static/                 # Web静态文件
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   └── requirements.txt        # Python依赖列表
└── user_data/                  # 用户数据目录（运行时生成）
    ├── pdf/
    ├── docx/
    ├── pptx/
    ├── xlsx/
    └── index.md
```

## 安装与运行

### 环境要求

- Python 3.11+
- CUDA 12.1+（NVIDIA GPU）
- Ollama（已安装qwen2:7b模型）

### 安装步骤

```bash
# 1. 创建并激活conda环境
conda create -n PersonalRAG python=3.11
conda activate PersonalRAG

# 2. 安装依赖
pip install -r scripts/requirements.txt

# 3. 启动Ollama服务
ollama serve

# 4. 拉取qwen2:7b模型
ollama pull qwen2:7b

# 5. 启动Web服务
python scripts/main.py
```

### 访问地址

- Web界面：http://localhost:8000
- API文档：http://localhost:8000/docs

## API接口

### 文档上传

```
POST /api/upload
Content-Type: multipart/form-data

参数：
- file: 文件（支持.pdf, .docx, .pptx, .xlsx）
```

### 文档列表

```
GET /api/documents
```

### 搜索文档

```
GET /api/search?q=关键词
```

### 智能问答

```
POST /api/ask
Content-Type: application/x-www-form-urlencoded

参数：
- question: 问题文本
```

### 删除文档

```
DELETE /api/documents/{file_path}
```

### 重建索引

```
POST /api/rebuild
```

## 使用说明

1. 打开Web界面 http://localhost:8000
2. 在"文档上传"标签页上传PDF/DOCX/PPTX/XLSX文件
3. 在"智能问答"标签页输入问题进行查询
4. 在"文档列表"标签页查看和管理已上传的文档

## 依赖列表

见 `scripts/requirements.txt`

## 许可证

MIT License