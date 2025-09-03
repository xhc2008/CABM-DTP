# -*- coding: utf-8 -*-
"""
最终的总结功能测试
"""

import time
from services.summarize import summarize_conversation_async, ConversationSummarizer

def test_comprehensive():
    """综合测试总结功能"""
    print("=== 开始综合测试总结功能 ===\n")
    
    # 测试1: 同步总结
    print("1. 测试同步总结功能...")
    summarizer = ConversationSummarizer()
    
    user_msg1 = "帮我查看当前目录的文件"
    assistant_msg1 = "好的，我来帮你查看当前目录的文件。"
    tool_calls1 = [{"function": {"name": "execute_command", "arguments": '{"command": "dir"}'}}]
    
    summarizer.summarize_conversation(user_msg1, assistant_msg1, tool_calls1)
    print("✓ 同步总结完成\n")
    
    # 测试2: 异步总结
    print("2. 测试异步总结功能...")
    user_msg2 = "教我Python装饰器的用法"
    assistant_msg2 = "装饰器是Python的重要特性，用于在不修改原函数的情况下增加功能。常见用法包括：@property、@staticmethod、@classmethod等。"
    
    summarize_conversation_async(user_msg2, assistant_msg2)
    print("✓ 异步总结已启动")
    print("等待异步任务完成...")
    time.sleep(3)
    print("✓ 异步总结完成\n")
    
    # 测试3: 包含notes的对话
    print("3. 测试notes功能...")
    user_msg3 = "请分享一些编程最佳实践"
    assistant_msg3 = "好的，以下是一些重要的编程最佳实践：1. 编写清晰的代码注释 2. 使用版本控制系统 3. 进行单元测试 4. 遵循代码规范"
    
    summarizer.summarize_conversation(user_msg3, assistant_msg3)
    print("✓ Notes功能测试完成\n")
    
    print("=== 所有测试完成 ===")
    print("请检查 data/memory.json 和 data/notes.json 文件")

if __name__ == "__main__":
    test_comprehensive()