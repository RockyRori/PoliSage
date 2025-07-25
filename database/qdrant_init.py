from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance


def init_qdrant():
    # 1. 连接到本地 Qdrant 服务
    client = QdrantClient(url="http://localhost:6333")

    collection_name = "PoliSage"

    # 2. 列出所有 collections 并检查目标是否已存在
    resp = client.get_collections()
    existing = [col.name for col in resp.collections]

    if collection_name in existing:
        print(f"ℹ️ Collection '{collection_name}' 已存在，跳过创建")
    else:
        # 3. 不存在则创建：768 维向量，Cosine 相似度
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )
        print(f"✅ Collection '{collection_name}' 已创建")


if __name__ == "__main__":
    init_qdrant()
