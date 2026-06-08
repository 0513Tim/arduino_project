from sqlalchemy import select
from sqlalchemy.orm import Session

from models import LeaveLog, NoiseLog, Seat, Student


NOISE_LIMIT = 700


def login_student(db: Session, student_id: str, password: str):
    """查詢學生並驗證密碼"""
    stmt = select(Student).where(
        Student.student_id == student_id,
        Student.password == password
    )
    return db.execute(stmt).scalar_one_or_none()


def get_student_by_uid(db: Session, uid: str):
    """用 UID 查詢學生"""
    stmt = select(Student).where(Student.uid == uid)
    return db.execute(stmt).scalar_one_or_none()


def get_seat(db: Session, seat_id: str):
    """取得座位資訊"""
    return db.get(Seat, seat_id)


def list_all_seats(db: Session):
    """列出所有座位，依 seat_id 排序"""
    stmt = select(Seat).order_by(Seat.seat_id)
    return db.execute(stmt).scalars().all()


def checkin_student(db: Session, uid: str, seat_id: str):
    """
    ESP32 NFC 刷卡報到流程
    """
    # 用 uid 查 students
    student = get_student_by_uid(db, uid)
    if not student:
        return None, "學生不存在"

    # 檢查 seat_id 是否存在
    seat = get_seat(db, seat_id)
    if not seat:
        return None, "座位不存在"

    # 檢查座位狀態是否為 empty
    if seat.status != "empty":
        return None, "座位已被佔用"

    # 更新座位狀態
    seat.status = "using"
    seat.student_id = student.student_id
    db.commit()
    db.refresh(seat)

    return {"seat_id": seat.seat_id, "student_id": student.student_id}, None


def create_noise_log(db: Session, seat_id: str, noise_value: int):
    """
    記錄噪音數值
    """
    # 檢查座位是否存在
    seat = get_seat(db, seat_id)
    if not seat:
        return None

    # 判斷是否警告
    is_warning = noise_value >= NOISE_LIMIT

    # 寫入 noise_logs
    noise_log = NoiseLog(
        seat_id=seat_id,
        noise_value=noise_value,
        is_warning=is_warning,
    )
    db.add(noise_log)
    db.commit()
    db.refresh(noise_log)
    return noise_log


def leave_seat(db: Session, seat_id: str):
    """
    GUI 直接離席
    """
    # 查詢該座位
    seat = get_seat(db, seat_id)
    if not seat:
        return None, "座位不存在"

    # 檢查座位狀態是否為 using
    if seat.status != "using":
        return None, "座位狀態錯誤"

    student_id = seat.student_id

    # 寫入 leave_logs
    leave_log = LeaveLog(
        seat_id=seat_id,
        student_id=student_id,
        action="leave",
    )
    db.add(leave_log)

    # 更新座位狀態
    seat.status = "empty"
    seat.student_id = None

    db.commit()
    return True, None


def get_latest_noise(db: Session):
    """取得最新噪音紀錄"""
    stmt = select(NoiseLog).order_by(NoiseLog.created_at.desc()).limit(1)
    return db.execute(stmt).scalar_one_or_none()
