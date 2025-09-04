# -*- coding: utf-8 -*-
"""
对话总结服务
在每次完整响应结束后被调用，记录本次对话到向量数据库
"""

import json
import os
import re
import requests
import asyncio
import threading
from datetime import datetime
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from config import SummaryConfig
from .memory import ChatHistoryVectorDB
from config import RAG_CONFIG
from .context_builder import get_current_relevant_notes


class ConversationSummarizer:
    """对话总结器，负责总结对话并存储到向量数据库"""
    
    def __init__(self):
        """初始化总结器"""
        # 加载环境变量
        load_dotenv()
        
        # API配置
        self.api_key = os.getenv('API_KEY')
        self.base_url = os.getenv('BASE_URL')
        self.model = os.getenv('SUMMURY_MODEL')  # 注意：环境变量中是SUMMURY_MODEL
        
        # 确保data目录存在
        os.makedirs('data', exist_ok=True)
        
        # 创建自定义的向量数据库实例，避免创建不必要的子目录
        self.memory_db = self._create_custom_db("memory")
        self.notes_db = self._create_custom_db("notes")
        
        # 加载现有数据库
        self._load_databases()
        
        # 清理不必要的目录结构
        self._cleanup_unnecessary_dirs()
    
   # 在 summarize.py 和 context_builder.py 中修改
    def _create_custom_db(self, db_name: str) -> ChatHistoryVectorDB:
        """创建自定义的向量数据库实例"""
        db = ChatHistoryVectorDB(
            RAG_config=RAG_CONFIG,
            db_name=db_name  # 修改参数名
        )
        return db
    
    def _cleanup_unnecessary_dirs(self):
        """清理不必要的目录结构"""
        import shutil
        
        # 清理可能创建的不必要目录
        unnecessary_dirs = [
            os.path.join('data', 'memory', 'memory'),
            os.path.join('data', 'memory', 'notes'),
            os.path.join('data', 'memory')
        ]
        
        for dir_path in unnecessary_dirs:
            if os.path.exists(dir_path) and os.path.isdir(dir_path):
                try:
                    # 只删除空目录
                    if not os.listdir(dir_path):
                        os.rmdir(dir_path)
                        print(f"已清理空目录: {dir_path}")
                except Exception as e:
                    # 静默处理清理失败的情况
                    pass
    
    def _load_databases(self):
        """加载现有的向量数据库"""
        try:
            # 加载memory数据库
            memory_file = os.path.join('data', 'memory.json')
            if os.path.exists(memory_file):
                self.memory_db.load_from_file(memory_file)
                # 确保character_name正确（防止被文件内容覆盖）
                self.memory_db.character_name = "memory"
            else:
                print(f"Memory数据库文件不存在: {memory_file}")
            
            # 加载notes数据库  
            notes_file = os.path.join('data', 'notes.json')
            if os.path.exists(notes_file):
                self.notes_db.load_from_file(notes_file)
                # 确保character_name正确（防止被文件内容覆盖）
                self.notes_db.character_name = "notes"
            else:
                print(f"Notes数据库文件不存在: {notes_file}")
                
        except Exception as e:
            print(f"加载数据库时出错: {e}")
    
    def _call_summary_api(self, conversation_text: str) -> Optional[Dict[str, Any]]:
        """调用总结模型API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建增强的系统提示词，包含相关笔记
        system_prompt = SummaryConfig.summary_prompt
        relevant_notes = get_current_relevant_notes()
        
        if relevant_notes:
            system_prompt += f"\n\n这是已经记录的笔记：```\n"
            system_prompt += "\n".join(relevant_notes)
            system_prompt += "\n```"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user", 
                    "content": conversation_text
                }
            ],
            "max_tokens": 512,
            "enable_thinking": False,
            "response_format": {"type": "json_object"},
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content']
                return self._parse_summary_response(content)
            
        except Exception as e:
            print(f"调用总结API失败: {e}")
            return None
    
    def _parse_summary_response(self, response_content: str) -> Optional[Dict[str, Any]]:
        """解析总结模型的响应"""
        try:
            # 移除可能的代码块标记
            content = response_content.strip()
            if content.startswith('```json'):
                content = content[7:]
            elif content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            # 解析JSON
            parsed = json.loads(content.strip())
            
            # 验证必需字段
            if 'summary' not in parsed:
                print("总结响应缺少summary字段")
                return None
            
            # 确保add字段是列表
            if 'add' not in parsed:
                parsed['add'] = []
            elif not isinstance(parsed['add'], list):
                parsed['add'] = []
            
            return parsed
            
        except json.JSONDecodeError as e:
            print(f"解析总结响应JSON失败: {e}")
            print(f"原始响应: {response_content}")
            return None
        except Exception as e:
            print(f"处理总结响应时出错: {e}")
            return None
    
    def _format_conversation(self, user_message: str, assistant_message: str, tool_calls: List[Dict[str, Any]] = None) -> str:
        """格式化对话内容"""
        conversation = f"用户：{user_message}\n助手：{assistant_message}"
        
        # 添加工具调用信息
        if tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call.get('function', {}).get('name', '未知工具')
                tool_args = tool_call.get('function', {}).get('arguments', '{}')
                conversation += f"\n工具调用（{tool_name}）：{tool_args}"
        
        return conversation
    
    def _save_to_memory_db(self, summary: str, timestamp: str):
        """保存总结到memory向量数据库"""
        try:
            # 添加时间戳信息的总结
            memory_text = f"[{timestamp}] {summary}"
            self.memory_db.add_text(memory_text)
            
            # 保存到data目录，文件名为memory.json
            self.memory_db.save_to_file()
            print(f"总结已保存到data/memory.json: {summary[:50]}...")
            
        except Exception as e:
            print(f"保存到memory数据库失败: {e}")
    
    def _save_to_notes_db(self, notes: List[str]):
        """保存笔记到notes向量数据库"""
        try:
            for note in notes:
                if note.strip():  # 跳过空笔记
                    self.notes_db.add_text(note.strip())
            
            # 保存到data目录，文件名为notes.json
            self.notes_db.save_to_file()
            print(f"已保存 {len(notes)} 条笔记到data/notes.json")
            
        except Exception as e:
            print(f"保存到notes数据库失败: {e}")
    
    def summarize_conversation_async(self, user_message: str, assistant_message: str, tool_calls: List[Dict[str, Any]] = None):
        """异步总结对话（在单独线程中执行）"""
        def _async_summarize():
            try:
                self.summarize_conversation(user_message, assistant_message, tool_calls)
            except Exception as e:
                print(f"异步总结对话时出错: {e}")
        
        # 在新线程中执行总结
        thread = threading.Thread(target=_async_summarize, daemon=True)
        thread.start()
    
    def summarize_conversation(self, user_message: str, assistant_message: str, tool_calls: List[Dict[str, Any]] = None):
        """总结对话并存储到向量数据库"""
        try:
            # Step 1: 格式化对话内容
            conversation_text = self._format_conversation(user_message, assistant_message, tool_calls)
            print(f"开始总结对话: {user_message[:30]}...")
            
            # Step 2: 调用总结模型
            summary_result = self._call_summary_api(conversation_text)
            if not summary_result:
                print("总结失败，跳过存储")
                return
            
            # Step 3: 提取字段
            summary = summary_result.get('summary', '')
            add_notes = summary_result.get('add', [])
            
            print(f"总结结果: {summary}")
            if add_notes:
                print(f"新增笔记: {add_notes}")
            
            # Step 4: 保存到向量数据库
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存总结到memory数据库
            if summary:
                self._save_to_memory_db(summary, timestamp)
            
            # 保存笔记到notes数据库
            if add_notes:
                self._save_to_notes_db(add_notes)
            
            print("对话总结完成")
            
        except Exception as e:
            print(f"总结对话时出错: {e}")


# 全局总结器实例
_summarizer = None

def get_summarizer() -> ConversationSummarizer:
    """获取全局总结器实例"""
    global _summarizer
    if _summarizer is None:
        _summarizer = ConversationSummarizer()
    return _summarizer

def summarize_conversation_async(user_message: str, assistant_message: str, tool_calls: List[Dict[str, Any]] = None):
    """异步总结对话的便捷函数"""
    summarizer = get_summarizer()
    summarizer.summarize_conversation_async(user_message, assistant_message, tool_calls)


# 使用示例
if __name__ == "__main__":
    # 测试总结功能
    summarizer = ConversationSummarizer()
    
    # 模拟对话
    user_msg = "帮我查看当前目录的文件"
    assistant_msg = "好的，我来帮你查看当前目录的文件。"
    tool_calls = [
        {
            "function": {
                "name": "execute_command",
                "arguments": '{"command": "dir"}'
            }
        }
    ]
    
    summarizer.summarize_conversation(user_msg, assistant_msg, tool_calls)