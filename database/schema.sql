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
