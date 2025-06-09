-- Roles Info Table
CREATE TABLE roles_info (
    role_no INT PRIMARY KEY,
    role_name VARCHAR(50)
);

-- User Info Table
CREATE TABLE user_info (
    username VARCHAR(100) PRIMARY KEY,
    passwords VARCHAR(100),
    role_no INT,
    FOREIGN KEY (role_no) REFERENCES roles_info(role_no) ON DELETE CASCADE
);

-- Student Info Table
CREATE TABLE student_info (
    roll_no INT AUTO_INCREMENT PRIMARY KEY,
    s_name VARCHAR(100),
    class VARCHAR(50),
    s_age INT,
    fee FLOAT,
    gender VARCHAR(10),
    username VARCHAR(100),
    FOREIGN KEY (username) REFERENCES user_info(username) ON DELETE CASCADE
);

-- Teacher Info Table
CREATE TABLE teacher_info (
    t_no INT AUTO_INCREMENT PRIMARY KEY,
    t_name VARCHAR(100),
    class VARCHAR(50),
    username VARCHAR(100),
    FOREIGN KEY (username) REFERENCES user_info(username) ON DELETE CASCADE
);

-- Subject Info Table
CREATE TABLE sub_info (
    sub_no INT AUTO_INCREMENT PRIMARY KEY,
    sub_name VARCHAR(100)
);

-- Marks Info Table
CREATE TABLE marks_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no INT,
    sub_no INT,
    marks FLOAT,
    grade CHAR(1),
    FOREIGN KEY (roll_no) REFERENCES student_info(roll_no) ON DELETE CASCADE,
    FOREIGN KEY (sub_no) REFERENCES sub_info(sub_no) ON DELETE CASCADE
);
