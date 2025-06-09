from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,session
from functools import wraps
import requests
app= Flask(__name__)
app.secret_key="my_secret_key_here"

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
                return redirect(url_for('home'))
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
                return render_template('students.html', students=res.json().get('info'))
            else:
                flash("You are not authorized to view that page.")
                return redirect(url_for('students'))
        else:
            roll_no = session.get('roll_no')
            res = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('roll_no')}/{roll_no}")
            if res.status_code==200:
                print("without rollno student                       ",res.json().get('info'))
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
                session['t_rollno']=roll_no
                return render_template('students.html', students=res.json().get('info'))
            else:
                flash("You are not authorized to view that page(student with roll_no).")
                return redirect(url_for('home'))
        else:
            print("not student,without roll_no",session['t_rollno'])
            roll_no=session['t_rollno']
            res = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('t_no')}/{roll_no}")
            if res.status_code==200:
                print("without rollno not student                       ",res.json().get('info'))
                session['t_rollno']=roll_no
                return render_template('students.html', students=res.json().get('info'))
            else:
                flash("You are not authorized to view that page(student without roll_no).")
                return redirect(url_for('home'))

@app.route('/home')
@checklogin
@check_not_stu
def home():
    res1 = requests.get(f"http://localhost:5000/api/students/{session.get('role')}/{session.get('t_no')}/")
    res2 = requests.get(f"http://localhost:5000/api/teachers/{session.get('role')}/{session.get('t_no')}/")
    if res1.status_code==200 and res2.status_code==200:
        flash("You are authorized to view that page.")
        print("students          ",res1.json().get('students'))
        print("teachers          ",res2.json().get('info'))
        return render_template('home.html', students=res1.json().get('students'),teachers=res2.json().get('info'))
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
        return redirect(url_for('home'))
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
            return redirect(url_for('home'))
        flash(res.json().get('message'))
        return redirect(url_for('home'))
    return render_template("addstudent.html")

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
    return render_template("addmarks.html")

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
                return redirect(url_for('home'))
            flash(res.json().get('message'))
            return redirect(url_for('home'))
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
            return redirect(url_for('home'))
        flash(res.json().get('message'))
        return redirect(url_for('home'))
    return render_template("editstudent.html")

@app.route('/deletestudent/<int:roll_no>')
@checklogin
@check_admin
def deletestudent(roll_no):
    res=requests.delete(f"http://127.0.0.1:5000/api/deletestudent/{session.get('role')}/{roll_no}/")
    if res.status_code==200:
        flash(res.json().get('message'))
        return redirect(url_for('home'))
    else:
        flash(res.json().get('message'))
        return redirect(url_for('home'))

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