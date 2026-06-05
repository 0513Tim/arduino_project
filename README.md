# Smart Study Room System

依照任務文件建立的智慧自習室專案，包含：

- `database/` MySQL schema 與初始資料
- `backend/` FastAPI 後端
- `gui/` Tkinter GUI
- `esp32/` 兩台 ESP32 的 Arduino 程式
- `node_red/` Node-RED Dashboard 建置說明

## 專案結構

```text
study-room-system/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── requirements.txt
│   └── .env.example
├── database/
│   └── schema.sql
├── gui/
│   ├── app.py
│   └── requirements.txt
├── esp32/
│   ├── esp32_1_nfc_noise/
│   │   └── esp32_1_nfc_noise.ino
│   └── esp32_2_nfc_noise/
│       └── esp32_2_nfc_noise.ino
├── node_red/
│   └── README.md
└── README.md
```

## 1. 建立資料庫

```bash
mysql -u root -p < database/schema.sql
```

## 2. 啟動 FastAPI

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload
```

預設 `.env.example` 是 MySQL 連線字串。
如果只是想先快速 demo，也可以把 `DATABASE_URL` 改成 `sqlite:///./study_room_system.db`。

啟動後可開啟：

- `http://127.0.0.1:8000/docs`

## 3. 啟動 GUI

```bash
cd gui
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 4. Arduino / ESP32

請先在 `.ino` 檔內修改：

- `WIFI_SSID`
- `WIFI_PASSWORD`
- `API_BASE_URL`

其中 `API_BASE_URL` 要改成電腦在區網內的 IP，例如 `http://192.168.1.100:8000`

## 5. API 對應

- `POST /login`
- `POST /checkin`
- `POST /leave`
- `POST /noise`
- `GET /seats`
- `GET /noise/latest`

## 6. 測試帳號

- `111410001 / 1234 / A35F2911`
- `111410002 / 1234 / B24C8832`
- `111410003 / 1234 / C91D782A`
