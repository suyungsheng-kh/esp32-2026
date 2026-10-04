"""建立可獨立分享的 XMLGrader 資料夾與 ZIP，只複製明確列出的發行檔案。"""
import hashlib
import json
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "XMLGrader_Standalone"
ARCHIVE = ROOT / "XMLGrader_Standalone.zip"
TEMPLATES = ROOT / "XML_Grader" / "package-templates"


def build():
    # 執行前以維護中的共用核心重新產生 Notebook，避免包到舊版儲存格。
    import build_notebook
    build_notebook.build()
    if OUTPUT.is_symlink():
        raise RuntimeError("獨立包目錄不可為其他位置的連結。")
    manifest_path = OUTPUT / "MANIFEST.json"
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding="utf-8"))
        for record in previous.get("files", []):
            destination = OUTPUT / record["path"]
            if not destination.resolve().is_relative_to(OUTPUT.resolve()):
                raise RuntimeError("發行清單含有不正確的檔案位置。")
            if destination.exists() and hashlib.sha256(destination.read_bytes()).hexdigest() != record["sha256"]:
                raise RuntimeError(f"獨立包內 {record['path']} 已被修改，請先保留修改後再重新產生套件。")
    elif OUTPUT.exists() and any(OUTPUT.iterdir()):
        raise RuntimeError("既有獨立包目錄沒有發行清單，為保留內容，請先將它移到其他位置。")
    OUTPUT.mkdir(exist_ok=True)
    files = ["teacher.html", "student.html", "grader-settings.js", "XMLGrader_Colab.ipynb", ".gitignore", ".gitattributes", "tests/test_grader.py",
             "XML_Grader/api_server.py", "XML_Grader/xml_grader_core.py", "XML_Grader/colab_server.py",
             "XML_Grader/XMLGrader_Colab.ipynb", "XML_Grader/README.md",
             "XML_Grader/XMLGrader_teacher.html", "XML_Grader/XMLGrader_student.html",
             "XML_Grader/Dockerfile", "XML_Grader/.gcloudignore", "XML_Grader/.dockerignore",
             "XML_Grader/cloudrun/Dockerfile", "XML_Grader/cloudrun/app.py",
             "XML_Grader/cloudrun/requirements.txt", "XML_Grader/cloudrun/xml_grader_core.py",
             "XML_Grader/cloudrun/部署說明_CloudRun.md", "XML_Grader/scripts/build_notebook.py"]
    files.extend(p.relative_to(ROOT).as_posix() for p in sorted((ROOT / "XML_Grader" / "esp32").glob("*.xml")))
    for name in files:
        destination = OUTPUT / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        # 統一文字換行，避免 Git checkout 改變發行清單的校驗值。
        destination.write_bytes((ROOT / name).read_bytes().replace(b"\r\n", b"\n"))
    teacher = OUTPUT / "teacher.html"
    teacher.write_text(teacher.read_text(encoding="utf-8").replace("Lung-Hwa 物聯網創客", "XMLGrader 系統首頁"), encoding="utf-8", newline="\n")
    student = OUTPUT / "student.html"
    student.write_text(student.read_text(encoding="utf-8").replace("回到課程首頁", "回到系統首頁").replace("motoBlockly程式自評闖關站", "積木程式 XML 自評闖關站"), encoding="utf-8", newline="\n")
    settings = OUTPUT / "grader-settings.js"
    # 公開網址也不沿用發行者的服務，讓收件者連接自己的後端。
    settings.write_text('// 🔴 依 README 填入自己的後端根網址；不要放入金鑰或教師密碼。\nwindow.XMLGRADER_SETTINGS = Object.freeze({\n  serverUrl: \'\',\n  expectedVersion: \'2026-10-04-unified\'\n});\n', encoding="utf-8", newline="\n")
    backend_readme = OUTPUT / "XML_Grader" / "README.md"
    backend_readme.write_text(backend_readme.read_text(encoding="utf-8").replace("本資料夾已與 ESP32 課程網站整合，詳細安裝與帳號申請請閱讀 [課程 README](../README.md)。", "本資料夾是獨立版共用後端，詳細安裝與帳號申請請閱讀 [獨立版 README](../README.md)。"), encoding="utf-8", newline="\n")
    for name in ("index.html", "README.md"):
        shutil.copyfile(TEMPLATES / name, OUTPUT / name)
        files.append(name)
    manifest = {"version": "2026-10-04-unified", "package": "XMLGrader_Standalone", "files": []}
    for name in sorted(files):
        content = (OUTPUT / name).read_bytes()
        manifest["files"].append({"path": name, "bytes": len(content), "sha256": hashlib.sha256(content).hexdigest()})
    (OUTPUT / "MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in sorted(files + ["MANIFEST.json"]):
            archive.write(OUTPUT / name, "XMLGrader_Standalone/" + name)
    print(f"獨立包已建立：{OUTPUT.name}（{len(files) + 1} 個檔案）與 {ARCHIVE.name}")


if __name__ == "__main__":
    build()
