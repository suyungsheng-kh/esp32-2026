"""僅供本機瀏覽器驗證，使用假 Gemini 回應和暫存成績。"""
import json
import os
from pathlib import Path
import sys
import tempfile
from flask import Response, abort, send_from_directory

ROOT = Path(__file__).resolve().parents[1]
TEMP = tempfile.TemporaryDirectory()
os.environ.update(XMLGRADER_CONFIG_PATH=str(Path(TEMP.name) / "config.json"),
                  XMLGRADER_SUBMISSIONS_PATH=str(Path(TEMP.name) / "records.sqlite3"),
                  XMLGRADER_ADMIN_TOKEN="preview-teacher-password", XMLGRADER_GEMINI_API_KEY_1="preview-not-real-key",
                  XMLGRADER_FIREBASE_ENABLED="false")
sys.path.insert(0, str(ROOT / "XML_Grader"))
import api_server as api
import xml_grader_core as core

core.save_config({"rubrics_json": json.dumps([
    {"id": "led", "name": "LED 閃爍", "theme": "LED 閃爍", "rules": "LED 能亮滅", "is_open": True},
    {"id": "hidden", "name": "未開放作業", "rules": "hidden", "is_open": False},
], ensure_ascii=False)})
SCENARIO = {"quota": False}


@api.app.route("/_test/reset", methods=["POST"])
def reset_preview():
    SCENARIO["quota"] = False
    core.save_config({"rubrics_json": json.dumps([
        {"id": "led", "name": "LED 閃爍", "theme": "LED 閃爍", "rules": "LED 能亮滅", "is_open": True},
        {"id": "hidden", "name": "未開放作業", "rules": "hidden", "is_open": False}], ensure_ascii=False),
        "student_show_score": True})
    import contextlib
    with contextlib.closing(core._local_db()) as db:
        with db:
            db.execute("DELETE FROM submissions")
    return {"ok": True}


def fake_ai(*args, **kwargs):
    if SCENARIO["quota"]:
        return {"score": None, "quota_exceeded": True, "comments": "AI 自評受到額度限制，這次不計分。"}
    return {"score": 86, "logic_analysis": "有正確的數位輸出，請檢查等待時間。", "comments": "完成 LED 控制。",
            "deducted_items": "等待時間可再調整", "creative_highlights": "無"}


core.single_agent_grading = fake_ai
core.list_available_models = lambda keys: {"ok": True, "models": ["gemini-2.5-flash", "offline-preview"]}
core.suggest_theme_and_rules = lambda code, keys, model: {"ok": True, "theme": "AI 建議 LED 作業", "rules": "LED 能亮滅（100 分）"}


@api.app.route("/grader-settings.js")
def settings():
    return Response('window.XMLGRADER_SETTINGS={serverUrl:"http://127.0.0.1:8765",expectedVersion:"2026-10-04-unified"};', mimetype="text/javascript")


@api.app.route("/_test/quota/<mode>", methods=["POST"])
def scenario(mode):
    SCENARIO["quota"] = mode == "on"
    return {"ok": True}


@api.app.route("/<path:name>")
def static_page(name):
    if not name.endswith((".html", ".js")) or ".." in name or name.startswith("."):
        abort(404)
    return send_from_directory(ROOT, name)


if __name__ == "__main__":
    api.app.run(host="127.0.0.1", port=8765, threaded=True)
