# 文件位置: ./tools/retrieve_notes.py
import os
import sys
from typing import Dict, Any, List

# 添加services目录到路径，以便导入memory模块
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from services.memory import ChatHistoryVectorDB
from config import RAG_CONFIG

# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "read_notes",
        "description": "再次从助手的笔记中检索相关信息",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "检索关键词或查询语句"
                },
                "top_k": {
                    "type": "integer",
                    "description": "返回的最相关结果数量，默认为5",
                    "minimum": 1,
                    "maximum": 20
                }
            },
            "required": ["query"]
        }
    }
}

# 全局笔记数据库实例
_notes_db = None

def get_notes_db():
    """获取全局笔记数据库实例"""
    global _notes_db
    if _notes_db is None:
        # 初始化笔记向量数据库
        _notes_db = ChatHistoryVectorDB(
            RAG_config=RAG_CONFIG,
            db_name="notes"
        )
        # 加载现有笔记数据
        notes_file = os.path.join('data', 'notes.json')
        if os.path.exists(notes_file):
            _notes_db.load_from_file(notes_file)
        else:
            print(f"警告: 笔记文件 {notes_file} 不存在，将创建空数据库")
    return _notes_db

def read_notes(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    从笔记数据库中检索相关信息
    
    Args:
        query: 检索关键词或查询语句
        top_k: 返回的最相关结果数量，默认为5
        
    Returns:
        包含检索结果和状态的字典
    """
    try:
        # 获取笔记数据库实例
        notes_db = get_notes_db()
        
        # 执行检索
        results = notes_db.search(query, top_k=top_k, timeout=10)
        
        # 格式化结果
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_results.append({
                "rank": i,
                "content": result['text'],
                # 可以添加更多元数据，如相似度分数等
            })
        
        return {
            "status": "success",
            "query": query,
            "top_k": top_k,
            "results": formatted_results,
            "total_results": len(formatted_results)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"检索笔记时发生错误: {str(e)}",
            "results": []
        }

# 标记为工具函数
read_notes.is_tool = True
read_notes.tool_definition = tool_definition