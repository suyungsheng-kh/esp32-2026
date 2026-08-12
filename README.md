# ESP32 × motoBlockly 物聯網創客課程

給國中生使用的 ESP32 軟硬整合課程網站。課程以積木程式、實體接線、除錯與小組專題為主線，並提供 XML 作業的 AI 自評功能。

> 本專案的課程頁是靜態 HTML；只有「程式評測」會連到 Google Colab 上的 Flask 後端。除了 `student.html` 以外，其餘工具即使沒有啟動後端也可以使用。

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
| `XMLGrader_Colab.ipynb` | Colab 後端：XML 解析、Gemini 評分、Flask API、ngrok | **是** |
| `example.7z` | 各天可測試的 motoBlockly XML 範例 | 否 |

## 快速開始

### 僅使用課程與互動工具

1. 將整個資料夾放在靜態網站主機，或使用本機 HTTP 伺服器開啟。
2. 開啟 `index.html`。
3. 依前導課程、Day 1～3 的順序上課。

> 請不要以 `file://` 直接雙擊開啟作為正式使用方式。雖多數頁面可運作，但 Day 3 的專題設計單使用 iframe，透過 HTTP／HTTPS 開啟會更穩定。

### 啟用學生程式自評

除了發布前端外，還要完成：

1. 申請 Gemini API Key。
2. 申請並設定 ngrok。
3. 建立 Firestore，或先使用 Colab 暫存設定。
4. 執行 `XMLGrader_Colab.ipynb`。
5. 在 `student.html` 設定後端網址。
6. 先以 `example.7z` 的 XML 範例試評，再開放學生使用。

完整步驟見後面的「[程式評測後端](#程式評測後端)」。

## 15 分鐘設定檢查表（首次啟用 AI 自評）

這份清單適合首次使用、希望先讓 AI 自評正常運作的教師。首次啟用**不必設定 Firebase**；先使用 Colab 暫存設定，確認流程可用後，再依後文啟用永久保存。

開始前，請先確認課程網站已可從網路開啟，而且你有權編輯 [student.html](student.html)。全程只會使用兩個必填 Secret，請勿把它們貼進 HTML、Notebook 儲存格或 GitHub。

### 0～3 分鐘｜取得兩個必填資料

- [ ] 申請 Gemini API Key，複製 API Key。
- [ ] 註冊 ngrok，從 Dashboard 複製 Authtoken。
- [ ] 準備一個可公開開啟的課程網站網址；若尚未發布，先完成「[發布靜態網站](#發布靜態網站)」。

### 3～6 分鐘｜開啟 Notebook 與新增 Secret

- [ ] 將 [XMLGrader_Colab.ipynb](XMLGrader_Colab.ipynb) 上傳到 Google Drive，再以 Google Colab 開啟。
- [ ] 在 Colab 左側開啟 **Secrets**，新增 `XMLGRADER_NGROK_AUTHTOKEN`，貼上 ngrok Authtoken，並允許 Notebook 存取。
- [ ] 新增 `XMLGRADER_GEMINI_API_KEY_1`，貼上 Gemini API Key，並允許 Notebook 存取。

### 6～9 分鐘｜填寫「步驟 4：🔴 部署設定」

在 Notebook 的「步驟 4：🔴 部署設定」只做下列設定：

- [ ] `USE_FIREBASE = False`（首次測試不需 Firebase）。
- [ ] `NGROK_STATIC_DOMAIN = ""`（沒有自己保留的 ngrok 固定網域時，保持空白）。
- [ ] `SHOW_SCORE_TO_STUDENT = True` 或 `False`，依你是否要讓學生立即看分數決定。
- [ ] 確認 `RUBRICS` 至少有一份 `is_open: True` 的作業；第一次可先保留範例規則，連線成功後再改成自己的題目。

### 9～12 分鐘｜啟動並取得網址

- [ ] 由上到下執行 Notebook 的所有儲存格。
- [ ] 看到「`✅ API 已上線`」後，複製 `https://...ngrok...` 的**根網址**。
- [ ] 在瀏覽器開啟 `<根網址>/api/health`，確認畫面出現 `"ok": true`。

若看到 Secret 讀取錯誤，請回到 Colab Secrets 檢查名稱、內容與「允許 Notebook 存取」是否都正確；不需要在程式碼中填 token。

### 12～15 分鐘｜連接學生頁並完成試評

- [ ] 開啟 [student.html](student.html)，找到 `const SERVER_URL = '...'`，將引號內改成剛剛複製的 ngrok 根網址。
- [ ] 重新發布靜態網站，並重新整理學生頁。
- [ ] 從 `example.7z` 解壓一個 XML 範例，完成一次上傳試評。
- [ ] 確認學生能看到作業名稱、收到回應，且瀏覽器沒有顯示「無法連線」。

### 完成後要知道的事

- 未設定固定網域時，每次 Colab 停止或重啟，ngrok 網址都會改變；請重做「12～15 分鐘」並重新發布 `student.html`。
- `USE_FIREBASE = False` 時，評測設定和提交紀錄只保留到這次 Colab 執行結束。需要跨課保存時，再依後面的「🔴 必改 4：設定 Firebase，或明確關閉 Firebase」啟用 Firebase。
- 課程頁、接線工具、除錯護照與專題設計單不依賴 AI 自評後端；後端暫停時，仍可照常上課。

## 發布靜態網站

本專案沒有建置步驟、套件安裝或資料庫遷移；可直接部署至 GitHub Pages、學校網站空間或任一靜態主機。

### GitHub Pages 建議流程

1. 在 GitHub 建立 repository，將此資料夾內的 HTML、Notebook、範例與 `README.md` 上傳。
2. 到 repository 的 **Settings → Pages**，選擇從分支部署。
3. 選擇含有 `index.html` 的分支與根目錄，儲存後等待網址建立。
4. 以 `https://<帳號>.github.io/<repository>/` 開啟網站。
5. 分別測試前導、Day 1～3、接線練習、除錯護照、專題設計單與程式評測。

### ⚠️ 前端網址改動提醒

目前各頁導覽列多使用既有 GitHub Pages 的完整網址。如果更換網站帳號、repository 名稱或網域，請在所有 `.html` 檔搜尋並更換：

```text
https://suyungsheng-kh.github.io/esp32-2026/
```

PowerShell 可用：

```powershell
rg -n "suyungsheng-kh.github.io/esp32-2026" -g "*.html"
```

## 程式評測後端

### 架構

```text
學生 student.html
      │ 上傳 XML + 學號
      ▼
Google Colab：Flask API（XMLGrader_Colab.ipynb）
      ├─ XML 解析、積木／腳位事實檢查
      ├─ Gemini API 評分
      ├─ Firestore：設定與成績紀錄（可選）
      ▼
ngrok HTTPS 公開網址
```

學生頁使用兩個端點：

| 方法 | 端點 | 用途 |
| --- | --- | --- |
| `GET` | `/api/student/config` | 讀取已開放的評測標準與顯示設定 |
| `POST` | `/api/student/grade` | 接收 `.xml` 與學號，回傳 AI 評語與分數 |

### 在 Colab 啟動

1. 將 [XMLGrader_Colab.ipynb](XMLGrader_Colab.ipynb) 上傳至自己的 Google Drive，並以 Google Colab 開啟。
2. 依「[後端必改清單](#後端必改清單)」完成帳號、金鑰與專案設定。
3. 由上到下依序執行所有儲存格：
   - 安裝 Python 套件。
   - 產生 `xml_grader_core.py` 與 `colab_server.py`。
   - **在「步驟 4：部署設定」集中填寫課程設定，並從 Colab Secret 讀取私密值。**
   - 啟動 Flask 與 ngrok。
4. 確認最後輸出含有：

```text
✅ API 已上線（背景執行）：https://<你的網域>
健康檢查：https://<你的網域>/api/health
```

5. 在瀏覽器開啟健康檢查網址，應回傳類似：

```json
{"ok": true, "version": "..."}
```

6. 將相同的根網址填入 `student.html` 的 `SERVER_URL`，重新發布網站。

### Colab 依賴套件

Notebook 目前會安裝：

```text
flask
flask-cors
pyngrok
pandas
google-genai
```

Colab 執行階段停止後，Flask 與 ngrok 都會停止；學生頁會無法評測，直到重新執行 Notebook。

## 帳號申請與服務設定

### 1. Google Colab

1. 使用 Google 帳號登入 [Google Colab](https://colab.research.google.com/)。
2. 將 Notebook 放到自己的 Google Drive，避免直接在來源檔上保存私人金鑰。
3. 開課當天開啟 Notebook，確認執行階段可連網。

### 2. Gemini API Key（AI 批改）

1. 前往 [Google AI Studio 的 API key 頁面](https://aistudio.google.com/app/apikey)。
2. 以 Google 帳號登入，選擇或建立 Google Cloud 專案。
3. 建立 Gemini API Key，僅保存於 Colab 或其他伺服器端環境。
4. 在 Google Cloud 的 **Credentials** 為金鑰設定 API 限制，只允許 Gemini API；並依授課情況設定預算、警示與額度。

Google 官方文件說明可由 AI Studio 建立 Gemini API Key，且 API key 應加以限制：[Gemini API key 文件](https://ai.google.dev/gemini-api/docs/api-key)、[Google Cloud API key 管理](https://cloud.google.com/docs/authentication/api-keys)。

### 3. ngrok（讓 Colab 後端具有 HTTPS 網址）

1. 到 [ngrok Dashboard](https://dashboard.ngrok.com/signup) 建立帳號。
2. 在 Dashboard 取得 Authtoken。
3. 若要固定網址，於 Dashboard 建立／保留一個網域，並將該網域填入 Notebook。
4. 在課前測試此網域可由 Colab 正常連線；若系統顯示 `ERR_NGROK_334`，代表仍有舊 agent 占用該網域，請在 Dashboard 停止舊 agent 或重啟舊的 Colab 執行階段。

參考：[ngrok Reserved Domains 文件](https://ngrok.com/docs/api-reference/reserveddomains/create)。固定網域是否可用取決於 ngrok 目前的帳戶方案與設定。

### 4. Firebase / Cloud Firestore（保存評測設定與成績）

若只做短暫單人測試，可先將 `FIREBASE["enabled"]` 設為 `False`，由 Colab 的本機 `grader_config.json` 保存資料；但每次 Colab 重置後，本機資料可能消失。

若要跨次上課保存設定與成績：

1. 前往 [Firebase Console](https://console.firebase.google.com/) 建立專案。
2. 在 **Build → Firestore Database** 建立 Native mode Firestore 資料庫，選擇資料庫地區。
3. 在專案設定中新增 Web app，取得 `project_id` 與 Web API key。
4. 將值填入 Notebook 的 `FIREBASE` 設定區。
5. 先以測試資料做讀寫驗證，再設計符合使用情境的 Firestore Security Rules。

> **重要：目前 Notebook 以 Firestore REST API + Web API key 讀寫設定與成績，並沒有使用 Firebase Authentication。** 若 Firestore 規則允許匿名讀寫，任何知道 API 的人都可能讀寫資料。正式對外使用前，應改為由受保護的後端憑證存取，或導入 Firebase Authentication 與安全規則。Firestore 官方也明確提醒，允許所有讀寫的規則不能用於正式環境：[Firestore Security Rules 文件](https://firebase.google.com/docs/firestore/security/get-started)。

## 後端必改清單

以下均位於 `XMLGrader_Colab.ipynb` 的 **「步驟 4：🔴 部署設定」**。新版已將所有部署值集中於此；除非維護核心功能，**不要直接修改** `xml_grader_core.py` 或 `colab_server.py` 的設定來源。

### Colab Secret 名稱

在 Colab 左側面板開啟 **Secrets**，新增下列秘密並允許 Notebook 存取：

| Secret 名稱 | 是否必填 | 用途 |
| --- | --- | --- |
| `XMLGRADER_NGROK_AUTHTOKEN` | 是 | ngrok tunnel 的認證 token |
| `XMLGRADER_GEMINI_API_KEY_1` | 是 | Gemini XML 作業評分 |
| `XMLGRADER_FIREBASE_PROJECT_ID` | Firestore 啟用時 | Firebase 專案 ID |
| `XMLGRADER_FIREBASE_API_KEY` | Firestore 啟用時 | Firestore REST API 使用的 Web API key |

### 🔴 必改 1：撤銷現有 ngrok Authtoken，改用自己的 Token

**操作：** 在 Colab Secret 新增 `XMLGRADER_NGROK_AUTHTOKEN`。新版 Notebook 會自動讀取，不需要再修改 `colab_server.py`。

不要把 token 寫回 Notebook、`student.html` 或 GitHub。

### 🔴 必改 2：設定 ngrok 固定網域，或採用每次更新網址的流程

**操作：** 在「步驟 4：部署設定」填寫 `NGROK_STATIC_DOMAIN`。

```python
NGROK_STATIC_DOMAIN = "<你保留的網域>.ngrok-free.app"
```

若沒有固定網域，將 `NGROK_STATIC_DOMAIN` 留為空字串即可；新版 Notebook 會自動建立暫時網址，不需要改動啟動程式。每次重啟 Colab 都會得到新網址，並且都要同步更新 `student.html` 的 `SERVER_URL` 後重新發布前端。

### 🔴 必改 3：設定 Gemini API Key 與評測規則

**操作：** 在「步驟 4：部署設定」修改 `MODEL_NAME`、`SHOW_SCORE_TO_STUDENT` 與 `RUBRICS`。Notebook 會自動將 Gemini API Key 與評測標準寫入 Firebase 或本機 `grader_config.json`。請依作業修改主題、規則與 `example_code`：

```python
import json
import xml_grader_core as core

cfg = core.load_config()
cfg.update({
    "api_key_1": "<你的 Gemini API Key>",
    "api_key_2": "",  # 選填：第二把 key，可在額度限制時輪替
    "model_name": "gemini-2.5-flash",
    "student_show_score": True,
    "max_size_mb": 10,
    "rubrics_json": json.dumps([{
        "id": "day1-traffic-light",
        "name": "Day 1 有聲紅綠燈",
        "theme": "有聲紅綠燈",
        "rules": "1. 正確設定紅、黃、綠 LED 腳位（30 分）\n2. 依序控制燈號（40 分）\n3. 加入蜂鳴器提示與合理等待時間（30 分）",
        "is_open": True,
        "is_standard_answer": False,
        "use_custom_extension": False,
        "extension_rules": "",
        "template_code": "",
        "example_code": ""
    }], ensure_ascii=False)
})
print(core.save_config(cfg))
```

- `is_open: True` 才會出現在學生頁的評測標準選單。
- 開放創意題時建議使用 `is_standard_answer: False`，避免完全相同於老師範例時才給滿分的指示。
- 若有老師參考作業 XML，可先用 `/api/teacher/convert_xml` 將其轉為虛擬碼後填入 `example_code`；但目前 repository 沒有教師管理頁，需要自行透過 API 或 Colab 呼叫完成。

### 🔴 必改 4：設定 Firebase，或明確關閉 Firebase

**操作：** 在「步驟 4：部署設定」將 `USE_FIREBASE = True`，並在 Colab Secret 新增 Firebase 的專案 ID 與 Web API key。Notebook 會轉成下列後端環境參數：

```python
FIREBASE = {
    "enabled": True,
    "project_id": "<Firebase project ID>",
    "api_key": "<Firebase Web API key>",
    "config_collection": "xmlgrader",
    "config_doc": "config",
    "submissions_collection": "xmlgrader_submissions",
}
```

若不使用 Firebase，請在「步驟 4：🔴 部署設定」設定：

```python
USE_FIREBASE = False
```

此時設定檔會寫入 `/content/XMLGrader/grader_config.json`，只在目前的 Colab 執行階段有效。要長期保留，需自行掛載 Google Drive 或改用安全的雲端資料庫。

### 🔴 必改 5：設定學生頁的後端根網址

**位置：** `student.html`。

```javascript
const SERVER_URL = 'https://<你的-ngrok-網域>';
```

只填網域根網址，不要加上 `/api/student/grade`；程式會自行接上 API 路徑。網址變更後，重新部署靜態網站並用 `/api/health` 先確認服務。

### 🟠 建議改 6：保護教師端 API

Notebook 的 `_require_admin()` 目前一律放行，`/api/teacher/config`、`/api/teacher/test` 與成績紀錄端點沒有登入保護。若未來加入教師頁或對外公開端點，至少要：

1. 實作管理者驗證，而非直接 `return None`。
2. 將管理 token 放入 Colab Secret，不放在前端與 repository。
3. 為 API 設定允許來源（CORS），不要長期使用 `origins: "*"`。
4. 將 Firestore 的匿名讀寫權限移除，改由伺服器端服務帳戶或使用者驗證控制。

## 設定評測標準

一份 rubric 至少包含：

| 欄位 | 用途 |
| --- | --- |
| `id` | 不重複的識別碼，例如 `day2-servo` |
| `name` | 學生頁顯示名稱 |
| `theme` | 作業主題 |
| `rules` | 評分規則與配分，建議總分 100 分 |
| `is_open` | 是否開放學生自評 |
| `is_standard_answer` | 是否視老師範例為標準答案 |
| `template_code` | 選填：初始空白範本的虛擬碼 |
| `example_code` | 選填：老師參考解答的虛擬碼 |

建議每次只開放當日作業：

```python
"is_open": True   # 今日作業
"is_open": False  # 尚未開放的作業
```

學生評測前檢查：

- 至少已有一把 Gemini API Key。
- 至少一份 rubric 的 `is_open` 為 `True`。
- `student.html` 的 `SERVER_URL` 可連到 API。
- API 根網址與 `/api/health` 都正常。

## 測試與故障排除

### 開課前建議驗收

1. 用手機與電腦各開一次課程首頁。
2. 測試前導課程的 G/V/S 接線與安全找錯題。
3. 開啟 `circuit.html`，加入模組、接線並檢查結果。
4. 開啟除錯護照，勾選步驟並確認徽章解鎖；重新整理後確認暫存仍在。
5. 在任一 Day 頁開啟「上電前檢核」與「下課回饋」，確認回饋內容重新整理後仍在。
6. 在 Day 3 開啟浮動式專題設計單，輸入內容、關閉後再開啟，確認內容仍在；確認三句式發表卡可直接填空練習。
7. 啟動 Colab，開啟 `/api/health`。
8. 用 `example.7z` 解壓出的 XML 完成一次 `student.html` 試評。
9. 確認學生頁只看得到 `is_open: True` 的作業。

### 常見問題

| 現象 | 可能原因 | 處理方式 |
| --- | --- | --- |
| 學生頁顯示無法連線 | Colab 已停止、ngrok 網址錯誤或 `SERVER_URL` 未更新 | 重啟 Notebook，先測 `/api/health`，再更新學生頁網址 |
| `ERR_NGROK_334` | 同一固定網域被舊 ngrok agent 占用 | 在 ngrok Dashboard 停止舊 agent，或中斷舊 Colab runtime |
| 顯示老師尚未設定 API Key | `grader_config` 沒有 `api_key_1`／`api_key_2` | 執行 README 的設定儲存格後重啟服務 |
| 評測標準沒有出現 | 所有 rubric 都是 `is_open: False` 或 `rubrics_json` 格式錯誤 | 檢查 JSON，至少開放一份 rubric |
| Firestore 讀寫失敗 | Firebase 設定、API key、資料庫或 Security Rules 不正確 | 暫時設 `FIREBASE["enabled"] = False` 確認評測本身可運作，再檢查 Firebase |
| AI 顯示 429／503 | API 額度不足或服務忙碌 | 等待後重試；可設定第二把 API Key，並檢查帳戶額度／預算 |

## 安全注意事項

1. **立即撤銷來源 Notebook 中已明碼出現的 ngrok token，並產生新 token。** 不要沿用、不要複製到新 repository。
2. Gemini API Key 只能留在 Colab／受保護後端，絕不可寫進 `student.html`、GitHub Pages 或公開 Git repository。
3. Firebase Web API key 不是用來保護資料的登入憑證；真正的資料保護取決於 Firestore Security Rules 與身分驗證。
4. 學生學號與評測紀錄屬於教育資料。正式使用前應確認校內資料保護規範，並限制可查看成績的教師帳號。
5. `CORS origins: "*"` 與未保護的教師端 API 只適合短期測試；公開授課前應完成存取控制。

## 維護建議

- 若新增課程頁，複製既有 Day 頁的導覽列、Hero 和頁尾，再更新目前頁面的高亮樣式。
- 若新增積木類型，補到 Notebook 的 `BLOCK_DICT` 與 `FIELD_DICT`，讓 XML 轉譯與 AI 評分更準確。
- 若後端路由或回傳格式有改動，調高 `SERVER_VERSION`，重新執行 Colab，並在學生頁試評。
- 課後可從 Firestore 的 `xmlgrader_submissions` 彙整常見錯誤，回頭優化接線題、除錯護照與下一次的任務卡。
