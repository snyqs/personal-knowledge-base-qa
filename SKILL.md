---
name: personal-knowledge-base-qa
description: Execute the local personal knowledge base intelligent QA system powered by NVIDIA GPU. This skill supports uploading PDF, DOCX, PPTX, XLSX documents, parsing them into Markdown format, building AI summaries, and providing intelligent question answering capabilities. All processing is done locally with Ollama qwen2:7b model.
---

# 私人知识库智能问答系统

## 技能描述

本技能自动化执行"私人知识库智能问答系统"项目，提供文档上传、解析、AI摘要和智能问答功能。所有处理均在本地完成，基于NVIDIA GPU加速推理，零API成本。

**核心功能：**

- 📁 **文档上传** — 支持PDF、DOCX、PPTX、XLSX格式
- 📝 **文档解析** — 自动转换为Markdown格式，按文件类型分类存储
- 🤖 **AI摘要生成** — 使用Ollama qwen2:7b模型生成文档摘要
- 🔍 **智能问答** — 通过LLM驱动的文档检索和问答
- 📋 **索引管理** — 三层索引结构（路径、文件名、内容概括）

**技术特色：**

- ✅ 完全本地运行，数据隐私保护
- ✅ 基于NVIDIA GPU加速推理（CUDA）
- ✅ 零API费用，无需Key
- ✅ 使用Ollama qwen2:7b模型

## 前置要求

### 系统要求

- **操作系统**: Windows 10/11（推荐）、Linux、macOS
- **Python**: 3.11
- **处理器**: NVIDIA GPU（推荐 RTX 4050 及以上）
- **内存**: 最低 8 GB，推荐 16 GB
- **显存**: 最低 8 GB（qwen2:7b INT8约占用7GB显存）
- **存储**: 至少 10 GB 可用空间（模型文件约 7 GB）

### 依赖工具

- **pip**（Python 包管理器）
- **Ollama**（用于本地LLM推理）

## 目录结构

```
<skill-root>/                   # 本 SKILL.md 所在目录
├── SKILL.md                    # 本技能定义文件
├── scripts/                    # 核心脚本包（Python 包）
│   ├── __init__.py
│   ├── main.py                 # FastAPI Web 应用入口
│   ├── document_processor.py   # 文档处理管道
│   ├── index_manager.py        # 索引管理
│   ├── knowledge_base.py       # 知识库管理
│   ├── llm_service.py          # LLM 服务
│   ├── summary_generator.py    # 摘要生成
│   ├── parsers/                # 文档解析器
│   │   ├── __init__.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   ├── pptx_parser.py
│   │   └── xlsx_parser.py
│   ├── static/                 # Web 静态文件
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   └── requirements.txt        # Python 依赖列表
└── user_data/                  # 用户数据目录（运行时生成）
    ├── pdf/
    ├── docx/
    ├── pptx/
    ├── xlsx/
    └── index.md
```

## 执行步骤

### 步骤 1: 安装 Python 依赖

```bash
# 确保在 skill 根目录下执行
cd /path/to/skill-root
pip install -r scripts/requirements.txt
```

### 步骤 2: 启动 Ollama 服务

```bash
# 启动 Ollama 服务（后台运行）
ollama serve

# 在另一个终端拉取 qwen2:7b 模型
ollama pull qwen2:7b
```

**说明：**

- 模型文件约 7 GB，下载时间取决于网络速度
- 首次下载后会自动缓存，后续启动无需重新下载

### 步骤 3: 启动 FastAPI Web 应用

```bash
python scripts/main.py
```

启动后浏览器访问 `http://localhost:8000`，即可在图形界面中使用所有功能。

---

## 🎯 核心功能说明

### 功能 1: 文档上传

**位置**: Web 界面「文档上传」Tab

支持上传 PDF、DOCX、PPTX、XLSX 格式文件，系统自动解析并按文件类型分类存储。

### 功能 2: 智能问答

**位置**: Web 界面「智能问答」Tab

输入问题后，系统会：
1. 将问题和索引传给 LLM，由 LLM 判断需要检索哪些文档
2. 读取相关文档内容
3. 将问题和文档内容一起传给 LLM 生成回答

### 功能 3: 文档列表与管理

**位置**: Web 界面「文档列表」Tab

查看已上传的文档列表，支持搜索和重建索引。

---

## 🚀 使用方式

### 方式一：Web 界面（推荐）

```bash
python scripts/main.py
```

打开浏览器访问 `http://localhost:8000`，按「上传文档 → 智能问答」流程使用。

### 方式二：API 调用

```bash
# 上传文档
curl -X POST -F "file=@test.pdf" http://localhost:8000/api/upload

# 智能问答
curl -X POST -d "question=文档中提到的主要内容是什么？" http://localhost:8000/api/ask

# 搜索文档
curl http://localhost:8000/api/search?q=关键词

# 获取文档列表
curl http://localhost:8000/api/documents

# 删除文档
curl -X DELETE http://localhost:8000/api/documents/user_data/pdf/test.md

# 重建索引
curl -X POST http://localhost:8000/api/rebuild
```

---

## 📝 API 接口说明

| API 路径 | 方法 | 功能 |
| -------- | ---- | ---- |
| `/api/upload` | POST | 上传文档（支持.pdf, .docx, .pptx, .xlsx） |
| `/api/documents` | GET | 获取文档列表 |
| `/api/search` | GET | 搜索文档（参数：q） |
| `/api/ask` | POST | 智能问答（参数：question） |
| `/api/documents/{file_path}` | DELETE | 删除文档 |
| `/api/rebuild` | POST | 重建索引 |

---

## 📄 许可证

MIT License