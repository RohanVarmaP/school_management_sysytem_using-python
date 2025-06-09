# school_management_sysytem_using-python
# Flask-based Role-Driven Student Management System

This system allows admin, teacher, and student users to manage and view student records, marks, and class statistics.

## Features
- Role-based login (Admin, Teacher, Student)
- Add/view/delete students and teachers
- Enter and view marks
- Dashboards and analytics
- Secure session-based access

## Roles
- **Admin (1):** Full access
- **Teacher (2):** Access to students of assigned class
- **Student (3):** Access to own data only

## Tech Stack
- Python (Flask)
- MySQL
- HTML, CSS

## Setup

1. Clone the repo
2. Create a virtual environment
3. Install dependencies:

```bash
pip install -r requirements.txt
