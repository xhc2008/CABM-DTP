# -*- coding: utf-8 -*-
"""
测试chat.py与summarize.py的集成
"""

import os
import time
from dotenv import load_dotenv
from services.chat import ChatService

def test_chat_integration():
    """测试聊天服务与总结功能的集成"""
    print("=== 测试聊天服务与总结功能的集成 ===\n")
    
    # 加载环境变量
    load_dotenv()
    
    # 初始化聊天服务
    chat_service = ChatService(
        api_key=os.getenv('API_KEY'),
        base_url=os.getenv('BASE_URL'),
        model=os.getenv('AGENT_MODEL')
    )
    
    print("1. 测试简单对话...")
    user_message = "你好，请简单介绍一下自己"
    
    print(f"用户: {user_message}")
    print("助手: ", end="", flush=True)
    
    # 处理消息并显示流式响应
    for chunk in chat_service.process_message_stream(user_message):
        print(chunk, end="", flush=True)
    
    print("\n\n等待总结完成...")
    time.sleep(3)
    print("✓ 对话1完成\n")
    
    print("2. 测试带工具调用的对话...")
    user_message2 = "帮我执行一个简单的Python代码"
    
    print(f"用户: {user_message2}")
    print("助手: ", end="", flush=True)
    
    # 处理消息并显示流式响应
    for chunk in chat_service.process_message_stream(user_message2):
        print(chunk, end="", flush=True)
    
    print("\n\n等待总结完成...")
    time.sleep(3)
    print("✓ 对话2完成\n")
    
    print("=== 集成测试完成 ===")
    print("请检查 data/memory.json 和 data/notes.json 文件是否有新的内容")

if __name__ == "__main__":
    test_chat_integration()