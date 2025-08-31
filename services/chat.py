import json
import requests
import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Iterator
from tools.execute_safe_command import execute_safe_command
from tools.read_txt_file import read_text_file


class ChatService:
    """AI聊天服务，支持连续的MCP调用"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        
        # 注册可用工具
        self.available_tools = {
            "execute_safe_command": execute_safe_command,
            "read_text_file": read_text_file
        }
        
        # 构建工具定义列表
        self.tools = []
        for tool_name, tool_func in self.available_tools.items():
            if hasattr(tool_func, 'tool_definition'):
                self.tools.append(tool_func.tool_definition)
    
    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        self.conversation_history.append({"role": role, "content": content})
        
        # 限制历史记录长度，避免过长
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]
    
    def log_request_response(self, request_data: Dict[str, Any], response_data: str):
        """记录请求和响应到日志文件"""
        try:
            with open("log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'='*50}\n")
                f.write(f"时间: {timestamp}\n")
                f.write(f"请求:\n{json.dumps(request_data, ensure_ascii=False, indent=2)}\n")
                f.write(f"响应:\n{response_data}\n")
                f.write(f"{'='*50}\n")
        except Exception as e:
            print(f"日志记录失败: {e}")

    def call_ai_api_stream(self, messages: List[Dict[str, str]], max_tokens: int = 512) -> Iterator[Dict[str, Any]]:
        """调用AI API流式响应"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
            "top_p": 0.7,
            "stream": True
        }
        
        # 如果有可用工具，添加到请求中
        if self.tools:
            payload["tools"] = self.tools
        
        # 记录请求
        self.log_request_response(payload, "")
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30,
                stream=True
            )
            response.raise_for_status()
            
            # 收集完整响应用于日志
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    full_response += line_str + "\n"
                    
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 去掉 'data: ' 前缀
                        
                        if data_str.strip() == '[DONE]':
                            break
                            
                        try:
                            data = json.loads(data_str)
                            yield data
                        except json.JSONDecodeError:
                            continue
            
            # 记录完整响应
            self.log_request_response({}, full_response)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API调用失败: {str(e)}"
            self.log_request_response({}, error_msg)
            raise Exception(error_msg)

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具函数"""
        if tool_name not in self.available_tools:
            return {
                "status": "error",
                "message": f"工具 '{tool_name}' 不存在"
            }
        
        try:
            tool_func = self.available_tools[tool_name]
            return tool_func(**parameters)
        except Exception as e:
            return {
                "status": "error",
                "message": f"执行工具时出错: {str(e)}"
            }

    def process_message_stream(self, user_message: str) -> Iterator[str]:
        """处理用户消息并返回流式AI回复"""
        # 添加用户消息到历史
        self.add_message("user", user_message)
        
        # 构建消息列表，包含系统提示和对话历史
        messages = [
            {
                "role": "system",
                "content": "你是一个桌面宠物助手，可以调用工具来帮助用户。请根据用户需求选择合适的工具，并以友好、可爱的语气回复用户。回复简短、口语化，不要使用markdown。"
            }
        ] + self.conversation_history
        
        # 最大工具调用轮次，防止无限循环
        max_tool_calls = 3
        tool_call_count = 0
        
        while tool_call_count < max_tool_calls:
            # 用于收集完整回复内容
            full_content = ""
            # 用于收集工具调用
            tool_calls = {}
            
            # 流式调用AI API
            for chunk in self.call_ai_api_stream(messages):
                if 'choices' not in chunk or len(chunk['choices']) == 0:
                    continue
                    
                choice = chunk['choices'][0]
                
                # 处理文本内容
                if 'delta' in choice and 'content' in choice['delta'] and choice['delta']['content']:
                    content = choice['delta']['content']
                    full_content += content
                    yield content
                
                # 处理工具调用
                if 'delta' in choice and 'tool_calls' in choice['delta'] and choice['delta']['tool_calls']:
                    for tool_call in choice['delta']['tool_calls']:
                        index = tool_call['index']
                        
                        # 初始化工具调用结构
                        if index not in tool_calls:
                            tool_calls[index] = {
                                'id': tool_call.get('id', f'call_{index}_{tool_call_count}'),
                                'type': tool_call.get('type', 'function'),
                                'function': {
                                    'name': tool_call['function'].get('name', ''),
                                    'arguments': tool_call['function'].get('arguments', '')
                                }
                            }
                        else:
                            # 累加参数
                            if 'arguments' in tool_call['function']:
                                tool_calls[index]['function']['arguments'] += tool_call['function']['arguments']
            
            # 如果有工具调用，执行工具
            if tool_calls:
                tool_call_count += 1
                
                # 将工具调用转换为列表
                tool_calls_list = [tool_calls[i] for i in sorted(tool_calls.keys())]
                
                # 添加助手消息到历史（包含工具调用）
                tool_call_message = {
                    "role": "assistant",
                    "content": full_content,
                    "tool_calls": tool_calls_list
                }
                messages.append(tool_call_message)
                
                # 执行所有工具调用
                tool_responses = []
                for tool_call in tool_calls_list:
                    function_name = tool_call['function']['name']
                    try:
                        function_args = json.loads(tool_call['function']['arguments'])
                    except json.JSONDecodeError:
                        function_args = {}
                    
                    # 执行工具
                    tool_result = self.execute_tool(function_name, function_args)
                    
                    # 添加工具响应
                    tool_responses.append({
                        "tool_call_id": tool_call['id'],
                        "role": "tool",
                        "name": function_name,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })
                
                # 添加工具响应到消息列表
                messages.extend(tool_responses)
                
                # 如果有工具调用，继续循环处理
                continue
            else:
                # 没有工具调用，添加助手消息到历史并退出循环
                if full_content:
                    self.add_message("assistant", full_content)
                break
        
        # 如果达到最大工具调用次数，返回提示
        if tool_call_count >= max_tool_calls:
            yield "\n\n已达到最大工具调用次数，对话结束。"

    def process_message(self, user_message: str) -> str:
        """处理用户消息并返回AI回复（非流式，保持兼容性）"""
        result = ""
        for chunk in self.process_message_stream(user_message):
            result += chunk
        return result
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []