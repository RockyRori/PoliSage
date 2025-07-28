import os

from flask import Blueprint, request, jsonify, current_app, send_from_directory

from backend.src.models.file_record import FileRecord
from backend.src.services.file_service import save_files, delete_file, list_files, modify_json_file

file_bp = Blueprint('file_bp', __name__, url_prefix='/api/files')


# 列表查询
@file_bp.route('', methods=['GET'])
def list_files():
    recs = FileRecord.query.order_by(FileRecord.upload_time.desc()).all()
    return jsonify([r.to_dict() for r in recs])


# 批量上传
@file_bp.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files provided'}), 400
    results = save_files(files)
    return jsonify(results), 201


# 批量删除
@file_bp.route('/<file_name>', methods=['DELETE'])
def delete(file_name):
    rec = FileRecord.query.get_or_404(file_name)
    if not rec.file_name:
        return jsonify({'error': 'No filenames provided'}), 400
    results = delete_file(file_name)
    return jsonify(results), 200


# 在线查看单个
@file_bp.route('/<filename>', methods=['GET'])
def view_file(filename):
    rec = FileRecord.query.get_or_404(filename)
    base_folder = current_app.config['UPLOAD_FOLDER']
    if rec.file_type == 'image':
        folder = os.path.join(base_folder, 'images')
    else:
        folder = base_folder
    return send_from_directory(folder, filename)


# 修改 JSON
@file_bp.route('/<filename>', methods=['PUT'])
def update(filename):
    if not filename.endswith('.json'):
        return jsonify({'error': 'Only JSON files can be modified'}), 400
    data = request.get_json()
    content = data.get('content')
    result = modify_json_file(filename, content)
    return jsonify(result), 200
