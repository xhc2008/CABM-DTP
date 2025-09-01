import subprocess
import json
from typing import Dict, Any, List, Union

# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "execute_command",
        "description": "在cmd中执行一条或多条指令，并等待执行完毕后获取输出",
        "parameters": {
            "type": "object",
            "properties": {
                "commands": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "要执行的一条或多条命令"
                }
            },
            "required": ["commands"]
        }
    }
}

def execute_command(commands: Union[List[str], str]) -> Dict[str, Any]:
    """
    在cmd中执行一条或多条指令
    
    Args:
        commands: 要执行的一条或多条命令
        
    Returns:
        包含执行结果和状态的字典，符合MCP工具调用返回格式
    """
    # 如果传入的是单个字符串，转换为列表
    if isinstance(commands, str):
        commands = [commands]
    
    results = []
    all_success = True
    
    try:
        for i, command in enumerate(commands):
            # 安全限制：检查命令是否包含潜在危险的字符或命令（暂时关闭）
            dangerous_patterns = [
            #    "&&", "||", "|", ">", "<", "`", "$", "(", ")", "{", "}", 
            #    "[", "]", ";", "sudo", "admin", "root", "chmod", "chown",
            #    "rm", "del", "format", "mkfs", "dd", "shutdown", "reboot"
            ]
            
            for pattern in dangerous_patterns:
                if pattern in command:
                    result = {
                        "command": command,
                        "status": "error",
                        "message": f"命令包含潜在危险模式: {pattern}",
                        "output": "",
                        "error": ""
                    }
                    results.append(result)
                    all_success = False
                    continue
            
            # 执行命令
            try:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=30  # 设置超时防止长时间运行
                )
                
                # 确保输出内容被正确转义
                def safe_string(s):
                    return json.dumps(s)[1:-1] if s else s
                
                command_result = {
                    "command": command,
                    "status": "success" if result.returncode == 0 else "error",
                    "return_code": result.returncode,
                    "output": safe_string(result.stdout),
                    "error": safe_string(result.stderr)
                }
                
                if result.returncode != 0:
                    all_success = False
                
                results.append(command_result)
                
            except subprocess.TimeoutExpired:
                result = {
                    "command": command,
                    "status": "error",
                    "message": "命令执行超时",
                    "output": "",
                    "error": ""
                }
                results.append(result)
                all_success = False
                
    except Exception as e:
        # 返回MCP标准格式的错误响应
        return {
            "content": [{
                "type": "text", 
                "text": f"执行命令时发生异常: {str(e)}"
            }]
        }
    
    # 构建符合MCP标准的返回格式
    result_text = "命令执行结果:\n\n"
    for i, result in enumerate(results, 1):
        result_text += f"命令 {i}: {result['command']}\n"
        result_text += f"状态: {result['status']}\n"
        result_text += f"返回码: {result.get('return_code', 'N/A')}\n"
        
        if result.get('output'):
            result_text += f"输出:\n{result['output']}\n"
        
        if result.get('error'):
            result_text += f"错误:\n{result['error']}\n"
        
        if result.get('message'):
            result_text += f"消息: {result['message']}\n"
        
        result_text += "-" * 50 + "\n"
    
    if all_success:
        result_text += "\n✅ 所有命令执行成功"
    else:
        result_text += "\n❌ 部分或全部命令执行失败"
    
    # 返回MCP标准格式的成功响应
    return {
        "content": [{
            "type": "text", 
            "text": result_text
        }]
    }

# 标记为工具函数
execute_command.is_tool = True
execute_command.tool_definition = tool_definition