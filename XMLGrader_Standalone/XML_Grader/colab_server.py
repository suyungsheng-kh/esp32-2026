"""Colab 專用啟動器；API 與評分邏輯由共用模組提供。"""
import os
import threading
from api_server import app, SERVER_VERSION
from werkzeug.serving import make_server

_server = None
_thread = None

def serve_background():
    global _server, _thread
    from pyngrok import ngrok
    token = os.environ.get("XMLGRADER_NGROK_AUTHTOKEN", "").strip()
    if not token:
        raise RuntimeError("🔴 請先完成 Notebook 步驟 4 的 XMLGRADER_NGROK_AUTHTOKEN。")
    port = int(os.environ.get("XMLGRADER_PORT", "5000"))
    if _server is not None:
        _server.shutdown()
        _server.server_close()
    _server = make_server("0.0.0.0", port, app, threaded=True)
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()
    ngrok.set_auth_token(token)
    ngrok.kill()
    domain = os.environ.get("XMLGRADER_NGROK_STATIC_DOMAIN", "").strip()
    public_url = ngrok.connect(port, **({"domain": domain} if domain else {})).public_url
    print(f"✅ API 已上線（背景執行）：{public_url}")
    print(f"版本：{SERVER_VERSION}")
    print(f"健康檢查：{public_url}/api/health")
    print("🔴 將根網址填入網站 grader-settings.js 的 serverUrl，再重新發布網站。")
    return public_url

def start():
    serve_background()
    _thread.join()

if __name__ == "__main__":
    start()
