from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    student_id: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    student_id: str
    name: str


class CheckinRequest(BaseModel):
    nfc_uid: str
    seat_no: int


class CheckinResponse(BaseModel):
    success: bool
    message: str
    student_id: str
    seat_no: int


class LeaveRequest(BaseModel):
    student_id: str


class BasicResponse(BaseModel):
    success: bool
    message: str


class NoiseRequest(BaseModel):
    seat_no: int
    noise_value: int


class NoiseResponse(BaseModel):
    success: bool
    level: str
    warning: bool


class SeatResponse(BaseModel):
    seat_no: int
    status: str
    student_id: Optional[str]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LatestNoiseResponse(BaseModel):
    seat_no: Optional[int]
    noise_value: int
    level: str
    created_at: datetime

    class Config:
        from_attributes = True
