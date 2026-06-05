from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

import crud
from database import Base, engine, get_db
from models import Student
from schemas import (
    BasicResponse,
    CheckinRequest,
    CheckinResponse,
    LatestNoiseResponse,
    LeaveRequest,
    LoginRequest,
    LoginResponse,
    NoiseRequest,
    NoiseResponse,
    SeatResponse,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    with next(get_db()) as db:
        crud.seed_data(db)
    yield


app = FastAPI(
    title="Smart Study Room System",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
def root():
    return {"message": "Smart Study Room System API"}


@app.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    student = crud.login_student(db, payload.student_id, payload.password)
    if student is None:
        raise HTTPException(status_code=401, detail="invalid student_id or password")
    return LoginResponse(success=True, student_id=student.student_id, name=student.name)


@app.post("/checkin", response_model=CheckinResponse)
def checkin(payload: CheckinRequest, db: Session = Depends(get_db)):
    result, error = crud.checkin_student(db, payload.nfc_uid, payload.seat_no)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return CheckinResponse(success=True, message="checkin success", **result)


@app.post("/leave", response_model=BasicResponse)
def leave(payload: LeaveRequest, db: Session = Depends(get_db)):
    success = crud.leave_student(db, payload.student_id)
    if not success:
        raise HTTPException(status_code=404, detail="student is not using any seat")
    return BasicResponse(success=True, message="seat released")


@app.post("/noise", response_model=NoiseResponse)
def upload_noise(payload: NoiseRequest, db: Session = Depends(get_db)):
    noise_log = crud.create_noise_log(db, payload.seat_no, payload.noise_value)
    if noise_log is None:
        raise HTTPException(status_code=404, detail="seat not found")
    return NoiseResponse(
        success=True,
        level=noise_log.level,
        warning=noise_log.level == "loud",
    )


@app.get("/seats", response_model=list[SeatResponse])
def get_seats(db: Session = Depends(get_db)):
    return crud.list_seats(db)


@app.get("/noise/latest", response_model=LatestNoiseResponse)
def get_latest_noise(db: Session = Depends(get_db)):
    noise_log = crud.get_latest_noise(db)
    if noise_log is None:
        raise HTTPException(status_code=404, detail="no noise data yet")
    return noise_log
