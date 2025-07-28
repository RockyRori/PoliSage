# backend/src/services/file_service.py
import os
import json
import shutil
from datetime import datetime, timezone, timedelta

from flask import current_app
from werkzeug.utils import secure_filename
from qdrant_client.http.models import Filter, FieldCondition, MatchValue, PointsSelector
from backend.src.models.file_record import FileRecord
from backend.config import db, qdrant, COLLECTION
from backend.src.services.embed import insert_vectors

ALLOWED_EXT = {'.json', '.png', '.jpg', '.jpeg'}


def get_upload_folder():
    """获取当前应用上下文中的上传目录"""
    return current_app.config['UPLOAD_FOLDER']


def save_files(files):
    """保存文件到本地、写入数据库、并对 JSON 触发向量化"""
    upload_folder = get_upload_folder()
    results = []
    for f in files:
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            continue
        if ext == '.json':
            dest = os.path.join(upload_folder, f.filename)
            f.save(dest)
            size = f"{os.path.getsize(dest) / 1024:.1f}KB"
        else:
            dest = os.path.join(upload_folder, "images", f.filename)
            f.save(dest)
            size = f"{os.path.getsize(dest) / 1024:.1f}KB"

        rec = FileRecord(
            file_name=f.filename,
            file_type='json' if ext == '.json' else 'image',
            file_size=size,
            upload_time=datetime.now(timezone(timedelta(hours=8)))
        )

        db.session.merge(rec)
        db.session.commit()

        # 如果是 JSON，调用向量服务
        if rec.file_type == 'json':
            insert_vectors(rec.file_name)
        results.append(rec.to_dict())
    return results


def delete_file(filename):
    """删除本地文件和数据库记录"""
    results = []
    rec = FileRecord.query.get_or_404(filename)
    upload_folder = get_upload_folder()

    # 删除 json 文件
    json_path = os.path.join(upload_folder, rec.file_name)
    if os.path.isfile(json_path):
        try:
            os.remove(json_path)
            results.append({'filename': rec.file_name, 'deleted': True})
        except Exception as e:
            current_app.logger.warning(f"删除 json 文件失败 {json_path}: {e}")

    # 删除 image 文件
    image_path = os.path.join(upload_folder, "images", rec.file_name)
    if os.path.isfile(image_path):
        try:
            os.remove(image_path)
            results.append({'filename': rec.file_name, 'deleted': True})
        except Exception as e:
            current_app.logger.warning(f"删除 image 文件失败 {image_path}: {e}")

    # 删除数据库记录
    db.session.delete(rec)
    db.session.commit()

    return results


def list_files(page, per_page):
    """分页查询文件列表"""
    pages = FileRecord.query.order_by(FileRecord.upload_time.desc()).paginate(page, per_page, False)
    return pages.items, pages.total


def modify_json_file(filename, content, new_name=None):
    """重写 JSON 内容、可选重新向量化"""
    upload_folder = get_upload_folder()
    path = os.path.join(upload_folder, filename)
    # 写入内容
    with open(path, 'w', encoding='utf-8') as fp:
        fp.write(json.dumps(content, ensure_ascii=False))
    # 删除旧向量（按 payload.filename 匹配）
    qdrant.delete(
        collection_name=COLLECTION,
        points_selector=PointsSelector(
            filter=Filter(
                must=[
                    FieldCondition(
                        key="filename",
                        match=MatchValue(value=filename)
                    )
                ]
            )
        )
    )
    # 重向量化
    insert_vectors(filename)
    return FileRecord.query.get(filename).to_dict()
