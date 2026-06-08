from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship

from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    uid = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())


class Seat(Base):
    __tablename__ = "seats"

    seat_id = Column(String(10), primary_key=True, index=True)
    status = Column(String(20), default="empty", nullable=False)
    student_id = Column(String(20), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class NoiseLog(Base):
    __tablename__ = "noise_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    seat_id = Column(String(10), nullable=True)
    noise_value = Column(Integer, nullable=False)
    is_warning = Column(Boolean, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class LeaveLog(Base):
    __tablename__ = "leave_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    seat_id = Column(String(10), nullable=True)
    student_id = Column(String(20), nullable=True)
    action = Column(String(20), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(20), nullable=False)
    seat_id = Column(String(10), nullable=False)
    reserved_time = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="reserved")
