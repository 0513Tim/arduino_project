from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator


class LoginRequest(BaseModel):
    student_id: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str
    student: Optional[dict] = None


class RegisterRequest(BaseModel):
    student_id: str
    name: str
    password: str
    uid: str


class RegisterResponse(BaseModel):
    success: bool
    message: str
    student: Optional[dict] = None


class CheckinRequest(BaseModel):
    uid: Optional[str] = None
    nfc_uid: Optional[str] = None
    seat_id: Optional[str] = None
    seat_no: Optional[int] = None

    @model_validator(mode="after")
    def normalize_fields(self):
        if not self.uid and self.nfc_uid:
            self.uid = self.nfc_uid
        if not self.seat_id and self.seat_no is not None:
            self.seat_id = f"{int(self.seat_no):02d}"
        return self


class CheckinResponse(BaseModel):
    success: bool
    message: str


class LeaveRequest(BaseModel):
    seat_id: Optional[str] = None
    seat_no: Optional[int] = None

    @model_validator(mode="after")
    def normalize_fields(self):
        if not self.seat_id and self.seat_no is not None:
            self.seat_id = f"{int(self.seat_no):02d}"
        return self


class BasicResponse(BaseModel):
    success: bool
    message: str


class NoiseRequest(BaseModel):
    seat_id: Optional[str] = None
    seat_no: Optional[int] = None
    noise_value: int

    @model_validator(mode="after")
    def normalize_fields(self):
        if not self.seat_id and self.seat_no is not None:
            self.seat_id = f"{int(self.seat_no):02d}"
        return self


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


class ScanUidRequest(BaseModel):
    uid: Optional[str] = None
    nfc_uid: Optional[str] = None
    source: Optional[str] = None
    seat_id: Optional[str] = None
    seat_no: Optional[int] = None

    @model_validator(mode="after")
    def normalize_fields(self):
        if not self.uid and self.nfc_uid:
            self.uid = self.nfc_uid
        if not self.seat_id and self.seat_no is not None:
            self.seat_id = f"{int(self.seat_no):02d}"
        return self


class LatestUidResponse(BaseModel):
    uid: str
    registered: bool
    student_id: Optional[str] = None
    name: Optional[str] = None
    source: Optional[str] = None
    seat_id: Optional[str] = None
    scanned_at: datetime
