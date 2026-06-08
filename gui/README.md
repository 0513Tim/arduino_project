# GUI 前端

這個 `gui` 資料夾包含一個純前端靜態網頁，用於連接後端 FastAPI API。

## 啟動後端

請先啟動 backend：

```bash
cd backend
uvicorn main:app --reload
```

後端啟動後，API base URL 為：

```
http://127.0.0.1:8000
```

## 開啟網頁

打開 `gui/index.html`：

1. 直接在瀏覽器中開啟 `index.html`。
2. 或使用簡單的本地靜態伺服器（例如 Python）：

```bash
cd gui
python -m http.server 8001
```

然後在瀏覽器開啟：

```
http://127.0.0.1:8001
```

## 使用的 API

- `POST http://127.0.0.1:8000/login`
- `GET http://127.0.0.1:8000/seats`
- `POST http://127.0.0.1:8000/leave`
- `GET http://127.0.0.1:8000/latest_noise`

## 測試流程

1. 開啟後端 API。
2. 在網頁輸入測試帳號：
   - `A001` / `1234`
   - `A002` / `1234`
   - `A003` / `1234`
3. 點擊登入。
4. 觀察座位卡片顏色與狀態。
5. 點擊任一座位卡片，選擇座位。
6. 點擊「直接離席」按鈕，測試離席功能。
7. 點擊「更新噪音」或等待自動更新，確認噪音狀態。

## 注意事項

- 本頁面使用純前端 HTML/CSS/JS，不依賴外部 CDN。
- 為了跨域存取 API，請確認後端已啟用 CORS。
