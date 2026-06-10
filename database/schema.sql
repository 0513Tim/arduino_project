DROP DATABASE IF EXISTS smart_study_room;
CREATE DATABASE smart_study_room CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_study_room;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL,
    password VARCHAR(100) NOT NULL,
    uid VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS seats (
    seat_id VARCHAR(10) PRIMARY KEY,
    status VARCHAR(20) NOT NULL DEFAULT 'empty',
    student_id VARCHAR(20) DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS noise_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seat_id VARCHAR(10),
    noise_value INT NOT NULL,
    is_warning BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leave_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    seat_id VARCHAR(10),
    student_id VARCHAR(20),
    action VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    seat_id VARCHAR(10) NOT NULL,
    reserved_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'reserved'
);

-- Insert test students
INSERT INTO students (student_id, name, password, uid)
VALUES
    ('A001', '王小明', '1234', 'EB4AA257'),
    ('A002', '陳小華', '1234', 'B6752807'),
    ('A003', '林小美', '1234', '1D958B79')
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    password = VALUES(password),
    uid = VALUES(uid);

-- Insert test seats
INSERT INTO seats (seat_id, status, student_id)
VALUES
    ('01', 'empty', NULL),
    ('02', 'empty', NULL),
    ('03', 'empty', NULL),
    ('04', 'empty', NULL)
ON DUPLICATE KEY UPDATE
    status = VALUES(status),
    student_id = VALUES(student_id);
