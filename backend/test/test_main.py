# backend/src/services/file_service.py
import os
import json
import shutil
from datetime import datetime, timezone, timedelta

from flask import current_app
from werkzeug.utils import secure_filename

from backend.src.models.file_record import FileRecord
from backend.config import db, UPLOAD_FOLDER
from backend.src.services.embed import insert_vectors

ALLOWED_EXT = {'.json', '.png', '.jpg', '.jpeg'}


def save_files(files):
    """保存文件到本地、写入数据库、并对 JSON 触发向量化"""
    results = []
    for f in files:
        fname = f.filename
        ext = os.path.splitext(fname)[1].lower()
        if ext not in ALLOWED_EXT:
            continue
        safe = secure_filename(fname)
        dest = os.path.join(UPLOAD_FOLDER, safe)
        f.save(dest)
        size = os.path.getsize(dest)
        rec = FileRecord(
            file_name=safe,
            file_type='json' if ext == '.json' else 'image',
            size=str(size),
            upload_time=datetime.now(timezone(timedelta(hours=8)))
        )
        db.session.merge(rec)
        db.session.commit()
        # 如果是 JSON，调用向量服务
        if rec.file_type == 'json':
            insert_vectors(rec.file_name)
        results.append(rec.to_dict())
    return results


def delete_files(filenames):
    """删除本地文件和数据库记录"""
    results = []
    for name in filenames:
        rec = FileRecord.query.get(name)
        if not rec:
            continue
        path = os.path.join(UPLOAD_FOLDER, name)
        if os.path.isfile(path):
            os.remove(path)
        db.session.delete(rec)
        db.session.commit()
        results.append({'filename': name, 'deleted': True})
    return results


def list_files(page, per_page):
    """分页查询文件列表"""
    pages = FileRecord.query.order_by(FileRecord.upload_time.desc()).paginate(page, per_page, False)
    return pages.items, pages.total


def get_file_record(filename):
    """获取单条文件记录"""
    return FileRecord.query.get_or_404(filename)


def modify_json_file(filename, content, new_name=None):
    """重写 JSON 内容、可选重命名并重新向量化"""
    path = os.path.join(UPLOAD_FOLDER, filename)
    # 写入内容
    with open(path, 'w', encoding='utf-8') as fp:
        fp.write(json.dumps(content, ensure_ascii=False))
    # 重向量化
    insert_vectors(filename)
    return FileRecord.query.get(filename).to_dict()
