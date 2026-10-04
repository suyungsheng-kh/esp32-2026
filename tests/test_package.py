"""確認 Releases 分享包獨立完整、沒有重複入口、執行資料或實際憑證。"""
import ast
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from urllib.parse import unquote, urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / ".publish" / "dist" / "XMLGrader_Standalone.zip"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag in ("a", "script", "iframe"):
            self.links.extend(v for k, v in attrs if k in ("href", "src") and v)


def verify():
    assert not (ROOT / "XMLGrader_Standalone").exists(), "不要在儲存庫內保留獨立版副本"
    assert not (ROOT / "XMLGrader_Standalone.zip").exists(), "ZIP 應放 Releases，不放儲存庫根目錄"
    with zipfile.ZipFile(ARCHIVE) as archive, tempfile.TemporaryDirectory(prefix="xmlgrader-package-") as folder:
        assert archive.testzip() is None
        manifest = json.loads(archive.read("XMLGrader_Standalone/MANIFEST.json"))
        names = {record["path"] for record in manifest["files"]}
        assert set(archive.namelist()) == {"XMLGrader_Standalone/" + p for p in names | {"MANIFEST.json"}}
        assert not any(".venv" in p or "__pycache__" in p or "runtime/" in p or p.endswith(".sqlite3") for p in names)
        assert [p for p in names if p.endswith(".ipynb")] == ["XMLGrader_Colab.ipynb"]
        assert [p for p in names if p.endswith("Dockerfile")] == ["XML_Grader/Dockerfile"]
        for record in manifest["files"]:
            path = record["path"]
            assert not Path(path).is_absolute() and ".." not in Path(path).parts
            content = archive.read("XMLGrader_Standalone/" + path)
            assert len(content) == record["bytes"]
            assert hashlib.sha256(content).hexdigest() == record["sha256"]
            assert not re.search(rb"AIza[0-9A-Za-z_-]{35}|-----BEGIN PRIVATE KEY-----", content)
        archive.extractall(folder)
        package = Path(folder) / "XMLGrader_Standalone"
        for page in package.rglob("*.html"):
            parser = Links()
            text = page.read_text(encoding="utf-8")
            parser.feed(text)
            assert "Lung-Hwa" not in text and "回到課程首頁" not in text
            for link in parser.links:
                parsed = urlsplit(link)
                if not parsed.scheme and not parsed.netloc and parsed.path:
                    target = (page.parent / unquote(parsed.path)).resolve()
                    assert target.is_relative_to(package.resolve()) and target.exists(), (page, link)
        for readme in package.rglob("*.md"):
            for link in re.findall(r"\]\(([^)]+)\)", readme.read_text(encoding="utf-8")):
                parsed = urlsplit(link)
                if not parsed.scheme and not parsed.netloc and parsed.path:
                    assert (readme.parent / unquote(parsed.path)).is_file(), (readme, link)
        assert "serverUrl: ''" in (package / "grader-settings.js").read_text(encoding="utf-8")
        for filename in ("api_server.py", "xml_grader_core.py", "colab_server.py"):
            assert (package / "XML_Grader" / filename).read_bytes() == (ROOT / "XML_Grader" / filename).read_bytes().replace(b"\r\n", b"\n")
        for cell in json.loads((package / "XMLGrader_Colab.ipynb").read_text(encoding="utf-8"))["cells"]:
            if cell["cell_type"] != "code":
                continue
            source = "".join(cell["source"])
            if source.startswith("%pip"):
                continue
            if source.startswith("%%writefile"):
                source = source.split("\n", 1)[1]
            ast.parse(source)
        result = subprocess.run([sys.executable, "tests/test_grader.py"], cwd=package,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"), text=True, encoding="utf-8", capture_output=True)
        assert result.returncode == 0, result.stdout + result.stderr
        print(result.stderr.split("----------------------------------------------------------------------")[-1].strip())
    print(f"PASS: {len(names) + 1} files, single Notebook/Dockerfile, checksums, links, empty URL, no keys, isolated backend tests")


if __name__ == "__main__":
    verify()
