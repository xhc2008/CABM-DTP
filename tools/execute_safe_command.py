import subprocess
from typing import Dict, Any

# 工具定义
tool_definition = {
    "type": "function",
    "function": {
        "name": "execute_safe_command",
        "description": "在cmd中执行一条安全的指令（没有管理员权限）",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "要执行的安全命令"
                }
            },
            "required": ["command"]
        }
    }
}

def execute_safe_command(command: str) -> Dict[str, Any]:
    """
    在cmd中执行一条安全的指令（没有管理员权限）
    
    Args:
        command: 要执行的命令
        
    Returns:
        包含执行结果和状态的字典
    """
    try:
        # 安全限制：检查命令是否包含潜在危险的字符或命令
        dangerous_patterns = [
            "&&", "||", "|", ">", "<", "`", "$", "(", ")", "{", "}", 
            "[", "]", ";", "sudo", "admin", "root", "chmod", "chown",
            "rm", "del", "format", "mkfs", "dd", "shutdown", "reboot"
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command:
                return {
                    "status": "error",
                    "message": f"命令包含潜在危险模式: {pattern}",
                    "output": ""
                }
        
        # 执行命令
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30  # 设置超时防止长时间运行
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "return_code": result.returncode,
            "output": result.stdout,
            "error": result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "命令执行超时",
            "output": ""
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"执行命令时发生异常: {str(e)}",
            "output": ""
        }

# 标记为工具函数
execute_safe_command.is_tool = True
execute_safe_command.tool_definition = tool_definition