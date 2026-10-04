"""離線整合驗證；不呼叫 Gemini、不連 ngrok／Firestore。"""
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "XML_Grader"))
import api_server as api
import xml_grader_core as core

RUBRICS = [
    {"id": "open", "name": "LED", "theme": "LED", "rules": "能控制 LED", "is_open": True,
     "template_code": "private-template", "example_code": "private-answer"},
    {"id": "closed", "name": "hidden-homework", "theme": "hidden-homework", "rules": "secret-rule", "is_open": False},
]
XML = b'<xml><block type="inout_digital_write"><field name="PIN">2</field><field name="STAT">HIGH</field></block></xml>'
RESULT = {"score": 86, "logic_analysis": "LED control works", "comments": "ok", "creative_highlights": "none", "deducted_items": "timing"}


class GraderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = patch.dict(os.environ, {
            "XMLGRADER_ADMIN_TOKEN": "test-teacher-password",
            "XMLGRADER_GEMINI_API_KEY_1": "test-gemini-key-for-offline-tests",
            "XMLGRADER_SUBMISSIONS_PATH": str(Path(self.temp.name) / "records.sqlite3"),
        })
        self.env.start()
        self.addCleanup(self.env.stop)
        for target, name, value in [(core, "CONFIG_PATH", str(Path(self.temp.name) / "config.json")),
                                    (api, "CONFIG_PATH", str(Path(self.temp.name) / "config.json")),
                                    (core, "FIREBASE", {"enabled": False})]:
            p = patch.object(target, name, value)
            p.start()
            self.addCleanup(p.stop)
        core.save_config({"rubrics_json": json.dumps(RUBRICS), "student_show_score": True})
        self.client = api.app.test_client()
        self.headers = {"X-Admin-Token": "test-teacher-password"}

    def submit(self, rubric="open", content=XML, teacher=False):
        return self.client.post("/api/teacher/test" if teacher else "/api/student/grade",
            headers=self.headers if teacher else {},
            data={"file": (io.BytesIO(content), "task.xml"), "student_id": "S001", "rubric_id": rubric})

    def test_teacher_guard_all_routes_and_preflight(self):
        for rule in api.app.url_map.iter_rules():
            if rule.rule.startswith("/api/teacher/"):
                method = "GET" if "GET" in rule.methods else "POST"
                self.assertEqual(self.client.open(rule.rule, method=method).status_code, 401)
        self.assertEqual(self.client.options("/api/teacher/config").status_code, 200)
        with patch.dict(os.environ, {"XMLGRADER_ADMIN_TOKEN": ""}):
            self.assertEqual(self.client.get("/api/teacher/config", headers=self.headers).status_code, 503)

    def test_teacher_config_no_secrets_roundtrip(self):
        data = self.client.get("/api/teacher/config", headers=self.headers).json["config"]
        self.assertTrue(data["has_api_key"])
        self.assertNotIn("api_key_1", data)
        response = self.client.post("/api/teacher/config", headers=self.headers, json={
            "student_show_score": False, "api_key_1": "injected-key", "admin_token": "replace-password"})
        self.assertTrue(response.json["ok"])
        saved = json.loads(Path(core.CONFIG_PATH).read_text(encoding="utf-8"))
        self.assertFalse(saved["student_show_score"])
        self.assertNotIn("api_key_1", saved)
        self.assertNotIn("admin_token", saved)
        self.assertTrue(self.client.get("/api/teacher/config", headers=self.headers).json["ok"])

    def test_rubric_validation(self):
        response = self.client.post("/api/teacher/config", headers=self.headers,
            json={"rubrics_json": json.dumps([RUBRICS[0], RUBRICS[0]])})
        self.assertEqual(response.status_code, 400)

    def test_public_config_no_keys_answers_or_closed_rules(self):
        response = self.client.get("/api/student/config")
        text = response.get_data(as_text=True)
        for hidden in ["test-gemini", "private-template", "private-answer", "hidden-homework", "secret-rule", "admin_token"]:
            self.assertNotIn(hidden, text)
        self.assertEqual([r["id"] for r in response.json["config"]["rubrics"]], ["open"])

    def test_closed_and_unknown_rubrics_never_call_ai(self):
        with patch.object(core, "single_agent_grading") as ai:
            self.assertEqual(self.submit("closed").status_code, 403)
            self.assertEqual(self.submit("unknown").status_code, 400)
            ai.assert_not_called()

    def test_success_and_real_hidden_score_records(self):
        core.save_config({"rubrics_json": json.dumps(RUBRICS), "student_show_score": False})
        with patch.object(core, "single_agent_grading", return_value=dict(RESULT)):
            response = self.submit()
        self.assertTrue(response.json["ok"])
        self.assertTrue(response.json["record_saved"])
        self.assertIsNone(response.json["result"]["score"])
        self.assertNotIn("clean_code", response.json["result"])
        rows = self.client.get("/api/teacher/submissions", headers=self.headers).json["submissions"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["score"], 86)

    def test_quota_and_errors_are_not_scores_or_records(self):
        for flag, status in [("quota_exceeded", 429), ("grading_error", 503)]:
            with patch.object(core, "single_agent_grading", return_value={"score": None, flag: True, "comments": "try later"}):
                response = self.submit()
            self.assertEqual(response.status_code, status)
            self.assertFalse(response.json["ok"])
        self.assertEqual(core.list_submissions()["submissions"], [])

    def test_invalid_xml_and_extension_not_recorded(self):
        self.assertFalse(self.submit(content=b'not xml').json["ok"])
        response = self.client.post("/api/student/grade", data={"file": (io.BytesIO(XML), "task.txt"), "student_id": "S1", "rubric_id": "open"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(core.list_submissions()["submissions"], [])

    def test_teacher_trial_unsaved_rules_no_record(self):
        with patch.object(core, "single_agent_grading", return_value=dict(RESULT)):
            response = self.client.post("/api/teacher/test", headers=self.headers, data={
                "file": (io.BytesIO(XML), "task.xml"), "rubric_override": json.dumps(RUBRICS[1]),
                "overrides": json.dumps({"model_name": "teacher-trial"})})
        self.assertTrue(response.json["ok"])
        self.assertIn("clean_code", response.json["result"])
        self.assertEqual(core.list_submissions()["submissions"], [])

    def test_gemini_failure_classification_and_key_rotation(self):
        class FakeClient:
            attempts = []
            errors = []
            def __init__(self, api_key):
                self.key = api_key
                self.models = self
            def generate_content(self, **kwargs):
                self.attempts.append(self.key)
                if self.errors:
                    raise Exception(self.errors.pop(0))
                return type("Response", (), {"text": json.dumps(RESULT)})()
        args = (["a" * 30, "b" * 30], "rules", "LED", "code", "", "", "offline", False)
        with patch.object(core.genai, "Client", FakeClient), patch.object(core.time, "sleep"):
            FakeClient.errors = ["429 RESOURCE_EXHAUSTED"]
            res = core.single_agent_grading(*args)
            self.assertEqual(res["score"], 86)
            self.assertEqual(FakeClient.attempts[:2], ["a" * 30, "b" * 30])
            FakeClient.errors = ["429 RESOURCE_EXHAUSTED"] * 4
            self.assertTrue(core.single_agent_grading(*args)["quota_exceeded"])
            FakeClient.errors = ["503 temporarily unavailable"] * 4
            res = core.single_agent_grading(*args)
            self.assertTrue(res["grading_error"])
            self.assertIsNone(res["score"])
            self.assertNotIn("quota_exceeded", res)

    def test_xml_examples_parse(self):
        examples = list((BASE / "XML_Grader" / "esp32").glob("*.xml"))
        self.assertGreater(len(examples), 0)
        for path in examples:
            with self.subTest(path=path.name):
                parsed = core.extract_project_xml(str(path))
                self.assertTrue(parsed)
                self.assertTrue(core.clean_xml_for_ai(parsed))

    def test_generated_notebooks_match_canonical_sources(self):
        rootbook = (BASE / "XMLGrader_Colab.ipynb").read_bytes()
        self.assertEqual(list((BASE / "XML_Grader").rglob("*.ipynb")), [])
        self.assertFalse((BASE / "XML_Grader" / "XMLGrader_Colab.ipynb").exists())
        book = json.loads(rootbook)
        for name in ["xml_grader_core.py", "api_server.py", "colab_server.py"]:
            source = next("".join(c["source"]).split("\n", 1)[1] for c in book["cells"]
                          if "".join(c.get("source", [])).startswith("%%writefile " + name))
            self.assertEqual(source, (BASE / "XML_Grader" / name).read_text(encoding="utf-8"))
        for name in ("xml_grader_core.py", "app.py", "Dockerfile"):
            self.assertFalse((BASE / "XML_Grader" / "cloudrun" / name).exists())
        self.assertTrue((BASE / "XML_Grader" / "Dockerfile").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
