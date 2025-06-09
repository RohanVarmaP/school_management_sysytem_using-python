# Student Management System (Flask-based)

This project is a role-based student management system built with Flask. It includes a **backend API** (`backend_app.py`) and a **frontend app** (`frontend_app.py`) that consumes the API. The system supports **Admin**, **Teacher**, and **Student** roles with different permissions and functionalities.

---

## Features

- **User Roles & Authentication**:
  - Admin (role 1)
  - Teacher (role 2)
  - Student (role 3)
- Role-based access control to pages and API endpoints.
- Login and session management.
- Admin can:
  - Add/view/delete students and teachers.
  - View dashboard statistics (student count, gender distribution, average marks, etc.)
- Teachers can:
  - View students assigned to their class.
  - Add marks for students.
- Students can:
  - View their own information and marks.
- Flask backend API provides RESTful endpoints for users, students, teachers, and marks.
- Frontend uses Flask and Jinja2 templates to interact with the API and render pages.

---

## Files

### backend_app.py

- Implements the REST API with endpoints for:
  - User login
  - Viewing, adding, deleting students and teachers
  - Adding marks
  - Retrieving dashboard stats
- Uses SQLAlchemy ORM with a MySQL database.
- Implements role-based authorization and validation.

### frontend_app.py

- Implements the frontend Flask app.
- Handles user login/logout and session management.
- Role-based route protection with decorators.
- Renders templates for:
  - Login page
  - Student listing/viewing
  - Teacher and admin dashboards
  - Forms for adding students, teachers, marks
- Communicates with backend API via HTTP requests (`requests` library).

---

## Requirements

- Python 3.8+
- Flask
- Flask-MySQLdb or PyMySQL (for database connectivity)
- SQLAlchemy
- requests
- MySQL database setup with required schema

---

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repo-url>
   cd <repo-directory>

2. **Create and activate a virtual environment**
   ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate     # Windows

3. **bash  Install dependencies**

   ```bash
    pip install -r requirements.txt

4. **Set up a MySQL database.**

Run the SQL scripts (provided separately) to create tables and initial data.

Update database connection settings in backend_app.py.

5. **Run the backend**

   ```bash
    python backend_app.py
  Backend runs by default on http://localhost:5000.

6. **Run the frontend**
  In another terminal.
   ```bash
    python frontend_app.py
Frontend runs on http://localhost:5001.

7. **Access the application**

Visit http://localhost:5001/login to log in.

Use appropriate credentials for admin, teacher, or student.

Navigate the app based on your role.
