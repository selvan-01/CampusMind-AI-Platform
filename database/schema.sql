CREATE DATABASE IF NOT EXISTS campusmind;
USE campusmind;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(255),
    role ENUM('admin', 'faculty', 'student')
);

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    year INT,
    email VARCHAR(100)
);
USE campusmind;
SHOW TABLES;

USE campusmind;

INSERT INTO users (username, password, role)
VALUES
('admin', '$pbkdf2-sha256$29000$adminhash', 'admin'),
('faculty1', '$pbkdf2-sha256$29000$facultyhash', 'faculty'),
('student1', '$pbkdf2-sha256$29000$studenthash', 'student');

INSERT INTO users (username, password, role)
VALUES
('admin', 'PASTE_ADMIN_HASH', 'admin'),
('faculty1', 'PASTE_FACULTY_HASH', 'faculty'),
('student1', 'PASTE_STUDENT_HASH', 'student');

USE campusmind;
DELETE FROM users;

INSERT INTO users (username, password, role) VALUES
(
  'admin',
  'scrypt:32768:8:1$1MchXtk0nfHGdKWd$1bc51d7bd96daba03fc89ae609cc58edb2a4afde966e3acfa620f428935916fc1cec517b82fa9b79e20441c42c057b3a5f2d8fbf3bc9b9be2785f4008be0f2fd',
  'admin'
),
(
  'faculty1',
  'scrypt:32768:8:1$AFdJtQuzBhgDhJFL$ed03b9656067e067dfcada929567ef06d8227d8aae4c7dcb58a83c43c66848e641530c54a0ae83f8ad7b910e14b9263f51ef54bd83c8a805bb1faf8852e634f0',
  'faculty'
),
(
  'student1',
  'scrypt:32768:8:1$DmenptCncfV27t96$5039bb601226a2698075d1a1461e77ea94a53030b1e25a71ac50d6a8879af6de1f4da908ebe61e326776c70000f17945e5f458094f8176247ee8ad0f6318adde',
  'student'
);

SELECT username, role FROM users;

USE campusmind;
DESCRIBE students;

USE campusmind;

DROP TABLE students;

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    year INT,
    email VARCHAR(100)
);

DESCRIBE students;

SELECT * FROM students;

USE campusmind;

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    month VARCHAR(20),
    year INT,
    percentage FLOAT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    semester INT,
    year INT,
    marks INT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

SELECT * FROM attendance;
SELECT * FROM marks;

SELECT * FROM students;
SELECT * FROM attendance;
SELECT * FROM marks;
SELECT * FROM students;
USE campusmind;
SELECT * FROM students;

SELECT * FROM students;
SELECT * FROM attendance;

ALTER TABLE students
ADD UNIQUE (student_id);

ALTER TABLE students
ADD CONSTRAINT uq_students_student_id UNIQUE (student_id);

ALTER TABLE students
ADD CONSTRAINT uq_students_student_id UNIQUE (student_id);

SHOW INDEX FROM students;

ALTER TABLE attendance
ADD UNIQUE (student_id);
ALTER TABLE marks
ADD UNIQUE (student_id);

SELECT * FROM attendance;
SELECT * FROM marks;

ALTER TABLE marks
DROP INDEX uq_marks_student_id;
USE campusmind;
SELECT student_id, month, year, COUNT(*)
FROM attendance
GROUP BY student_id, month, year
HAVING COUNT(*) > 1;

SELECT student_id, semester, year, COUNT(*)
FROM marks
GROUP BY student_id, semester, year
HAVING COUNT(*) > 1;

DELETE a1
FROM attendance a1
JOIN attendance a2
WHERE a1.id > a2.id
AND a1.student_id = a2.student_id
AND a1.month = a2.month
AND a1.year = a2.year;

DELETE m1
FROM marks m1
JOIN marks m2
WHERE m1.id > m2.id
AND m1.student_id = m2.student_id
AND m1.semester = m2.semester
AND m1.year = m2.year;

SELECT student_id, month, year, COUNT(*)
FROM attendance
GROUP BY student_id, month, year
HAVING COUNT(*) > 1;

SELECT student_id, semester, year, COUNT(*)
FROM marks
GROUP BY student_id, semester, year
HAVING COUNT(*) > 1;

ALTER TABLE attendance
ADD CONSTRAINT uq_attendance
UNIQUE (student_id, month, year);
ALTER TABLE marks
ADD CONSTRAINT uq_marks
UNIQUE (student_id, semester, year);

SHOW INDEX FROM attendance;
SHOW INDEX FROM marks;

SELECT * FROM students;
SELECT * FROM attendance;
SELECT * FROM marks;

CREATE TABLE exam_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department VARCHAR(50),
    year INT,
    subject VARCHAR(100),
    exam_date DATE,
    notified BOOLEAN DEFAULT FALSE
);

ALTER TABLE marks
ADD COLUMN performance_mail_sent BOOLEAN DEFAULT FALSE;

USE campusmind;

ALTER TABLE attendance
ADD COLUMN mail_sent BOOLEAN DEFAULT FALSE;

DESC attendance;

SELECT student_id, percentage, mail_sent FROM attendance;

SELECT * FROM students;
SELECT * FROM attendance;
SELECT * FROM marks;
SELECT student_id, percentage, mail_sent FROM attendance;

SELECT student_id, mail_sent FROM attendance;

SELECT student_id, performance_mail_sent FROM marks;

UPDATE attendance SET mail_sent = FALSE;
UPDATE marks SET performance_mail_sent = FALSE;

USE campusmind;

CREATE TABLE exam_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject VARCHAR(100),
    exam_date DATE,
    reminder_sent BOOLEAN DEFAULT FALSE
);
DESC exam_schedule;

ALTER TABLE exam_schedule
ADD COLUMN reminder_sent BOOLEAN DEFAULT FALSE;

SELECT * FROM exam_schedule;
UPDATE exam_schedule
SET reminder_sent = FALSE;

INSERT INTO exam_schedule (student_id, subject, exam_date)
VALUES (101, 'Mathematics', DATE_ADD(CURDATE(), INTERVAL 7 DAY));

DESC exam_schedule;
ALTER TABLE exam_schedule
ADD COLUMN student_id INT;

DESC exam_schedule;

INSERT INTO exam_schedule (student_id, subject, exam_date)
VALUES (101, 'Mathematics', DATE_ADD(CURDATE(), INTERVAL 7 DAY));

USE campusmind;
UPDATE exam_schedule
SET exam_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY),
    reminder_sent = FALSE;

SELECT student_id, subject, exam_date, reminder_sent
FROM exam_schedule;

ALTER TABLE exam_schedule
ADD COLUMN department VARCHAR(50),
ADD COLUMN year INT;

INSERT INTO exam_schedule (subject, exam_date, department, year)
VALUES ('Mathematics', DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'CSE', 2);

ALTER TABLE exam_schedule
ADD COLUMN department VARCHAR(50),
ADD COLUMN year INT;

INSERT INTO exam_schedule (subject, exam_date, department, year)
VALUES ('Mathematics', DATE_ADD(CURDATE(), INTERVAL 1 DAY), 'CSE', 2);

UPDATE exam_schedule SET reminder_sent = FALSE;
UPDATE exam_schedule SET reminder_sent = FALSE;

UPDATE exam_schedule
SET exam_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY);

SELECT id, subject, exam_date, department, year, reminder_sent
FROM exam_schedule;

UPDATE exam_schedule SET reminder_sent = FALSE;

UPDATE exam_schedule
SET exam_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY);

SELECT subject, exam_date, department, year, reminder_sent
FROM exam_schedule;

SELECT name, email, department, year FROM students;
SELECT 
    id,
    subject,
    exam_date,
    department,
    year,
    reminder_sent
FROM exam_schedule;

SELECT 
    student_id,
    name,
    email,
    department,
    year
FROM students;
SELECT 
    e.id,
    e.subject,
    e.exam_date,
    e.department AS exam_dept,
    e.year AS exam_year,
    s.email,
    s.name,
    s.department AS student_dept,
    s.year AS student_year
FROM exam_schedule e
JOIN students s
  ON s.department = e.department
 AND s.year = e.year
WHERE e.reminder_sent = FALSE;

UPDATE exam_schedule
SET department = 'CSE',
    year = 2,
    reminder_sent = FALSE,
    exam_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY);


UPDATE students
SET department = 'CSE',
    year = 2;

SELECT 
    e.id,
    e.subject,
    s.email
FROM exam_schedule e
JOIN students s
  ON s.department = e.department
 AND s.year = e.year
WHERE e.reminder_sent = FALSE;

USE campusmind;
SELECT subject, exam_date, department, year, reminder_sent
FROM exam_schedule;

UPDATE exam_schedule
SET exam_date = DATE_ADD(CURDATE(), INTERVAL 1 DAY),
    reminder_sent = FALSE;

DESC marks;

ALTER TABLE marks
ADD COLUMN result_published BOOLEAN DEFAULT FALSE;

UPDATE marks SET result_published = FALSE;

SELECT * FROM marks;
USE campusmind;

SELECT * FROM students;
SELECT * FROM attendance;
SELECT * FROM marks;
DESCRIBE attendance;

SELECT * FROM attendance;
SELECT student_id FROM users WHERE role = 'student';
ALTER TABLE users ADD COLUMN student_id INT;
UPDATE users SET student_id = 1 WHERE username = 'anbu';
SELECT username, role, student_id FROM users;
ALTER TABLE users ADD COLUMN student_id INT;
SELECT student_id, name FROM students;

UPDATE users 
SET student_id = 1 
WHERE username = 'anbu';

SELECT username, role, student_id FROM users;

SELECT * FROM attendance WHERE student_id = 1;
SHOW TABLES;
SELECT * FROM attendance;
SELECT * FROM marks;
SELECT * FROM users;

DESC users;

ALTER TABLE users ADD COLUMN student_id INT;

SELECT student_id, name FROM students;
WHERE student_id = session_student_id

SELECT id, username, role, student_id FROM users;
UPDATE users
SET student_id = 103
WHERE username = 'anbu';

UPDATE users SET student_id = 101 WHERE username = 'senthamil';
UPDATE users SET student_id = 102 WHERE username = 'riya';

SELECT username, role, student_id FROM users;

SELECT username, student_id FROM users WHERE role = 'student';
SELECT * FROM attendance WHERE student_id = 101;
INSERT INTO attendance (student_id, month, year, percentage)
VALUES (101, 'February', 2026, 82.5);

UPDATE attendance
SET percentage = 82.5
WHERE student_id = 101;

SELECT AVG(percentage) FROM attendance WHERE student_id = 101;
SELECT id, username, role FROM users;

SELECT student_id, name FROM students;
SELECT username, student_id FROM users;
UPDATE users
SET student_id = 101
WHERE username = 'student1';

SELECT username, student_id FROM users;

SELECT username, student_id FROM users;

USE campusmind;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','faculty','student') NOT NULL,
    student_id INT DEFAULT NULL
);

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(50),
    year INT
);
INSERT INTO users (username, password, role)
VALUES ('admin', '<PASTE_HASH>', 'admin');

DESC users;

DELETE FROM users;


INSERT INTO users (username, password, role)
VALUES ('admin', 'scrypt:32768:8:1$e3BLx0oHxBkCFdnH$c058fca1140608e12e4751b902651d73e7dae92f7ed1112c704d8a862b8c212bf16f5833da866f23d1cff0ff20960703f359b71da6dfa7adbea29b55475ac785', 'admin');

SELECT username, role FROM users;


INSERT INTO users (username, password, role)
VALUES ('faculty1', 'scrypt:32768:8:1$kWu4vionnOKaweMz$529a1b4c55e1b87978be1d73597d59caf470b4a0f29765d5b0f3b9589a2365b803e91fef9c94e10319561061347d39d2cc806f56e738b2a14845ffc93f71575c', 'faculty');

SELECT student_id, name FROM students;

INSERT INTO users (username, password, role, student_id)
VALUES ('student1', 'scrypt:32768:8:1$DP6rbHUXonrGaztJ$31dd54eb49fc6bf638ace73429c76aa980937404fd13eb8a72bdb768083e10650f95f3c3d4275ef4b87adc8662a3b10aa1bc82d4139dd55bca68ba43fc3fdf85', 'student', 101);

SELECT username, role, student_id FROM users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','faculty','student') NOT NULL,
    student_id INT DEFAULT NULL
);

SELECT * FROM students;

SELECT username, role, student_id FROM users;


SELECT username, role, student_id FROM users;

CREATE TABLE students (
  student_id INT PRIMARY KEY,
  name VARCHAR(100),
  department VARCHAR(50),
  year INT,
  semester INT,
  email VARCHAR(100)
);

CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50),
  password VARCHAR(255),
  role ENUM('admin','faculty','student'),
  student_id INT NULL
);

CREATE TABLE attendance (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  subject VARCHAR(50),
  percentage FLOAT,
  semester INT
);

CREATE TABLE marks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  student_id INT,
  subject VARCHAR(50),
  marks FLOAT,
  semester INT
);

SELECT department, COUNT(*) as total_students
FROM students
GROUP BY department;

SELECT s.name, s.department, a.subject, a.percentage
FROM students s
JOIN attendance a ON s.student_id = a.student_id
WHERE s.department = 'IT' AND s.year = 3;

DESC attendance;

SELECT 
    s.name,
    s.department,
    a.percentage
FROM students s
JOIN attendance a 
    ON s.student_id = a.student_id
WHERE s.department = 'IT'
  AND s.year = 3;

ALTER TABLE attendance
ADD subject VARCHAR(100);

UPDATE attendance
SET subject = 'DBMS'
WHERE student_id = 101;

SELECT s.name, s.department, a.subject, a.percentage
FROM students s
JOIN attendance a ON s.student_id = a.student_id
WHERE s.department = 'IT' AND s.year = 3;

SELECT s.name, m.subject, m.marks
FROM students s
JOIN marks m ON s.student_id = m.student_id;

DESC marks;

ALTER TABLE marks
ADD subject VARCHAR(100);

UPDATE marks
SET subject = 'DBMS'
WHERE student_id = 101;

SELECT 
    s.name,
    s.department,
    m.subject,
    m.marks
FROM students s
JOIN marks m 
    ON s.student_id = m.student_id;

SELECT s.name, m.subject, m.marks
FROM students s
JOIN marks m ON s.student_id = m.student_id;


USE campusmind;
DESC attendance;

SELECT s.department, AVG(a.percentage) AS avg_attendance
FROM students s
JOIN attendance a ON s.student_id = a.student_id
GROUP BY s.department;
ALTER TABLE users ADD department VARCHAR(50);
UPDATE users
SET department = 'IT'
WHERE username = 'faculty1';

CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    department VARCHAR(100),
    subject VARCHAR(100),
    email VARCHAR(100)
);

INSERT INTO faculty (name, department, subject, email) VALUES
('Arun Kumar', 'CSE', 'DBMS', 'arun@college.com'),
('Meena Priya', 'CSE', 'OS', 'meena@college.com'),
('Ravi Shankar', 'IT', 'CN', 'ravi@college.com'),
('Divya', 'IT', 'AI', 'divya@college.com'),
('Suresh', 'ECE', 'VLSI', 'suresh@college.com');

CREATE TABLE faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    email VARCHAR(100)
);
SHOW TABLES;
SELECT * FROM faculty;

USE campusmind;
SHOW TABLES;

USE campusmind;

CREATE TABLE IF NOT EXISTS faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    subject VARCHAR(100) NOT NULL,
    email VARCHAR(100)
);

INSERT INTO faculty (name, department, subject, email) VALUES
('Arun Kumar', 'CSE', 'DBMS', 'arun@college.com'),
('Meena Priya', 'CSE', 'OS', 'meena@college.com'),
('Ravi Shankar', 'IT', 'CN', 'ravi@college.com'),
('Divya', 'IT', 'AI', 'divya@college.com'),
('Suresh', 'ECE', 'VLSI', 'suresh@college.com');

USE campusmind;
SHOW TABLES;

SELECT * FROM faculty;

ALTER TABLE attendance 
ADD COLUMN status VARCHAR(10) DEFAULT 'Present';


CREATE TABLE manual_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject VARCHAR(100),
    date DATE,
    status VARCHAR(10),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

CREATE TABLE internal_marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject VARCHAR(100),
    cia1 INT,
    cia2 INT,
    model INT,
    final_internal FLOAT,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

SELECT * FROM marks WHERE student_id = 101;

INSERT INTO marks (student_id, subject, semester, year, marks)
VALUES
(101, 'DBMS', 1, 2024, 70),
(101, 'Python', 2, 2024, 75),
(101, 'AI', 3, 2025, 60);

INSERT INTO attendance (student_id, subject, percentage)
VALUES
(101, 'DBMS', 82),
(101, 'Python', 68),
(101, 'AI', 90);


SELECT * FROM marks;

SELECT semester, year, marks
FROM marks
WHERE student_id = 1;

SELECT * FROM users;

UPDATE users
SET student_id = 101
WHERE username = 'your_student_username';


UPDATE users
SET student_id = 101
WHERE username = 'senthamil';


SELECT semester, year, marks 
FROM marks 
WHERE student_id = 101;


SELECT * FROM marks WHERE student_id = 101;



