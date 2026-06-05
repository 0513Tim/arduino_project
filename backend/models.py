from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from database import Base


seat_status_enum = ("available", "using", "away", "warning", "reserved")
reservation_status_enum = ("reserved", "checked_in", "cancelled", "finished")
noise_level_enum = ("quiet", "normal", "loud")
leave_type_enum = ("temporary", "final")
leave_status_enum = ("away", "returned", "finished", "timeout")


class Student(Base):
    __tablename__ = "students"

    student_id = Column(String(20), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    password = Column(String(100), nullable=False)
    nfc_uid = Column(String(50), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())

    seats = relationship("Seat", back_populates="student")


class Seat(Base):
    __tablename__ = "seats"

    seat_no = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(*seat_status_enum, name="seat_status"), default="available", nullable=False)
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    student = relationship("Student", back_populates="seats")


class Reservation(Base):
    __tablename__ = "reservations"

    reservation_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=False)
    seat_no = Column(Integer, ForeignKey("seats.seat_no"), nullable=False)
    status = Column(
        Enum(*reservation_status_enum, name="reservation_status"),
        default="reserved",
        nullable=False,
    )
    reserve_time = Column(DateTime, server_default=func.now())
    checkin_time = Column(DateTime, nullable=True)
    finish_time = Column(DateTime, nullable=True)


class NoiseLog(Base):
    __tablename__ = "noise_logs"

    noise_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    seat_no = Column(Integer, ForeignKey("seats.seat_no"), nullable=True)
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=True)
    noise_value = Column(Integer, nullable=False)
    level = Column(Enum(*noise_level_enum, name="noise_level"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class LeaveLog(Base):
    __tablename__ = "leave_logs"

    leave_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(String(20), ForeignKey("students.student_id"), nullable=False)
    seat_no = Column(Integer, ForeignKey("seats.seat_no"), nullable=False)
    leave_type = Column(Enum(*leave_type_enum, name="leave_type"), nullable=False)
    leave_time = Column(DateTime, server_default=func.now())
    return_time = Column(DateTime, nullable=True)
    status = Column(Enum(*leave_status_enum, name="leave_status"), default="away", nullable=False)
