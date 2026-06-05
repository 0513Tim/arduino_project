CREATE DATABASE IF NOT EXISTS study_room_system
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE study_room_system;

CREATE TABLE IF NOT EXISTS students (
    student_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    nfc_uid VARCHAR(50) UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seats (
    seat_no INT PRIMARY KEY,
    status ENUM('available', 'using', 'away', 'warning', 'reserved') DEFAULT 'available',
    student_id VARCHAR(20),
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_seats_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS reservations (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    seat_no INT NOT NULL,
    status ENUM('reserved', 'checked_in', 'cancelled', 'finished') DEFAULT 'reserved',
    reserve_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    checkin_time DATETIME,
    finish_time DATETIME,
    CONSTRAINT fk_reservations_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_reservations_seat
        FOREIGN KEY (seat_no) REFERENCES seats(seat_no)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS noise_logs (
    noise_id INT AUTO_INCREMENT PRIMARY KEY,
    seat_no INT,
    student_id VARCHAR(20),
    noise_value INT NOT NULL,
    level ENUM('quiet', 'normal', 'loud') NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_noise_logs_seat
        FOREIGN KEY (seat_no) REFERENCES seats(seat_no)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    CONSTRAINT fk_noise_logs_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS leave_logs (
    leave_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    seat_no INT NOT NULL,
    leave_type ENUM('temporary', 'final') NOT NULL,
    leave_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    return_time DATETIME,
    status ENUM('away', 'returned', 'finished', 'timeout') DEFAULT 'away',
    CONSTRAINT fk_leave_logs_student
        FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_leave_logs_seat
        FOREIGN KEY (seat_no) REFERENCES seats(seat_no)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

INSERT INTO students (student_id, name, password, nfc_uid)
VALUES
    ('111410001', '王小明', '1234', 'A35F2911'),
    ('111410002', '陳小華', '1234', 'B24C8832'),
    ('111410003', '林大安', '1234', 'C91D782A')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    password = VALUES(password),
    nfc_uid = VALUES(nfc_uid);

INSERT INTO seats (seat_no, status, student_id)
VALUES
    (1, 'available', NULL),
    (2, 'available', NULL),
    (3, 'available', NULL),
    (4, 'available', NULL)
ON DUPLICATE KEY UPDATE
    status = VALUES(status),
    student_id = VALUES(student_id);
