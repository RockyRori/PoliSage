from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter

COLLECTION = "PoliSage"

# 初始化客户端
client = QdrantClient(url="http://localhost:6333")


def clear_collection_points(collection_name):
    try:
        # 使用 delete 接口 + 空 Filter 删除所有点
        client.delete(
            collection_name=collection_name,
            points_selector=Filter(),  # 空 Filter 表示匹配所有点
            wait=True
        )
        print(f"✅ 集合 '{collection_name}' 中的所有向量已成功删除。")
    except Exception as e:
        print(f"❌ 删除向量失败：{e}")


if __name__ == "__main__":
    clear_collection_points(COLLECTION)
