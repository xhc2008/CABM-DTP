# -*- coding: utf-8 -*-
"""
上下文构建服务
负责在发送消息给AI前，检索相关记忆和笔记，并整合到系统提示词中
"""

import os
from typing import Optional
from .memory import ChatHistoryVectorDB
from config import RAG_CONFIG, ChatConfig


class ContextBuilder:
    """上下文构建器，负责检索记忆和笔记，构建完整的系统提示词"""
    
    def __init__(self):
        """初始化上下文构建器"""
        # 创建记忆和笔记的向量数据库实例
        self.memory_db = self._create_custom_db("memory")
        self.notes_db = self._create_custom_db("notes")
        
        # 加载现有数据库
        self._load_databases()
    
    def _create_custom_db(self, db_name: str) -> ChatHistoryVectorDB:
        """创建自定义的向量数据库实例"""
        db = ChatHistoryVectorDB(
            RAG_config=RAG_CONFIG,
            db_name=db_name  # 修改参数名
        )
        return db
    
    def _load_databases(self):
        """加载现有的向量数据库"""
        try:
            # 加载memory数据库
            memory_file = os.path.join('data', 'memory.json')
            if os.path.exists(memory_file):
                self.memory_db.load_from_file(memory_file)
                self.memory_db.character_name = "memory"
            
            # 加载notes数据库  
            notes_file = os.path.join('data', 'notes.json')
            if os.path.exists(notes_file):
                self.notes_db.load_from_file(notes_file)
                self.notes_db.character_name = "notes"
                
        except Exception as e:
            print(f"加载数据库时出错: {e}")
    
    def _search_memory(self, query: str, top_k: int = 3) -> list:
        """搜索相关记忆"""
        try:
            results = self.memory_db.search(query, top_k=top_k, timeout=5)
            return [result['text'] for result in results] if results else []
        except Exception as e:
            print(f"搜索记忆时出错: {e}")
            return []
    
    def _search_notes(self, query: str, top_k: int = 3) -> list:
        """搜索相关笔记"""
        try:
            results = self.notes_db.search(query, top_k=top_k, timeout=5)
            return [result['text'] for result in results] if results else []
        except Exception as e:
            print(f"搜索笔记时出错: {e}")
            return []
    
    def build_enhanced_system_prompt(self, user_message: str) -> str:
        """
        构建增强的系统提示词
        
        参数:
            user_message: 用户输入消息，用作检索查询
            
        返回:
            增强后的系统提示词
        """
        # 基础系统提示词
        enhanced_prompt = ChatConfig.system_prompt
        
        # 搜索相关记忆
        relevant_memories = self._search_memory(user_message)
        
        # 搜索相关笔记
        relevant_notes = self._search_notes(user_message)
        
        # 保存相关笔记供总结时使用
        set_current_relevant_notes(relevant_notes)
        
        # 添加相关记忆
        if relevant_memories:
            enhanced_prompt += "\n\n以下是相关的记忆（如有）：\n```\n"
            enhanced_prompt += "\n".join(relevant_memories)
            enhanced_prompt += "\n```"
        
        # 添加相关笔记
        if relevant_notes:
            enhanced_prompt += "\n\n以下是相关笔记（如有）：\n```\n"
            enhanced_prompt += "\n".join(relevant_notes)
            enhanced_prompt += "\n```"
        
        return enhanced_prompt


# 全局上下文构建器实例
_context_builder = None

# 全局变量，保存当前对话的相关笔记，供总结时使用
_current_relevant_notes = []

def get_context_builder() -> ContextBuilder:
    """获取全局上下文构建器实例"""
    global _context_builder
    if _context_builder is None:
        _context_builder = ContextBuilder()
    return _context_builder

def get_current_relevant_notes() -> list:
    """获取当前对话的相关笔记"""
    global _current_relevant_notes
    return _current_relevant_notes

def set_current_relevant_notes(notes: list):
    """设置当前对话的相关笔记"""
    global _current_relevant_notes
    _current_relevant_notes = notes


# 使用示例
if __name__ == "__main__":
    # 测试上下文构建功能
    builder = ContextBuilder()
    
    # 测试构建增强提示词
    user_input = "帮我查看文件"
    enhanced_prompt = builder.build_enhanced_system_prompt(user_input)
    print("增强后的系统提示词:")
    print(enhanced_prompt)