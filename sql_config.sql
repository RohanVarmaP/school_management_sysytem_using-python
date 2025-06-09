CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

-- Table: roles_info
CREATE TABLE roles_info (
    role_no INT PRIMARY KEY,
    role_name VARCHAR(100)
);

-- Table: user_info
CREATE TABLE user_info (
    username VARCHAR(100) PRIMARY KEY,
    passwords VARCHAR(100),
    role_no INT,
    FOREIGN KEY (role_no) REFERENCES roles_info(role_no) ON DELETE CASCADE
);

-- Table: sub_info
CREATE TABLE sub_info (
    sub_no INT PRIMARY KEY,
    sub_name VARCHAR(100)
);

-- Table: teacher_info
CREATE TABLE teacher_info (
    t_no INT PRIMARY KEY,
    t_name VARCHAR(100),
    class VARCHAR(100) UNIQUE,
    username VARCHAR(100),
    FOREIGN KEY (username) REFERENCES user_info(username) ON DELETE CASCADE
);

-- Table: student_info
CREATE TABLE student_info (
    roll_no INT PRIMARY KEY,
    s_name VARCHAR(100),
    class VARCHAR(100),
    username VARCHAR(100),
    s_age INT,
    fee VARCHAR(100),
    gender VARCHAR(100),
    FOREIGN KEY (class) REFERENCES teacher_info(class) ON DELETE CASCADE,
    FOREIGN KEY (username) REFERENCES user_info(username) ON DELETE CASCADE
);

-- Table: marks_info
CREATE TABLE marks_info (
    id INT PRIMARY KEY AUTO_INCREMENT,
    roll_no INT,
    sub_no INT,
    marks INT,
    grade VARCHAR(100),
    FOREIGN KEY (roll_no) REFERENCES student_info(roll_no) ON DELETE CASCADE,
    FOREIGN KEY (sub_no) REFERENCES sub_info(sub_no) ON DELETE CASCADE
);
