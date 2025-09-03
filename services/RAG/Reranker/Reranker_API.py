import requests
class Reranker_API:
    def __init__(self, base_url, api_key, model):
        self.api_key = api_key
        self.model = model
        self.api_base = base_url.rstrip("/")

    def rerank(self, docs, query, k=5):
        docs_ = []
        for item in docs:
            if isinstance(item, str):
                docs_.append(item)
            else:
                docs_.append(item.page_content)
        docs = list(set(docs_))
        url = f"{self.api_base}/rerank"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "query": query,
            "documents": docs,
            "top_n": k,
            "return_documents": False
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json()["results"]
        # 按得分排序并返回文档索引
        idx_score = [(r["index"], r["relevance_score"]) for r in results]
        idx_score = sorted(idx_score, key=lambda x: x[1], reverse=True)
        docs_ = [docs[idx] for idx, _ in idx_score]
        return docs_[:k]

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()
    reranker = Reranker_API(base_url=os.getenv('BASE_URL'),
                        api_key=os.getenv('API_KEY'),
                        model=os.getenv('RERANKER_MODEL', 'netease-youdao/bce-reranker-base_v1'))
    docs = ['这是关于镜流的信息', '镜流是一个角色', '镜流的属性很强', '其他无关信息']
    query = '镜流的属性数据'
    print(reranker.rerank(docs, query, k=2))