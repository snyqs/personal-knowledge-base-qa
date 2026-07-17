import os
import sys
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import KnowledgeBase

app = FastAPI(title="私人知识库智能问答系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

kb = KnowledgeBase("user_data", use_llm_summary=True)

static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse(content="<html><body><h1>私人知识库智能问答系统</h1><p>请创建 static/index.html</p></body></html>")


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="文件名不能为空")
    
    allowed_extensions = [".pdf", ".docx", ".pptx", ".xlsx"]
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file_ext}")
    
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        results = kb.add_documents_from_dir(str(upload_dir))
        
        os.remove(file_path)
        
        if results and "error" not in results[0]:
            return JSONResponse(content={
                "status": "success",
                "message": f"文件 {file.filename} 上传并处理成功",
                "summary": results[0].get("summary", "")[:200]
            })
        else:
            error_msg = results[0].get("error", "未知错误") if results else "处理失败"
            raise HTTPException(status_code=500, detail=f"文档处理失败: {error_msg}")
            
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"处理文件时出错: {str(e)}")


@app.get("/api/documents")
async def list_documents():
    documents = kb.get_all_documents()
    return JSONResponse(content={
        "status": "success",
        "count": len(documents),
        "documents": documents
    })


@app.get("/api/search")
async def search_documents(q: str = ""):
    if not q:
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    
    results = kb.search(q)
    return JSONResponse(content={
        "status": "success",
        "query": q,
        "count": len(results),
        "results": results
    })


@app.post("/api/ask")
async def ask_question(question: str = Form(...)):
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    result = kb.smart_ask(question)
    
    return JSONResponse(content={
        "status": result["status"],
        "answer": result["answer"],
        "sources": result["sources"],
        "context": result.get("context", "")
    })


@app.delete("/api/documents/{file_path:path}")
async def delete_document(file_path: str):
    try:
        success = kb.remove_document(file_path)
        if success:
            return JSONResponse(content={
                "status": "success",
                "message": f"文档 {file_path} 已删除"
            })
        else:
            raise HTTPException(status_code=404, detail=f"文档 {file_path} 不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


@app.post("/api/rebuild")
async def rebuild_index():
    try:
        kb.rebuild_index()
        return JSONResponse(content={
            "status": "success",
            "message": "索引重建成功"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重建失败: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)