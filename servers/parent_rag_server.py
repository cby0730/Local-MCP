# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import pickle
from typing import List, Dict
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from langchain.retrievers import ParentDocumentRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.storage._lc_store import create_kv_docstore
from langchain.storage import InMemoryStore
from dotenv import load_dotenv
import os

load_dotenv()
EMBEDDING_MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "")
DB_DIR = os.getenv("DB_DIR", "")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "")
CHILD_CHUNK_SIZE = os.getenv("CHILD_CHUNK_SIZE", "")
CHILD_CHUNK_OVERLAP = os.getenv("CHILD_CHUNK_OVERLAP", "")
TOP_K = os.getenv("TOP_K", "")
DEVICE = os.getenv("DEVICE", "")
DOCUMENT_PATH = os.getenv("MARKITDOWN_OUTPUT_PATH", "")

# ---------- 自訂持久化的 InMemoryStore ----------
class PersistentInMemoryStore(InMemoryStore):
    def __init__(self, file_path: str):
        """
        功能: 初始化可持久化的 InMemoryStore。
        參數:
            file_path (str): 用於序列化與反序列化的檔案路徑。
        回傳:
            None
        """
        self.file_path = file_path
        self.store = self._load()

    def _load(self):
        """
        功能: 從檔案載入先前儲存的 store。
        參數:
            無
        回傳:
            dict: 載入的鍵值對儲存結構；若檔案不存在則回傳空 dict。
        """
        if os.path.exists(self.file_path):
            with open(self.file_path, "rb") as f:
                return pickle.load(f)
        return {}

    def _save(self):
        """
        功能: 將目前的 store 序列化後寫入檔案。
        參數:
            無
        回傳:
            None
        """
        with open(self.file_path, "wb") as f:
            pickle.dump(self.store, f)

    def mset(self, key_value_pairs):
        """
        功能: 批次寫入多組鍵值並立即持久化。
        參數:
            key_value_pairs (Iterable): 要寫入的鍵值對清單。
        回傳:
            None
        """
        super().mset(key_value_pairs)
        self._save()

    def mdelete(self, keys):
        """
        功能: 批次刪除多個鍵並立即持久化。
        參數:
            keys (Iterable): 要刪除的鍵列表。
        回傳:
            None
        """
        super().mdelete(keys)
        self._save()

# ---------- ParentRAGEngine ----------
class ParentRAGEngine:
    def __init__(
        self,
        *,
        embedding_model_path: str = EMBEDDING_MODEL_PATH,
        database_dir: str = DB_DIR,
        collection_name: str = COLLECTION_NAME,
        child_chunk_size: int = int(CHILD_CHUNK_SIZE),
        child_chunk_overlap: int = int(CHILD_CHUNK_OVERLAP),
        top_k: int = int(TOP_K),
        device: str = DEVICE,
    ):
        """
        功能: 建立 Parent RAG 引擎，初始化 embedding、向量資料庫、分割器與檢索器。
        參數:
            embedding_model_path (str): Embedding 模型路徑或名稱。
            database_dir       (str): 向量資料庫目錄。
            collection_name    (str): 資料集合名稱。
            child_chunk_size   (int): 子 chunk 大小。
            child_chunk_overlap(int): 子 chunk 重疊大小。
            top_k              (int): 檢索時的 top-K 數量。
            device             (str): 運算裝置（如 'cpu' 或 'cuda'）。
        回傳:
            None
        """
        self.top_k = top_k
        self._init_embeddings(embedding_model_path, device)
        self._init_vector_store(database_dir, collection_name)
        self._init_child_splitter(size=child_chunk_size, overlap=child_chunk_overlap)
        self._init_retriever()

    # ---------- private ----------
    def _init_embeddings(self, model_path: str, device: str):
        """
        功能: 初始化 HuggingFace Embeddings。
        參數:
            model_path (str): Embedding 模型路徑或名稱。
            device     (str): 運算裝置。
        回傳:
            None
        """
        self.embeddings = HuggingFaceEmbeddings(
            model_name=model_path,
            model_kwargs={"device": device},
            encode_kwargs={"normalize_embeddings": True},
        )

    def _init_vector_store(self, db_dir: str, collection: str):
        """
        功能: 初始化 Milvus 向量資料庫與持久化 docstore。
        參數:
            db_dir     (str): 資料庫目錄。
            collection (str): 集合名稱。
        回傳:
            None
        """
        os.makedirs(db_dir, exist_ok=True)
        uri = os.path.join(db_dir, f"{collection}.db")
        self.vector_store = Milvus(
            embedding_function=self.embeddings,
            collection_name=collection,
            connection_args={"uri": uri},
            index_params={"index_type": "FLAT", "metric_type": "L2"},
            auto_id=True,
        )

        # 父文件 docstore（可持久化）
        store_file = os.path.join(db_dir, f"{collection}.pkl")
        self.doc_store = create_kv_docstore(PersistentInMemoryStore(store_file))

    def _init_child_splitter(self, size: int, overlap: int):
        """
        功能: 初始化子文件分割器。
        參數:
            size    (int): chunk 大小。
            overlap (int): chunk 重疊大小。
        回傳:
            None
        """
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=overlap,
            separators=["\n\n", "\n", "。", "，", " "],
        )

    def _init_retriever(self):
        """
        功能: 建立 ParentDocumentRetriever 作為檢索器。
        參數:
            無
        回傳:
            None
        """
        self.retriever = ParentDocumentRetriever(
            vectorstore=self.vector_store,
            docstore=self.doc_store,
            child_splitter=self.child_splitter,
            search_kwargs={"k": self.top_k},
        )

    # ---------- public ----------
    def add_documents(self, docs: List[Document]) -> None:
        """
        功能: 新增文件至檢索器與向量資料庫。
        參數:
            docs (List[Document]): 要新增的文件列表。
        回傳:
            None
        """
        if docs:
            self.retriever.add_documents(docs)

    def retrieve(self, query: str) -> Dict[str, List[Document]]:
        """
        功能: 執行檢索，回傳父文件與子 chunk。
        參數:
            query (str): 查詢字串。
        回傳:
            Dict[str, List[Document]]: 
                'parent' -> 父文件列表，
                'child'  -> 子 chunk 列表。
        """
        parent_docs = self.retriever.invoke(query)
        child_docs = self.vector_store.similarity_search(query, k=self.top_k)

        return {"parent_documents": parent_docs, "child_documents": child_docs}
    

from mcp.server.fastmcp import FastMCP
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import os

mcp = FastMCP("ParentRAG")

ParentRAG = ParentRAGEngine()

@mcp.tool(description="從指定目錄添加文件到知識庫")
def add_documents(directory_path: str = None):
    """
    功能: 從指定目錄載入所有txt文件，並添加到ParentRAG知識庫
    參數: 
        directory_path (str, optional): 文件目錄路徑，默認使用環境變數DOCUMENT_PATH
    回傳:
        dict: 包含添加的文件數量和狀態信息
    """
    logger.info(f"Called add_documents with args: directory_path={directory_path}")
    # 使用提供的路徑或環境變數
    document_path = directory_path or DOCUMENT_PATH
    
    # 檢查路徑是否存在且為目錄
    if not document_path:
        return {"status": "error", "message": "未提供文件路徑，請指定路徑或設置MARKITDOWN_OUTPUT_PATH環境變數"}
    
    if not os.path.exists(document_path):
        return {"status": "error", "message": f"路徑不存在: {document_path}"}
    
    if not os.path.isdir(document_path):
        return {"status": "error", "message": f"{document_path} 不是有效目錄"}
    
    try:
        # 使用DirectoryLoader加載文件，啟用多線程和進度條
        loader = DirectoryLoader(
            document_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            use_multithreading=True,  # 啟用多線程
            show_progress=True,  # 顯示進度條
            max_concurrency=8  # 控制最大線程數量
        )

        documents = loader.load()
        
        if not documents:
            return {"status": "warning", "message": f"在 {document_path} 中未找到txt文件", "count": 0}
        
        ParentRAG.add_documents(documents)
        
        return {
            "status": "success", 
            "message": f"成功添加 {len(documents)} 個文件到知識庫", 
            "count": len(documents)
        }
        
    except Exception as e:
        return {"status": "error", "message": f"添加文件時發生錯誤: {str(e)}", "count": 0}

@mcp.tool(description="使用查詢語句從知識庫中檢索相關文件")
def retrieve(query: str):
    """
    功能: 根據查詢字串從知識庫中檢索相關文件
    參數:
        query (str): 查詢字串
    回傳:
        dict: 包含父文檔檢索結果的字典
    """
    logger.info(f"Called retrieve with args: query={query}")
    if not query or not query.strip():
        return {"status": "error", "message": "查詢字串不能為空"}
    
    try:
        result = ParentRAG.retrieve(query=query)
        
        return {
            "status": "success",
            "documents": result["parent_documents"],
            "count": len(result["parent_documents"])
        }
    except Exception as e:
        return {"status": "error", "message": f"檢索過程中發生錯誤: {str(e)}"}
    
if __name__ == "__main__":
    mcp.run(transport="stdio")