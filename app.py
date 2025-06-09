from flask import Flask, request, jsonify, render_template, redirect, url_for, flash,session
import mysql.connector
from functools import wraps
app= Flask(__name__)
app.secret_key="my_secret_key_here"

def get_sql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Rohan@2003",
        database="rohandb1"
    )
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

@app.route('/', methods=['POST','GET'])
@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=="POST":
        username=request.form['username']
        passwords=request.form['password']
        db=get_sql_connection()
        cursor=db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM user_info WHERE username=%s AND passwords=%s", (username, passwords))
        try:
            user=cursor.fetchone()
            print(user)
            session['logged_in'] = True
            session['role'] = user['role_no']
            if session.get('role')==3:
                cursor.execute("SELECT roll_no,s_name FROM student_info WHERE username=%s", (user['username'],))
                student_info= cursor.fetchone()
                print(type(student_info))
                session['rollno'] = student_info['roll_no']
                session['username'] = student_info['s_name']
                print(session['username'], session['rollno'])
                cursor.close()
                db.close()
                flash("Login successful!")
                return redirect(url_for('students', rollno=session['rollno']))
            
            elif session.get('role')==2:
                cursor.execute("SELECT t_name,class FROM teacher_info WHERE username=%s", (user['username'],))
                teacher_info= cursor.fetchone()
                print(type(teacher_info),"hello")
                session['username'] = teacher_info['t_name']
                session['class']=teacher_info['class']
                flash("Login successful!")
                return redirect(url_for('home'))

            else:
                cursor.execute("SELECT t_name,class FROM teacher_info WHERE username=%s", (user['username'],))
                teacher_info= cursor.fetchone()
                print(type(teacher_info),"hello")
                session['username'] = teacher_info['t_name']
                session['class']=teacher_info['class']
                flash("Login successful!")
                return redirect(url_for('dashboard'))
        except TypeError:
            flash(f"Error: Invalid username or password.")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/students', methods=['GET'])
@checklogin
def students():
    db=get_sql_connection()
    cursor = db.cursor(dictionary=True)
    rollno = request.args.get('rollno')
    print("Roll number from request:", rollno)
    if session.get('role')==3:
        if rollno:
            print("Roll number from session:", session.get('rollno'))
            if (int(rollno)==session.get('rollno')):
                cursor.execute("SELECT s.roll_no, s.s_name, s.username, s.class, s.s_age, s.fee, s.gender, su.sub_name,m.marks,m.grade FROM student_info s LEFT JOIN marks_info m ON s.roll_no=m.roll_no LEFT JOIN sub_info su ON su.sub_no=m.sub_no WHERE s.roll_no=%s;", (rollno,))
                student_data = cursor.fetchall()
                print(student_data)
                cursor.close()
                db.close()
                return render_template('students.html', students=student_data)
            else:
                flash("You are not authorized to view that page.")
                return redirect(url_for('students'))
        else:
            rollno = session.get('rollno')
            cursor.execute("SELECT s.roll_no, s.s_name, s.username, s.class, s.s_age, s.fee, s.gender, su.sub_name,m.marks,m.grade FROM student_info s LEFT JOIN marks_info m ON s.roll_no=m.roll_no LEFT JOIN sub_info su ON su.sub_no=m.sub_no WHERE s.roll_no=%s;", (rollno,))
            student_data = cursor.fetchall()
            print(student_data)
            cursor.close()
            db.close()
            return render_template('students.html', students=student_data)
    elif session.get('role')==2:
        if rollno:
            session['t_rollno']=rollno
            cursor.execute("SELECT s.roll_no, s.s_name, s.username, s.class, s.s_age, s.fee, s.gender, su.sub_name,m.marks,m.grade FROM student_info s LEFT JOIN marks_info m ON s.roll_no=m.roll_no LEFT JOIN sub_info su ON su.sub_no=m.sub_no LEFT JOIN teacher_info t ON s.class=t.class WHERE t.class=%s AND s.roll_no=%s;", (session['class'],rollno))
            student_data = cursor.fetchall()
            print(student_data)
            if student_data:
                cursor.close()
                db.close()
                return render_template('students.html', students=student_data)
            else:
                flash("You are not authorized to view that page.")
                cursor.close()
                db.close()
                return redirect(url_for('home'))
        else:
            rollno = session.get('t_rollno')
            cursor.execute("SELECT s.roll_no, s.s_name, s.username, s.class, s.s_age, s.fee, s.gender, su.sub_name,m.marks,m.grade FROM student_info s LEFT JOIN marks_info m ON s.roll_no=m.roll_no LEFT JOIN sub_info su ON su.sub_no=m.sub_no LEFT JOIN teacher_info t ON s.class=t.class WHERE t.class=%s AND s.roll_no=%s;", (session['class'],rollno))
            student_data = cursor.fetchall()
            print(student_data)
            if student_data:
                cursor.close()
                db.close()
                return render_template('students.html', students=student_data)
            else:
                flash("You are not authorized to view that page.")
                cursor.close()
                db.close()
                return redirect(url_for('home'))
    else:
        if rollno:
            session['t_rollno']=rollno
            cursor.execute("SELECT s.roll_no, s.s_name, s.username, s.class, s.s_age, s.fee, s.gender, su.sub_name,m.marks,m.grade FROM student_info s LEFT JOIN marks_info m ON s.roll_no=m.roll_no LEFT JOIN sub_info su ON su.sub_no=m.sub_no WHERE s.roll_no=%s;", (rollno,))
            student_data = cursor.fetchall()
            print(student_data)
            cursor.close()
            db.close()
            return render_template('students.html', students=student_data)

        else:
            rollno = session.get('t_rollno')
            cursor.execute("SELECT s.roll_no, s.s_name, s.username, s.class, s.s_age, s.fee, s.gender, su.sub_name,m.marks,m.grade FROM student_info s LEFT JOIN marks_info m ON s.roll_no=m.roll_no LEFT JOIN sub_info su ON su.sub_no=m.sub_no WHERE s.roll_no=%s;", (rollno,))
            student_data = cursor.fetchall()
            print(student_data)
            cursor.close()
            db.close()
            return render_template('students.html', students=student_data)

@app.route('/home')
@checklogin
@check_not_stu
def home():
    db=get_sql_connection()
    cursor= db.cursor(dictionary=True)
    cursor.execute("SELECT roll_no,s_name,class FROM student_info;")
    student_data = cursor.fetchall()
    cursor.execute("SELECT t_no,t_name,class FROM teacher_info;")
    teacher_data = cursor.fetchall()
    cursor.close()
    db.close()
    print(student_data)
    return render_template('home.html', students=student_data,teachers=teacher_data)

@app.route('/dashboard')
@checklogin
@check_admin
def dashboard():
    db=get_sql_connection()
    cursor= db.cursor()
    cursor.execute("SELECT COUNT(*) FROM student_info;")
    total=cursor.fetchone()[0]
    cursor.execute("SELECT gender,COUNT(*) FROM student_info GROUP BY gender;")
    gender=dict(cursor.fetchall())
    cursor.execute("SELECT fee,COUNT(*) FROM student_info GROUP BY fee;")
    fee=dict(cursor.fetchall())
    cursor.execute("SELECT s.sub_name,AVG(m.marks) FROM marks_info m JOIN sub_info s GROUP BY s.sub_name;")
    avgmarks=dict(cursor.fetchall())
    cursor.execute("SELECT class,COUNT(*) FROM student_info GROUP BY class;")
    stuinclass=dict(cursor.fetchall())
    cursor.execute("SELECT class,COUNT(*) FROM student_info WHERE gender='male' GROUP BY class;")
    male=dict(cursor.fetchall())
    cursor.execute("SELECT class,COUNT(*) FROM student_info WHERE gender='female' GROUP BY class;")
    female=dict(cursor.fetchall())
    
    data={"total":total,
          "gender": gender,
          "fee": fee,
          "avgmarks": avgmarks,
          "stuinclass": stuinclass,
          "male": male,
          "female": female
          }
    print(data)
    return render_template('dashboard.html',data=data)

@app.route('/addstudent', methods=["POST","GET"])
@checklogin
@check_admin
def addstudent():
    if request.method=="POST":
        db=get_sql_connection()
        cursor=db.cursor()
        role_no=3
        name = request.form["name"]
        classes = request.form["class"]
        age = request.form["age"]
        fee = request.form["fee"]
        gender = request.form["gender"]
        username = request.form["username"]
        password=request.form["password"]
        print(name,classes,age,fee,gender,username,password)
        cursor.execute("INSERT INTO user_info(username,passwords,role_no) VALUES(%s,%s,%s);",(username,password,role_no))
        db.commit()
        cursor.execute("INSERT INTO student_info(s_name,class,s_age, fee, gender, username) VALUES(%s,%s,%s,%s,%s,%s);",(name, classes, age, fee, gender, username))
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('home'))
    return render_template("addstudent.html")

@app.route('/addmarks',methods=["POST","GET"])
@checklogin
@check_teacher
def addmarks():
    if request.method=="POST":
        db=get_sql_connection()
        cursor=db.cursor()
        rollno=request.args.get('rollno')
        sub_no = int(request.form["subject"])
        marks = request.form["marks"]
        print(rollno,sub_no,marks)
        cursor.execute("INSERT INTO marks_info(roll_no,sub_no,marks) VALUES(%s,%s,%s);",(rollno,sub_no,marks))
        db.commit()
        cursor.execute("UPDATE marks_info SET grade = CASE WHEN marks >= 90 THEN 'A' WHEN marks >= 75 THEN 'B' WHEN marks >= 60 THEN 'C' WHEN marks >= 40 THEN 'P' ELSE 'F'END where roll_no is not null and sub_no is not null;")
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('students'))
    return render_template("addmarks.html")

@app.route('/addteacher',methods=["POST","GET"])
@checklogin
@check_admin
def addteacher():
        if request.method=="POST":
            db=get_sql_connection()
            cursor=db.cursor()
            role_no=2
            name = request.form["name"]
            classes = request.form["class"]
            username = request.form["username"]
            password=request.form["password"]
            print(name,classes,username,password)
            cursor.execute("INSERT INTO user_info(username,passwords,role_no) VALUES(%s,%s,%s);",(username,password,role_no))
            db.commit()
            cursor.execute("INSERT INTO teacher_info(t_name,class, username) VALUES(%s,%s,%s);",(name, classes, username))
            db.commit()
            cursor.close()
            db.close()
            return redirect(url_for('home'))
        return render_template("addteacher.html")

@app.route('/delete')
@checklogin
@check_admin
def delete():
    db=get_sql_connection()
    cursor=db.cursor()
    rollno=request.args.get('rollno')
    cursor.execute("SELECT username FROM student_info WHERE roll_no=%s",(rollno,))
    username=cursor.fetchone()[0]
    cursor.execute("DELETE FROM user_info WHERE username=%s",(username,))
    db.commit()
    cursor.close()
    db.close()
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