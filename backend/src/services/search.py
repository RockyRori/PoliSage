import os
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from transformers import AutoTokenizer, AutoModel
import torch

# 配置
COLLECTION = "PoliSage"

# 初始化 Qdrant 客户端
client = QdrantClient(url="http://localhost:6333")

# 使用多语言模型（支持简体/繁体中文 + 英语）
tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
model = AutoModel.from_pretrained('bert-base-multilingual-cased')


# 生成完整文件路径


# 文本编码函数
def encode_text(text):
    if not text or len(text.strip()) == 0:
        return None
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy().tolist()


# 插入向量到 Qdrant

def get_collection_point_count(collection_name):
    try:
        info = client.get_collection(collection_name=collection_name)
        return info.points_count
    except Exception as e:
        print(f"⚠️ 获取集合信息失败: {e}")
        return 0


# 查询相似内容
def search_similar(query_text, top_k=5):
    vector = encode_text(query_text)
    if vector is None:
        print("⚠️ 输入文本为空，无法查询。")
        return
    # 获取集合中实际的向量数量
    total_points = get_collection_point_count(COLLECTION)
    actual_limit = min(top_k, total_points)

    if total_points == 0:
        print("❌ 数据库中没有可查询的向量。")
        return
    hits = client.query_points(
        collection_name=COLLECTION,
        query=vector,
        limit=actual_limit,
        with_payload=True
    )
    return hits


def result_understand(hits):
    print(f"🔍 找到 {len(hits.points)} 条最相似记录：")
    for point in hits.points:
        payload = point.payload
        if payload["type"] == "text":
            print(
                f"- ID={point.id}, Score={point.score:.4f}, Type=text, Page={payload['page_idx']}, Text='{payload['content'][:400]}...'")  # 限制输出长度
        elif payload["type"] == "image":
            print(
                f"- ID={point.id}, Score={point.score:.4f}, Type=image, Page={payload['page_idx']}, Caption='{payload['caption']}', ImagePath='{payload['img_path']}'")


# 示例运行
if __name__ == "__main__":
    # 示例查询
    query = "技术创新"
    print(f"\n🔎 查询文本：'{query}'")
    answer = search_similar(query, top_k=3)
    result_understand(answer)

    query = "封面图片"
    print(f"\n🔎 查询文本：'{query}'")
    answer = search_similar(query, top_k=3)
    result_understand(answer)
