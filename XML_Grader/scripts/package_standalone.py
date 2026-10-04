"""由唯一維護來源產生 Releases ZIP；不建立儲存庫內的原始碼副本。"""
import hashlib
import json
from pathlib import Path
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / ".publish" / "dist" / "XMLGrader_Standalone.zip"
TEMPLATES = ROOT / "XML_Grader" / "package-templates"


def build():
    import build_notebook
    build_notebook.build()
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    files = ["teacher.html", "student.html", "grader-settings.js", "XMLGrader_Colab.ipynb",
             ".gitignore", ".gitattributes", "tests/test_grader.py",
             "XML_Grader/api_server.py", "XML_Grader/xml_grader_core.py", "XML_Grader/colab_server.py",
             "XML_Grader/README.md", "XML_Grader/Dockerfile",
             "XML_Grader/.gcloudignore", "XML_Grader/.dockerignore",
             "XML_Grader/cloudrun/requirements.txt", "XML_Grader/cloudrun/部署說明_CloudRun.md",
             "XML_Grader/scripts/build_notebook.py"]
    files.extend(p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "XML_Grader" / "esp32").glob("*.xml")))
    # 暫存解壓目錄只用於建置，不保留第二份可編輯的系統。
    with tempfile.TemporaryDirectory(prefix="xmlgrader-build-", dir=ARCHIVE.parent) as temporary:
        output = Path(temporary) / "XMLGrader_Standalone"
        for name in files:
            destination = output / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((ROOT / name).read_bytes().replace(b"\r\n", b"\n"))
        teacher = output / "teacher.html"
        teacher.write_text(teacher.read_text(encoding="utf-8").replace("Lung-Hwa 物聯網創客", "XMLGrader 系統首頁"), encoding="utf-8", newline="\n")
        student = output / "student.html"
        student.write_text(student.read_text(encoding="utf-8").replace("回到課程首頁", "回到系統首頁").replace("motoBlockly程式自評闖關站", "積木程式 XML 自評闖關站"), encoding="utf-8", newline="\n")
        (output / "grader-settings.js").write_text('// 🔴 依 README 填入自己的後端根網址；不要放入金鑰或教師密碼。\nwindow.XMLGRADER_SETTINGS = Object.freeze({\n  serverUrl: \'\',\n  expectedVersion: \'2026-10-04-unified\'\n});\n', encoding="utf-8", newline="\n")
        backend_readme = output / "XML_Grader" / "README.md"
        backend_readme.write_text(backend_readme.read_text(encoding="utf-8").replace("本資料夾已與 ESP32 課程網站整合，詳細安裝與帳號申請請閱讀 [課程 README](../README.md)。", "本資料夾是獨立版唯一後端，詳細安裝與帳號申請請閱讀 [獨立版 README](../README.md)。"), encoding="utf-8", newline="\n")
        (output / "index.html").write_text((TEMPLATES / "index.html").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
        readme = (ROOT / "XML_Grader" / "STANDALONE.md").read_text(encoding="utf-8")
        readme = readme.replace("(cloudrun/部署說明_CloudRun.md)", "(XML_Grader/cloudrun/部署說明_CloudRun.md)")
        (output / "README.md").write_text(readme, encoding="utf-8", newline="\n")
        files.extend(["index.html", "README.md"])
        manifest = {"version": "2026-10-04-unified", "package": "XMLGrader_Standalone", "files": []}
        for name in sorted(files):
            content = (output / name).read_bytes()
            manifest["files"].append({"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
        (output / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        # 建置完成才替換舊 ZIP；不影響使用者下載後自行修改的系統。
        candidate = Path(temporary) / ARCHIVE.name
        with zipfile.ZipFile(candidate, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name in sorted(files + ["MANIFEST.json"]):
                archive.write(output / name, "XMLGrader_Standalone/" + name)
        candidate.replace(ARCHIVE)
    print(f"Releases 附件已建立：{ARCHIVE.relative_to(ROOT)}（{len(files) + 1} 個檔案）")
    return ARCHIVE


if __name__ == "__main__":
    build()
