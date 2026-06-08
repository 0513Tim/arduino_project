from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    student_id: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    student: Optional[dict] = None


class CheckinRequest(BaseModel):
    uid: str
    seat_id: str


class CheckinResponse(BaseModel):
    success: bool
    message: str


class LeaveRequest(BaseModel):
    seat_id: str


class BasicResponse(BaseModel):
    success: bool
    message: str


class NoiseRequest(BaseModel):
    seat_id: str
    noise_value: int


class NoiseResponse(BaseModel):
    success: bool
    warning: bool
    message: str


class SeatResponse(BaseModel):
    seat_id: str
    status: str
    student_id: Optional[str] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class LatestNoiseResponse(BaseModel):
    id: int
    seat_id: Optional[str]
    noise_value: int
    is_warning: bool
    created_at: datetime

    class Config:
        from_attributes = True
