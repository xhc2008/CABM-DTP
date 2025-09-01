import subprocess
import json
from typing import Dict, Any, List, Union

# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "execute_command_async",
        "description": "在cmd中连续执行一条或多条指令，不等待执行完成，不获取输出",
        "parameters": {
            "type": "object",
            "properties": {
                "commands": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要连续执行的一条或多条命令"
                }
            },
            "required": ["commands"]
        }
    }
}

def execute_command_async(commands: Union[List[str], str]) -> Dict[str, Any]:
    """
    在cmd中连续执行一条或多条指令，不等待执行完成，不获取反馈
    
    Args:
        commands: 要连续执行的一条或多条命令
        
    Returns:
        包含执行状态的字典，符合MCP工具调用返回格式
    """
    # 如果传入的是单个字符串，转换为列表
    if isinstance(commands, str):
        commands = [commands]
    
    launched_count = 0
    
    try:
        for command in commands:
            # 安全限制：检查命令是否包含潜在危险的字符或命令（暂时关闭）
            dangerous_patterns = [
            #    "&&", "||", "|", ">", "<", "`", "$", "(", ")", "{", "}", 
            #    "[", "]", ";", "sudo", "admin", "root", "chmod", "chown",
            #    "rm", "del", "format", "mkfs", "dd", "shutdown", "reboot"
            ]
            
            for pattern in dangerous_patterns:
                if pattern in command:
                    # 返回MCP标准格式的错误响应
                    return {
                        "content": [{
                            "type": "text", 
                            "text": f"命令包含潜在危险模式: {pattern}，已停止执行"
                        }]
                    }
            
            # 使用Popen启动进程，不等待完成
            try:
                subprocess.Popen(
                    command, 
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    # 分离进程，使其在父进程退出后继续运行
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                )
                launched_count += 1
                
            except Exception as e:
                # 返回MCP标准格式的错误响应
                return {
                    "content": [{
                        "type": "text", 
                        "text": f"启动命令时发生异常: {str(e)}"
                    }]
                }
                
    except Exception as e:
        # 返回MCP标准格式的错误响应
        return {
            "content": [{
                "type": "text", 
                "text": f"处理命令时发生异常: {str(e)}"
            }]
        }
    
    # 构建符合MCP标准的返回格式
    result_text = f"已成功启动 {launched_count}/{len(commands)} 个命令\n"
    result_text += "这些命令将在后台继续执行，不会返回输出结果"
    
    # 返回MCP标准格式的成功响应
    return {
        "content": [{
            "type": "text", 
            "text": result_text
        }]
    }

# 标记为工具函数
execute_command_async.is_tool = True
execute_command_async.tool_definition = tool_definition