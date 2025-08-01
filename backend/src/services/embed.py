import json
import os
from typing import Optional

import torch
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
from qdrant_client.http.models import PointStruct, FilterSelector
from transformers import AutoTokenizer, AutoModel

from backend.config import qdrant, COLLECTION, UPLOAD_FOLDER


class BertLoader:
    """
    封装 Hugging Face 的 BERT tokenizer 和 model 加载逻辑。
    如果初始化失败，会抛出详细错误信息。
    """

    def __init__(self, model_name: str = 'bert-base-multilingual-cased'):
        """
        初始化并加载 tokenizer 和 model。

        Args:
            model_name (str): 预训练模型名称，默认为 'bert-base-multilingual-cased'。

        Raises:
            RuntimeError: 如果加载失败，包含具体错误信息。
        """
        self.model_name = model_name
        self.tokenizer: Optional[AutoTokenizer] = None
        self.model: Optional[AutoModel] = None

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
            self.model = AutoModel.from_pretrained(model_name, local_files_only=True)
        except Exception as e:
            raise RuntimeError(
                f"Failed to load tokenizer or model '{model_name}'. Error: {str(e)}"
            )

    @property
    def get_tokenizer(self):
        """返回 tokenizer，如果未加载则抛出错误。"""
        if self.tokenizer is None:
            raise RuntimeError("Tokenizer not loaded! Check initialization.")
        return self.tokenizer

    @property
    def get_model(self):
        """返回 model，如果未加载则抛出错误。"""
        if self.model is None:
            raise RuntimeError("Model not loaded! Check initialization.")
        return self.model


# 生成完整文件路径
def get_json_file_path(json_name):
    if not json_name.endswith(".json"):
        json_name += ".json"
    return os.path.join(UPLOAD_FOLDER, json_name)


# 文本编码函数
def encode_text(text):
    if not text or len(text.strip()) == 0:
        return None

    bert_loader = BertLoader('bert-base-multilingual-cased')
    inputs = bert_loader.get_tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    with torch.no_grad():
        outputs = bert_loader.get_model(**inputs)
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
        qdrant.upsert(
            collection_name=COLLECTION,
            points=points,
            wait=True
        )
        print(f"✅ 已插入 {len(points)} 个向量点。")
    else:
        print("❌ 没有可插入的向量。")


def delete_vectors(file_name):
    """使用 FilterSelector 按 file_name 删除所有点。"""
    selector = FilterSelector(
        filter=Filter(
            must=[
                FieldCondition(
                    key="file_name",
                    match=MatchValue(value=file_name)
                )
            ]
        )
    )
    resp = qdrant.delete(
        collection_name=COLLECTION,
        points_selector=selector,
        wait=True
    )
    print(f"🗑️ 已调用 delete() 删除 file_name={file_name} 对应的向量点。")


# 示例运行
if __name__ == "__main__":
    json_name = "input"

    # 插入数据
    insert_vectors(json_name)
    # 删除数据
    delete_vectors(json_name)
