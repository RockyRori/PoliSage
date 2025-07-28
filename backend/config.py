import os
from flask_sqlalchemy import SQLAlchemy
from qdrant_client import QdrantClient

# 初始化 Qdrant 客户端
qdrant = QdrantClient(url="http://localhost:6333")
COLLECTION = "PoliSage"
db = SQLAlchemy()


class Config:
    # 格式："mysql+pymysql://<自己电脑的数据库名称>:<自己电脑的数据库密码>@localhost:3306/docmind?charset=utf8mb4"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:qwertyuiop@localhost:3306/polisage?charset=utf8mb4"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 上传与生成文件都放在这里
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
