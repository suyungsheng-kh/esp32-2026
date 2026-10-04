# XMLGrader 獨立版

下載入口：[獨立版 ZIP](https://github.com/suyungsheng-kh/esp32-2026/releases/latest/download/XMLGrader_Standalone.zip)。請下載此附件並解壓，只使用解壓後的資料夾；不必另外下載課程網站原始碼。

以下檔案位置以 ZIP 解壓後的 `XMLGrader_Standalone/` 為準。本文件也會以 `README.md` 放進 ZIP。

版本：`2026-10-04-unified`。這個資料夾包含完整的教師／學生網頁及評分後端，可以直接分享、搬移和自行部署，不需要 ESP32 課程網站。

系統支援 Blockly XML（例如 motoBlockly／Motoduino／Arduino 積木匯出的 `.xml`），不接受 Scratch `.sb3`。未收錄的積木會保留原始類型供 AI 判讀；請先以自己的作業範例確認解析與評語。

## 資料夾內容

```text
XMLGrader_Standalone/
  index.html                 系統首頁
  teacher.html               教師登入、規則、試評、成績
  student.html               學生上傳 XML 自評
  grader-settings.js         唯一的前端後端網址設定
  XMLGrader_Colab.ipynb       Colab 一鍵啟動檔
  README.md                  本文件
  MANIFEST.json              發行檔案與 SHA-256 校驗資訊
  tests/test_grader.py        離線驗證（不消耗 Gemini 額度）
  XML_Grader/
    api_server.py            共用 API（含教師密碼驗證）
    xml_grader_core.py        共用 XML 解析／Gemini 評分
    colab_server.py          Colab＋ngrok 啟動器
    Dockerfile               Cloud Run 容器
    cloudrun/                相依套件與 Cloud Run 部署說明
    esp32/                   22 份 XML 練習範例
    scripts/build_notebook.py  後端變更後同步 Notebook
```

前端發布 `index.html`、`teacher.html`、`student.html`、`grader-settings.js` 與 `README.md` 五個檔案即可；後端可以由另一位管理者啟動。完整資料夾適合提供給想自行建立系統的教師。

## 第一次操作：15 分鐘設定檢查表

帳號已準備好時，可依此完成設定；首次申請帳號、驗證或發布網站可能需要額外時間。

### 0～3 分鐘：準備帳號

- [ ] 使用 Google 帳號登入 [Google Colab](https://colab.research.google.com/)。
- [ ] 到 [Google AI Studio](https://aistudio.google.com/apikey) 建立自己的 Gemini API Key。
- [ ] 註冊 [ngrok](https://dashboard.ngrok.com/)，取得自己的 Authtoken。
- [ ] 自行設定一組教師管理密碼；這不是 Google 密碼。

### 3～6 分鐘：設定 Colab Secrets

- [ ] 上傳本資料夾根目錄的 `XMLGrader_Colab.ipynb` 到 Google Drive，再以 Colab 開啟。
- [ ] 在 Colab 左側 **Secrets** 新增下列名稱，填入對應值，並逐項允許 Notebook 存取。

| 名稱（必須逐字相同） | 填入內容 | 必填 |
| --- | --- | --- |
| `XMLGRADER_NGROK_AUTHTOKEN` | 自己的 ngrok Authtoken | 是 |
| `XMLGRADER_GEMINI_API_KEY_1` | 自己的 Gemini Key | 是 |
| `XMLGRADER_ADMIN_TOKEN` | 自己設定的教師管理密碼 | 是 |
| `XMLGRADER_GEMINI_API_KEY_2` | 備援 Gemini Key | 選填 |

私密值只放在 Secrets，不貼進 HTML 或 Notebook 程式碼。

### 6～9 分鐘：集中設定與啟動

- [ ] 在 Notebook **步驟 4：🔴 部署設定**，首次保持 `USE_FIREBASE = False`。
- [ ] 沒有自己的固定 ngrok 網域時，保持 `NGROK_STATIC_DOMAIN = ""`。
- [ ] `REPLACE_SAVED_RUBRICS = False` 避免重跑時覆蓋教師已儲存的規則。
- [ ] 首次可保留範例作業，稍後從教師網頁編輯。
- [ ] 由上到下執行全部儲存格，看到「✅ API 已上線」。
- [ ] 開啟輸出的 `<根網址>/api/health`，確認 `"ok": true` 與版本 `2026-10-04-unified`。

### 9～12 分鐘：發布前端檔案

- [ ] 🔴 修改根目錄 `grader-settings.js` 的 `serverUrl`，填入上一步取得的 HTTPS **根網址**，不要加 `/api/...`。

```javascript
window.XMLGRADER_SETTINGS = Object.freeze({
  serverUrl: 'https://<你的-ngrok-網域>',
  expectedVersion: '2026-10-04-unified'
});
```

- [ ] 將 `index.html`、`teacher.html`、`student.html`、`grader-settings.js` 與 `README.md` 發布到 GitHub Pages 或學校的靜態網站空間。
- [ ] 開啟網址中的 `index.html`；網站內部連結均為相對路徑。

GitHub Pages：建立自己的 repository → 上傳上述五個檔案 → **Settings → Pages** 選取分支及根目錄 → 等待網站網址建立。金鑰、教師密碼、服務帳戶 JSON 及成績資料都不能上傳。

### 12～15 分鐘：完成一次試評

- [ ] 進入「教師管理」，輸入自己設定的教師密碼登入。
- [ ] 修改作業名稱、主題、規則與配分；勾選「開放學生自評」後儲存。
- [ ] 在「單檔試評」上傳 `XML_Grader/esp32/` 的範例，確認能收到評語。
- [ ] 進入「學生自評」，輸入測試學號，選作業並上傳 XML。
- [ ] 回教師頁讀取成績，確認學生那筆已記錄。

## 日常使用

教師可建立多份評測標準、上傳範本與參考解答、取得 AI 規則建議、試評及查成績。標準答案練習可勾選「標準答案題型」；開放創意題建議取消。AI 建議的規則仍需教師檢查再儲存。

學生只會取得開放中的作業名稱、主題與規則，不取得參考解答或金鑰。教師試評不建立成績；成功的學生自評才建立成績。額度／速率限制和服務失敗不算成 0 分。

教師密碼只保留在網頁記憶體，重新整理後需重新登入。Gemini 金鑰由後端 Secrets 管理，不從教師網頁修改。

Colab 必須維持執行；沒有固定 ngrok 網域時，重啟後需重新更新 `grader-settings.js` 並發布網站。關閉 Firestore 時，設定與成績只保存在目前執行環境，Colab 被釋放後就不保留。

## 選用：Firestore 永久保存

1. 在 [Firebase Console](https://console.firebase.google.com/) 建立自己的專案及 Firestore `(default)` 資料庫。
2. 建立專用服務帳戶，授予 **Cloud Datastore User**（`roles/datastore.user`）。
3. Colab：建立服務帳戶 JSON 金鑰；整份 JSON 放入 Secret `XMLGRADER_FIREBASE_SERVICE_ACCOUNT_JSON`，專案 ID 放入 `XMLGRADER_FIREBASE_PROJECT_ID`。
4. Notebook 步驟 4 改為 `USE_FIREBASE = True`，重跑設定及啟動。

新版以服務帳戶授權，不需要 Firebase Web API key 或匿名公開讀寫規則。授權機制請參考 [Firestore REST 文件](https://firebase.google.com/docs/firestore/use-rest-api)。如果資料庫沒有其他用戶端應用，可將客戶端規則設為拒絕讀寫；先確認是否有其他應用共用。

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} { allow read, write: if false; }
  }
}
```

規則存於 `xmlgrader/config`，成績存於 `xmlgrader_submissions`。Firestore 失敗時退回本機；本機紀錄不是永久雲端備份。

## 選用：Cloud Run 持續提供服務

完整步驟請閱讀 [Cloud Run 部署說明](cloudrun/部署說明_CloudRun.md)。解壓後的文件位置是 `XML_Grader/cloudrun/部署說明_CloudRun.md`。必須從本套件的 `XML_Grader` 目錄部署，不能只上傳 `cloudrun/` 子資料夾。

Cloud Run 與 Colab 使用同一份核心與 API；不需要 ngrok。取得 Service URL 後，同樣填入根目錄的 `grader-settings.js`。長期保存請啟用 Firestore，服務費用依自己的 Google Cloud 帳戶與用量確認。

## 常見問題

| 現象 | 處理方式 |
| --- | --- |
| 尚未設定自評服務 | 更新 `grader-settings.js` 的 `serverUrl` 並重新發布 |
| 連不上伺服器 | 先開 `/api/health`，檢查 Colab、ngrok 與根網址 |
| 教師密碼錯誤 | 核對 `XMLGRADER_ADMIN_TOKEN` Secret，修改後重啟後端 |
| 學生沒有可選作業 | 教師勾選「開放學生自評」後儲存，學生重新整理 |
| 尚未設定 Gemini 金鑰 | 檢查 Secret 名稱、存取許可與後端是否重啟 |
| AI 額度限制 | 稍後再試或使用自己的備援金鑰；不會產生成績 |
| 只看到本機成績 | 檢查 Firestore 是否啟用、專案 ID 與服務帳戶 IAM |
| 網站／後端版本不同 | 同步本套件的網站設定與 Notebook，再重新發布／啟動 |

`CORS_ORIGINS` 填網站 origin（例 `https://your-name.github.io`），不含 repository 路徑；多個來源以逗號分隔。學生免登入提交，學號是自行輸入，並非驗證過的身分。

## 維護與分享

後端只維護 `XML_Grader/xml_grader_core.py`、`api_server.py`、`colab_server.py`。修改後從本資料夾執行：

```powershell
python XML_Grader/scripts/build_notebook.py
```

它只產生根目錄的一個 Notebook；Cloud Run 直接使用 `XML_Grader/` 的唯一核心及 Dockerfile。此命令只需要 Python；首次生成的套件也可以直接使用，不必執行此命令。

**修改位置只有三種：**公開後端網址改 `grader-settings.js`；部署選項在 Notebook 步驟 4 調整，私密值放 Secrets；評分程式只改 `XML_Grader/*.py` 再產生 Notebook，不要改步驟 2 的自動產生區。

維護者可建立本機環境並驗證後端：

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r XML_Grader/cloudrun/requirements.txt
.venv\Scripts\python.exe tests/test_grader.py
```

這些測試使用模擬的 Gemini 回應，檢查教師驗證、作業開放、評分錯誤與成績保存，不需要自己的 API Key。

分享給另一位教師時，將 `grader-settings.js` 的 `serverUrl` 清空，不包含自己的執行環境、成績、Secret 或 JSON 憑證。對方依本 README 使用自己的帳號與後端即可。

本套件含 `MANIFEST.json`，記錄初次產生的檔案校驗資訊；自行編輯後校驗值會不同，屬正常情況。
