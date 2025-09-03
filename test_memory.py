#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试memory.py功能的脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.memory import ChatHistoryVectorDB
from config import RAG_CONFIG

def test_memory_functions():
    """测试memory.py中的三个主要功能"""
    
    print("=== 测试向量数据库功能 ===")
    
    # 初始化向量数据库
    print("1. 初始化向量数据库...")
    try:
        vector_db = ChatHistoryVectorDB(RAG_CONFIG, character_name="test_character")
        vector_db.initialize_database()
        print("✓ 初始化成功")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return
    
    # 测试功能1：将一段文本加入向量数据库
    print("\n2. 测试添加文本到向量数据库...")
    try:
        test_texts = [
            "这是第一段测试文本，包含一些关于AI的信息。",
            "这是第二段测试文本，讲述了机器学习的基础知识。",
            "这是第三段测试文本，介绍了深度学习的应用场景。"
        ]
        
        for i, text in enumerate(test_texts, 1):
            vector_db.add_text(text)
            print(f"✓ 添加文本 {i}: {text[:30]}...")
            
    except Exception as e:
        print(f"✗ 添加文本失败: {e}")
        return
    
    # 测试功能2：通过检索词获取相关记忆
    print("\n3. 测试检索相关记忆...")
    try:
        query = "AI和机器学习"
        results = vector_db.search(query, top_k=3)
        
        if results:
            print(f"✓ 检索成功，找到 {len(results)} 条相关记录:")
            for i, result in enumerate(results, 1):
                print(f"  记录 {i}: {result['text'][:50]}...")
        else:
            print("✓ 检索完成，但未找到相关记录")
            
    except Exception as e:
        print(f"✗ 检索失败: {e}")
        return
    
    # 测试功能3：将文件构建成向量数据库
    print("\n4. 测试从文件构建向量数据库...")
    try:
        # 创建一个测试文件
        test_file_path = "test_document.txt"
        test_content = """这是一个测试文档。

第一段：人工智能是计算机科学的一个分支，它试图理解智能的实质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。

第二段：机器学习是人工智能的一个子领域，它使计算机系统能够自动学习和改进，而无需明确编程。

第三段：深度学习是机器学习的一个子集，它使用多层神经网络来模拟人脑的工作方式。"""
        
        with open(test_file_path, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        # 从文件构建向量数据库
        vector_db.build_from_file(test_file_path)
        print(f"✓ 从文件 {test_file_path} 构建向量数据库成功")
        
        # 清理测试文件
        os.remove(test_file_path)
        
    except Exception as e:
        print(f"✗ 从文件构建向量数据库失败: {e}")
        return
    
    # 测试保存和加载功能
    print("\n5. 测试保存和加载功能...")
    try:
        # 保存数据库
        vector_db.save_to_file()
        print("✓ 保存向量数据库成功")
        
        # 创建新的实例并加载
        new_vector_db = ChatHistoryVectorDB(RAG_CONFIG, character_name="test_character")
        new_vector_db.load_from_file()
        print("✓ 加载向量数据库成功")
        
        # 测试加载后的检索功能
        results = new_vector_db.search("深度学习", top_k=2)
        if results:
            print(f"✓ 加载后检索成功，找到 {len(results)} 条记录")
        else:
            print("✓ 加载后检索完成")
            
    except Exception as e:
        print(f"✗ 保存/加载失败: {e}")
        return
    
    print("\n=== 所有测试完成 ===")
    print("memory.py 的三个主要功能都已验证:")
    print("1. ✓ 将一段文本加入向量数据库")
    print("2. ✓ 通过检索词获取相关记忆") 
    print("3. ✓ 将文件构建成向量数据库")

if __name__ == "__main__":
    # 检查环境变量
    required_env_vars = ['BASE_URL', 'API_KEY', 'EMBEDDING_MODEL']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("错误：缺少必要的环境变量:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\n请在 .env 文件中设置这些变量，参考 .env.example")
        sys.exit(1)
    
    test_memory_functions()