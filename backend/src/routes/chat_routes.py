from flask import Blueprint, request, jsonify
from backend.src.services.chat_service import process_query, record_feedback

chat_bp = Blueprint('chat_bp', __name__, url_prefix='/api/chat')


# 问答接口
@chat_bp.route('/query', methods=['POST'])
def chat_query():
    data = request.get_json()
    question = data.get('question')
    previous_id = data.get('previous_id')
    model = data.get('model')
    language = data.get('language')
    if not question:
        return jsonify({'error': 'Question is required'}), 400
    response = process_query(question, previous_id, model, language)
    return jsonify(response), 200


# 回答质量评价接口
@chat_bp.route('/feedback', methods=['POST'])
def chat_feedback():
    data = request.get_json()
    question_id = data.get('question_id')
    rating = data.get('rating')
    comments = data.get('comments', '')
    if not question_id or rating is None:
        return jsonify({'error': 'question_id and rating are required'}), 400
    record_feedback(question_id, rating, comments)
    return jsonify({'status': 'ok'}), 200
