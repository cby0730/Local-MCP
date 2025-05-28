from mcp.server.fastmcp import FastMCP
import sqlite3
from typing import List, Dict, Any
import os # 新增匯入
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化MCP服務器和SQLite資料庫
mcp = FastMCP("Database")
DB_PATH = "./database/example.db"

def get_connection():  
    """獲取資料庫連線"""
    # 確保資料庫目錄存在
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 設置結果以字典形式返回
    return conn

@mcp.tool()
def create_table(table_name: str, columns: List[str]) -> str:
    """
    建立新的資料表
    
    參數:
    - table_name: 資料表名稱
    - columns: 欄位定義列表，例如 ["id INTEGER PRIMARY KEY", "name TEXT", "age INTEGER"]
    
    返回:
    - 成功訊息
    """
    logger.info(f"Called create_table with args: table_name={table_name}, columns={columns}")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 建立SQL語句
        columns_str = ", ".join(columns)
        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
        
        return f"成功建立資料表 '{table_name}'"
    except Exception as e:
        return f"建立資料表失敗: {str(e)}"

@mcp.tool()
def insert_data(table_name: str, data: Dict[str, Any]) -> str:
    """
    向資料表插入一筆資料
    
    參數:
    - table_name: 資料表名稱
    - data: 要插入的資料，格式為 {"column_name": value}
    
    返回:
    - 成功訊息
    """
    logger.info(f"Called insert_data with args: table_name={table_name}, data={data}")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        values = tuple(data.values())
        
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.execute(insert_sql, values)
        
        conn.commit()
        conn.close()
        
        return f"成功插入資料到 '{table_name}'"
    except Exception as e:
        return f"插入資料失敗: {str(e)}"

@mcp.tool()
def query_data(table_name: str, conditions: str = "", limit: int = 100) -> List[Dict[str, Any]]:
    """
    查詢資料表中的資料
    
    參數:
    - table_name: 資料表名稱
    - conditions: WHERE子句條件 (可選)，例如 "age > 18 AND name LIKE 'A%'"
    - limit: 返回結果的最大數量
    
    返回:
    - 符合條件的資料列表
    """
    logger.info(f"Called query_data with args: table_name={table_name}, conditions={conditions}, limit={limit}")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query_sql = f"SELECT * FROM {table_name}"
        if conditions:
            query_sql += f" WHERE {conditions}"
        query_sql += f" LIMIT {limit}"
        
        cursor.execute(query_sql)
        results = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return results
    except Exception as e:
        return [{"error": f"查詢失敗: {str(e)}"}]

@mcp.tool()
def update_data(table_name: str, data: Dict[str, Any], condition: str) -> str:
    """
    更新資料表中的資料
    
    參數:
    - table_name: 資料表名稱
    - data: 要更新的資料，格式為 {"column_name": new_value}
    - condition: WHERE子句條件，例如 "id = 1"
    
    返回:
    - 成功訊息
    """
    logger.info(f"Called update_data with args: table_name={table_name}, data={data}, condition={condition}")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = tuple(data.values())
        
        update_sql = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        cursor.execute(update_sql, values)
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return f"成功更新 {affected_rows} 筆資料在 '{table_name}'"
    except Exception as e:
        return f"更新資料失敗: {str(e)}"

@mcp.tool()
def delete_data(table_name: str, condition: str) -> str:
    """
    從資料表中刪除資料
    
    參數:
    - table_name: 資料表名稱
    - condition: WHERE子句條件，例如 "id = 1"
    
    返回:
    - 成功訊息
    """
    logger.info(f"Called delete_data with args: table_name={table_name}, condition={condition}")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        delete_sql = f"DELETE FROM {table_name} WHERE {condition}"
        cursor.execute(delete_sql)
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return f"成功刪除 {affected_rows} 筆資料從 '{table_name}'"
    except Exception as e:
        return f"刪除資料失敗: {str(e)}"

@mcp.tool()
def get_table_schema(table_name: str) -> List[Dict[str, Any]]:
    """
    取得資料表的結構資訊
    
    參數:
    - table_name: 資料表名稱
    
    返回:
    - 資料表結構資訊列表
    """
    logger.info(f"Called get_table_schema with args: table_name={table_name}")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        schema_sql = f"PRAGMA table_info({table_name})"
        cursor.execute(schema_sql)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    except Exception as e:
        return [{"error": f"取得資料表結構失敗: {str(e)}"}]

@mcp.tool()
def list_tables() -> List[str]:
    """列出資料庫中的所有資料表"""
    logger.info("Called list_tables")
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row['name'] for row in cursor.fetchall()]
        
        conn.close()
        return tables
    except Exception as e:
        return [f"列出資料表失敗: {str(e)}"]

def test_database_operations():
    """測試資料庫操作函式"""
    print("開始資料庫操作測試...\n")

    # 清理：如果舊的資料庫檔案存在，先刪除它以便從乾淨的狀態開始測試
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"已刪除舊的資料庫檔案: {DB_PATH}")

    # 1. 測試建立資料表
    table_name = "users"
    columns = ["id INTEGER PRIMARY KEY AUTOINCREMENT", "name TEXT NOT NULL", "email TEXT UNIQUE"]
    print(f"測試 create_table('{table_name}', {columns}):")
    result = create_table(table_name, columns)
    print(f"結果: {result}\n")

    # 2. 測試插入資料
    user1_data = {"name": "Alice", "email": "alice@example.com"}
    print(f"測試 insert_data('{table_name}', {user1_data}):")
    result = insert_data(table_name, user1_data)
    print(f"結果: {result}\n")

    user2_data = {"name": "Bob", "email": "bob@example.com"}
    print(f"測試 insert_data('{table_name}', {user2_data}):")
    result = insert_data(table_name, user2_data)
    print(f"結果: {result}\n")

    # 嘗試插入重複 email (應失敗)
    user3_data_conflict = {"name": "Charlie", "email": "alice@example.com"}
    print(f"測試 insert_data('{table_name}', {user3_data_conflict}) (預期失敗):")
    result = insert_data(table_name, user3_data_conflict)
    print(f"結果: {result}\n")

    # 3. 測試查詢資料
    print(f"測試 query_data('{table_name}'):")
    results = query_data(table_name)
    print(f"結果: {results}\n")

    print(f"測試 query_data('{table_name}', conditions=\"name = 'Alice'\"):")
    results = query_data(table_name, conditions="name = 'Alice'")
    print(f"結果: {results}\n")

    # 4. 測試更新資料
    update_values = {"email": "alice_updated@example.com"}
    condition = "name = 'Alice'"
    print(f"測試 update_data('{table_name}', {update_values}, '{condition}'):")
    result = update_data(table_name, update_values, condition)
    print(f"結果: {result}\n")

    # 驗證更新
    print(f"測試 query_data('{table_name}', conditions=\"name = 'Alice'\") (驗證更新):")
    results = query_data(table_name, conditions="name = 'Alice'")
    print(f"結果: {results}\n")

    # 5. 測試取得資料表結構
    print(f"測試 get_table_schema('{table_name}'):")
    schema = get_table_schema(table_name)
    print(f"結果: {schema}\n")

    # 6. 測試列出所有資料表
    print("測試 list_tables():")
    tables = list_tables()
    print(f"結果: {tables}\n")

    # 7. 測試刪除資料
    delete_condition = "name = 'Bob'"
    print(f"測試 delete_data('{table_name}', '{delete_condition}'):")
    result = delete_data(table_name, delete_condition)
    print(f"結果: {result}\n")

    # 驗證刪除
    print(f"測試 query_data('{table_name}') (驗證刪除):")
    results = query_data(table_name)
    print(f"結果: {results}\n")
    
    print("資料庫操作測試完成。")
    print(f"若要清理，請手動刪除資料庫檔案: {DB_PATH}")


if __name__ == "__main__":
    mcp.run(transport="stdio") # 註解掉原來的啟動方式
    # test_database_operations() # 呼叫測試函式

