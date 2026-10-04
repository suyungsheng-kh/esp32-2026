# XMLGrader 整合版（2026-10-04-unified）

本資料夾已與 ESP32 課程網站整合，詳細安裝與帳號申請請閱讀 [課程 README](../README.md)。

- 教師入口：[teacher.html](../teacher.html)，用後端設定的教師密碼登入。
- 學生入口：[student.html](../student.html)；兩個頁面共用 [grader-settings.js](../grader-settings.js) 的公開後端網址。
- 共用核心：`xml_grader_core.py`。
- 共用 API：`api_server.py`，教師路由須通過 `XMLGRADER_ADMIN_TOKEN` 驗證。
- Colab 啟動器：`colab_server.py`。
- Colab Notebook：[根目錄唯一啟動檔](../XMLGrader_Colab.ipynb)，由共用原始碼產生。
- Cloud Run：[部署說明](cloudrun/部署說明_CloudRun.md)，使用根目錄 Dockerfile 與相同核心。
- 唯一教師／學生入口是網站根目錄 `teacher.html`／`student.html`，不另放相同功能的頁面。

## 整合內容

保留 Blockly XML 解析、腳位事實檢查、分數範圍限制、雙金鑰輪替與多份評測標準。
新增教師驗證、學生公開設定白名單、額度／服務失敗不計分、本機 SQLite 成績暫存。
Firestore 改用服務帳戶驗證；不再使用內建專案、Web API key 或公開讀寫規則。
Gemini 金鑰只由後端環境參數提供，不儲存到 Firestore 或下發網頁。

## 維護

修改 `xml_grader_core.py`、`api_server.py` 或 `colab_server.py` 後，於專案根目錄執行：

```powershell
python XML_Grader/scripts/build_notebook.py
```

它只產生根目錄的一個 Notebook；不可單獨修改其步驟 2 的後端儲存格，避免與原始碼分歧。
Cloud Run 只使用本目錄的 Dockerfile、API 與核心，`cloudrun/` 只保留相依套件與部署說明。
`esp32/` 中的 XML 範例保留，可供教師試評。
