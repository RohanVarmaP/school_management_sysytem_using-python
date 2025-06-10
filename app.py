from urllib.parse import quote_plus
from flask import Flask, request, render_template, redirect, url_for, flash,session
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import requests
from backend_api import Subinfo,Marksinfo,Teacherinfo
app= Flask(__name__)
app.secret_key="my_secret_key_here"
password=quote_plus("Rohan@2003")
app.config['SQLALCHEMY_DATABASE_URI']=f'mysql+pymysql://root:{password}@localhost/rohandb1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)

def check_not_stu(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Checking user role...")
        if session.get('role') == 3:
            print("You do not have permission to access this page.")
            flash("You do not have permission to access this page.")
            return redirect(url_for('logout'))
        print("User has the correct role.")
        return func(*args, **kwargs)
    return wrapper

def check_teacher(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Checking user role...")
        if session.get('role') != 2:
            print("You are not teacher. So, you do not have permission to access this page.")
            flash("You do not have permission to access this page.")
            return redirect(url_for('logout'))
        print("User has the correct role.")
        return func(*args, **kwargs)
    return wrapper

def check_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Checking user role...")
        if session.get('role') != 1:
            print("You are not admin. So, you do not have permission to access this page.")
            flash("You do not have permission to access this page.")
            return redirect(url_for('logout'))
        print("User has the correct role.")
        return func(*args, **kwargs)
    return wrapper
    
def checklogin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Checking login status...")
        if not session.get('logged_in'):
            print("You need to log in first.")
            flash("You need to log in first.")
            return redirect(url_for('login'))
        print("User is logged in.")
        return func(*args, **kwargs)
    return wrapper

def beforelogin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Checking login status...")
        if session.get('logged_in'):
            if session.get('role')==1:
                print("You(admin) have already logged in.")
                flash("You(admin) have already logged in.")
                return redirect(url_for('dashboard'))
            elif session.get('role')==2:
                print("You(teacher) have already logged in.")
                flash("You(teacher) have already logged in.")
                return redirect(url_for('dashboard'))
            else:
                print("You(student) have already logged in.")
                flash("You(student) have already logged in.")
                return redirect(url_for('students'))
        print("User is logged in.")
        return func(*args, **kwargs)
    return wrapper



@app.route('/', methods=['POST','GET'])
@app.route('/login', methods=['POST','GET'])
@beforelogin
def login():
    if request.method=="POST":
        username=request.form['username']
        passwords=request.form['password']
        res = requests.post("http://localhost:5000/api/login", json={"username": username, "password": passwords})
        if res.status_code==200:
            user=res.json().get('info')
            print(user)
            session['logged_in'] = True
            session['role'] = user['role_no']
            session['user'] = user['name']
            print("s.role",session.get('role'))
            if session.get('role')==3:
                print("student")
                session['roll_no']=user['roll_no']
                flash("Login successful!")
                return redirect(url_for('students'))
            elif session.get('role')==2:
                print("Teacher")
                session['t_no']=user['t_no']
                flash("Login successful!")
                return redirect(url_for('teacherslist'))
            else:
                print("admin")
                session['t_no']=user['t_no']
                flash("Login successful!")
                return redirect(url_for('dashboard'))
        else:
            flash(res.json().get('message'))
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/students/', methods=['GET'])
@app.route('/students/<int:roll_no>', methods=['GET'])
@checklogin
def students(roll_no=None):
    print("Roll number from request:", roll_no)
    if session.get('role')==3:
        if roll_no:
            res = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('roll_no')}/{roll_no}")
            if res.status_code==200:
                print("with rollno student                       ",res.json().get('info'))
                subjects=db.session.query(Subinfo.sub_name).all()
                stu_sub=db.session.query(Subinfo.sub_name).outerjoin(Marksinfo,Marksinfo.sub_no==Subinfo.sub_no).filter(Marksinfo.roll_no==roll_no).all()
                if subjects==stu_sub:
                    session['mark']=True
                else:
                    session['mark']=False
                return render_template('students.html', students=res.json().get('info'))
            else:
                flash("You are not authorized to view that page.")
                return redirect(url_for('students'))
        else:
            roll_no = session.get('roll_no')
            res = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('roll_no')}/{roll_no}")
            if res.status_code==200:
                print("without rollno student                       ",res.json().get('info'))
                subjects=db.session.query(Subinfo.sub_name).all()
                stu_sub=db.session.query(Subinfo.sub_name).outerjoin(Marksinfo,Marksinfo.sub_no==Subinfo.sub_no).filter(Marksinfo.roll_no==roll_no).all()
                if subjects==stu_sub:
                    session['mark']=True
                else:
                    session['mark']=False
                return render_template('students.html', students=res.json().get('info'))
            else:
                flash("You are not authorized to view that page.")
                return redirect(url_for('students'))
    else:
        if roll_no:
            print("not student with roll_NO                    cvbnjkytrdcvbnkuytfdcvbnkuytrd")
            print(session.get('role'),session.get('t_no'),roll_no)
            res = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('t_no')}/{roll_no}")
            if res.status_code==200:
                print("with rollno not student                       ",res.json().get('info'))
                subjects=db.session.query(Subinfo.sub_name).all()
                stu_sub=db.session.query(Subinfo.sub_name).outerjoin(Marksinfo,Marksinfo.sub_no==Subinfo.sub_no).filter(Marksinfo.roll_no==roll_no).all()
                if subjects==stu_sub:
                    session['mark']=True
                else:
                    session['mark']=False
                session['t_rollno']=roll_no
                print("session marks is                                   ",session.get('mark'))
                return render_template('students.html', students=res.json().get('info'))
            else:
                flash("You are not authorized to view that page(student with roll_no).")
                return redirect(url_for('teacherslist'))
        else:
            print("not student,without roll_no",session['t_rollno'])
            roll_no=session['t_rollno']
            res = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('t_no')}/{roll_no}")
            if res.status_code==200:
                print("without rollno not student                       ",res.json().get('info'))
                subjects=db.session.query(Subinfo.sub_name).all()
                stu_sub=db.session.query(Subinfo.sub_name).outerjoin(Marksinfo,Marksinfo.sub_no==Subinfo.sub_no).filter(Marksinfo.roll_no==roll_no).all()
                if subjects==stu_sub:
                    session['mark']=True
                else:
                    session['mark']=False
                session['t_rollno']=roll_no
                return render_template('students.html', students=res.json().get('info'))
            else:
                flash("You are not authorized to view that page(student without roll_no).")
                return redirect(url_for('teacherslist'))

@app.route('/studentslist')
@checklogin
@check_not_stu
def studentslist():
    res1 = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('t_no')}/")
    if res1.status_code==200:
        flash("You are authorized to view that page.")
        print("students          ",res1.json().get('students'))
        return render_template('students_list.html', students=res1.json().get('students'))
    else:
        flash("You are not authorized to view that page.")
        return redirect(url_for('logout'))

@app.route('/teacherslist')
@checklogin
@check_not_stu
def teacherslist():
    res2 = requests.get(f"http://localhost:5000/api/teachers/{session.get('role')}/{session.get('t_no')}/")
    if res2.status_code==200:
        flash("You are authorized to view that page.")
        print("teachers          ",res2.json().get('info'))
        return render_template('teachers_list.html', teachers=res2.json().get('info'))
    else:
        flash("You are not authorized to view that page.")
        return redirect(url_for('logout'))

@app.route('/dashboard')
@checklogin
@check_admin
def dashboard():
    print("helloooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo",session.get('role'))
    res = requests.get(f"http://localhost:5000/api/dashboard/{session.get('role')}/")
    print(res)
    if res.status_code!=200:
        flash(res.json().get('message'))
        return redirect(url_for('teaherslist'))
    flash(res.json().get('message'))
    data=res.json().get("info")
    print(data)
    return render_template('dashboard.html',data=data)
    

@app.route('/addstudent', methods=["POST","GET"])
@checklogin
@check_admin
def addstudent():
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
        print("adding student!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",data)
        res = requests.post(f"http://localhost:5000/api/adduser/{session.get('role')}/",json=data)
        if res.status_code!=200:
            flash(res.json().get('message'))
            return redirect(url_for('studentslist'))
        flash(res.json().get('message'))
        return redirect(url_for('studentslist'))
    tch_class = db.session.query(Teacherinfo.t_class).all()
    tch_class_flat = [cls[0] for cls in tch_class]
    print("stu subs are :::::::::::::::::::::::::::::::::::::::",tch_class_flat)
    return render_template("addstudent.html",classes=tch_class_flat)

@app.route('/addmarks/<int:roll_no>',methods=["POST","GET"])
@checklogin
@check_teacher
def addmarks(roll_no):
    if request.method=="POST":
        data={
            "roll_no":roll_no,
            "sub_no": request.form["subject"],
            "marks" : int(request.form["marks"])
        }
        print("adding teacher!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",data)
        res = requests.post(f"http://localhost:5000/api/addmarks/{session.get('role')}/{session.get('t_no')}/",json=data)
        if res.status_code!=200:
            flash(res.json().get('message'))
            return redirect(url_for('students'))
        flash(res.json().get('message'))
        return redirect(url_for('students'))
    stu_sub = db.session.query(Subinfo.sub_name).outerjoin(Marksinfo, Marksinfo.sub_no == Subinfo.sub_no).filter(Marksinfo.roll_no == roll_no).all()
    stu_sub_names = [sub[0] for sub in stu_sub]
    subs = db.session.query(Subinfo.sub_no,Subinfo.sub_name).filter(Subinfo.sub_name.notin_(stu_sub_names)).all()
    print("stu subs are :::::::::::::::::::::::::::::::::::::::",stu_sub_names)
    print("subs are :::::::::::::::::::::::::::::::::::::::",subs)
    return render_template("addmarks.html", subjects=subs)

@app.route('/addteacher',methods=["POST","GET"])
@checklogin
@check_admin
def addteacher():
        if request.method=="POST":
            data={
                "role":2,
                "username": request.form["username"],
                "password": request.form["password"],
                "teacher_name" : request.form["name"],
                "class" : request.form["class"]
            }
            print("adding teacher!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",data)
            res = requests.post(f"http://localhost:5000/api/adduser/{session.get('role')}/",json=data)
            if res.status_code!=200:
                flash(res.json().get('message'))
                return redirect(url_for('teacherslist'))
            flash(res.json().get('message'))
            return redirect(url_for('teacherslist'))
        return render_template("addteacher.html")

@app.route('/editstudent/<int:roll_no>',methods=["POST","GET","PUT"])
@checklogin
@check_admin
def editstudent(roll_no):
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
        res=requests.put(f"http://localhost:5000/api/editstudent/{session.get('role')}/{roll_no}/",json=data)
        if res.status_code!=200:
            flash(res.json().get('message'))
            return redirect(url_for('studentslist'))
        flash(res.json().get('message'))
        return redirect(url_for('studentslist'))
    tch_class = db.session.query(Teacherinfo.t_class).all()
    tch_class_flat = [cls[0] for cls in tch_class]
    print("stu subs are :::::::::::::::::::::::::::::::::::::::",tch_class_flat)
    return render_template("editstudent.html",classes=tch_class_flat)

@app.route('/editmarks/<int:roll_no>/',methods=["POST","GET"])
@checklogin
@check_teacher
def editmarks(roll_no):
    if request.method=="POST":
        data={
            "sub_no": request.form["subject"],
            "marks" : int(request.form["marks"])
        }
        print("adding teacher!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",data)
        res = requests.put(f"http://localhost:5000/api/editmarks/{session.get('role')}/{session.get('t_no')}/{roll_no}/",json=data)
        if res.status_code!=200:
            flash(res.json().get('message'))
            return redirect(url_for('students'))
        flash(res.json().get('message'))
        return redirect(url_for('students'))
    stu_sub = db.session.query(Subinfo.sub_no,Subinfo.sub_name).outerjoin(Marksinfo, Marksinfo.sub_no == Subinfo.sub_no).filter(Marksinfo.roll_no == roll_no).all()
    print("stu subs are :::::::::::::::::::::::::::::::::::::::",stu_sub)
    return render_template("editmarks.html", subjects=stu_sub)


@app.route('/deletestudent/<int:roll_no>')
@checklogin
@check_admin
def deletestudent(roll_no):
    res=requests.delete(f"http://127.0.0.1:5000/api/deletestudent/{session.get('role')}/{roll_no}/")
    if res.status_code==200:
        flash(res.json().get('message'))
        return redirect(url_for('studentslist'))
    else:
        flash(res.json().get('message'))
        return redirect(url_for('studentslist'))

@app.route('/logout')
def logout():
    if session.get('logged_in'):
        session.clear()
        flash("You have been logged out.")
        return redirect(url_for('login'))
    else:
        flash("You are not logged in.")
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True,port=5001)