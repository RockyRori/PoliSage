# file_record.py

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone, timedelta

db = SQLAlchemy()


class FileRecord(db.Model):
    __tablename__ = 'files'

    file_name = db.Column(db.String(255), primary_key=True)
    file_type = db.Column(db.Enum('json', 'image', name='file_types'), nullable=False)
    upload_time = db.Column(
        db.DateTime, nullable=False,
        default=datetime.now(timezone(timedelta(hours=8)))
    )
    size = db.Column(db.String(28), nullable=False)

    @property
    def json_url(self):
        # 仅对 JSON 文件有效
        if self.file_type == 'json':
            return f"{['API_BASE']}/files/{self.filename}"
        return None
