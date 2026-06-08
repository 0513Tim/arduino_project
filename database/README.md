# database

此資料夾存放與 MySQL 資料庫初始化有關的檔案。

## 檔案用途
- `schema.sql`: 用於建立 `smart_study_room` 資料庫及必要的資料表，並匯入測試資料。

## 資料庫名稱
`smart_study_room`

## 各資料表用途
- `students`: 儲存學生帳號資訊（學號、姓名、密碼、NFC/UID 等）。
- `seats`: 座位狀態管理（座位編號、佔用狀態、對應學生）。
- `noise_logs`: 噪音數值紀錄（座位、噪音值、是否警示、時間）。
- `leave_logs`: 離開/返回紀錄（座位、學生、動作、時間）。
- `reservations`: 預約紀錄（學生、座位、預約時間、狀態）。

## 如何匯入 MySQL
使用下列命令（會要求輸入 MySQL root 密碼）：

```bash
mysql -u root -p < database/schema.sql
```

匯入後可以進行以下測試指令：

```sql
USE smart_study_room;
SHOW TABLES;
SELECT * FROM students;
SELECT * FROM seats;
```

## 測試用 SQL 指令（範例）
- 顯示所有學生：
  `SELECT * FROM students;`
- 顯示所有座位：
  `SELECT * FROM seats;`
- 查詢某學生預約：
  `SELECT * FROM reservations WHERE student_id = 'A001';`

---

如需修改 schema 或新增測試資料，請編輯 `schema.sql`，再重新匯入。
