import os
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct
from transformers import AutoTokenizer, AutoModel
import torch

from backend.config import Config

# 配置
COLLECTION = "PoliSage"

# 初始化 Qdrant 客户端
client = QdrantClient(url="http://localhost:6333")

# 使用多语言模型（支持简体/繁体中文 + 英语）
tokenizer = AutoTokenizer.from_pretrained('bert-base-multilingual-cased')
model = AutoModel.from_pretrained('bert-base-multilingual-cased')


# 生成完整文件路径
def get_json_file_path(json_name):
    if not json_name.endswith(".json"):
        json_name += ".json"
    config = Config()
    return os.path.join(config.UPLOAD_FOLDER, json_name)


# 文本编码函数
def encode_text(text):
    if not text or len(text.strip()) == 0:
        return None
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    return outputs.last_hidden_state[:, 0, :].squeeze().numpy().tolist()


# 插入向量到 Qdrant
def insert_vectors(file_name):
    json_path = get_json_file_path(file_name)

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    points = []
    unique_id = 1  # 生成唯一 ID

    for item in data:
        item_type = item.get("type")
        page_idx = item.get("page_idx", -1)
        text = item.get("text", "")
        img_path = item.get("img_path", "")
        vector = encode_text(text)
        if vector is None:
            print(f"⚠️ 跳过空文本块，page_idx={page_idx}")
            continue
        payload = {
            "file_name": file_name,
            "type": item_type,
            "page_idx": page_idx,
            "text": text,
            "img_path": img_path
        }
        points.append(PointStruct(id=unique_id, vector=vector, payload=payload))
        unique_id += 1

    if points:
        client.upsert(
            collection_name=COLLECTION,
            points=points,
            wait=True
        )
        print(f"✅ 已插入 {len(points)} 个向量点。")
    else:
        print("❌ 没有可插入的向量。")


# 示例运行
if __name__ == "__main__":
    json_name = "input"  # 或 "abc.json"

    # 插入数据
    insert_vectors(json_name)
