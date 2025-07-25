from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, VectorParams, Distance

# 1. 初始化客户端
client = QdrantClient(url="http://localhost:6333")

COLLECTION = "poli_sage_multimodal"


# 2. 插入向量（Upsert）
def insert_vectors():
    # 示例数据：3 条不同模态的点
    points = [
        PointStruct(
            id=1,
            vector=[0.01 * i for i in range(768)],  # 示例 embedding
            payload={
                "text": "这是一个示例文本",
                "image_url": "http://example.com/image1.jpg",
                "table": {"col1": [1, 2], "col2": ["A", "B"]}
            }
        ),
        PointStruct(
            id=2,
            vector=[0.02 * i for i in range(768)],
            payload={
                "text": "第二条带图像和表格的示例",
                "image_url": "http://example.com/image2.png",
                "table": {"col1": [3, 4], "col2": ["C", "D"]}
            }
        ),
        PointStruct(
            id=3,
            vector=[0.03 * i for i in range(768)],
            payload={"text": "仅文本示例"}
        ),
    ]
    # 批量 upsert
    client.upsert(
        collection_name=COLLECTION,
        points=points,
        wait=True  # 同步等待写入完成
    )
    print(f"✅ 已插入 {len(points)} 个向量点。")


# 3. 根据查询向量检索（Search）
def search_similar(query_vector, top_k=5):
    hits = client.search(
        collection_name=COLLECTION,
        query_vector=query_vector,
        limit=top_k,
        with_payload=True  # 同时返回 payload
    )
    print(f"🔍 找到 {len(hits)} 条最相似记录：")
    for hit in hits:
        print(f"- id={hit.id}, score={hit.score:.4f}, payload={hit.payload}")


# 4. 示例运行
if __name__ == "__main__":
    # 先插入
    # insert_vectors()

    # 构造一个示例查询向量
    query_vec = [0.015 * i for i in range(768)]

    # 再执行检索
    search_similar(query_vec, top_k=3)
