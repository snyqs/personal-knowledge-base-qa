document.addEventListener('DOMContentLoaded', function() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(`${btn.dataset.tab}-tab`).classList.add('active');
            
            if (btn.dataset.tab === 'documents') {
                loadDocuments();
            }
        });
    });
    
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            uploadFile(files[0]);
        }
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            uploadFile(e.target.files[0]);
        }
    });
    
    async function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        uploadStatus.innerHTML = `<div class="status-message">正在上传 ${file.name}...</div>`;
        
        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok && data.status === 'success') {
                uploadStatus.innerHTML = `
                    <div class="status-message success">
                        ✅ ${data.message}<br>
                        <small>摘要: ${data.summary}</small>
                    </div>
                `;
            } else {
                throw new Error(data.detail || '上传失败');
            }
        } catch (error) {
            uploadStatus.innerHTML = `
                <div class="status-message error">
                    ❌ 上传失败: ${error.message}
                </div>
            `;
        }
    }
    
    const questionInput = document.getElementById('question-input');
    const askBtn = document.getElementById('ask-btn');
    const chatContainer = document.getElementById('chat-container');
    
    askBtn.addEventListener('click', askQuestion);
    questionInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            askQuestion();
        }
    });
    
    async function askQuestion() {
        const question = questionInput.value.trim();
        if (!question) return;
        
        chatContainer.innerHTML += `
            <div class="message user">
                <p>${escapeHtml(question)}</p>
            </div>
        `;
        
        questionInput.value = '';
        askBtn.disabled = true;
        askBtn.textContent = '思考中...';
        
        chatContainer.innerHTML += `
            <div class="message system" id="loading-message">
                <p>正在检索知识库...</p>
            </div>
        `;
        
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        try {
            const formData = new FormData();
            formData.append('question', question);
            
            const response = await fetch('/api/ask', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            const loadingMessage = document.getElementById('loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            if (data.status === 'success') {
                let sourcesHtml = '';
                if (data.sources && data.sources.length > 0) {
                    sourcesHtml = '<div class="sources"><strong>参考来源:</strong>';
                    data.sources.forEach(source => {
                        sourcesHtml += `
                            <div class="source-item">
                                <strong>${escapeHtml(source.file_name)}</strong><br>
                                <small>${escapeHtml(source.summary)}</small>
                            </div>
                        `;
                    });
                    sourcesHtml += '</div>';
                }
                
                chatContainer.innerHTML += `
                    <div class="message system">
                        <p>${escapeHtml(data.answer).replace(/\n/g, '<br>')}</p>
                        ${sourcesHtml}
                    </div>
                `;
            } else {
                throw new Error(data.detail || '问答失败');
            }
        } catch (error) {
            const loadingMessage = document.getElementById('loading-message');
            if (loadingMessage) {
                loadingMessage.remove();
            }
            
            chatContainer.innerHTML += `
                <div class="message system">
                    <p style="color: #dc2626;">❌ ${escapeHtml(error.message)}</p>
                </div>
            `;
        }
        
        askBtn.disabled = false;
        askBtn.textContent = '发送';
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const refreshBtn = document.getElementById('refresh-btn');
    const rebuildBtn = document.getElementById('rebuild-btn');
    const documentsList = document.getElementById('documents-list');
    
    searchBtn.addEventListener('click', searchDocuments);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            searchDocuments();
        }
    });
    
    refreshBtn.addEventListener('click', loadDocuments);
    rebuildBtn.addEventListener('click', rebuildIndex);
    
    async function loadDocuments() {
        documentsList.innerHTML = '<p class="loading">加载中...</p>';
        
        try {
            const response = await fetch('/api/documents');
            const data = await response.json();
            
            if (data.status === 'success') {
                if (data.count === 0) {
                    documentsList.innerHTML = '<p class="no-documents">暂无文档</p>';
                } else {
                    documentsList.innerHTML = '';
                    data.documents.forEach(doc => {
                        documentsList.innerHTML += `
                            <div class="document-item">
                                <h4>${escapeHtml(doc.file_name)}</h4>
                                <p>${escapeHtml(doc.summary)}</p>
                            </div>
                        `;
                    });
                }
            } else {
                throw new Error(data.detail || '加载失败');
            }
        } catch (error) {
            documentsList.innerHTML = `<p class="status-message error">加载失败: ${escapeHtml(error.message)}</p>`;
        }
    }
    
    async function searchDocuments() {
        const query = searchInput.value.trim();
        if (!query) {
            loadDocuments();
            return;
        }
        
        documentsList.innerHTML = '<p class="loading">搜索中...</p>';
        
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                if (data.count === 0) {
                    documentsList.innerHTML = `<p class="no-documents">未找到包含 "${escapeHtml(query)}" 的文档</p>`;
                } else {
                    documentsList.innerHTML = `<p class="status-message success" style="margin: 10px;">找到 ${data.count} 个结果</p>`;
                    data.results.forEach(doc => {
                        documentsList.innerHTML += `
                            <div class="document-item">
                                <h4>${escapeHtml(doc.file_name)}</h4>
                                <p>${escapeHtml(doc.summary)}</p>
                            </div>
                        `;
                    });
                }
            } else {
                throw new Error(data.detail || '搜索失败');
            }
        } catch (error) {
            documentsList.innerHTML = `<p class="status-message error">搜索失败: ${escapeHtml(error.message)}</p>`;
        }
    }
    
    async function rebuildIndex() {
        if (!confirm('确定要重建索引吗？这将重新处理所有文档。')) {
            return;
        }
        
        documentsList.innerHTML = '<p class="loading">正在重建索引...</p>';
        
        try {
            const response = await fetch('/api/rebuild', {
                method: 'POST'
            });
            const data = await response.json();
            
            if (data.status === 'success') {
                documentsList.innerHTML = `<p class="status-message success">${data.message}</p>`;
                setTimeout(loadDocuments, 1000);
            } else {
                throw new Error(data.detail || '重建失败');
            }
        } catch (error) {
            documentsList.innerHTML = `<p class="status-message error">重建失败: ${escapeHtml(error.message)}</p>`;
        }
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
});