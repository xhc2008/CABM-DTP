from typing import List, Union
import logging
from importlib import import_module
from traceback import print_exc
import traceback
# from langchain.vectorstores import FAISS

class Retriever:
    def __init__(self, config: dict):
        self.logger = logging.getLogger(f"Retriever")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
        self.config = config

        self.initialize()
        
    def save_to_file(self, file_path: str):
        dic = {}
        for recall_func in self.recall_dict:
            dic[recall_func] = self.recall_dict[recall_func].save_to_file(file_path)
        dic['id_to_doc'] = self.id_to_doc
        return dic
    
    def load_from_file(self, data_dict: dict):
        self.id_to_doc = data_dict['id_to_doc'].copy()
        self.id_to_doc = {int(k): v for k, v in self.id_to_doc.items()}  # 确保id是int类型
        for recall_func in self.recall_dict:
            self.recall_dict[recall_func].load_from_file(data_dict)
        return self
            
    def initialize(self):
        self.recall_config = self.config['Multi_Recall']
        self.id_to_doc = {}  # 用于存储文档的映射
        self.recall_dict = {}
        for recall_func in self.recall_config:
            self.logger.info(f"Loading {recall_func}...")
            func_kwds = self.recall_config[recall_func]
            try:
                module = import_module(f"services.RAG.Multi_Recall.{recall_func}")  # 动态导入包
            except Exception as e:
                self.logger.error(f"Error loading {recall_func}: {e}")
                print_exc()
                continue
            try:
                self.recall_dict[recall_func] = getattr(module, recall_func)(**func_kwds)  # 创建召回对象
            except Exception as e:
                self.logger.error(f"Error creating {recall_func}: {e}")
                print_exc()
                continue
        return self
    
    def process_corpus(self, corpus: Union[List[str], str]) -> List[str]:  # 进行如分段, 去除标点等前处理操作
        return corpus
    
    def add(self, corpus: Union[List[str], str]) -> None:
        if isinstance(corpus, str):
            corpus = [corpus]
        corpus = self.process_corpus(corpus)  # 前处理
        self.logger.info(f"Process {len(corpus)} documents")
        
        for recall_func, recall_module in self.recall_dict.items():  # 循环添加
            self.logger.info(f"Adding {recall_func}...")
            recall_module.add(corpus, self.id_to_doc)
        
        starId = len(self.id_to_doc)  # 更新id_to_doc
        for doc in corpus:
            self.id_to_doc[starId] = doc
            starId += 1
        return self
    def retrieval(self, query, 
                  methods = None,
                  top_k = 10
                  ) -> List[str]:
        search_res = list()
        if methods is None:
            methods = list(self.recall_dict.keys())
        for method in methods:
            if method in self.recall_dict:
                res = self.recall_dict[method].retrieval(query, self.id_to_doc, top_k)
                search_res.extend(res)
        search_res = list(set(search_res))  # 结果去重
        return search_res

    def remove_by_query(self, query: str, threshold: float = None, methods = None, max_remove_count: int = None) -> List[int]:
        """
        根据查询删除高于阈值的记录
        
        参数:
            query: 查询文本
            threshold: 相似度阈值，如果为None则从配置中读取
            methods: 使用的召回方法列表，如果为None则使用所有方法
            max_remove_count: 最大删除数量，如果为None则从配置中读取
            
        返回:
            被删除的文档ID列表
        """
        # 从配置中获取默认值
        if threshold is None:
            threshold = self.config.get('Remove', {}).get('threshold', 0.75)
        if max_remove_count is None:
            max_remove_count = self.config.get('Remove', {}).get('max_remove_count', 10)
            
        if methods is None:
            methods = list(self.recall_dict.keys())
        
        all_removed_ids = []
        
        for method in methods:
            if method in self.recall_dict and hasattr(self.recall_dict[method], 'remove_by_query'):
                removed_ids = self.recall_dict[method].remove_by_query(query, self.id_to_doc, threshold)
                all_removed_ids.extend(removed_ids)
                self.logger.info(f"方法 {method} 删除了 {len(removed_ids)} 条记录")
        
        # 限制删除数量
        unique_removed_ids = sorted(set(all_removed_ids), reverse=True)
        if len(unique_removed_ids) > max_remove_count:
            self.logger.warning(f"删除数量 {len(unique_removed_ids)} 超过限制 {max_remove_count}，将只删除前 {max_remove_count} 条")
            unique_removed_ids = unique_removed_ids[:max_remove_count]
        
        # 从id_to_doc中删除对应的记录
        removed_docs = []
        for doc_id in unique_removed_ids:
            if doc_id in self.id_to_doc:
                removed_doc = self.id_to_doc.pop(doc_id)
                removed_docs.append(removed_doc)
                self.logger.info(f"删除文档 ID {doc_id}: {removed_doc[:50]}...")
        
        # 重新整理id_to_doc的索引
        self._reindex_documents()
        
        return sorted(unique_removed_ids)
    
    def _reindex_documents(self):
        """重新整理文档索引，确保索引连续"""
        if not self.id_to_doc:
            return
            
        # 获取所有文档内容
        docs = list(self.id_to_doc.values())
        
        # 清空原有映射
        self.id_to_doc.clear()
        
        # 重新建立连续的索引映射
        for i, doc in enumerate(docs):
            self.id_to_doc[i] = doc
        
        self.logger.info(f"重新索引完成，当前文档数量: {len(self.id_to_doc)}")

if __name__ == "__main__":
    from config import RAG_CONFIG
    vector_db = Retriever(config=RAG_CONFIG)
    
    # 测试数据
    test_docs = ["这是测试文档1", "这是测试文档2", "关于镜流的信息"]
    vector_db.add(test_docs)
    
    print(vector_db.retrieval('镜流的属性', top_k=1, methods=['Cosine_Similarity']))