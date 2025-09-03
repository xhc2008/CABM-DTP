import json
import os
import signal
import logging
from datetime import datetime
import traceback
from dotenv import load_dotenv
from .RAG import RAG
class TimeoutError(Exception):
    """超时异常"""
    pass

def timeout_handler(signum, frame):
    """超时处理函数"""
    raise TimeoutError("操作超时")

class ChatHistoryVectorDB:
    def __init__(self, RAG_config: dict, model: str = None, character_name: str = "default", is_story: bool = False):
        """
        初始化向量数据库
        
        参数:
            RAG_config: RAG配置字典
            model: 使用的嵌入模型，如果为None则从环境变量读取
            character_name: 角色名称或故事ID，用于确定数据库文件名
            is_story: 是否为故事模式
        """
        self.config = RAG_config
        self.character_name = character_name
        self.model = model
        self.is_story = is_story
        
        # 设置日志
        self.logger = logging.getLogger(f"MemoryDB_{character_name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
        
        # 根据模式设置数据目录
        if is_story:
            # 故事模式：保存到 data/saves/{story_id}/
            self.data_memory = os.path.join('data', 'saves', character_name)
        else:
            # 角色模式：保存到 data/memory/{character_name}/
            self.data_memory = os.path.join('data', 'memory', character_name)
        
        os.makedirs(self.data_memory, exist_ok=True)    
        
        # 从环境变量读取API配置
        load_dotenv()
        
        # 更新配置中的API参数
        updated_config = RAG_config.copy()
        if 'Multi_Recall' in updated_config and 'Cosine_Similarity' in updated_config['Multi_Recall']:
            embed_kwds = updated_config['Multi_Recall']['Cosine_Similarity']['embed_kwds']
            embed_kwds['base_url'] = os.getenv('BASE_URL')
            embed_kwds['api_key'] = os.getenv('API_KEY')
            embed_kwds['model'] = os.getenv('EMBEDDING_MODEL')
        
        if 'Reranker' in updated_config:
            reranker_kwds = updated_config['Reranker']['reranker_kwds']
            reranker_kwds['base_url'] = os.getenv('BASE_URL')
            reranker_kwds['api_key'] = os.getenv('API_KEY')
            reranker_kwds['model'] = os.getenv('RERANKER_MODEL', 'netease-youdao/bce-reranker-base_v1')
        
        self.rag = RAG(updated_config)
        
    def add_text(self, text: str):
        """
        添加单个文本到向量数据库
        
        参数:
            text: 要添加的文本
            metadata: 可选的元数据字典
        """
        self.rag.add(text)
    
    def search(self, query: str, top_k: int = 5, timeout: int = 10):
        """
        搜索与查询文本最相似的文本（带超时）
        
        参数:
            query: 查询文本
            top_k: 返回的最相似结果数量
            timeout: 超时时间（秒）
            
        返回:
            包含相似结果和元数据的字典列表
            
        异常:
            TimeoutError: 当操作超时时
        """
        
        # 设置超时处理（仅在非Windows系统上）
        if os.name != 'nt':  # 非Windows系统
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        
        try:
            # 获取最相似的top_k个结果
            top_indices = self.rag.req(query=query, top_k=top_k)
            
            results = []
            for text in top_indices:
                result = {  #TODO 去除了<相似度>键, 多路召回后不是都有相似度
                    'text': text
                }
                results.append(result)
            
            # 记录检索结果到日志
            if results:
                self.logger.info(f"记忆检索查询: '{query}' -> 找到 {len(results)} 条相关记录")
                for i, result in enumerate(results, 1):
                    text_preview = result['text'][:50] + "..." if len(result['text']) > 50 else result['text']
                    self.logger.info(f"  记录 {i}: '{text_preview}'")
            else:
                self.logger.info(f"记忆检索查询: '{query}' -> 未找到相关记录")
                
            return results
            
        except TimeoutError:
            self.logger.warning(f"记忆检索超时 ({timeout}秒)")
            return []
        finally:
            # 取消超时设置（仅在非Windows系统上）
            if os.name != 'nt':
                signal.alarm(0)
    
    def save_to_file(self, file_path: str = None):
        """
        将向量数据库保存到文件
        
        参数:
            file_path: 保存路径，如果为None则使用默认路径
        """
        if file_path is None:
            file_path = self.data_memory
        
        # 确保目录存在
        os.makedirs(file_path, exist_ok=True)
        
        rag_save = self.rag.save_to_file(file_path)
        data = {
            'character_name': self.character_name,
            'model': self.model,
            'rag': rag_save,
            'last_updated': datetime.now().isoformat()
        }
        
        # 根据character_name决定文件名
        if self.character_name in ['memory', 'notes']:
            # 对于summarize.py使用的特殊数据库，直接使用character_name.json
            filename = f"{self.character_name}.json"
        else:
            # 对于其他数据库，使用原来的命名方式
            filename = f"{self.character_name}_memory.json"
        
        with open(os.path.join(file_path, filename), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            
        self.logger.info(f"向量数据库已保存到 {os.path.join(file_path, filename)}")

    def load_from_file(self, file_path: str = None):
        """
        从文件加载向量数据库
        
        参数:
            file_path: 加载路径，如果为None则使用默认路径
        """
        self.logger.info("加载向量数据库...")
        
        if file_path is None:
            # 根据character_name决定文件路径
            if self.character_name in ['memory', 'notes']:
                # 对于summarize.py使用的特殊数据库，直接使用character_name.json
                file_path = os.path.join(self.data_memory, f"{self.character_name}.json")
            else:
                # 对于其他数据库，使用原来的命名方式
                file_path = os.path.join(self.data_memory, f"{self.character_name}_memory.json")
        
        if not os.path.exists(file_path):
            self.logger.info(f"数据库文件不存在，将创建新的数据库: {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.character_name = data.get('character_name', self.character_name)
            self.model = data.get('model', self.model)
            self.logger.info(f"加载RAG缓存")
            self.rag.load_from_file(data.get('rag', None))
            self.logger.info(f"向量数据库加载完成，角色: {self.character_name}")
        except Exception as e:
            self.logger.error(f"加载数据库失败: {e}")

    def add_chat_turn(self, user_message: str, assistant_message: str, timestamp: str = None):
        """
        添加一轮对话到向量数据库
        
        参数:
            user_message: 用户消息
            assistant_message: 助手回复
            timestamp: 时间戳，如果为None则使用当前时间
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # 将用户消息和助手回复组合成一个对话单元（用于向量化）
        conversation_text = f"用户: {user_message}\\{self.character_name}: {assistant_message}"
    
        self.add_text(conversation_text)
        self.logger.info(f"添加对话记录到向量数据库: {user_message[:50]}...")
    
    def initialize_database(self):
        """
        初始化数据库（加载现有数据）
        """
        self.load_from_file()
        self.logger.info(f"记忆数据库初始化完成，角色: {self.character_name}")
    
    def get_relevant_memory(self, query: str, top_k: int = 5, timeout: int = 10, min_similarity: float = 0.3) -> str:
        """
        获取相关记忆并格式化为提示词
        
        参数:
            query: 查询文本
            top_k: 返回的最相似结果数量
            timeout: 超时时间（秒）
            min_similarity: 最小相似度阈值
            
        返回:
            格式化的记忆提示词
        """
        try:
            results = self.search(query, top_k, timeout)
            
            if not results:
                return ""
                    
            # 格式化为提示词
            memory_prompt = "这是唤醒的记忆，可以作为参考：\n```\n" + \
                '\n'.join([r['text'] for r in results])
            
            memory_prompt += "\n```\n以上是记忆而不是最近的对话，可以不使用。"
            
            self.logger.info(f"生成记忆提示词: {len(memory_prompt)} 字符")
            self.logger.debug(f"生成的记忆提示词内容: {memory_prompt}")
            return memory_prompt
            
        except Exception as e:
            self.logger.error(f"获取相关记忆失败: {e}")
            traceback.print_exc()
            return ""


    def build_from_file(self, file_path: str):
        """
        从文件构建向量数据库
        
        参数:
            file_path: 文件路径
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件 {file_path} 不存在")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的文本分段处理
            # 可以根据需要调整分段策略
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            
            for paragraph in paragraphs:
                if len(paragraph) > 10:  # 过滤太短的段落
                    self.add_text(paragraph)
            
            self.logger.info(f"从文件 {file_path} 构建向量数据库完成，共添加 {len(paragraphs)} 个段落")
            
        except Exception as e:
            self.logger.error(f"从文件构建向量数据库失败: {e}")
            raise


# 使用示例
if __name__ == "__main__":
    # 初始化向量数据库（从环境变量自动读取配置）
    from config import RAG_CONFIG
    vector_db = ChatHistoryVectorDB(RAG_CONFIG)
    
    print("初始化完成")

    vector_db.add_text('测试文本1')
    print("加载完成")
    
    # 搜索相似文本
    results = vector_db.search("静流的外号", top_k=5)  # 使用默认值
    print("搜索结果:")
    for res in results:
        print(f"文本: {res['text']}")