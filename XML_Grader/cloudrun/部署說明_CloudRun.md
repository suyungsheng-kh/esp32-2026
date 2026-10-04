# XMLGrader 整合版：Cloud Run 部署

版本：`2026-10-04-unified`。與 Colab 共用 `XML_Grader/api_server.py` 和 `xml_grader_core.py`，學生與教師頁面使用同一個服務網址。

## 1. 準備自己的專案

1. 到 [Google Cloud Console](https://console.cloud.google.com/) 建立或選擇自己的專案，記下 PROJECT_ID。
2. 依 Console 要求設定帳單與啟用 Cloud Run、Cloud Build、Artifact Registry、Secret Manager API。
3. 如果要跨次保存作業規則與成績，在同一專案建立 Cloud Firestore `(default)` 資料庫。
4. 費用依部署、使用量與帳戶方案而定，請自行設定預算；這份文件不保證免費。

## 2. 服務帳戶與 Secret

在 IAM → Service Accounts 建立 `xmlgrader-runtime`：

- 使用 Firestore 時，授予 **Cloud Datastore User**（`roles/datastore.user`）。
- 在 Secret Manager 建立以下秘密，再逐項授予此服務帳戶 **Secret Manager Secret Accessor**（`roles/secretmanager.secretAccessor`）。

| Secret 名稱（範例） | 內容 |
| --- | --- |
| `xmlgrader-gemini` | 自己的 Gemini API Key |
| `xmlgrader-admin` | 自己設定的教師管理密碼 |
| `xmlgrader-gemini-backup` | 備援 Gemini API Key（可選） |

秘密內容透過 Console 填寫，不放進 Dockerfile、HTML 或 repository。Cloud Run 的服務帳戶會自動取得 Firestore 授權，不需下載服務帳戶 JSON。設定方式參考 [Cloud Run Secrets 文件](https://docs.cloud.google.com/run/docs/configuring/services/secrets)，Firestore 授權參考 [Firestore REST 文件](https://firebase.google.com/docs/firestore/use-rest-api)。

## 3. 上傳共用後端

使用 Cloud Shell，上傳 `XML_Grader` 資料夾中的：

```text
XML_Grader/
  Dockerfile
  .gcloudignore
  .dockerignore
  api_server.py
  xml_grader_core.py
  cloudrun/
    requirements.txt
```

進入 `XML_Grader` 目錄。🔴 必須從這個目錄部署，不能只上傳原來的 `cloudrun/` 資料夾，否則缺少共用 API。

## 4. 部署服務

🔴 先把下列 `YOUR_PROJECT_ID`、網站來源與 Secret 名稱改成自己的值。網站來源只填 origin，不加 repository 路徑。

```bash
gcloud run deploy xmlgrader \
  --source . \
  --project YOUR_PROJECT_ID \
  --region asia-east1 \
  --allow-unauthenticated \
  --service-account xmlgrader-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com \
  --memory 512Mi \
  --timeout 180 \
  --concurrency 8 \
  --max-instances 2 \
  --set-env-vars "XMLGRADER_FIREBASE_ENABLED=true,XMLGRADER_FIREBASE_PROJECT_ID=YOUR_PROJECT_ID,XMLGRADER_CORS_ORIGINS=https://YOUR_NAME.github.io" \
  --set-secrets "XMLGRADER_GEMINI_API_KEY_1=xmlgrader-gemini:latest,XMLGRADER_ADMIN_TOKEN=xmlgrader-admin:latest"
```

- 如有備援金鑰，在 `--set-secrets` 加入 `XMLGRADER_GEMINI_API_KEY_2=xmlgrader-gemini-backup:latest`。
- 如果暫時不用 Firestore，改為 `XMLGRADER_FIREBASE_ENABLED=false`；資料只保存在目前執行個體，不能長期保存或跨個體共用。
- `--allow-unauthenticated` 讓學生免 Google 登入；教師管理 API 仍會驗證教師密碼。
- 依 Console／Cloud Shell 提示完成建置權限，等待部署完成。不要把 Gemini Key 直接寫進此指令。

Docker 使用單一共用核心；未再以 HF／Colab 的副本部署。

## 5. 連接網站

1. 複製部署輸出的 Service URL，例如 `https://xmlgrader-...run.app`。
2. 在瀏覽器開啟 `<Service URL>/api/health`，確認版本是 `2026-10-04-unified`。
3. 🔴 在網站根目錄 `grader-settings.js` 的 `serverUrl` 填入 Service URL，重新發布網站。
4. 開啟 `teacher.html`，用 `xmlgrader-admin` 的內容登入。
5. 首次 Cloud Run 沒有範例規則：新增一份作業、填主題與配分、勾選開放並儲存。
6. 教師試評 XML，學生自評一次，再讀取成績確認儲存。

教師管理密碼與 Gemini Key 都不會出現在前端設定或作業資料庫。

## 6. 更新與故障排除

改動共用後端後，重新執行同一部署指令；服務網址一般可沿用。變更 Secret 後請讓新修訂版本使用更新的值。

| 現象 | 檢查 |
| --- | --- |
| 建置找不到檔案 | 是否從 `XML_Grader` 根目錄部署、檔案與 `cloudrun/requirements.txt` 是否齊全 |
| Secret 存取遭拒 | 執行服務帳戶是否具有該 Secret 的 Accessor 權限 |
| Firestore 無法保存 | 專案 ID、`(default)` 資料庫、Cloud Datastore User 權限 |
| 只能看到本機成績 | Firestore 連線失敗或未啟用；Cloud Run 本機資料不會跨個體保留 |
| 教師登入失敗 | 核對 `XMLGRADER_ADMIN_TOKEN` 對應的 Secret 值 |
| 瀏覽器無法連線 | Service URL、CORS origin、健康檢查與部署日誌 |

只有 `XML_Grader/Dockerfile` 一份容器設定，直接啟動同目錄的 `api_server:app`；不要使用舊版 `cloudrun/app.py`、核心副本或 Dockerfile。
