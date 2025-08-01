# question.py

from datetime import datetime, timezone, timedelta
from backend.config import db


class Chat(db.Model):
    __tablename__ = 'chats'

    question_id = db.Column(db.String(16), primary_key=True)
    previous_id = db.Column(db.String(16), db.ForeignKey('chats.question_id'), nullable=True)
    created_at = db.Column(
        db.DateTime, nullable=False,
        default=datetime.now(timezone(timedelta(hours=8)))
    )
    question_text = db.Column(db.Text, nullable=False)
    answer_text = db.Column(db.Text, nullable=True)
    reference = db.Column(db.Text, nullable=True)
    feedback = db.Column(db.Text, nullable=True)

    prev = db.relationship('Chat', remote_side=[question_id], backref='next')
