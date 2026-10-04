// 🔴 網站連線設定唯一入口（對應 README「15 分鐘設定檢查表」）。
// 貼上 Colab 顯示的 ngrok 根網址，或 Cloud Run 的 Service URL；不要加 /api/...。
// 只放公開網址，Gemini 金鑰與教師密碼請留在後端 Secrets。
window.XMLGRADER_SETTINGS = Object.freeze({
  serverUrl: '',
  expectedVersion: '2026-10-04-unified'
});
