from mcp.server.fastmcp import FastMCP
import os
import shutil
import datetime
from typing import List, Dict, Any, Optional
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化MCP服務器
mcp = FastMCP("FileSystem")

@mcp.tool()
def list_directory(path: str = ".") -> List[Dict[str, Any]]:
    """
    列出指定目錄中的檔案和子目錄
    
    參數:
    - path: 要列出內容的目錄路徑，預設為當前目錄
    
    返回:
    - 目錄內容的詳細資訊列表
    """
    logger.info(f"Called list_directory with args: path={path}")
    try:
        items = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            item_stat = os.stat(item_path)
            items.append({
                "name": item,
                "path": os.path.abspath(item_path),
                "is_directory": os.path.isdir(item_path),
                "size_bytes": item_stat.st_size,
                "modified_time": datetime.datetime.fromtimestamp(item_stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                "created_time": datetime.datetime.fromtimestamp(item_stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            })
        return items
    except Exception as e:
        return [{"error": str(e)}]

@mcp.tool()
def create_directory(path: str) -> str:
    """
    創建新目錄
    
    參數:
    - path: 要創建的目錄路徑
    
    返回:
    - 成功或失敗訊息
    """
    logger.info(f"Called create_directory with args: path={path}")
    try:
        os.makedirs(path, exist_ok=True)
        return f"成功創建目錄: {path}"
    except Exception as e:
        return f"創建目錄失敗: {str(e)}"

@mcp.tool()
def check_exists(path: str) -> Dict[str, Any]:
    """
    檢查檔案或目錄是否存在
    
    參數:
    - path: 要檢查的路徑
    
    返回:
    - 檔案/目錄的存在狀態和類型
    """
    logger.info(f"Called check_exists with args: path={path}")
    exists = os.path.exists(path)
    result = {
        "exists": exists,
        "type": None,
        "absolute_path": None
    }
    
    if exists:
        result["absolute_path"] = os.path.abspath(path)
        if os.path.isdir(path):
            result["type"] = "directory"
        elif os.path.isfile(path):
            result["type"] = "file"
        else:
            result["type"] = "other"
            
    return result

@mcp.tool()
def get_file_info(path: str) -> Dict[str, Any]:
    """
    獲取檔案或目錄的詳細資訊
    
    參數:
    - path: 檔案或目錄的路徑
    
    返回:
    - 檔案或目錄的詳細資訊
    """
    logger.info(f"Called get_file_info with args: path={path}")
    try:
        if not os.path.exists(path):
            return {"error": f"路徑不存在: {path}"}
            
        stat_info = os.stat(path)
        info = {
            "name": os.path.basename(path),
            "path": os.path.abspath(path),
            "size_bytes": stat_info.st_size,
            "is_directory": os.path.isdir(path),
            "is_file": os.path.isfile(path),
            "created_time": datetime.datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
            "modified_time": datetime.datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            "accessed_time": datetime.datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        if os.path.isdir(path):
            info["item_count"] = len(os.listdir(path))
            
        return info
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def delete_item(path: str, recursive: bool = False) -> str:
    """
    刪除檔案或目錄
    
    參數:
    - path: 要刪除的檔案或目錄路徑
    - recursive: 若為目錄，是否遞迴刪除其內容
    
    返回:
    - 成功或失敗訊息
    """
    logger.info(f"Called delete_item with args: path={path}, recursive={recursive}")
    try:
        if not os.path.exists(path):
            return f"路徑不存在: {path}"
            
        if os.path.isfile(path):
            os.remove(path)
            return f"成功刪除檔案: {path}"
        elif os.path.isdir(path):
            if recursive:
                shutil.rmtree(path)
                return f"成功刪除目錄及其內容: {path}"
            else:
                os.rmdir(path)
                return f"成功刪除空目錄: {path}"
        else:
            return f"未知的檔案類型: {path}"
    except Exception as e:
        return f"刪除失敗: {str(e)}"

@mcp.tool()
def move_or_rename(source_path: str, destination_path: str) -> str:
    """
    移動或重命名檔案/目錄
    
    參數:
    - source_path: 原始檔案或目錄路徑
    - destination_path: 目標檔案或目錄路徑
    
    返回:
    - 成功或失敗訊息
    """
    logger.info(f"Called move_or_rename with args: source_path={source_path}, destination_path={destination_path}")
    try:
        if not os.path.exists(source_path):
            return f"源路徑不存在: {source_path}"
            
        shutil.move(source_path, destination_path)
        return f"成功將 {source_path} 移動/重命名為 {destination_path}"
    except Exception as e:
        return f"移動/重命名失敗: {str(e)}"

@mcp.tool()
def copy_item(source_path: str, destination_path: str) -> str:
    """
    複製檔案或目錄
    
    參數:
    - source_path: 原始檔案或目錄路徑
    - destination_path: 目標檔案或目錄路徑
    
    返回:
    - 成功或失敗訊息
    """
    logger.info(f"Called copy_item with args: source_path={source_path}, destination_path={destination_path}")
    try:
        if not os.path.exists(source_path):
            return f"源路徑不存在: {source_path}"
            
        if os.path.isfile(source_path):
            shutil.copy2(source_path, destination_path)
            return f"成功複製檔案: {source_path} 到 {destination_path}"
        elif os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
            return f"成功複製目錄: {source_path} 到 {destination_path}"
        else:
            return f"未知的檔案類型: {source_path}"
    except Exception as e:
        return f"複製失敗: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="stdio")
