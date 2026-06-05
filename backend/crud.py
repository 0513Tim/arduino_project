from sqlalchemy import select
from sqlalchemy.orm import Session

from models import LeaveLog, NoiseLog, Seat, Student


def seed_data(db: Session) -> None:
    students = [
        Student(student_id="111410001", name="王小明", password="1234", nfc_uid="A35F2911"),
        Student(student_id="111410002", name="陳小華", password="1234", nfc_uid="B24C8832"),
        Student(student_id="111410003", name="林大安", password="1234", nfc_uid="C91D782A"),
    ]
    for student in students:
        if db.get(Student, student.student_id) is None:
            db.add(student)

    for seat_no in range(1, 5):
        if db.get(Seat, seat_no) is None:
            db.add(Seat(seat_no=seat_no, status="available"))

    db.commit()


def login_student(db: Session, student_id: str, password: str):
    stmt = select(Student).where(Student.student_id == student_id, Student.password == password)
    return db.execute(stmt).scalar_one_or_none()


def get_student_by_nfc(db: Session, nfc_uid: str):
    stmt = select(Student).where(Student.nfc_uid == nfc_uid)
    return db.execute(stmt).scalar_one_or_none()


def get_seat(db: Session, seat_no: int):
    return db.get(Seat, seat_no)


def get_student_active_seat(db: Session, student_id: str):
    stmt = select(Seat).where(Seat.student_id == student_id, Seat.status.in_(("using", "warning", "away")))
    return db.execute(stmt).scalar_one_or_none()


def checkin_student(db: Session, nfc_uid: str, seat_no: int):
    student = get_student_by_nfc(db, nfc_uid)
    if student is None:
        return None, "student not found"

    seat = get_seat(db, seat_no)
    if seat is None:
        return None, "seat not found"

    if seat.status != "available":
        return None, "seat is not available"

    current_seat = get_student_active_seat(db, student.student_id)
    if current_seat is not None:
        return None, "student already occupies a seat"

    seat.status = "using"
    seat.student_id = student.student_id
    db.commit()
    db.refresh(seat)
    return {"student_id": student.student_id, "seat_no": seat.seat_no}, None


def leave_student(db: Session, student_id: str):
    seat = get_student_active_seat(db, student_id)
    if seat is None:
        return False

    leave_log = LeaveLog(
        student_id=student_id,
        seat_no=seat.seat_no,
        leave_type="final",
        status="finished",
    )
    db.add(leave_log)
    seat.status = "available"
    seat.student_id = None
    db.commit()
    return True


def get_noise_level(noise_value: int) -> str:
    if noise_value < 400:
        return "quiet"
    if noise_value < 700:
        return "normal"
    return "loud"


def create_noise_log(db: Session, seat_no: int, noise_value: int):
    seat = get_seat(db, seat_no)
    if seat is None:
        return None

    level = get_noise_level(noise_value)
    noise_log = NoiseLog(
        seat_no=seat_no,
        student_id=seat.student_id,
        noise_value=noise_value,
        level=level,
    )
    db.add(noise_log)

    if level == "loud":
        seat.status = "warning"
    elif seat.status == "warning" and seat.student_id:
        seat.status = "using"

    db.commit()
    db.refresh(noise_log)
    return noise_log


def list_seats(db: Session):
    stmt = select(Seat).order_by(Seat.seat_no)
    return list(db.execute(stmt).scalars().all())


def get_latest_noise(db: Session):
    stmt = select(NoiseLog).order_by(NoiseLog.created_at.desc(), NoiseLog.noise_id.desc())
    return db.execute(stmt).scalars().first()
