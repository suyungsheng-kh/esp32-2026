"""由唯一後端來源產生根目錄 Notebook；不要直接編輯產生的 Python 儲存格。"""
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def cell(kind, source):
    entry = {"cell_type": kind, "metadata": {}, "source": source.splitlines(keepends=True)}
    if kind == "code":
        entry.update(execution_count=None, outputs=[])
    return entry


CONFIG = '''# 🔴 部署設定（對應 README「15 分鐘設定檢查表／後端必改清單」）
# 所有私密值在 Colab 左側 Secrets 填寫並允許此 Notebook 存取。
import os, json, importlib, sys
from google.colab import userdata

def read_secret(name, required=False):
    try:
        value = userdata.get(name) or ""
    except Exception:
        value = ""
    if required and not value.strip():
        raise ValueError(f"🔴 請先在 Colab Secrets 填寫 {name}，並允許 Notebook 存取。")
    return value.strip()

# 🔴 必填 3 個 Secrets（不要將實際值寫入此儲存格）
for name in ("XMLGRADER_NGROK_AUTHTOKEN", "XMLGRADER_GEMINI_API_KEY_1", "XMLGRADER_ADMIN_TOKEN"):
    os.environ[name] = read_secret(name, required=True)
os.environ["XMLGRADER_GEMINI_API_KEY_2"] = read_secret("XMLGRADER_GEMINI_API_KEY_2")  # 選填備援

# 🔴 可修改：連線與儲存方式
NGROK_STATIC_DOMAIN = ""  # 選填：自己的固定網域；留空時每次產生新網址。
CORS_ORIGINS = "*"  # 正式發布可填網站 origin，例如 https://your-name.github.io（不含路徑）。
USE_FIREBASE = False  # 初次使用保持 False；需要跨課保留資料才啟用。
CONFIG_PATH = "/content/XMLGrader/grader_config.json"  # 可改成已掛載 Google Drive 的檔案路徑。

os.environ["XMLGRADER_NGROK_STATIC_DOMAIN"] = NGROK_STATIC_DOMAIN.strip()
os.environ["XMLGRADER_CORS_ORIGINS"] = CORS_ORIGINS
os.environ["XMLGRADER_CONFIG_PATH"] = CONFIG_PATH
os.environ["XMLGRADER_FIREBASE_ENABLED"] = str(USE_FIREBASE).lower()
if USE_FIREBASE:
    # 🔴 改用服務帳戶：不需要 Web API key，不要把 Firestore 規則設成公開。
    os.environ["XMLGRADER_FIREBASE_PROJECT_ID"] = read_secret("XMLGRADER_FIREBASE_PROJECT_ID", True)
    os.environ["XMLGRADER_FIREBASE_SERVICE_ACCOUNT_JSON"] = read_secret("XMLGRADER_FIREBASE_SERVICE_ACCOUNT_JSON", True)

# 🔴 以下是首次初始化用的作業，教師登入 teacher.html 後可編輯多份作業。
MODEL_NAME = "gemini-2.5-flash"
SHOW_SCORE_TO_STUDENT = True
REPLACE_SAVED_RUBRICS = False  # 只有確定要覆蓋教師已儲存的規則才改為 True。
RUBRICS = [{
    "id": "day1-traffic-light", "name": "Day 1 有聲紅綠燈", "theme": "有聲紅綠燈",
    "rules": "1. 正確設定紅、黃、綠 LED 腳位（30 分）\\n2. 依序控制燈號（40 分）\\n3. 蜂鳴器提示與合理等待時間（30 分）",
    "is_open": True, "is_standard_answer": False,
    "template_code": "", "example_code": "",
}]

# 如需重跑設定，先停止舊伺服器，讓新設定確實生效。
old = sys.modules.get("colab_server")
if old and getattr(old, "_server", None):
    old._server.shutdown()
    old._server.server_close()
import xml_grader_core as core
importlib.reload(core)
cfg = core.load_config()
if REPLACE_SAVED_RUBRICS or not core.get_rubrics(cfg):
    cfg.update(model_name=MODEL_NAME, student_show_score=SHOW_SCORE_TO_STUDENT,
               rubrics_json=json.dumps(RUBRICS, ensure_ascii=False))
    core.save_config(cfg)
import api_server
importlib.reload(api_server)
print("✅ 部署設定完成；教師密碼與 Gemini 金鑰只保留在環境中。")
print("✅ 儲存模式：", "Firestore" if USE_FIREBASE else "本次 Colab 暫存（設定與成績）")
'''


def build():
    cells = [
        cell("markdown", "# XMLGrader 整合版｜2026-10-04-unified\n\nColab 與 Cloud Run 共用 XML 解析、教師管理與學生自評。\n\n🔴 **首次使用請先閱讀網站根目錄 README 的 15 分鐘設定檢查表。**\n\n必填 Secrets：`XMLGRADER_NGROK_AUTHTOKEN`、`XMLGRADER_GEMINI_API_KEY_1`、`XMLGRADER_ADMIN_TOKEN`。\n私密值不要寫入本 Notebook；Firestore 預設關閉。\n\n本檔由 `XML_Grader/scripts/build_notebook.py` 產生，核心維護請修改 `XML_Grader/*.py` 後重新產生。"),
        cell("markdown", "## 步驟 1：安裝相依套件"),
        cell("code", '%pip install -q "flask>=3.1,<4" "flask-cors>=6,<7" "google-genai>=1,<3" "google-auth>=2,<3" "requests>=2,<3" "pyngrok>=7,<9"'),
        cell("markdown", "## 步驟 2：產生共用後端（自動產生，不需要修改此區）"),
    ]
    for name in ("xml_grader_core.py", "api_server.py", "colab_server.py"):
        cells.append(cell("code", f"%%writefile {name}\n" + (BASE / name).read_text(encoding="utf-8")))
    cells.extend([
        cell("markdown", "## 步驟 3：準備 Secrets\n\n在 Colab 左側 Secrets 新增上述三個名稱，逐項允許 Notebook 存取。\n教師密碼由你自行設定，之後在網站 `teacher.html` 登入。"),
        cell("markdown", "## 步驟 4：🔴 部署設定\n\n此處集中設定公開網域、網站來源、儲存方式與首次評分規則；私密值從 Secrets 載入。\n\n啟用 Firestore 時另需 Secrets：`XMLGRADER_FIREBASE_PROJECT_ID`、`XMLGRADER_FIREBASE_SERVICE_ACCOUNT_JSON`。"),
        cell("code", CONFIG),
        cell("markdown", "## 步驟 5：啟動後端\n\n把輸出的 HTTPS 根網址填入網站 `grader-settings.js` 的 `serverUrl`；教師端與學生端會共用，不需各自修改 HTML。"),
        cell("code", "import importlib, colab_server\nif getattr(colab_server, '_server', None):\n    colab_server._server.shutdown()\n    colab_server._server.server_close()\nimportlib.reload(colab_server)\npublic_url = colab_server.serve_background()\n"),
    ])
    notebook = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "name": "python3"}, "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 0}
    text = json.dumps(notebook, ensure_ascii=False, indent=2) + "\n"
    (BASE.parent / "XMLGrader_Colab.ipynb").write_text(text, encoding="utf-8", newline="\n")
    print("唯一 Colab 入口已產生：XMLGrader_Colab.ipynb（2026-10-04-unified）")


if __name__ == "__main__":
    build()
