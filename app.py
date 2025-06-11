from urllib.parse import quote_plus
from flask import Flask, request, render_template, redirect, url_for, flash,session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import requests
from apis import Subinfo,Marksinfo,Teacherinfo
import logging
from logging.handlers import RotatingFileHandler
import os

# Logger setup
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set root logger to catch everything from DEBUG and above

# Formatter
formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Capture all logs for console
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File handler (rotating)
file_handler = RotatingFileHandler('app_logs.log', maxBytes=1_000_000, backupCount=1)
file_handler.setLevel(logging.DEBUG)  # Capture all logs for file
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

app= Flask(__name__)
app.secret_key="my_secret_key_here"
password=quote_plus("Rohan@2003")
app.config['SQLALCHEMY_DATABASE_URI']=f'mysql+pymysql://root:{password}@localhost/rohandb1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

def check_not_stu(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Checking user role...")
        if session.get('role') == 3:
            logger.warning("Student tried to access a restricted page.")
            flash("You do not have permission to access this page.")
            return redirect(url_for('logout'))
        logger.info("User has the correct role.")
        return func(*args, **kwargs)
    return wrapper

def check_teacher(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Checking user role...")
        if session.get('role') != 2:
            logger.warning("Non-teacher tried to access teacher-only page.")
            flash("You do not have permission to access this page.")
            return redirect(url_for('logout'))
        logger.info("User is a teacher.")
        return func(*args, **kwargs)
    return wrapper

def check_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Checking user role...")
        if session.get('role') != 1:
            logger.warning("Non-admin tried to access admin-only page.")
            flash("You do not have permission to access this page.")
            return redirect(url_for('logout'))
        logger.info("User is an admin.")
        return func(*args, **kwargs)
    return wrapper
    
def checklogin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Checking login status...")
        if not session.get('logged_in'):
            logger.warning("Unauthenticated user tried to access a protected page.")
            flash("You need to log in first.")
            return redirect(url_for('login'))
        logger.info("User is logged in.")
        return func(*args, **kwargs)
    return wrapper

def beforelogin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info("Checking login status before login page access...")
        if session.get('logged_in'):
            role = session.get('role')
            if role == 1:
                logger.info("Admin already logged in. Redirecting to dashboard.")
                flash("You(admin) have already logged in.")
                return redirect(url_for('dashboard'))
            elif role == 2:
                logger.info("Teacher already logged in. Redirecting to dashboard.")
                flash("You(teacher) have already logged in.")
                return redirect(url_for('dashboard'))
            else:
                logger.info("Student already logged in. Redirecting to students page.")
                flash("You(student) have already logged in.")
                return redirect(url_for('students'))
        logger.info("No active session. Proceeding to requested page.")
        return func(*args, **kwargs)
    return wrapper


@app.route('/', methods=['POST','GET'])
@app.route('/login', methods=['POST','GET'])
@beforelogin
def login():
    if request.method=="POST":
        username=request.form['username']
        passwords=request.form['password']
        app.logger.info(f"Attempting login for user: {username}")  # LOG
        try:
            res = requests.post("http://localhost:5000/api/login", json={"username": username, "password": passwords})
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Login request failed: {e}")  # LOG
            flash("Unable to connect to authentication service.")
            return redirect(url_for('login'))
        app.logger.info(f"Response status code from /api/login: {res.status_code}")  # LOG
        if res.status_code==200:
            user=res.json().get('info')
            app.logger.info(f"User authenticated successfully: {user}")
            session['logged_in'] = True
            session['role'] = user['role_no']
            session['user'] = user['name']
            app.logger.info(f"Session set with role: {session['role']}, user: {session['user']}")
            if session.get('role')==3:
                session['roll_no']=user['roll_no']
                app.logger.info(f"Student logged in with roll_no: {session['roll_no']}")  # LOG
                flash("Login successful!")
                return redirect(url_for('students'))
            elif session.get('role')==2:
                session['t_no']=user['t_no']
                app.logger.info(f"Teacher logged in with t_no: {session['t_no']}")  # LOG
                flash("Login successful!")
                return redirect(url_for('teacherslist'))
            else:
                session['t_no']=user['t_no']
                app.logger.info(f"Admin or other role logged in with t_no: {session['t_no']}")  # LOG
                flash("Login successful!")
                return redirect(url_for('dashboard'))
        else:
            app.logger.warning(f"Login failed: {res.json().get('message')}")  # LOG
            flash(res.json().get('message'))
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
@checklogin
@check_admin
def dashboard():
    app.logger.info(f"Accessing dashboard with role: {session.get('role')}")  # LOG
    try:
        res = requests.get(f"http://localhost:5000/api/dashboard/{session.get('role')}/")
        app.logger.info(f"Response received from dashboard API with status code: {res.status_code}")  # LOG
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Dashboard request failed: {e}")  # LOG
        flash("Unable to fetch dashboard data.")
        return redirect(url_for('teacherslist'))
    if res.status_code!=200:
        app.logger.warning(f"Dashboard API returned error: {res.json().get('message')}") 
        flash(res.json().get('message'))
        return redirect(url_for('teaherslist'))
    app.logger.info(f"Dashboard load message: {res.json().get('message')}")
    flash(res.json().get('message'))
    data=res.json().get("info")
    app.logger.debug(f"Dashboard data: {data}")
    app.logger.info(f"Accessed dashboard with User: {session.get('user')}")  # LOG
    return render_template('dashboard.html',data=data)

@app.route('/studentslist')
@checklogin
@check_not_stu
def studentslist():
    app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' (t_no: {session.get('t_no')}) is accessing /studentslist")
    try:
        res1 = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('t_no')}/")
        app.logger.info(f"Request to students list API returned status: {res1.status_code}")  # LOG
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Failed to retrieve students list: {e}")  # LOG
        flash("Error connecting to student data service.")
        return redirect(url_for('logout'))
    if res1.status_code==200:
        flash("You are authorized to view that page.")
        app.logger.debug(f"Students data: {res1.json().get('students')}") 
        app.logger.debug(f"Retrieved {res1.json().get('students')} students")
        return render_template('students_list.html', students=res1.json().get('students'))
    else:
        app.logger.warning(f"Access denied for user '{session.get('user')}' on /studentslist. API response: {res1.text}")
        flash("You are not authorized to view that page.")
        return redirect(url_for('logout'))

@app.route('/teacherslist')
@checklogin
@check_not_stu
def teacherslist():
    app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' (t_no: {session.get('t_no')}) is accessing /teacherslist")
    try:
        res2 = requests.get(f"http://localhost:5000/api/teachers/{session.get('role')}/{session.get('t_no')}/")
        app.logger.info(f"Request to teachers list API returned status: {res2.status_code}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Failed to retrieve teachers list: {e}")
        flash("Error connecting to teacher data service.")
        return redirect(url_for('logout'))
    if res2.status_code==200:
        flash("You are authorized to view that page.")
        app.logger.debug(f"Retrieved {len(res2.json().get('info', []))} teachers: {res2.json().get('info', [])}")
        return render_template('teachers_list.html', teachers=res2.json().get('info'))
    else:
        flash("You are not authorized to view that page.")
        return redirect(url_for('logout'))

@app.route('/students/', methods=['GET'])
@app.route('/students/<int:roll_no>', methods=['GET'])
@checklogin
def students(roll_no=None):
    if session.get('role')==3:
        app.logger.debug("This is a DEBUG message")
        app.logger.info("This is an INFO message")
        app.logger.warning("This is a WARNING message")
        app.logger.error("This is an ERROR message")
        app.logger.critical("This is a CRITICAL message")
        roll_no = roll_no or session.get('roll_no')
        app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' (Roll_no: {roll_no}) is accessing /students")
        try:
            res = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('roll_no')}/{roll_no}")
            app.logger.info(f"Request to students API returned status: {res.status_code}")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to retrieve student data: {e}")
            flash("Error connecting to student data service.")
            return redirect(url_for('students'))
        if res.status_code==200:
            subjects=db.session.query(Subinfo.sub_name).all()
            stu_sub=db.session.query(Subinfo.sub_name).outerjoin(Marksinfo,Marksinfo.sub_no==Subinfo.sub_no).filter(Marksinfo.roll_no==roll_no).all()
            if subjects==stu_sub:
                session['mark']=True
            else:
                session['mark']=False
            return render_template('students.html', students=res.json().get('info'))
        else:
            app.logger.error(f"{session.get('user')} are not authorized to view that page. Failed to retrieve student data.")
            flash(f"{session.get('user')} are not authorized to view that page. Failed to retrieve student data.")
            return redirect(url_for('students'))
    else:
        app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' (teacher_no: {session.get('t_no')}) is accessing /students")
        roll_no=roll_no or session['t_rollno']
        try:
            res = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('t_no')}/{roll_no}")
            app.logger.info(f"Request to students API returned status: {res.status_code}")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to retrieve student data: {e}")
            flash("Error connecting to student data service.")
            return redirect(url_for('logout'))
        if res.status_code==200:
            subjects=db.session.query(Subinfo.sub_name).all()
            stu_sub=db.session.query(Subinfo.sub_name).outerjoin(Marksinfo,Marksinfo.sub_no==Subinfo.sub_no).filter(Marksinfo.roll_no==roll_no).all()
            if subjects==stu_sub:
                session['mark']=True
            else:
                session['mark']=False
            session['t_rollno']=roll_no
            return render_template('students.html', students=res.json().get('info'))
        else:
            flash("You are not authorized to view that page(student with roll_no).")
            return redirect(url_for('teacherslist'))

@app.route('/addstudent', methods=["POST","GET"])
@checklogin
@check_admin
def addstudent():
    app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' is accessing /addstudent")
    if request.method=="POST":
        data={
            "role":3,
            "username": request.form["username"],
            "password": request.form["password"],
            "name" : request.form["name"],
            "class" : request.form["class"],
            "age" : request.form["age"],
            "fee_details" : request.form["fee"],
            "gender":request.form["gender"]
        }
        app.logger.debug(f"Submitting new student data: {data}")
        try:
            res = requests.post(f"http://localhost:5000/api/adduser/{session.get('role')}/",json=data)
            app.logger.info(f"Add student API returned status: {res.status_code}")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to add student: {e}")
            flash("Error connecting to student registration service.")
            return redirect(url_for('studentslist'))
        if res.status_code!=200:
            app.logger.error(f"Failed to add student: {res.json().get('message')}")
            flash(res.json().get('message'))
            return redirect(url_for('studentslist'))
        flash(res.json().get('message'))
        app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' is has added a student: {request.form["name"]}")
        return redirect(url_for('studentslist'))
    tch_class = db.session.query(Teacherinfo.t_class).all()
    tch_class_flat = [cls[0] for cls in tch_class]
    app.logger.debug(f"Available classes for new student: {tch_class_flat}")
    return render_template("addstudent.html",classes=tch_class_flat)

@app.route('/addteacher',methods=["POST","GET"])
@checklogin
@check_admin
def addteacher():
    app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' is accessing /addteacher")
    if request.method=="POST":
        data={
            "role":2,
            "username": request.form["username"],
            "password": request.form["password"],
            "teacher_name" : request.form["name"],
            "class" : request.form["class"]
        }
        app.logger.debug(f"Submitting new teacher data: {data}")
        try:
            res = requests.post(f"http://localhost:5000/api/adduser/{session.get('role')}/",json=data)
            app.logger.info(f"Add teacher API returned status: {res.status_code}")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to add teacher: {e}")
        if res.status_code!=200:
            app.logger.error(f"Failed to add teacher: {res.json().get('message')}")
            flash(res.json().get('message'))
            return redirect(url_for('teacherslist'))
        flash(res.json().get('message'))
        app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' is has added a teacher: {request.form["name"]}")
        return redirect(url_for('teacherslist'))
    return render_template("addteacher.html")

@app.route('/addmarks/<int:roll_no>',methods=["POST","GET"])
@checklogin
@check_teacher
def addmarks(roll_no):
    app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' is accessing /editstudent/{roll_no}")
    if request.method=="POST":
        data={
            "roll_no":roll_no,
            "sub_no": request.form["subject"],
            "marks" : int(request.form["marks"])
        }
        app.logger.debug(f"Submitting marks data: {data}")
        try:
            res = requests.post(f"http://localhost:5000/api/addmarks/{session.get('role')}/{session.get('t_no')}/",json=data)
            app.logger.info(f"Add marks API returned status: {res.status_code}")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to submit marks: {e}")
            flash("Error connecting to marks submission service.")
            return redirect(url_for('students'))
        if res.status_code!=200:
            app.logger.error(f"Failed to submit marks: {res.json().get('message')}")
            flash(res.json().get('message'))
            return redirect(url_for('students'))
        app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' has successfully added marks for student with roll_no:{roll_no} for subject_no:{request.form["subject"]}")
        flash(res.json().get('message'))
        return redirect(url_for('students'))
    stu_sub = db.session.query(Subinfo.sub_name).outerjoin(Marksinfo, Marksinfo.sub_no == Subinfo.sub_no).filter(Marksinfo.roll_no == roll_no).all()
    stu_sub_names = [sub[0] for sub in stu_sub]
    subs = db.session.query(Subinfo.sub_no,Subinfo.sub_name).filter(Subinfo.sub_name.notin_(stu_sub_names)).all()
    return render_template("addmarks.html", subjects=subs)

@app.route('/editstudent/<int:roll_no>',methods=["POST","GET","PUT"])
@checklogin
@check_admin
def editstudent(roll_no):
    app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' is accessing /editstudent/{roll_no}")
    if request.method=="POST":
        name=request.form.get('name')
        age=request.form.get('age')
        classes=request.form.get('class')
        fee=request.form.get('fee')
        gender=request.form.get('gender')
        data={
            "name": name,
            "class": classes,
            "age": age,
            "fee_details": fee,
            "gender": gender
        }
        app.logger.debug(f"Submitting updated student data for roll_no {roll_no}: {data}")
        try:
            res=requests.put(f"http://localhost:5000/api/editstudent/{session.get('role')}/{roll_no}/",json=data)
            app.logger.info(f"Edit student API returned status: {res.status_code}")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to update student data: {e}")
            flash("Error connecting to student update service.")
            return redirect(url_for('studentslist'))
        if res.status_code!=200:
            app.logger.error(f"Failed to update student data: {res.json().get('message')}")
            flash(res.json().get('message'))
            return redirect(url_for('studentslist'))
        app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' has successfully edited student(roll_no: {roll_no}) details.")
        flash(res.json().get('message'))
        return redirect(url_for('studentslist'))
    tch_class = db.session.query(Teacherinfo.t_class).all()
    tch_class_flat = [cls[0] for cls in tch_class]
    return render_template("editstudent.html",classes=tch_class_flat)

@app.route('/editmarks/<int:roll_no>/',methods=["POST","GET"])
@checklogin
@check_teacher
def editmarks(roll_no):
    app.logger.info(f"User '{session.get('user')}' (teacher ID: {session.get('t_no')}, role: {'role'}) is accessing /editmarks/{roll_no}")
    if request.method=="POST":
        data={
            "sub_no": request.form["subject"],
            "marks" : int(request.form["marks"])
        }
        app.logger.debug(f"Submitting updated marks for roll_no {roll_no}: {data}")
        try:
            res = requests.put(f"http://localhost:5000/api/editmarks/{session.get('role')}/{session.get('t_no')}/{roll_no}/",json=data)
            app.logger.info(f"Edit marks API returned status: {res.status_code}")
        except requests.exceptions.RequestException as e:
            app.logger.error(f"Failed to update marks: {e}")
            flash("Error connecting to marks update service.")
            return redirect(url_for('students'))
        if res.status_code!=200:
            app.logger.error(f"Failed to update marks: {res.json().get('message')}")
            flash(res.json().get('message'))
            return redirect(url_for('students'))
        app.logger.info(f"User '{session.get('user')}' (teacher ID: {session.get('t_no')}, role: {'role'}) has successfully edited marks for student(roll_no:{roll_no}) for a subject(sub_no:{request.form["subject"]})")
        flash(res.json().get('message'))
        return redirect(url_for('students'))
    stu_sub = db.session.query(Subinfo.sub_no,Subinfo.sub_name).outerjoin(Marksinfo, Marksinfo.sub_no == Subinfo.sub_no).filter(Marksinfo.roll_no == roll_no).all()
    return render_template("editmarks.html", subjects=stu_sub)


@app.route('/deletestudent/<int:roll_no>')
@checklogin
@check_admin
def deletestudent(roll_no):
    app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' is attempting to delete student with roll_no {roll_no}")
    try:
        res=requests.delete(f"http://127.0.0.1:5000/api/deletestudent/{session.get('role')}/{roll_no}/")
        app.logger.info(f"Delete student API response status: {res.status_code}")
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Failed to delete student with roll_no {roll_no}: {e}")
        flash("Error connecting to delete student service.")
        return redirect(url_for('studentslist'))
    if res.status_code==200:
        app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' has successful deleted student with roll_no {roll_no}")
        flash(res.json().get('message'))
        return redirect(url_for('studentslist'))
    else:
        app.logger.error(f"Failed to delete student with roll_no {roll_no}: {res.json().get('message')}")
        flash(res.json().get('message'))
        return redirect(url_for('studentslist'))

@app.route('/logout')
def logout():
    if session.get('logged_in'):
        app.logger.info(f"User '{session.get('user')}' with role '{session.get('role')}' is logging out.")
        session.clear()
        flash("You have been logged out.")
    else:
        app.logger.warning("Logout attempted without logging in.")
        flash("You are not logged in.")
        
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True,port=5001)