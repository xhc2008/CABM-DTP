import os
from typing import Dict, Any

# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "modify_file",
        "description": "修改文本或代码文件的内容，替换指定的文本块",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "要修改的文件的路径（相对或绝对）"
                },
                "text_to_replace": {
                    "type": "string",
                    "description": "需要被替换的文本块"
                },
                "replacement_text": {
                    "type": "string",
                    "description": "替换后的文本块"
                },
                "replace_all": {
                    "type": "boolean",
                    "description": "是否全部替换，如果为False则只替换第一个找到的文本块，默认为False",
                }
            },
            "required": ["file_path", "text_to_replace", "replacement_text"]
        }
    }
}

def modify_file(file_path: str, text_to_replace: str, replacement_text: str, replace_all: bool = False) -> Dict[str, Any]:
    """
    修改文本文件的内容，替换指定的文本块
    
    Args:
        file_path: 要修改的文本文件的路径
        text_to_replace: 需要被替换的文本块
        replacement_text: 替换后的文本块
        replace_all: 是否全部替换，如果为False则只替换第一个找到的文本块，默认为False
        
    Returns:
        包含修改结果和状态的字典
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
        if file_size > 100 * 1024:  # 100KB
            return {
                "status": "error",
                "message": f"文件过大（{file_size}字节），超过100KB限制",
                "content": ""
            }
        
        # 检查写入权限
        if not os.access(file_path, os.W_OK):
            return {
                "status": "error",
                "message": f"没有修改文件的权限: {file_path}",
                "content": ""
            }
        
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            original_content = file.read()
        
        # 检查要替换的文本是否存在
        if text_to_replace not in original_content:
            return {
                "status": "error",
                "message": f"文件中未找到要替换的文本: '{text_to_replace}'",
                "content": original_content
            }
        
        # 执行替换操作
        if replace_all:
            new_content = original_content.replace(text_to_replace, replacement_text)
            replacements_count = original_content.count(text_to_replace)
        else:
            new_content = original_content.replace(text_to_replace, replacement_text, 1)
            replacements_count = 1
        
        # 写入修改后的内容
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        return {
            "status": "success",
            "file_path": file_path,
            "replacements_count": replacements_count,
            "replaced_all": replace_all,
            "original_content_length": len(original_content),
            "new_content_length": len(new_content),
            "message": f"成功替换了 {replacements_count} 处文本"
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
            "message": "没有修改文件的权限",
            "content": ""
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"修改文件时发生异常: {str(e)}",
            "content": ""
        }

# 标记为工具函数
modify_file.is_tool = True
modify_file.tool_definition = tool_definition