import os
from typing import Dict, Any

# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "read_text_file",
        "description": "读取文本文件的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要读取的文本文件的路径"
                },
                "max_lines": {
                    "type": "integer",
                    "description": "最大读取行数（可选），如果未指定则读取全部内容",
                    "minimum": 1
                }
            },
            "required": ["file_path"]
        }
    }
}

def read_text_file(file_path: str, max_lines: int = None) -> Dict[str, Any]:
    """
    读取文本文件的内容
    
    Args:
        file_path: 要读取的文本文件的路径
        max_lines: 最大读取行数（可选），如果未指定则读取全部内容
        
    Returns:
        包含文件内容和状态的字典
    """
    try:
        # 安全检查：验证文件路径是否合法
        if not os.path.exists(file_path):
            return {
                "status": "error",
                "message": f"文件不存在: {file_path}",
                "content": ""
            }
        
        # 安全检查：确保是文件而不是目录
        if not os.path.isfile(file_path):
            return {
                "status": "error",
                "message": f"路径不是文件: {file_path}",
                "content": ""
            }
        
        # 安全检查：限制文件大小（例如最大10MB）
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            return {
                "status": "error",
                "message": f"文件过大（{file_size}字节），超过10MB限制",
                "content": ""
            }
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            if max_lines:
                # 读取指定行数
                lines = []
                for i, line in enumerate(file):
                    if i >= max_lines:
                        break
                    lines.append(line)
                content = ''.join(lines)
            else:
                # 读取全部内容
                content = file.read()
        
        return {
            "status": "success",
            "file_path": file_path,
            "content": content,
            "lines_read": len(content.splitlines()) if content else 0,
            "total_size": file_size
        }
        
    except UnicodeDecodeError:
        return {
            "status": "error",
            "message": "文件不是有效的文本文件（编码问题）",
            "content": ""
        }
    except PermissionError:
        return {
            "status": "error",
            "message": "没有读取文件的权限",
            "content": ""
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"读取文件时发生异常: {str(e)}",
            "content": ""
        }

# 标记为工具函数
read_text_file.is_tool = True
read_text_file.tool_definition = tool_definition