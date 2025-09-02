import subprocess
import json
import os
import tempfile
from typing import Dict, Any

# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "run_python",
        "description": "创建一个Python程序并执行，等待执行完毕后获取输出",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Python文件的路径（包含文件名，可以是相对或绝对路径）"
                },
                "file_content": {
                    "type": "string",
                    "description": "Python文件的内容"
                }
            },
            "required": ["file_path", "file_content"]
        }
    }
}

def run_python(file_path: str, file_content: str) -> Dict[str, Any]:
    """
    创建Python程序并执行，等待执行完毕后获取输出
    
    Args:
        file_path: Python文件的路径
        file_content: Python文件的内容
        
    Returns:
        包含执行结果和状态的字典，符合MCP工具调用返回格式
    """
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        # 写入Python文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        
        # 执行Python程序
        result = subprocess.run(
            ['python', file_path], 
            capture_output=True, 
            text=True,
            timeout=60  # 设置超时防止长时间运行
        )
        
        # 构建结果
        execution_result = {
            "file_path": file_path,
            "return_code": result.returncode,
            "output": result.stdout,
            "error": result.stderr
        }
        
        # 返回MCP标准格式的响应
        result_text = f"Python程序执行结果:\n\n"
        result_text += f"文件路径: {file_path}\n"
        result_text += f"返回码: {result.returncode}\n"
        
        if result.stdout:
            result_text += f"输出:\n{result.stdout}\n"
        
        if result.stderr:
            result_text += f"错误:\n{result.stderr}\n"
        
        if result.returncode == 0:
            result_text += "\n✅ 程序执行成功"
        else:
            result_text += "\n❌ 程序执行失败"
        
        return {
            "content": [{
                "type": "text", 
                "text": result_text
            }]
        }
        
    except subprocess.TimeoutExpired:
        return {
            "content": [{
                "type": "text", 
                "text": f"Python程序执行超时: {file_path}"
            }]
        }
    except Exception as e:
        return {
            "content": [{
                "type": "text", 
                "text": f"执行Python程序时发生异常: {str(e)}"
            }]
        }

# 标记为工具函数
run_python.is_tool = True
run_python.tool_definition = tool_definition