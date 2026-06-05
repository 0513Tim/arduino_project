# Node-RED Dashboard 建置說明

## 1. 安裝與啟動

1. 安裝 Node-RED。
2. 安裝 Dashboard 套件：
   `npm install node-red-dashboard`
3. 啟動 Node-RED：
   `node-red`
4. 在瀏覽器開啟 `http://127.0.0.1:1880`

## 2. 建立 Dashboard 分頁

建立一個 `智慧自習室` tab，底下可放三個 group：

- `座位狀態`
- `噪音資訊`
- `警告資訊`

## 3. Flow 需求

### 座位狀態

1. 放一個 `inject` 節點，每 5 秒觸發一次。
2. 接到 `http request` 節點，Method 選 `GET`。
3. URL 設成 `http://127.0.0.1:8000/seats`
4. 接一個 `function` 節點，把回傳 JSON 整理成文字：

```javascript
let lines = msg.payload.map(
  seat => `座位 ${String(seat.seat_no).padStart(2, "0")}: ${seat.status} / ${seat.student_id || "-"}`
);
msg.payload = lines.join("\n");
return msg;
```

5. 接到 `ui_text` 或 `ui_template` 顯示座位狀態。

### 噪音資訊

1. 再放一組 `inject` 節點，每 3 秒觸發一次。
2. 接到 `http request` 節點，URL 設成 `http://127.0.0.1:8000/noise/latest`
3. 接 `function` 節點：

```javascript
msg.payload = `座位 ${msg.payload.seat_no} / 數值 ${msg.payload.noise_value} / 狀態 ${msg.payload.level}`;
return msg;
```

4. 接 `ui_text` 顯示最新噪音。

### warning 狀態

可直接沿用 `/noise/latest` 的結果，在 `function` 節點加入判斷：

```javascript
msg.payload = msg.payload.level === "loud" ? "warning" : "normal";
return msg;
```

再接一個 `ui_text` 或 `ui_led` 顯示警告狀態。

## 4. 建議畫面

- 第一區塊顯示 4 個座位的目前狀態
- 第二區塊顯示最新噪音值
- 第三區塊顯示是否進入 warning

## 5. 選做

如果後端之後補上 `GET /warnings/today`，可再增加一個 `http request` 與 `ui_text` 顯示今日警告次數。
