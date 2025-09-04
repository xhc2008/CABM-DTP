import os
from typing import Dict, Any

# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "读取文本或代码文件的内容",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要读取的文件的路径"
                },
                "start_line": {
                    "type": "integer",
                    "description": "起始行号（可选，从1开始），如果未指定则从文件开头开始",
                },
                "end_line": {
                    "type": "integer",
                    "description": "终止行号（可选），如果未指定则读到文件结尾",
                }
            },
            "required": ["file_path"]
        }
    }
}

def read_file(file_path: str, start_line: int = None, end_line: int = None) -> Dict[str, Any]:
    """
    读取文本文件的内容
    
    Args:
        file_path: 要读取的文本文件的路径
        start_line: 起始行号（可选，从1开始），如果未指定则从文件开头开始
        end_line: 终止行号（可选），如果未指定则读到文件结尾
        
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
        
        # 安全检查：限制文件大小（例如最大100KB）
        file_size = os.path.getsize(file_path)
        if file_size > 100 * 1024 :  # 100KB
            return {
                "status": "error",
                "message": f"文件过大（{file_size}字节），超过100KB限制",
                "content": ""
            }
        
        # 处理参数有效性
        if start_line is not None and start_line < 1:
            start_line = None
        
        if end_line is not None and end_line < 1:
            end_line = None
        
        # 如果起始行和终止行都指定但起始行大于终止行，则调换两者
        if start_line is not None and end_line is not None and start_line > end_line:
            start_line, end_line = end_line, start_line
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            total_lines = len(lines)
            
            # 处理行号参数
            if start_line is None:
                start_line = 1
            if end_line is None:
                end_line = total_lines
            
            # 确保行号在有效范围内
            start_line = max(1, min(start_line, total_lines))
            end_line = max(1, min(end_line, total_lines))
            
            # 如果起始行大于终止行（可能由于调整后），再次调换
            if start_line > end_line:
                start_line, end_line = end_line, start_line
            
            # 提取指定行范围的内容（注意：列表索引从0开始，行号从1开始）
            selected_lines = lines[start_line-1:end_line]
            content = ''.join(selected_lines)
            
            lines_read = len(selected_lines)
        
        return {
            "status": "success",
            "file_path": file_path,
            "content": content,
            "start_line": start_line,
            "end_line": end_line,
            "lines_read": lines_read,
            "total_lines": total_lines,
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
read_file.is_tool = True
read_file.tool_definition = tool_definition