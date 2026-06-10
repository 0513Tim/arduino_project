# 智慧自習室專案操作手冊

這份文件是給專題操作用的 HackMD 版本，目標是讓我們可以一步一步完成：

1. 建立資料庫
2. 啟動 FastAPI 後端
3. 啟動前端畫面
4. 設定 ESP32
5. 驗證 ESP32 是否成功送資料到系統

---

## 1. 專案用途

這個專案是在做一套「智慧自習室系統」。

功能包含：

- 學生登入
- 顯示座位狀態
- ESP32 讀取 NFC 卡片 UID
- ESP32 讀取聲音感測器數值
- ESP32 將資料送到 FastAPI
- MySQL 儲存座位、學生、噪音、離席資料
- GUI 或網頁顯示目前狀態

---

## 2. 專案資料夾說明

```text
arduino_project/
├── backend/        FastAPI 後端
├── database/       MySQL schema
├── gui/            前端畫面
├── esp32/          ESP32 程式
├── node_red/       Node-RED 說明
└── HACKMD_ESP32_SETUP.md
```

各資料夾用途：

- `backend/`：API 伺服器
- `database/`：建立 MySQL 資料表
- `gui/`：查看座位與噪音畫面
- `esp32/`：燒錄到 ESP32 的 Arduino 程式

---

## 3. 先備條件

開始前請先確認電腦有：

- Python 3
- MySQL
- Arduino IDE
- ESP32 開發板套件
- RC522 函式庫

如果只是想先測後端，不一定要先接好 RC522。

---

## 4. 建立資料庫

### Step 1：啟動 MySQL

如果是用 Homebrew 安裝：

```bash
brew services start mysql
```

確認 MySQL 是否有成功啟動：

```bash
brew services list | rg mysql
```

---

### Step 2：匯入資料庫 schema

在專案根目錄執行：

```bash
mysql -u root -p < /Users/tim/Documents/Codex/arduino_project/database/schema.sql
```

如果成功，資料庫會建立：

- 資料庫名稱：`smart_study_room`
- 資料表：
  - `students`
  - `seats`
  - `noise_logs`
  - `leave_logs`
  - `reservations`

---

### Step 3：進 MySQL 檢查資料

```bash
mysql -u root -p
```

進去後輸入：

```sql
USE smart_study_room;
SHOW TABLES;
SELECT * FROM students;
SELECT * FROM seats;
```

預期會看到：

- 3 筆學生資料
- 4 個座位 `01`、`02`、`03`、`04`

---

## 5. 啟動 FastAPI 後端

### Step 1：進入 backend

```bash
cd /Users/tim/Documents/Codex/arduino_project/backend
```

---

### Step 2：建立虛擬環境

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

### Step 3：安裝套件

```bash
pip install -r requirements.txt
```

---

### Step 4：建立 `.env`

如果還沒有 `.env`：

```bash
cp .env.example .env
```

打開 `.env`，確認內容正確，例如：

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=你的MySQL密碼
DB_NAME=smart_study_room
```

---

### Step 5：啟動 FastAPI

```bash
uvicorn main:app --reload
```

如果成功，終端機會看到類似：

```text
Uvicorn running on http://127.0.0.1:8000
```

---

### Step 6：打開 API 文件

在瀏覽器開啟：

```text
http://127.0.0.1:8000/docs
```

可以看到 API 文件頁面，代表後端成功啟動。

---

## 6. 測試後端 API

目前後端提供：

- `POST /login`
- `GET /seats`
- `POST /checkin`
- `POST /noise`
- `POST /leave`
- `GET /latest_noise`
- `GET /noise/latest`

---

### Step 1：測試登入

在 `/docs` 裡測試 `POST /login`

範例：

```json
{
  "student_id": "A001",
  "password": "1234"
}
```

如果成功，會回傳登入成功訊息。

---

### Step 2：測試查座位

測試 `GET /seats`

應該會看到四個座位，狀態一開始是：

- `empty`

---

## 7. 啟動前端畫面

這個專案目前有兩種 GUI：

1. 網頁版
2. Tkinter 桌面版

建議先用網頁版，比較簡單。

---

### 方法 A：網頁版 GUI

進入 `gui/`：

```bash
cd /Users/tim/Documents/Codex/arduino_project/gui
python3 -m http.server 8001
```

打開瀏覽器：

```text
http://127.0.0.1:8001
```

可以登入並查看座位、噪音資訊。

測試帳號：

- `A001 / 1234`
- `A002 / 1234`
- `A003 / 1234`

---

### 方法 B：Tkinter GUI

```bash
cd /Users/tim/Documents/Codex/arduino_project/gui
python3 app.py
```

如果電腦有安裝 Tkinter，就會開啟桌面視窗。

---

## 8. 設定 ESP32

要修改的檔案：

- `esp32/esp32_1_nfc_noise/esp32_1_nfc_noise.ino`
- `esp32/esp32_2_nfc_noise/esp32_2_nfc_noise.ino`

---

### Step 1：修改 Wi-Fi 資訊

打開 `.ino` 檔，把這三個值改掉：

```cpp
const char* WIFI_SSID = "你的WiFi名稱";
const char* WIFI_PASSWORD = "你的WiFi密碼";
const char* API_BASE_URL = "http://你的電腦IP:8000";
```

---

### Step 2：查電腦 IP

在 Mac 終端機輸入：

```bash
ipconfig getifaddr en0
```

如果沒有值，可以試：

```bash
ipconfig getifaddr en1
```

假設查到：

```text
192.168.1.100
```

那麼 `.ino` 裡要寫成：

```cpp
const char* API_BASE_URL = "http://192.168.1.100:8000";
```

注意：ESP32 和電腦一定要在同一個 Wi-Fi。

---

### Step 3：Arduino IDE 設定

在 Arduino IDE 中：

1. 選擇正確的 ESP32 板子
2. 選擇正確的 COM Port / Serial Port
3. 安裝需要的函式庫：
   - `MFRC522`
   - `WiFi`
   - `HTTPClient`
   - `SPI`

---

### Step 4：燒錄程式

先從 `esp32_1_nfc_noise.ino` 開始燒錄。

燒錄完成後，打開 `Serial Monitor`，波特率設成：

```text
115200
```

---

## 9. ESP32 成功的判斷方式

如果成功，序列埠會看到：

### Wi-Fi 成功

```text
Connecting to Wi-Fi...
Wi-Fi connected
192.168.x.x
```

### 聲音感測器有工作

```text
Noise value: 523
POST /noise => 200
```

### NFC 有讀到卡片

```text
NFC UID: XXXXXXXX
POST /checkin => 200
```

---

## 10. 實際測試流程

建議照下面順序測：

### 第 1 階段：只測後端

1. 啟動 MySQL
2. 匯入 `schema.sql`
3. 啟動 FastAPI
4. 在 `/docs` 測試 `login`、`seats`

---

### 第 2 階段：測前端

1. 開網頁版 GUI
2. 用 `A001 / 1234` 登入
3. 確認能看到座位狀態

---

### 第 3 階段：測 ESP32 網路

1. 修改 Wi-Fi 與 IP
2. 燒錄 ESP32
3. 看序列埠是否成功送出 `/noise`

---

### 第 4 階段：測 NFC

1. 刷卡
2. 看序列埠是否出現 UID
3. 看後端是否收到 `/checkin`
4. 看座位是否從 `empty` 變成 `using`

---

## 11. 常見問題

### 問題 1：MySQL 連不到

錯誤範例：

```text
Can't connect to local MySQL server through socket '/tmp/mysql.sock'
```

解法：

```bash
brew services start mysql
```

---

### 問題 2：ESP32 送不到 API

請確認：

1. `API_BASE_URL` 是否寫成電腦區網 IP
2. 電腦與 ESP32 是否同一個 Wi-Fi
3. FastAPI 是否真的在 `8000` port 執行
4. macOS 防火牆是否阻擋 Python

---

### 問題 3：刷卡沒反應

請確認：

1. RC522 接線是否正確
2. 板子供電是否正常
3. Arduino IDE 是否有安裝 `MFRC522`
4. `Serial Monitor` 是否設成 `115200`

---

### 問題 4：前端打不通 API

請確認後端有啟動：

```text
http://127.0.0.1:8000
```

並確認瀏覽器可開啟：

```text
http://127.0.0.1:8000/docs
```

---

## 12. 展示時建議流程

1. 啟動 MySQL
2. 啟動 FastAPI
3. 開網頁 GUI
4. 登入測試帳號
5. 顯示座位狀態
6. 啟動 ESP32
7. 顯示噪音數值
8. 刷 NFC 卡
9. 座位狀態變成 `using`
10. 噪音高於門檻時顯示 warning
11. 按下離席
12. 座位恢復 `empty`

---

## 13. 本專案目前最重要的檔案

- 後端入口：[backend/main.py](backend/main.py)
- 資料庫設定：[backend/database.py](backend/database.py)
- 後端邏輯：[backend/crud.py](backend/crud.py)
- 資料庫 schema：[database/schema.sql](database/schema.sql)
- 網頁前端：[gui/index.html](gui/index.html)
- 前端邏輯：[gui/app.js](gui/app.js)
- ESP32 程式：[esp32/esp32_1_nfc_noise/esp32_1_nfc_noise.ino](esp32/esp32_1_nfc_noise/esp32_1_nfc_noise.ino)

---

## 14. 結論

建議實作順序：

1. 先讓 MySQL 和 FastAPI 跑起來
2. 再確認 GUI 可以看到座位
3. 再接 ESP32 的 Wi-Fi 與 API
4. 最後才測 NFC 與聲音感測器

這樣最不容易卡住，也最容易一步一步除錯。
