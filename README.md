# MCPTest 專案

這是一個基於Model Context Protocol (MCP)的智能工具型系統，通過整合多種功能伺服器，實現了一個多面的AI助手系統。該系統可以執行數學運算、檔案系統操作、資料庫操作、文檔處理以及基於RAG（檢索增強生成）的問答功能。

## 目錄
- [專案簡介](#專案簡介)
- [系統架構](#系統架構)
- [功能特色](#功能特色)
- [安裝指南](#安裝指南)
- [使用方法](#使用方法)
- [伺服器模組](#伺服器模組)
- [擴充功能](#擴充功能)
- [問題排解](#問題排解)
- [代碼結構](#代碼結構)

## 專案簡介

MCPTest是一個展示如何使用Model Context Protocol (MCP)架構構建複雜AI系統的專案。通過將各種功能劃分為獨立的 MCP 伺服器模組，並使用 MCP 客戶端進行協調，系統可以靈活地整合多種工具和資源，提供更靈活的AI助手功能。

本專案特別側重於如何使用MCP框架整合RAG（檢索增強生成）技術，使AI助手能夠基於知識庫回答用戶問題，同時還提供了檔案系統操作、資料庫管理和數學計算等功能。

## 系統架構

系統主要由以下部分組成：

1. **客戶端 (client.py)**：
   - 整合所有伺服器模組
   - 使用langgraph的ReAct代理架構
   - 處理用戶輸入和系統回應
   - 維護對話歷史

2. **伺服器模組**：
   - `math_server.py`: 提供數學計算功能
   - `db_server.py`: 提供SQLite資料庫操作功能
   - `filesystem_server.py`: 提供檔案系統操作功能
   - `markitdown_server.py`: 提供Markdown處理功能
   - `parent_rag_server.py`: 提供基於ParentDocumentRetriever的RAG功能
   - `test_server.py`: 提供測試功能

3. **文檔存儲**：
   - `documents/`: 存放知識庫文檔

## 功能特色

- **多模組整合**：通過MCP協議，無縫整合多個功能伺服器
- **對話記憶**：維護對話歷史，實現連續對話體驗
- **數學運算**：支援基本數學運算和三角函數計算
- **資料庫管理**：支援SQLite資料庫的建立、查詢和管理
- **檔案系統操作**：提供檔案和目錄的創建、讀取、修改和刪除功能
- **文檔處理**：支援Markitdown文檔的處理和轉換
- **RAG問答**：基於ParentDocumentRetriever的知識庫問答功能
- **彈性擴充**：易於添加新的功能伺服器模組

## 安裝指南

### 安裝步驟

1. 克隆專案：
   ```bash
   git clone [專案Git URL]
   cd MCPTest
   ```

2. 創建並激活虛擬環境（可選但推薦）：
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. 安裝依賴：
   ```bash
   pip install -r requirements.txt
   ```

4. 配置環境變數（可能需要修改以下）：
   ```
   LLM_URL=http://IP:Port/v1 (不可包含/chat/completions)
   LLM_MODEL_PATH=Path/to/llm/model
   EMBEDDING_MODEL_PATH=Path/to/embedding/model
   DB_DIR=./database
   COLLECTION_NAME=your_collection_name
   MARKITDOWN_OUTPUT_PATH=./documents
   ```

5. 啟動本地LLM服務（可選）：
   ```bash
   ./vllm.sh
   ```

## 使用方法

1. 啟動客戶端：
   ```bash
   python client.py
   ```

2. 開始與AI助手對話：
   ```
   User > 你好，請告訴我你能做什麼？
   ```

3. 使用特定功能：
   ```
   User > 請計算 5 乘以 3 加上 10 等於多少？
   User > 請創建一個名為'users'的資料表，包含id、name和age欄位
   User > 請幫我列出當前目錄下的檔案
   User > 基於我的文件回答：什麼是RAG技術？
   ```

4. 退出系統：
   ```
   User > q
   ```

## 伺服器模組

### 1. 數學伺服器 (math_server.py)
提供以下數學功能：
- 加法（add）
- 減法（subtract）
- 乘法（multiply）
- 除法（divide）
- 正弦函數（sin）
- 餘弦函數（cos）
- 其他數學運算

### 2. 資料庫伺服器 (db_server.py)
提供SQLite資料庫操作：
- 建立資料表
- 插入資料
- 查詢資料
- 更新資料
- 刪除資料
- 執行自定義SQL

### 3. 檔案系統伺服器 (filesystem_server.py)
提供檔案系統操作：
- 列出目錄內容
- 創建目錄
- 讀取檔案
- 寫入檔案
- 移動/重命名檔案
- 刪除檔案/目錄

### 4. Markdown處理伺服器 (markitdown_server.py)
提供Markitdown文檔處理功能：
- 讀取多種格式的單一檔案，轉換成Markdown格式
- 讀取目錄底下所有檔案，轉換成Markdown格式

### 5. RAG伺服器 (parent_rag_server.py)
基於知識庫的問答功能：
- 文檔加載與分塊 && 向量嵌入與存儲
- 文檔檢索

### 6. 測試伺服器 (test_server.py)
提供測試功能，方便系統開發和除錯。

## 擴充功能

要添加新的伺服器模組，請按照以下步驟操作：

1. 在`servers/`目錄中創建新的伺服器檔案，例如`my_new_server.py`
2. 使用MCP架構實現功能 (建議額外加入logger，清楚知道使用了那些工具):
   ```python
   from mcp.server.fastmcp import FastMCP
   
   mcp = FastMCP("MyNewService")
   
   @mcp.tool()
   def my_new_function(param1: str, param2: int) -> str:
       """功能描述"""
       return f"結果: {param1}, {param2}"
   ```

3. 在`client.py`中註冊新伺服器:
   ```python
   "my_new_service": {
       "command": "python",
       "args": ["servers/my_new_server.py"],
       "transport": "stdio",
   }
   ```

## 問題排解

### 常見問題

1. **出現錯誤('str' has no attribution model_dump())**
   - 檢查.env中的`LLM_URL`是否正確
   - 去除/chat/completions，保持結尾只有/v1

## 代碼結構

```
MCPTest/
├── client.py              # 主客戶端
├── requirements.txt       # 依賴包
├── vllm.sh                # LLM服務啟動腳本
├── documents/             # 知識庫文檔
├── Experiments/           # 實驗記錄
└── servers/               # 伺服器模組
    ├── db_server.py       # 資料庫伺服器
    ├── filesystem_server.py # 檔案系統伺服器
    ├── markitdown_server.py # Markdown處理伺服器
    ├── math_server.py     # 數學運算伺服器
    ├── parent_rag_server.py # RAG伺服器
    └── test_server.py     # 測試伺服器
```
