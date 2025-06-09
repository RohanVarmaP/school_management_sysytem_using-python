
# Student Management System (Flask-Based)

A comprehensive **role-based student management system** built using Flask, designed to streamline the administration of students, teachers, and marks through a clean frontend and a RESTful backend API.

---

## Overview

This project consists of two Flask applications:

* **Backend API (`backend_app.py`)**
  Provides RESTful endpoints to manage users (admins, teachers, students), marks, and dashboard data. It uses SQLAlchemy ORM with MySQL for data persistence and enforces role-based authorization.

* **Frontend App (`frontend_app.py`)**
  A user-friendly web interface that consumes the backend API. It offers login/logout functionality, role-based access controls, and pages for managing and viewing student and teacher information, marks, and admin dashboards.

---

## Key Features

* **Role-Based Access Control:**
  Separate permissions for Admin, Teacher, and Student roles to ensure secure data access and management.

* **Authentication & Session Management:**
  Secure login sessions with role-aware page access and navigation.

* **Admin Capabilities:**

  * Manage (add, view, delete) students and teachers
  * View detailed dashboard statistics such as student counts, gender distribution, fees, and average marks.

* **Teacher Capabilities:**

  * View students in their assigned classes
  * Add or update marks for students.

* **Student Capabilities:**

  * View personal information and marks.

* **RESTful API Backend:**
  Designed with clear endpoints for each resource, allowing easy integration or extension.

* **Frontend with Flask & Jinja2:**
  Dynamic templates and forms, enhanced with flash messaging for user feedback.

---

## Project Structure

| File              | Description                                                                     |
| ----------------- | ------------------------------------------------------------------------------- |
| `backend_app.py`  | Flask REST API backend implementing core logic, database models, and endpoints. |
| `frontend_app.py` | Flask frontend application handling UI, user sessions, and API communication.   |

---

## Requirements

* Python 3.8 or higher
* Flask
* SQLAlchemy
* Requests (for API communication in frontend)
* MySQL Server
* MySQL Connector (e.g., `PyMySQL` or `Flask-MySQLdb`)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repo-url>
cd <repo-directory>
```

### 2. Create and Activate a Virtual Environment

```bash
python -m venv venv
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure the Database

* Set up a MySQL database instance.
* Execute the provided SQL scripts to create necessary tables and seed initial data.
* Update the database connection details in `backend_app.py` accordingly.

### 5. Run the Backend API

```bash
python backend_app.py
```

The backend API will run at: `http://localhost:5000`

### 6. Run the Frontend Application

Open a new terminal and run:

```bash
python frontend_app.py
```

The frontend will be accessible at: `http://localhost:5001`

### 7. Access the Application

* Open your browser and visit:
  `http://localhost:5001/login`

* Log in with credentials based on your role (Admin, Teacher, Student).

* Navigate the app as per your role’s permissions.

---

## Usage Tips

* **Admins** should use their dashboard to monitor student metrics and manage users.
* **Teachers** can assign marks to students in their classes.
* **Students** can only view their personal data and marks.

Flash messages guide the user through success/error states for better UX.

---

## Future Enhancements

* Implement password hashing and stronger authentication measures.
* Add API rate limiting and improved error handling.
* Enhance frontend with AJAX for dynamic content loading.
* Integrate graphical charts into the dashboard for visual data insights.
* Add unit tests and integration tests for robustness.

---

## Contact

For questions, feedback, or support, please reach out to:

**Rohan Varma**

---

**Thank you for using the Student Management System!**

---

Would you like me to help generate the `requirements.txt` file or example SQL schema next?

