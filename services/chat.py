import json
import requests
import re
import os
import importlib.util
from datetime import datetime
from typing import List, Dict, Any, Optional, Iterator
from config import ChatConfig
from .summarize import summarize_conversation_async
from .context_builder import get_context_builder


class ChatService:
    """AI聊天服务，支持连续的MCP调用"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.conversation_history: List[Dict[str, str]] = []
        
        # 动态注册tools/目录下的所有工具
        self.available_tools = {}
        self.tools = []
        print("开始加载工具...")
        self._load_tools_from_directory()
        print(f"工具加载完成，共加载 {len(self.available_tools)} 个工具")
    
    def _load_tools_from_directory(self):
        """从tools/目录动态加载所有工具"""
        tools_dir = "tools"
        successful_tools = []
        failed_tools = []
        
        print(f"检查工具目录: {tools_dir}")
        if not os.path.exists(tools_dir):
            print(f"工具目录 {tools_dir} 不存在")
            self._log_tool_info(f"工具目录 {tools_dir} 不存在")
            return
        
        print(f"工具目录存在，开始扫描.py文件...")
        
        # 遍历tools目录下的所有.py文件
        all_files = os.listdir(tools_dir)
        print(f"目录中的所有文件: {all_files}")
        
        for filename in all_files:
            print(f"检查文件: {filename}")
            if filename.endswith('.py') and not filename.startswith('__'):
                tool_name = filename[:-3]  # 去掉.py扩展名
                file_path = os.path.join(tools_dir, filename)
                print(f"尝试加载工具: {tool_name} from {file_path}")
                
                try:
                    # 动态导入模块
                    spec = importlib.util.spec_from_file_location(tool_name, file_path)
                    if spec is None or spec.loader is None:
                        failed_tools.append(f"{tool_name}: 无法创建模块规范")
                        continue
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # 检查模块是否有对应的函数和tool_definition
                    if hasattr(module, tool_name):
                        tool_func = getattr(module, tool_name)
                        
                        # 检查函数是否有tool_definition属性
                        if hasattr(tool_func, 'tool_definition'):
                            self.available_tools[tool_name] = tool_func
                            self.tools.append(tool_func.tool_definition)
                            successful_tools.append(tool_name)
                        else:
                            failed_tools.append(f"{tool_name}: 缺少tool_definition属性")
                            print("取消加载，因为缺少tool_definition属性")
                    else:
                        failed_tools.append(f"{tool_name}: 模块中没有找到同名函数")
                        print("取消加载，因为模块中没有找到同名函数")
                        
                except Exception as e:
                    failed_tools.append(f"{tool_name}: 加载失败 - {str(e)}")
                    print(f"取消加载，因为{str(e)}")
        
        # 记录工具注册结果到日志
        self._log_tool_registration_result(successful_tools, failed_tools)
    
    def _log_tool_info(self, message: str):
        """记录工具信息到日志文件"""
        try:
            with open("log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] 工具加载: {message}\n")
        except Exception:
            pass  # 静默处理日志写入失败
    
    def _log_tool_registration_result(self, successful_tools: List[str], failed_tools: List[str]):
        """记录工具注册结果"""
        try:
            with open("log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'='*50}\n")
                f.write(f"[{timestamp}] 工具注册结果:\n")
                
                if successful_tools:
                    f.write(f"✓ 成功注册的工具 ({len(successful_tools)}个): {', '.join(successful_tools)}\n")
                else:
                    f.write("✗ 没有成功注册任何工具\n")
                
                if failed_tools:
                    f.write(f"✗ 跳过的工具 ({len(failed_tools)}个):\n")
                    for failed in failed_tools:
                        f.write(f"  - {failed}\n")
                
                f.write(f"{'='*50}\n\n")
        except Exception:
            pass  # 静默处理日志写入失败
    
    def add_message(self, role: str, content: str):
        """添加消息到对话历史"""
        self.conversation_history.append({"role": role, "content": content})
        
        # 限制历史记录长度，避免过长
        if len(self.conversation_history) > ChatConfig.MAX_CONVERSATION_HISTORY:
            self.conversation_history = self.conversation_history[-ChatConfig.MAX_CONVERSATION_HISTORY:]
    
    def log_request_response(self, request_data: Dict[str, Any], response_data: str, parsed_response: Optional[Dict[str, Any]] = None):
        """记录请求和响应到日志文件"""
        try:
            with open("log.txt", "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n{'='*50}\n")
                f.write(f"时间: {timestamp}\n")
                
                # 记录原始请求的message字段
                if "messages" in request_data:
                    f.write(f"请求消息:\n")
                    for msg in request_data["messages"]:
                        f.write(f"  {msg['role']}: {msg['content']}\n")
                
                # 记录合并后的原始响应message
                if parsed_response:
                    f.write(f"响应消息:\n")
                    if "content" in parsed_response:
                        f.write(f"  内容: {parsed_response['content']}\n")
                    
                    # 如果响应包含工具调用，显示工具调用信息
                    if "tool_calls" in parsed_response:
                        for tool_call in parsed_response["tool_calls"]:
                            function_name = tool_call["function"]["name"]
                            function_args = tool_call["function"]["arguments"]
                            f.write(f"  工具调用: {function_name}\n")
                            f.write(f"  参数: {function_args}\n")
                
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
            "temperature": ChatConfig.TEMPERATURE,
            "top_p": ChatConfig.TOP_P,
            "stream": True
        }
        
        # 如果有可用工具，添加到请求中
        if self.tools:
            payload["tools"] = self.tools
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=ChatConfig.API_TIMEOUT,
                stream=True
            )
            response.raise_for_status()
            
            # 收集完整响应用于日志和解析
            parsed_response = {"content": "", "tool_calls": []}
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 去掉 'data: ' 前缀
                        
                        if data_str.strip() == '[DONE]':
                            break
                            
                        try:
                            data = json.loads(data_str)
                            
                            # 解析响应内容用于日志记录
                            if 'choices' in data and len(data['choices']) > 0:
                                choice = data['choices'][0]
                                if 'delta' in choice:
                                    delta = choice['delta']
                                    if 'content' in delta and delta['content']:
                                        parsed_response["content"] += delta['content']
                                    if 'tool_calls' in delta and delta['tool_calls']:
                                        # 处理工具调用的增量更新
                                        for tool_call in delta['tool_calls']:
                                            index = tool_call['index']
                                            # 确保有足够的位置
                                            while len(parsed_response["tool_calls"]) <= index:
                                                parsed_response["tool_calls"].append({
                                                    'id': '',
                                                    'type': 'function',
                                                    'function': {'name': '', 'arguments': ''}
                                                })
                                            
                                            if 'id' in tool_call:
                                                parsed_response["tool_calls"][index]['id'] = tool_call['id']
                                            if 'type' in tool_call:
                                                parsed_response["tool_calls"][index]['type'] = tool_call['type']
                                            if 'function' in tool_call:
                                                if 'name' in tool_call['function']:
                                                    parsed_response["tool_calls"][index]['function']['name'] = tool_call['function']['name']
                                                if 'arguments' in tool_call['function']:
                                                    parsed_response["tool_calls"][index]['function']['arguments'] += tool_call['function']['arguments']
                            
                            yield data
                        except json.JSONDecodeError:
                            continue
            
            # 记录请求和解析后的响应
            self.log_request_response(payload, "", parsed_response)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API调用失败: {str(e)}"
            self.log_request_response(payload, error_msg)
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
        
        # 使用上下文构建器构建增强的系统提示词
        context_builder = get_context_builder()
        enhanced_system_prompt = context_builder.build_enhanced_system_prompt(user_message)
        
        # 构建消息列表，包含增强的系统提示和对话历史
        messages = [
            {
                "role": "system",
                "content": enhanced_system_prompt
            }
        ] + self.conversation_history
        
        # 最大工具调用轮次，防止无限循环
        max_tool_calls = ChatConfig.MAX_TOOL_CALLS
        tool_call_count = 0
        
        while tool_call_count < max_tool_calls:
            # 用于收集完整回复内容
            full_content = ""
            # 用于收集工具调用
            tool_calls = {}
            # 用于跟踪已显示的工具调用
            displayed_tool_calls = set()
            
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
                            
                            # 当工具名称首次出现时，显示工具调用信息
                            if tool_call['function'].get('name') and index not in displayed_tool_calls:
                                function_name = tool_call['function']['name']
                                
                                # 从配置中获取友好显示名称，如果没有则使用默认格式
                                display_name = ChatConfig.TOOL_CALL_DISPLAY_NAMES.get(
                                    function_name, 
                                    f"工具调用：{function_name}"
                                )
                                if full_content:
                                    yield f"\n> {display_name}\n"
                                else:
                                    yield f"> {display_name}\n"
                                displayed_tool_calls.add(index)
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
                
                # 显示工具执行完成提示
                #yield "正在处理工具结果...\n"
                
                # 如果有工具调用，继续循环处理
                continue
            else:
                # 没有工具调用，添加助手消息到历史并退出循环
                if full_content:
                    self.add_message("assistant", full_content)
                break
        
        # 如果达到最大工具调用次数，返回提示
        if tool_call_count >= max_tool_calls:
            yield "\n已达到最大工具调用次数，对话结束。"
        
        # 对话完成后，异步调用总结功能
        # 获取最终的助手回复（可能包含多轮工具调用的结果）
        final_assistant_message = self._get_final_assistant_message()
        all_tool_calls = self._get_all_tool_calls_from_history()
        self._summarize_conversation_async(user_message, final_assistant_message, all_tool_calls)

    def process_message(self, user_message: str) -> str:
        """处理用户消息并返回AI回复（非流式，保持兼容性）"""
        result = ""
        for chunk in self.process_message_stream(user_message):
            result += chunk
        return result
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
    
    def _get_final_assistant_message(self) -> str:
        """获取最终的助手回复消息"""
        # 从对话历史中获取最后一条助手消息
        for message in reversed(self.conversation_history):
            if message.get("role") == "assistant" and message.get("content"):
                return message["content"]
        return ""
    
    def _get_all_tool_calls_from_history(self) -> List[Dict[str, Any]]:
        """从对话历史中获取本轮对话的所有工具调用"""
        tool_calls = []
        # 从最后开始查找，直到遇到用户消息为止
        for message in reversed(self.conversation_history):
            if message.get("role") == "user":
                break
            elif message.get("role") == "assistant" and "tool_calls" in message:
                # 将工具调用添加到列表开头，保持正确的顺序
                tool_calls = message["tool_calls"] + tool_calls
        return tool_calls
    
    def _summarize_conversation_async(self, user_message: str, assistant_message: str, tool_calls: List[Dict[str, Any]] = None):
        """异步调用对话总结功能"""
        try:
            # 只有当有实际内容时才进行总结
            if user_message and assistant_message:
                summarize_conversation_async(user_message, assistant_message, tool_calls)
        except Exception as e:
            # 静默处理总结失败，不影响主要对话流程
            print(f"总结对话时出错: {e}")