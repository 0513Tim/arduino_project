from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

import crud
from database import get_db
from schemas import (
    BasicResponse,
    CheckinRequest,
    CheckinResponse,
    LatestNoiseResponse,
    LatestUidResponse,
    LeaveRequest,
    LoginRequest,
    LoginResponse,
    NoiseRequest,
    NoiseResponse,
    RegisterRequest,
    RegisterResponse,
    ScanUidRequest,
    SeatResponse,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 應用啟動時不需要建立表（資料庫已存在），只需驗證連接
    try:
        with next(get_db()) as db:
            db.execute(text("SELECT 1"))
    except Exception as e:
        print(f"Database connection error: {e}")
    yield


app = FastAPI(
    title="Smart Study Room System",
    version="1.0.0",
    description="智慧自習室系統 API",
    lifespan=lifespan,
)

# 允許 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Smart Study Room System API"}


@app.post(
    "/login",
    response_model=LoginResponse,
    response_model_exclude_none=True,
)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    GUI 登入
    """
    student = crud.login_student(db, payload.student_id, payload.password)
    if not student:
        return {
            "success": False,
            "message": "帳號或密碼錯誤",
        }

    return {
        "success": True,
        "message": "登入成功",
        "student": {
            "student_id": student.student_id,
            "name": student.name,
        },
    }


@app.post(
    "/register",
    response_model=RegisterResponse,
    response_model_exclude_none=True,
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    student, error = crud.register_student(
        db,
        student_id=payload.student_id,
        name=payload.name,
        password=payload.password,
        uid=payload.uid,
    )
    if error:
        raise HTTPException(status_code=400, detail=error)

    latest = crud.get_latest_uid()
    if latest and latest["uid"] == student.uid:
        crud.clear_latest_uid()

    return {
        "success": True,
        "message": "註冊成功",
        "student": {
            "student_id": student.student_id,
            "name": student.name,
            "uid": student.uid,
        },
    }


@app.get("/seats", response_model=list[SeatResponse])
def get_seats(db: Session = Depends(get_db)):
    """
    查詢所有座位狀態，依 seat_id 排序
    """
    seats = crud.list_all_seats(db)
    return seats


@app.post("/checkin", response_model=CheckinResponse)
def checkin(payload: CheckinRequest, db: Session = Depends(get_db)):
    """
    ESP32 NFC 刷卡報到
    """
    if not payload.uid or not payload.seat_id:
        raise HTTPException(status_code=422, detail="uid/nfc_uid and seat_id/seat_no are required")

    result, error = crud.checkin_student(db, payload.uid, payload.seat_id)
    if error:
        raise HTTPException(status_code=400, detail=error)

    return CheckinResponse(
        success=True,
        message="報到成功"
    )


@app.post("/noise", response_model=NoiseResponse)
def upload_noise(payload: NoiseRequest, db: Session = Depends(get_db)):
    """
    ESP32 上傳噪音數值
    """
    if not payload.seat_id:
        raise HTTPException(status_code=422, detail="seat_id/seat_no is required")

    noise_log = crud.create_noise_log(db, payload.seat_id, payload.noise_value)
    if not noise_log:
        raise HTTPException(status_code=404, detail="座位不存在")

    return NoiseResponse(
        success=True,
        warning=noise_log.is_warning,
        message="警告" if noise_log.is_warning else "正常"
    )


@app.post("/leave", response_model=BasicResponse)
def leave(payload: LeaveRequest, db: Session = Depends(get_db)):
    """
    GUI 直接離席
    """
    if not payload.seat_id:
        raise HTTPException(status_code=422, detail="seat_id/seat_no is required")

    success, error = crud.leave_seat(db, payload.seat_id)
    if not success:
        raise HTTPException(status_code=400, detail=error)

    return BasicResponse(
        success=True,
        message="離席成功"
    )


@app.get("/latest_noise", response_model=LatestNoiseResponse)
def get_latest_noise(db: Session = Depends(get_db)):
    """
    取得最新噪音紀錄
    """
    noise_log = crud.get_latest_noise(db)
    if not noise_log:
        raise HTTPException(status_code=404, detail="無噪音資料")

    return noise_log


@app.post("/scan_uid", response_model=LatestUidResponse)
def scan_uid(payload: ScanUidRequest, db: Session = Depends(get_db)):
    if not payload.uid:
        raise HTTPException(status_code=422, detail="uid/nfc_uid is required")

    student = crud.get_student_by_uid(db, payload.uid)
    latest = crud.remember_latest_uid(
        uid=payload.uid,
        source=payload.source or "scanner",
        seat_id=payload.seat_id,
        registered=student is not None,
        student_id=student.student_id if student else None,
        name=student.name if student else None,
    )
    return latest


@app.get("/latest_uid", response_model=LatestUidResponse)
def get_latest_uid():
    latest = crud.get_latest_uid()
    if not latest:
        raise HTTPException(status_code=404, detail="尚無刷卡 UID")
    return latest


@app.get("/noise/latest", response_model=LatestNoiseResponse)
def get_latest_noise_legacy(db: Session = Depends(get_db)):
    """
    舊版相容端點，提供 Node-RED / 舊版 ESP32 說明使用
    """
    noise_log = crud.get_latest_noise(db)
    if not noise_log:
        raise HTTPException(status_code=404, detail="無噪音資料")

    return noise_log
