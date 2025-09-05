from abc import ABC, abstractmethod
from typing import List, Dict
import logging
__all__ = ['Retriever', 'tqdm', 'logger']

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, *args, **kwargs):
        return iterable
    
class Retriever(ABC):
    @abstractmethod
    def __init__(self, *args, **kwargs):
        pass
    
    @abstractmethod
    def add(self,
            corpus: List[str] | str,  # 新增文档
            id_to_doc: Dict[int, str]  # 已有的文档id_to_doc
            ):
        pass

    @abstractmethod
    def retrieval(self, 
                  query: str,  # 查询字符串
                  id_to_doc: Dict[int, str],  # 文档id_to_doc  
                  top_k: int = 10  # 召回文档数目
                  ):
        pass
    
    @abstractmethod
    def save_to_file(self, file_path: str):
        pass
    
    @abstractmethod
    def load_from_file(self, data_dict: dict):
        pass

    def remove_by_query(self, 
                       query: str, 
                       id_to_doc: Dict[int, str], 
                       threshold: float = None
                       ) -> List[int]:
        """
        根据查询删除高于阈值的记录（可选实现）
        
        参数:
            query: 查询文本
            id_to_doc: 文档id到文档内容的映射
            threshold: 相似度阈值
            
        返回:
            被删除的文档ID列表
        """
        # 默认实现：不支持删除操作
        logger.warning(f"当前召回方法不支持删除操作")
        return []

logger = logging.getLogger(f"Recall Loading")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)