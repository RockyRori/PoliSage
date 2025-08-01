# backend/src/services/chat_service.py
import uuid
from datetime import datetime, timezone, timedelta
from flask import current_app

from qdrant_client.http.models import ScoredPoint

from backend.src.llms.adapter import generate_answer
from backend.config import db, qdrant, COLLECTION
from backend.src.models.question import Question
from backend.src.services.embed import encode_text
from backend.src.services.search import search_similar


def process_query(question_text: str) -> dict:
    """
    1. 为问题生成唯一 16 位 ID
    2. 对问题进行向量编码并在 Qdrant 检索相似文档
    3. 基于返回的文档片段调用 LLM 生成回答
    4. 存储问题、回答及引用文档原文到 MySQL
    5. 返回 { question_id, answer }
    """
    # 1. 生成 ID
    qid = uuid.uuid4().hex[:16]

    # 2. 向量检索
    hits = search_similar(question_text, top_k=10)
    # 提取参考文本
    snippets = [hit.payload.get('text', '') + hit.payload.get('img_path', '') for hit in hits.points]
    reference = "\n".join(snippets)

    # 3. 调用 LLM 生成回答
    answer = generate_answer(question_text, reference)

    # 4. 写入数据库
    q = Question(
        questions_id=qid,
        prev_id=None,
        created_at=datetime.now(timezone(timedelta(hours=8))),
        question_text=question_text,
        answer_text=answer,
        reference=reference,
        feedback=None
    )
    db.session.add(q)
    db.session.commit()

    # 5. 返回
    return {'question_id': qid, 'answer': answer}


def record_feedback(question_id: str, rating: int, comments: str = '') -> None:
    """
    更新指定问题的 feedback 字段，存储用户评分及可选备注。
    """
    q = Question.query.get(question_id)
    if not q:
        raise ValueError(f"Question {question_id} not found")
    # 拼接评分与备注
    feedback_entry = f"Rating={rating}"
    if comments:
        feedback_entry += f"; Comments={comments}"
    q.feedback = feedback_entry
    db.session.commit()


# 示例运行
if __name__ == "__main__":
    process_query("what to do next")
