"""相容舊路徑；部署時使用 XML_Grader 根目錄的共用 api_server。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api_server import app, SERVER_VERSION

if __name__ == "__main__":
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
