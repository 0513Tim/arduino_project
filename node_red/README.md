# Node-RED Dashboard 建置說明

目前 `node_red/` 已經補了一份可直接匯入的 [flow.json](/Users/tim/Documents/Codex/arduino_project/node_red/flow.json:1)。

## 1. 安裝與啟動

1. 安裝 Node-RED
2. 安裝 Dashboard 套件
```bash
cd ~/.node-red
npm install node-red-dashboard
```
3. 啟動 Node-RED
```bash
node-red
```
4. 開啟瀏覽器
```text
http://127.0.0.1:1880
```

## 2. 匯入 flow

1. 右上角選單 `Import`
2. 選擇 [node_red/flow.json](/Users/tim/Documents/Codex/arduino_project/node_red/flow.json:1)
3. 按 `Import`
4. 按右上角 `Deploy`

## 3. 這份 flow 會做什麼

- 每 5 秒呼叫 `GET /seats`
- 每 3 秒呼叫 `GET /latest_noise`
- 顯示目前 4 個座位狀態
- 顯示最新噪音值
- 顯示目前是否 warning

## 4. 目前對應的後端 API

這次已經改成跟目前 FastAPI 一致的欄位：

- `GET http://127.0.0.1:8000/seats`
- `GET http://127.0.0.1:8000/latest_noise`

回傳欄位使用：

- `seat_id`
- `status`
- `student_id`
- `noise_value`
- `is_warning`

## 5. Dashboard 畫面區塊

- `座位狀態`
  顯示像 `座位 01: using / A001`
- `噪音資訊`
  顯示像 `座位 01 / 數值 119 / normal`
- `警告資訊`
  顯示 `warning` 或 `normal`

## 6. 如果畫面沒資料

先確認：

1. FastAPI 有啟動
2. `http://127.0.0.1:8000/seats` 打得開
3. `http://127.0.0.1:8000/latest_noise` 打得開
4. 至少有一筆噪音資料

如果 `/latest_noise` 回 404，代表目前還沒有任何 ESP32 上傳過噪音值。

## 7. 現在的實際後端資料格式

目前我本地看到的 API 格式是：

### `/seats`

```json
[
  {
    "seat_id": "01",
    "status": "using",
    "student_id": "A001"
  }
]
```

### `/latest_noise`

```json
{
  "seat_id": "01",
  "noise_value": 119,
  "is_warning": false
}
```

## 8. 選做

如果你之後想再擴充，可以加：

- `ui_led` 顯示 warning
- `chart` 顯示噪音歷史
- `GET /warnings/today` 顯示今日警告次數
