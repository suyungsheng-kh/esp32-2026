"""XMLGrader 統一 API；Colab 與 Cloud Run 共用。設定請參閱根目錄 README。"""
import hmac
import json
import os
import tempfile

from flask import Flask, jsonify, request
from flask_cors import CORS
import xml_grader_core as core

SERVER_VERSION = "2026-10-04-unified"
CONFIG_PATH = core.CONFIG_PATH
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024
CORS(app, resources={r"/api/*": {"origins": [s.strip() for s in os.environ.get("XMLGRADER_CORS_ORIGINS", "*").split(",") if s.strip()]}},
     allow_headers=["Content-Type", "X-Admin-Token", "ngrok-skip-browser-warning"])

EDITABLE_FIELDS = {"model_name", "student_show_score", "max_size_mb", "rubrics_json",
                   "theme", "rules", "is_standard_answer", "use_custom_extension",
                   "extension_rules", "template_code", "example_code"}


def load_cfg():
    cfg = core.load_config(CONFIG_PATH)
    # 金鑰不回傳前端、不儲存設定；優先採用新名稱，兼容原 Cloud Run 環境名稱。
    for n in (1, 2):
        cfg[f"api_key_{n}"] = os.environ.get(f"XMLGRADER_GEMINI_API_KEY_{n}") or os.environ.get(f"GEMINI_API_KEY_{n}", "")
    return cfg


@app.before_request
def protect_teacher():
    if request.method == "OPTIONS" or not request.path.startswith("/api/teacher/"):
        return None
    expected = os.environ.get("XMLGRADER_ADMIN_TOKEN", "").strip()
    if not expected:
        return jsonify(ok=False, error="教師管理尚未啟用：請在後端設定 XMLGRADER_ADMIN_TOKEN。"), 503
    supplied = request.headers.get("X-Admin-Token", "")
    if not hmac.compare_digest(supplied.encode(), expected.encode()):
        return jsonify(ok=False, error="教師密碼不正確，請重新登入。"), 401


@app.after_request
def no_cache(response):
    response.headers["Cache-Control"] = "no-store"
    return response


@app.errorhandler(413)
def too_large(error):
    return jsonify(ok=False, error="檔案過大，請選擇課程匯出的 XML。"), 413


@app.errorhandler(Exception)
def safe_error(error):
    from werkzeug.exceptions import HTTPException
    if isinstance(error, HTTPException):
        return jsonify(ok=False, error=error.description), error.code
    app.logger.error("XMLGrader request failed (%s)", type(error).__name__)
    return jsonify(ok=False, error="服務暫時無法完成，請稍後再試或通知老師。"), 500


@app.route("/")
@app.route("/api/health")
def health():
    return jsonify(ok=True, version=SERVER_VERSION, service="XMLGrader",
                   teacher_auth=True, storage="firestore" if core.FIREBASE["enabled"] else "local")


def validate_settings(incoming):
    if not isinstance(incoming, dict):
        raise ValueError("設定格式必須為物件。")
    filtered = {k: v for k, v in incoming.items() if k in EDITABLE_FIELDS}
    if "max_size_mb" in filtered:
        filtered["max_size_mb"] = max(1, min(18, int(filtered["max_size_mb"])))
    if "student_show_score" in filtered and not isinstance(filtered["student_show_score"], bool):
        raise ValueError("顯示分數必須為布林值。")
    if "rubrics_json" in filtered:
        rubrics = json.loads(filtered["rubrics_json"])
        if not isinstance(rubrics, list) or any(not isinstance(r, dict) for r in rubrics):
            raise ValueError("評測標準必須為陣列。")
        ids = [r.get("id") for r in rubrics]
        if any(not isinstance(i, str) or not i for i in ids) or len(set(ids)) != len(ids):
            raise ValueError("每份評測標準需要不重複的 ID。")
    return filtered


@app.route("/api/teacher/config", methods=["GET", "POST"])
def teacher_config():
    cfg = load_cfg()
    if request.method == "POST":
        try:
            cfg.update(validate_settings(request.get_json(silent=True)))
        except (ValueError, TypeError):
            return jsonify(ok=False, error="設定格式有誤，請確認作業清單與檔案大小。"), 400
        saved_to = core.save_config(cfg, CONFIG_PATH)
        return jsonify(ok=True, saved_to=saved_to, updated_at=cfg["updated_at"])
    safe = {k: v for k, v in cfg.items() if k not in core._SENSITIVE_KEYS}
    safe["has_api_key"] = bool(cfg.get("api_key_1") or cfg.get("api_key_2"))
    return jsonify(ok=True, config=safe, storage="firestore" if core.FIREBASE["enabled"] else "local")


def uploaded_path(max_mb):
    file = request.files.get("file")
    if file is None or not (file.filename or "").lower().endswith(".xml"):
        raise ValueError("請選擇 .xml 檔案。")
    content = file.read(int(max_mb) * 1024 * 1024 + 1)
    if len(content) > int(max_mb) * 1024 * 1024:
        raise ValueError("XML 超過老師設定的檔案大小上限。")
    with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as handle:
        handle.write(content)
        return handle.name


@app.route("/api/teacher/convert_xml", methods=["POST"])
def teacher_convert_xml():
    try:
        max_mb = max(1, min(18, int(request.form.get("max_size_mb", 10))))
        path = uploaded_path(max_mb)
    except (ValueError, TypeError) as e:
        return jsonify(ok=False, error=str(e)), 400
    try:
        parsed = core.extract_project_xml(path, max_mb)
        if not parsed:
            return jsonify(ok=False, error="XML 無法解析，請重新匯出。"), 400
        return jsonify(ok=True, clean_code=core.clean_xml_for_ai(parsed))
    finally:
        os.remove(path)


@app.route("/api/teacher/models", methods=["POST"])
def teacher_models():
    cfg = load_cfg()
    return jsonify(core.list_available_models([cfg["api_key_1"], cfg["api_key_2"]]))


@app.route("/api/teacher/suggest_rules", methods=["POST"])
def teacher_suggest_rules():
    cfg = load_cfg()
    body = request.get_json(silent=True) or {}
    result = core.suggest_theme_and_rules(body.get("clean_code", ""),
        [cfg["api_key_1"], cfg["api_key_2"]], body.get("model_name") or cfg["model_name"])
    return jsonify(result), 200 if result.get("ok") else 400


@app.route("/api/teacher/submissions")
def teacher_submissions():
    return jsonify(core.list_submissions())


@app.route("/api/student/config")
def student_config():
    return jsonify(ok=True, version=SERVER_VERSION, config=core.public_config(load_cfg()))


@app.route("/api/student/grade", methods=["POST"])
@app.route("/api/teacher/test", methods=["POST"])
def grade():
    teacher = request.path.startswith("/api/teacher/")
    cfg = load_cfg()
    rubric_override = None
    if teacher:
        try:
            cfg.update(validate_settings(json.loads(request.form.get("overrides") or "{}")))
            rubric_override = json.loads(request.form.get("rubric_override") or "null")
            if rubric_override is not None and not isinstance(rubric_override, dict):
                raise ValueError("invalid rubric")
        except (ValueError, TypeError):
            return jsonify(ok=False, error="試評設定格式有誤。"), 400
    student_id = (request.form.get("student_id") or "").strip()[:100]
    if not teacher and not student_id:
        return jsonify(ok=False, error="請先輸入學號。"), 400
    if not (cfg.get("api_key_1") or cfg.get("api_key_2")):
        return jsonify(ok=False, error="老師尚未設定 Gemini 金鑰，暫時無法自評。"), 503
    rubric_id = request.form.get("rubric_id")
    if not teacher:
        rubrics = core.get_rubrics(cfg)
        if rubric_id and not any(r.get("id") == rubric_id for r in rubrics):
            return jsonify(ok=False, error="這份作業不存在，請重新載入作業清單。"), 400
        if not rubric_id and len(rubrics) != 1:
            return jsonify(ok=False, error="請選擇老師開放的作業。"), 400
    try:
        path = uploaded_path(cfg.get("max_size_mb", 10))
    except (ValueError, TypeError) as e:
        return jsonify(ok=False, error=str(e)), 400
    try:
        result = core.grade_project_file(path, cfg, rubric_id=rubric_id,
            rubric_override=rubric_override, enforce_open=not teacher)
        if result.get("closed"):
            return jsonify(ok=False, error=result["comments"]), 403
        if result.get("quota_exceeded"):
            return jsonify(ok=False, quota_exceeded=True, error=result["comments"]), 429
        if result.get("grading_error"):
            return jsonify(ok=False, error=result["comments"]), 503
        recorded = None
        if not teacher:
            recorded = core.record_submission(student_id, result,
                theme=result.get("rubric_theme", ""), rubric_name=result.get("rubric_name", ""))
            if not cfg.get("student_show_score", True):
                result["score"] = None
            result.pop("clean_code", None)
        return jsonify(ok=True, result=result, student_id=student_id,
            show_score=cfg.get("student_show_score", True),
            record_saved=bool(recorded) if not teacher else False)
    finally:
        os.remove(path)
