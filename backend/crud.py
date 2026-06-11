from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import LeaveLog, NoiseLog, Seat, Student


NOISE_LIMIT = 150
SEAT_TIMEOUT_HOURS = 8
latest_uid_scan = {
    "uid": None,
    "registered": False,
    "student_id": None,
    "name": None,
    "source": None,
    "seat_id": None,
    "scanned_at": None,
}


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


def register_student(db: Session, student_id: str, name: str, password: str, uid: str):
    existing_student = db.execute(
        select(Student).where(Student.student_id == student_id)
    ).scalar_one_or_none()
    if existing_student:
        return None, "學號已存在"

    existing_uid = get_student_by_uid(db, uid)
    if existing_uid:
        return None, "UID 已被綁定"

    student = Student(
        student_id=student_id,
        name=name,
        password=password,
        uid=uid,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student, None


def get_seat(db: Session, seat_id: str):
    """取得座位資訊"""
    return db.get(Seat, seat_id)


def release_expired_seats(db: Session):
    """超過 8 小時未釋放的座位自動回收"""
    timeout_before = datetime.now() - timedelta(hours=SEAT_TIMEOUT_HOURS)
    stmt = select(Seat).where(
        Seat.status == "using",
        Seat.updated_at.is_not(None),
        Seat.updated_at < timeout_before,
    )
    expired_seats = list(db.execute(stmt).scalars().all())

    if not expired_seats:
        return []

    for seat in expired_seats:
        leave_log = LeaveLog(
            seat_id=seat.seat_id,
            student_id=seat.student_id,
            action="timeout",
        )
        db.add(leave_log)
        seat.status = "empty"
        seat.student_id = None

    db.commit()
    return expired_seats


def list_all_seats(db: Session):
    """列出所有座位，依 seat_id 排序"""
    release_expired_seats(db)
    stmt = select(Seat).order_by(Seat.seat_id)
    return db.execute(stmt).scalars().all()


def checkin_student(db: Session, uid: str, seat_id: str):
    """
    ESP32 NFC 刷卡報到流程
    """
    release_expired_seats(db)
    remember_latest_uid(uid=uid, source="checkin", seat_id=seat_id)

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
    release_expired_seats(db)
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
    release_expired_seats(db)
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


def remember_latest_uid(
    uid: str,
    source: str | None = None,
    seat_id: str | None = None,
    registered: bool = False,
    student_id: str | None = None,
    name: str | None = None,
):
    latest_uid_scan["uid"] = uid
    latest_uid_scan["registered"] = registered
    latest_uid_scan["student_id"] = student_id
    latest_uid_scan["name"] = name
    latest_uid_scan["source"] = source
    latest_uid_scan["seat_id"] = seat_id
    latest_uid_scan["scanned_at"] = datetime.now()
    return latest_uid_scan.copy()


def get_latest_uid():
    if not latest_uid_scan["uid"]:
        return None
    return latest_uid_scan.copy()


def clear_latest_uid():
    latest_uid_scan["uid"] = None
    latest_uid_scan["registered"] = False
    latest_uid_scan["student_id"] = None
    latest_uid_scan["name"] = None
    latest_uid_scan["source"] = None
    latest_uid_scan["seat_id"] = None
    latest_uid_scan["scanned_at"] = None
