# backend/src/app.py

import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS

from backend.config import Config, UPLOAD_FOLDER
from backend.src.routes.file_routes import file_bp
from backend.src.routes.chat_routes import chat_bp
from backend.config import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 1) 跨域配置
    allowed_origins = [
        "http://localhost:5173",
        "http://172.20.41.146:5173",
    ]
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

    # 确保上传目录存在
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_FOLDER, 'images'), exist_ok=True)

    # 初始化数据库
    db.init_app(app)
    migrate = Migrate(app, db)

    # 注册蓝图
    app.register_blueprint(file_bp)
    app.register_blueprint(chat_bp)

    return app


if __name__ == '__main__':
    # 直接运行时启动开发服务
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
