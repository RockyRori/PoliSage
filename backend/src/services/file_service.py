# backend/src/services/file_service.py
import os
import json
from datetime import datetime, timezone, timedelta
from PIL import Image
from flask import current_app
from backend.src.models.file_record import FileRecord
from backend.config import db, qdrant, COLLECTION, UPLOAD_FOLDER
from backend.src.services.embed import insert_vectors, delete_vectors

ALLOWED_EXT = {'.json', '.png', '.jpg', '.jpeg'}


def save_files(files):
    """保存文件到本地、写入数据库、并对 JSON 触发向量化"""
    upload_folder = UPLOAD_FOLDER
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
    upload_folder = UPLOAD_FOLDER

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
    upload_folder = UPLOAD_FOLDER
    path = os.path.join(upload_folder, filename)
    # 写入内容
    with open(path, 'w', encoding='utf-8') as fp:
        fp.write(json.dumps(content, ensure_ascii=False))
    # 删除旧向量（按 payload.filename 匹配）
    delete_vectors(filename)
    # 重向量化
    insert_vectors(filename)
    return FileRecord.query.get(filename).to_dict()


def generate_image_captions(filename: str) -> dict:
    """
    1. 加载指定 JSON 文件
    2. 遍历所有 item, 对 type==text/equation/table/image
    3. 更新 JSON 并重写文件
    4. 删除旧向量 & 重新向量化该 JSON
    5. 返回更新了多少段
    """
    upload_folder = UPLOAD_FOLDER
    json_path = os.path.join(upload_folder, filename)
    data = json.load(open(json_path, 'r', encoding='utf-8'))
    print(data)
    count = 0
    for item in data:
        if item.get('type') == 'text':
            # 无需修改
            pass
        elif item.get('type') == 'equation':
            # 无需修改
            pass
        elif item.get('type') == 'table':
            # 移动 table_body 到 text
            if not item.get('text'):
                item['text'] = item.get('table_body')
                count += 1
        elif item.get('type') == 'image':
            # 移动 image_caption 和 image_footnote 到 text
            if not item.get('text'):
                image_caption = "".join(item.get('image_caption'))
                image_footnote = "".join(item.get('image_footnote'))
                text = image_caption + image_footnote
                if len(text) == 0:
                    img_rel = item.get('img_path')  # e.g. "images/xxx.jpg"
                    img_path = os.path.join(upload_folder, img_rel)
                    if os.path.exists(img_path):
                        # 调用你的 caption 模型
                        text = generate_caption_for_image(img_path)
                else:
                    image_caption = "None" if len(image_caption) == 0 else image_caption
                    image_footnote = "None" if len(image_footnote) == 0 else image_footnote
                    text = ("image_caption: " + image_caption + " image_footnote: " + image_footnote)
                item['text'] = text
                count += 1

    # 重写 JSON 文件
    with open(json_path, 'w', encoding='utf-8') as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)

    # 先删除旧向量
    delete_vectors(filename)
    # 重新向量化整个 JSON
    insert_vectors(filename)

    return {'filename': filename, 'captions_generated': count}


def generate_caption_for_image(img_path) -> str:
    Image.open(img_path)
    return "wait for next step"


# 示例运行
if __name__ == "__main__":
    print(generate_image_captions("test.json"))
