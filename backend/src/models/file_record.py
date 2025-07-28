# file_record.py

from datetime import datetime, timezone, timedelta
from backend.config import db


class FileRecord(db.Model):
    __tablename__ = 'files'

    file_name = db.Column(db.String(255), primary_key=True)
    file_type = db.Column(db.Enum('json', 'image', name='file_types'), nullable=False)
    file_size = db.Column(db.String(28), nullable=False)
    upload_time = db.Column(
        db.DateTime, nullable=False,
        default=datetime.now(timezone(timedelta(hours=8)))
    )

    @property
    def json_url(self):
        # 仅对 JSON 文件有效
        if self.file_type == 'json':
            return f"/api/files/{self.file_name}"
        return None

    @property
    def image_url(self):
        # 仅对 image 文件有效
        if self.file_type == 'image':
            return f"/api/files/{self.file_name}"
        return None

    def to_dict(self):
        return {
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "upload_time": self.upload_time.strftime("%Y/%m/%d %H:%M:%S"),

            "json_url": self.json_url,
            "image_url": self.image_url
        }
