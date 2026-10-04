"""確認分享包離開課程目錄後仍完整，且沒有帶入執行資料或實際憑證。"""
import ast
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "XMLGrader_Standalone"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "script", "iframe"):
            self.links.extend(v for k, v in attrs if k in ("href", "src") and v)


def verify():
    manifest = json.loads((PACKAGE / "MANIFEST.json").read_text(encoding="utf-8"))
    names = {record["path"] for record in manifest["files"]}
    for record in manifest["files"]:
        path = PACKAGE / record["path"]
        assert path.resolve().is_relative_to(PACKAGE.resolve())
        assert path.stat().st_size == record["bytes"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"]
    assert not any(".venv" in p or "__pycache__" in p or "runtime/" in p or p.endswith(".sqlite3") for p in names)
    for page in PACKAGE.rglob("*.html"):
        parser = Links()
        text = page.read_text(encoding="utf-8")
        parser.feed(text)
        assert "Lung-Hwa" not in text
        assert "回到課程首頁" not in text
        for link in parser.links:
            parsed = urlsplit(link)
            if not parsed.scheme and not parsed.netloc and parsed.path:
                target = (page.parent / unquote(parsed.path)).resolve()
                assert target.is_relative_to(PACKAGE.resolve()), (page, link)
                assert target.exists(), (page, link)
    assert "serverUrl: ''" in (PACKAGE / "grader-settings.js").read_text(encoding="utf-8")
    for filename in ("api_server.py", "xml_grader_core.py", "colab_server.py"):
        assert (PACKAGE / "XML_Grader" / filename).read_bytes() == (ROOT / "XML_Grader" / filename).read_bytes()
    for notebook in PACKAGE.rglob("*.ipynb"):
        for cell in json.loads(notebook.read_text(encoding="utf-8"))["cells"]:
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            if source.startswith("%pip"):
                continue
            if source.startswith("%%writefile"):
                source = source.split("\n", 1)[1]
            ast.parse(source)
    with zipfile.ZipFile(ROOT / "XMLGrader_Standalone.zip") as archive:
        assert archive.testzip() is None
        assert set(archive.namelist()) == {"XMLGrader_Standalone/" + p for p in names | {"MANIFEST.json"}}
        for path in names | {"MANIFEST.json"}:
            assert archive.read("XMLGrader_Standalone/" + path) == (PACKAGE / path).read_bytes()
        # 解壓到與課程網站無關的暫存目錄，執行包內自己的測試。
        with tempfile.TemporaryDirectory(prefix="xmlgrader-package-") as folder:
            archive.extractall(folder)
            isolated = Path(folder) / "XMLGrader_Standalone"
            environment = dict(os.environ, PYTHONIOENCODING="utf-8")
            result = subprocess.run([sys.executable, "tests/test_grader.py"], cwd=isolated,
                                    env=environment, text=True, encoding="utf-8", capture_output=True)
            if result.returncode:
                raise AssertionError(result.stdout + result.stderr)
            print(result.stderr.split("----------------------------------------------------------------------")[-1].strip())
    print(f"PASS: {len(names) + 1} packaged files, checksums, internal links, empty service URL, isolated backend tests and ZIP integrity")


if __name__ == "__main__":
    verify()
