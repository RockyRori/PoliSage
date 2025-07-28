# run.py
from backend.app import create_app

app = create_app()

if __name__ == "__main__":
    # 可选：你也可以在这里设置 debug、host、port
    app.run(host="0.0.0.0", port=5000, debug=True)
