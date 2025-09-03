# Memory 模块使用说明

## 概述

`services/memory.py` 提供了基于向量数据库的记忆功能，支持文本的存储、检索和管理。

## 主要功能

### 1. 将一段文本加入向量数据库

```python
from services.memory import ChatHistoryVectorDB
from config import RAG_CONFIG

# 初始化向量数据库
vector_db = ChatHistoryVectorDB(RAG_CONFIG, character_name="my_character")
vector_db.initialize_database()

# 添加文本
vector_db.add_text("这是一段要记住的文本内容")
```

### 2. 通过检索词获取相关记忆

```python
# 检索相关记忆
results = vector_db.search("检索关键词", top_k=5)

for result in results:
    print(f"相关文本: {result['text']}")
```

### 3. 将文件构建成向量数据库

```python
# 从文件构建向量数据库
vector_db.build_from_file("path/to/your/document.txt")
```

## 环境配置

在 `.env` 文件中配置以下变量：

```env
# 向量数据库相关配置
EMBEDDING_API_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
EMBEDDING_MODEL=BAAI/bge-large-zh-v1.5

# 重排序模型配置（可选）
RERANKER_API_BASE_URL=https://api.siliconflow.cn/v1
RERANKER_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx
RERANKER_MODEL=netease-youdao/bce-reranker-base_v1
```

## 完整示例

```python
from services.memory import ChatHistoryVectorDB
from config import RAG_CONFIG

# 初始化
vector_db = ChatHistoryVectorDB(RAG_CONFIG, character_name="assistant")
vector_db.initialize_database()

# 添加一些文本
texts = [
    "人工智能是计算机科学的一个分支",
    "机器学习是AI的重要组成部分",
    "深度学习使用神经网络进行学习"
]

for text in texts:
    vector_db.add_text(text)

# 检索相关内容
results = vector_db.search("AI和机器学习", top_k=3)
for result in results:
    print(result['text'])

# 保存数据库
vector_db.save_to_file()
```

## 测试

运行测试脚本验证功能：

```bash
python test_memory.py
```

## 注意事项

1. 确保已正确配置环境变量
2. 需要有效的API密钥和网络连接
3. 向量数据库文件会保存在 `data/memory/{character_name}/` 目录下
4. 支持增量添加文本，无需重新构建整个数据库