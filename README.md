# ESP32 × motoBlockly 物聯網創客課程

給國中生使用的 ESP32 軟硬整合課程網站。課程以積木程式、實體接線、除錯與小組專題為主線，並提供 XML 作業的 AI 自評功能。

> 本專案的課程頁是靜態 HTML；「學生自評」與「教師管理」連到共用 Flask 後端（Colab 或 Cloud Run）；其餘課程工具不需要啟動後端。

## 目錄

- [課程流程與功能](#課程流程與功能)
- [檔案說明](#檔案說明)
- [快速開始](#快速開始)
- [15 分鐘設定檢查表](#15-分鐘設定檢查表首次啟用-ai-自評)
- [發布靜態網站](#發布靜態網站)
- [程式評測後端](#程式評測後端)
- [帳號申請與服務設定](#帳號申請與服務設定)
- [後端必改清單](#後端必改清單)
- [設定評測標準](#設定評測標準)
- [測試與故障排除](#測試與故障排除)
- [安全注意事項](#安全注意事項)

目前使用 **XMLGrader 整合版 `2026-10-04-unified`**。

只想使用 AI 評分系統，請下載 [Releases 的 XMLGrader 獨立版 ZIP](https://github.com/suyungsheng-kh/esp32-2026/releases/latest/download/XMLGrader_Standalone.zip)，依 [獨立版安裝說明](XML_Grader/STANDALONE.md) 操作。ZIP 內有自己的首頁、教師／學生頁及完整 README，不需要其他課程檔案，也不沿用此網站的後端網址。

### 選一種下載方式，不要混用

| 使用目的 | 唯一下載入口 | 不需要另外下載 |
| --- | --- | --- |
| 使用完整 ESP32 課程 | 本儲存庫的 Code → Download ZIP，或複製儲存庫 | Releases 獨立版 |
| 只使用 XML 作業評分 | 上方 Releases 的 `XMLGrader_Standalone.zip` 附件 | 本儲存庫原始碼；Releases 下方自動附帶的 Source code ZIP／tar.gz |

儲存庫只保留一份後端原始碼、一個根目錄 Colab 啟動檔及一份 Dockerfile；不再放獨立版資料夾與 ZIP 副本。兩種下載方式使用相同評分核心，不是兩套系統。

**一般教師只需設定：**Notebook 步驟 4 的部署選項、Colab Secrets，以及 `grader-settings.js` 的 `serverUrl`。評分規則從教師網頁管理；不需改後端 Python 或 Notebook 步驟 2。

## 課程流程與功能

| 階段 | 學生任務 | 對應頁面／工具 |
| --- | --- | --- |
| 課前／Day 1 | 認識 ESP32、motoBlockly、G/V/S 與用電安全 | `index.html` |
| Day 1 | 有聲紅綠燈：輸出、按鈕與控制邏輯 | `day-1.html` |
| Day 2 | 光影與閘門：類比輸入、伺服馬達與條件控制 | `day-2.html` |
| Day 3 | 感測器整合、專題設計、實作與發表 | `day-3.html` |
| 延伸課 | 將資料送至 Google 表單／試算表 | `day-n.html` |
| 全程 | 接線練習、除錯流程、程式自評 | `circuit.html`、`debug-passport.html`、`student.html` |

### 新增的教學鷹架

- **接線與安全闖關**：在前導課程中複習 G/V/S，並以「找錯接線」題目確認 VCC、GND 不可接反。
- **除錯闖關護照**：依「描述現象 → 接線 → 程式 → 查資源 → 問 AI → 求助 → 反思」七步驟逐步解鎖徽章。紀錄只存於學生目前的瀏覽器。
- **專題設計單**：Day 3 內用浮動視窗開啟，學生先規劃問題、輸入／輸出、判斷邏輯與成功條件，再接線實作。
- **分層任務卡**：每組從基礎關開始，可再進入挑戰關、創意關，降低整合專題的門檻。
- **每日最低完成線**：Day 1～3 都先列出當日必達的小目標，讓學生先完成可驗證的核心功能，再延伸挑戰。
- **上電前互相檢核**：小組在接上 USB 前共同確認 G/V/S、腳位與短路風險，完成三項才可上電。
- **三分鐘下課回饋**：每一天都有可儲存、複製的回饋單，記錄成功內容、卡關點、嘗試方法與下一步需要的協助。
- **三句式成果發表**：Day 3 以「問題 → 系統規則 → 解法」引導每組完成簡短且有重點的發表。

## 檔案說明

| 檔案 | 用途 | 是否需要後端 |
| --- | --- | --- |
| `index.html` | 前導課程、G/V/S 接線與安全闖關 | 否 |
| `day-1.html`～`day-3.html` | 三天的教學頁與互動模擬 | 否 |
| `day-n.html` | 雲端資料庫延伸課 | 否 |
| `circuit.html` | React 單檔接線練習器與挑戰關 | 否 |
| `pre-power-check.html` | 上電前小組互相檢核卡 | 否 |
| `debug-passport.html` | 除錯闖關護照與徽章 | 否 |
| `daily-reflection.html` | 每日三分鐘回饋單；依 `?day=1`、`?day=2`、`?day=3` 切換 | 否 |
| `project-design.html` | 專題設計單；由 Day 3 的浮動視窗載入，也可單獨開啟列印 | 否 |
| `student.html` | 上傳 `.xml` 作品、取得 AI 自評結果 | **是** |
| `teacher.html` | 教師登入、作業規則、XML 試評、成績查詢 | **是** |
| `grader-settings.js` | 教師與學生共用的公開後端根網址 | 否 |
| `XML_Grader/*.py` | Colab／Cloud Run 共用評分核心、API 與啟動器 | **是** |
| `XMLGrader_Colab.ipynb` | 整合版 Colab 啟動檔；由共用後端自動產生 | **是** |
| `example.7z` | 各天可測試的 motoBlockly XML 範例 | 否 |

## 快速開始

課程網站與 AI 自評可以分開使用。課程頁、接線、安全、除錯、設計單與回饋單不需要後端；學生自評與教師管理需要啟動後端。

1. 將網站資料夾發布到 GitHub Pages、學校網站空間或其他靜態主機。
2. 開啟 `index.html`，依前導、Day 1～3 的順序上課。
3. 要啟用自評，再完成下方檢查表。
4. 首頁「教師管理」會開啟 `teacher.html`；學生從「程式評測」進入 `student.html`。

請透過 HTTP／HTTPS 使用網站。專題設計單會在 Day 3 的浮動視窗中載入，回饋與除錯護照保存在目前瀏覽器。

## 15 分鐘設定檢查表（首次啟用 AI 自評）

適合帳號已準備好的教師；第一次申請帳號、等待驗證或發布網站可能需要額外時間。先使用 Colab、關閉 Firestore，就能啟用自評與本次課程的成績紀錄。

### 0～3 分鐘｜準備帳號、網站與三個 Secret

- [ ] 在 [Google AI Studio](https://aistudio.google.com/apikey) 取得自己的 Gemini API Key。
- [ ] 在 [ngrok Dashboard](https://dashboard.ngrok.com/) 取得自己的 Authtoken。
- [ ] 自行設定一組教師管理密碼，建議使用密碼管理器產生。
- [ ] 確認課程網站已發布，而且能修改 `grader-settings.js`。

### 3～6 分鐘｜開啟 Colab

- [ ] 上傳根目錄的 [XMLGrader_Colab.ipynb](XMLGrader_Colab.ipynb) 到自己的 Google Drive，以 [Google Colab](https://colab.research.google.com/) 開啟。
- [ ] 左側 **Secrets** 新增下列三個名稱，填入對應值，逐項允許 Notebook 存取。

| Secret 名稱（逐字相同） | 填入內容 | 必填 |
| --- | --- | --- |
| `XMLGRADER_NGROK_AUTHTOKEN` | 自己的 ngrok Authtoken | 是 |
| `XMLGRADER_GEMINI_API_KEY_1` | 自己的 Gemini API Key | 是 |
| `XMLGRADER_ADMIN_TOKEN` | 自己設定的教師管理密碼 | 是 |
| `XMLGRADER_GEMINI_API_KEY_2` | 第二把 Gemini Key | 選填備援 |

不要把實際值貼入 HTML、Notebook 程式碼或公開 repository。

### 6～9 分鐘｜步驟 4 的集中設定

- [ ] `USE_FIREBASE = False`：初次測試不需要 Firebase 帳號。
- [ ] `NGROK_STATIC_DOMAIN = ""`：有自己保留的固定網域才填入，格式不含 `https://`。
- [ ] `SHOW_SCORE_TO_STUDENT` 決定學生是否立即看分數。
- [ ] `REPLACE_SAVED_RUBRICS = False` 保持預設，避免重跑 Notebook 時覆蓋教師已修改的作業。
- [ ] 首次可保留範例 `RUBRICS`，連線後從教師網頁調整規則。

### 9～12 分鐘｜啟動與共用網址

- [ ] 由上到下執行 Notebook；看到「✅ API 已上線」。
- [ ] 開啟輸出的 `<根網址>/api/health`，確認 `"ok": true` 與版本 `2026-10-04-unified`。
- [ ] 🔴 修改網站 [grader-settings.js](grader-settings.js)，只更動 `serverUrl`：

```javascript
window.XMLGRADER_SETTINGS = Object.freeze({
  serverUrl: 'https://<你的-ngrok-網域>',
  expectedVersion: '2026-10-04-unified'
});
```

- [ ] 重新發布網站。教師與學生會共用同一網址，無需分別改 HTML。

### 12～15 分鐘｜教師登入與試評

- [ ] 開啟首頁「教師管理」，輸入 `XMLGRADER_ADMIN_TOKEN` 的密碼登入。
- [ ] 確認畫面顯示「後端已設定 Gemini 金鑰」。
- [ ] 修改或新增作業名稱、主題、配分規則，勾選「開放學生自評」，按「儲存設定」。
- [ ] 用 `XML_Grader/esp32/` 或 `example.7z` 的 XML 做「單檔試評」。
- [ ] 開啟學生頁，輸入測試學號，選作業並上傳 XML，確認收到評語。
- [ ] 回教師頁讀取成績：學生自評會記錄；教師試評不會記錄。

完成後，Colab 必須維持執行。沒有固定 ngrok 網域時，每次重啟要重新更新 `grader-settings.js`。教師密碼只存在頁面記憶體，重新整理後需重新登入。

## 發布靜態網站

本網站沒有前端建置步驟，可直接發布 HTML 與 `grader-settings.js`。

### GitHub Pages

1. 將課程 HTML、`teacher.html`、`student.html`、`grader-settings.js` 與文件上傳 repository。
2. **Settings → Pages** 選擇從分支發布，指定根目錄。
3. 待網址建立後，開啟 `https://<帳號>.github.io/<repository>/`。
4. 確認課程頁、設計單、教師登入與學生自評入口可開啟。

網站內部導覽已改成相對路徑，更換帳號或 repository 不需逐頁修改網址。只需在 `grader-settings.js` 更新後端根網址。請勿上傳 `.venv/`、`runtime/`、SQLite 成績檔或服務帳戶 JSON；專案的 `.gitignore` 已列出本機執行資料。

## 程式評測後端

整合版版本為 `2026-10-04-unified`，兩種部署共用相同解析、評分與 API：

```text
teacher.html ── 教師密碼 ──┐
                          ├─ api_server.py ── xml_grader_core.py ── Gemini
student.html ── XML／學號 ─┘                        └─ Firestore 或本機暫存
                     └─ Colab＋ngrok / Cloud Run
```

- 教師可管理多份作業、上傳範本與參考解答、生成規則、單檔試評及查詢成績。
- 學生只取得開放中的作業名稱、主題與規則，不取得金鑰、教師密碼、未開放作業或參考解答。
- 教師 API 全部驗證 `X-Admin-Token`。未設定教師密碼時，管理功能保持關閉。
- Gemini 額度／速率限制與服務異常不算成 0 分，也不建立成績。
- 成功的學生評測會記錄真實分數；「學生不顯示分數」只影響畫面，不影響教師成績。
- 教師／學生入口僅使用根目錄 `teacher.html`／`student.html`，不再保留舊版入口副本。

### 選擇部署方式

| 方式 | 適用情況 | 操作 |
| --- | --- | --- |
| Colab＋ngrok | 先試用、單次工作坊、教師手動啟動 | 依 15 分鐘檢查表 |
| Cloud Run | 需要持續可用、固定服務網址 | 依 [Cloud Run 部署說明](XML_Grader/cloudrun/部署說明_CloudRun.md) |

Cloud Run 的服務建立與計費須依自己的 Google Cloud 帳戶確認；本專案不保證免費。學生不用登入 Google Cloud，教師仍須輸入管理密碼。

## 帳號申請與服務設定

### Colab、Gemini 與 ngrok（必需）

1. 使用 Google 帳號登入 [Colab](https://colab.research.google.com/)，上傳 Notebook。
2. 在 [Google AI Studio API Keys](https://aistudio.google.com/apikey) 建立 Gemini Key；若頁面要求專案，依頁面完成建立／選擇。
3. 註冊 [ngrok](https://dashboard.ngrok.com/)，複製自己的 Authtoken；固定網域可選填。
4. 在 Colab Secrets 新增三個必填值。教師管理密碼是你自己設定的，不是 Google 密碼。

### Firestore（需要跨課保存時才啟用）

未啟用時，設定與成績存在 Colab 本機；重跑儲存格不會清除，但 Colab 執行環境被釋放後就不保留。Cloud Run 本機檔案也不是永久儲存。

新版透過服務帳戶存取 Firestore，移除舊版 Web API key 與匿名公開讀寫方式。OAuth 服務帳戶請求依 IAM 授權，與 Firebase 使用者的安全規則不同，詳見 [Firestore REST 驗證文件](https://firebase.google.com/docs/firestore/use-rest-api)。

1. 在 [Firebase Console](https://console.firebase.google.com/) 建立自己的專案與 Cloud Firestore 資料庫，使用 `(default)` 資料庫。
2. 建立專用服務帳戶，授予該專案 **Cloud Datastore User**（`roles/datastore.user`）。
3. **Colab**：為該服務帳戶建立 JSON 金鑰，整份 JSON 放進 `XMLGRADER_FIREBASE_SERVICE_ACCOUNT_JSON` Secret，專案 ID 放進 `XMLGRADER_FIREBASE_PROJECT_ID` Secret。
4. 在 Notebook 步驟 4 改為 `USE_FIREBASE = True`，重跑設定與啟動。
5. **Cloud Run**：直接使用執行服務帳戶的權限；不需下載 JSON，依 Cloud Run 文件操作。

前端不直接讀寫 Firestore；若此專案沒有其他需要用戶端直接存取的功能，可使用：

```text
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} { allow read, write: if false; }
  }
}
```

不要把此規則套用到另有其他應用程式共用的資料庫；請先確認它們的存取需求。

## 後端必改清單

🔴 私密值只設在 Colab Secrets 或 Cloud Run Secrets；公開網域只設在 `grader-settings.js`。

| 設定 | Colab | Cloud Run |
| --- | --- | --- |
| Gemini 主金鑰 | `XMLGRADER_GEMINI_API_KEY_1` Secret | 同名 Secret |
| Gemini 備援金鑰 | `XMLGRADER_GEMINI_API_KEY_2` Secret（可選） | 同名 Secret（可選） |
| 教師管理密碼 | `XMLGRADER_ADMIN_TOKEN` Secret | 同名 Secret |
| ngrok Token | `XMLGRADER_NGROK_AUTHTOKEN` Secret | 不需要 |
| 固定 ngrok 網域 | 步驟 4 的 `NGROK_STATIC_DOMAIN` | 不需要 |
| 網站來源 | 步驟 4 的 `CORS_ORIGINS` | `XMLGRADER_CORS_ORIGINS` |
| Firestore 啟用 | `USE_FIREBASE` | `XMLGRADER_FIREBASE_ENABLED=true` |
| Firestore 專案 | `XMLGRADER_FIREBASE_PROJECT_ID` Secret | 同名環境變數 |
| Firestore 授權 | `XMLGRADER_FIREBASE_SERVICE_ACCOUNT_JSON` Secret | 執行服務帳戶與 IAM |
| 前端共用根網址 | `grader-settings.js` 的 `serverUrl` | 同一欄填 Service URL |

`CORS_ORIGINS` 填網站 **origin**（例 `https://your-name.github.io`），不加 `/repository/` 路徑；多個來源以逗號分隔。它限制瀏覽器來源，教師授權仍由密碼驗證。

### 從舊版遷移

1. 以新版 Notebook 取代原啟動檔；原 `xmlgrader/config` 與 `xmlgrader_submissions` 集合名稱保留，可讀取原規則與成績。
2. 重新設定自己的金鑰與教師密碼，不沿用原檔內建的憑證與網域。
3. 啟用 Firestore 時，改用服務帳戶授權；不再需要 `XMLGRADER_FIREBASE_API_KEY`。
4. 在新版教師頁載入舊作業後儲存。新版會移除設定內的 `api_key_1`、`api_key_2`、`admin_token` 欄位，金鑰改從後端 Secrets 取得。
5. 更新 `grader-settings.js` 後重新發布。若曾分享舊版入口，改提供根目錄的 `teacher.html`／`student.html`。
6. 若舊憑證曾公開分享，請撤銷並換新。

## 設定評測標準

從首頁「教師管理」登入後：

1. 在「③ 作業主題與評分規則」新增一份，填標準名稱、主題、規則與配分。
2. 固定練習可用標準答案模式；創意專題取消「標準答案題型」。
3. 視需要在④上傳初始範本或老師參考解答，系統會轉成虛擬碼。
4. 可用 AI 生成規則，但需由教師檢查後儲存。
5. 勾選「開放學生自評」，按⑤儲存。取消勾選會使學生看不到且無法提交該作業。
6. 先做⑥教師試評，再讓學生上傳。
7. 從⑦讀取成績。學生輸入的學號與 XML 屬作業資料，請依學校的保存與使用安排管理。

Gemini 金鑰不能從教師網頁修改；要變更時回後端 Secrets。模型可以由教師頁的「讀取可用模型」選取，以目前帳號實際可用的清單為準。

### 本機暫存與 Firestore

| 模式 | 規則 | 成績 | 保留範圍 |
| --- | --- | --- | --- |
| 未啟用 Firestore | `grader_config.json` | `submissions.sqlite3` | 目前後端的檔案系統 |
| 啟用 Firestore | `xmlgrader/config` | `xmlgrader_submissions` | 跨執行環境保留 |

Firestore 失敗時會退回本機保存；教師頁的儲存回應及本機紀錄提示可用來確認。Cloud Run 的本機暫存不會跨執行個體同步，正式長期使用請啟用 Firestore。

## 測試與故障排除

### 開課前驗收

- [ ] 手機與電腦能開啟首頁、Day 1～3、接線、安全、除錯護照、回饋與設計單。
- [ ] `/api/health` 顯示整合版版本。
- [ ] 正確密碼可登入教師管理；錯誤密碼無法讀取設定與成績。
- [ ] 新增與儲存一份開放作業後，學生能選到；關閉後學生不再看見。
- [ ] 教師試評與學生自評各一次，確認學生那筆出現在成績清單。
- [ ] 若取消顯示學生分數，學生只看評語，教師仍能讀到真實分數。

### 常見問題

| 現象 | 檢查與處理 |
| --- | --- |
| 老師尚未設定自評服務 | 填寫 `grader-settings.js` 的 `serverUrl`，重新發布網站 |
| 無法連線 | 先開 `/api/health`；檢查 Colab／ngrok 是否停止、網址是否已變 |
| 教師密碼錯誤 | 核對後端 `XMLGRADER_ADMIN_TOKEN`；不是 Gemini Key 或 Google 密碼 |
| 教師管理尚未啟用 | 在後端設好 `XMLGRADER_ADMIN_TOKEN` 後重啟 |
| 學生沒有可選作業 | 教師勾選「開放學生自評」，儲存後讓學生重新整理 |
| 尚未設定 Gemini 金鑰 | 檢查主金鑰 Secret 名稱、存取許可與後端是否重啟 |
| 額度／速率限制 | 等待後重試，或使用自己的備援金鑰；這次不評分也不記錄 |
| Firestore 失敗／只顯示本機紀錄 | 核對專案 ID、資料庫與服務帳戶 IAM，不要改成公開讀寫 |
| 網站／後端版本不同 | 同步新版 Notebook、HTML 與 `grader-settings.js`，再重啟與發布 |

### 維護者驗證

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r XML_Grader/cloudrun/requirements.txt
python XML_Grader/scripts/build_notebook.py
.venv\Scripts\python.exe tests/test_grader.py
```

離線測試使用模擬 Gemini 回應，不消耗 API 額度。涵蓋教師驗證、金鑰隔離、作業開放、正常評分、額度與服務失敗、真實分數紀錄，以及附帶的 XML 範例解析。

## 安全注意事項

教師密碼與 Gemini Key 只存在後端環境／Secrets，不寫入 HTML、Notebook 程式碼或設定資料庫。學生可免登入提交作業，學號為自行輸入，不能視為已驗證身分。對外大規模使用時，請依需求加入學生身分與流量限制。

## 維護建議

後端只維護 `XML_Grader/xml_grader_core.py`、`api_server.py`、`colab_server.py`。修改後執行：

```powershell
python XML_Grader/scripts/build_notebook.py
```

這只產生根目錄的 `XMLGrader_Colab.ipynb`。其步驟 2 是供 Colab 自足執行的自動產生區，請勿直接修改；部署選項可在步驟 4 調整。Cloud Run 直接使用 `XML_Grader/` 的共用核心與唯一 Dockerfile，不複製另一套後端。

更新後要重新產生獨立分享包，於本專案根目錄執行：

```powershell
python XML_Grader/scripts/package_standalone.py
```

它只打包指定的程式、文件與 XML 範例，不包含本機執行環境、成績或憑證。產物只存於已忽略的 `.publish/dist/XMLGrader_Standalone.zip`；不會在儲存庫建立第二份可修改的原始碼資料夾。獨立版文件的維護來源是 `XML_Grader/STANDALONE.md`。

發布前執行 `.venv\Scripts\python.exe tests/test_package.py`，確認 ZIP 能獨立使用。通過後，在 GitHub **Releases → Draft a new release** 選擇這次提交、建立版本標籤，附上該 ZIP，並發布為最新版本。README 的下載連結會指向最新 Release 的附件；不要把 ZIP 或解壓資料夾提交回 `main`。

若有不相容變更，同步更新 `api_server.py` 的 `SERVER_VERSION` 與 `grader-settings.js` 的 `expectedVersion`。備份作業規則與成績時，不要把私密憑證一起分享。
