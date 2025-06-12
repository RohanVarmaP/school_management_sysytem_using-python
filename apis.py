from functools import wraps
from urllib.parse import quote_plus
from flask import Flask, redirect, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource,Api
from sqlalchemy.orm import foreign
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, func


app=Flask(__name__)
app.secret_key="secret_key"
password=quote_plus("Rohan@2003")
app.config['SQLALCHEMY_DATABASE_URI']=f'mysql+pymysql://root:{password}@localhost/rohandb1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
api=Api(app)

#decoretor to check login status
# def checklogin(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         print("Checking login status...")
#         if not session.get('log_in'):
#             print("You need to log in first.")
#             return {"message":"Unauthorized – Authentication required(login first)"}, 401
#         print("User is logged in.")
#         return func(*args, **kwargs)
#     return wrapper

# SQLAlchemy models
class Subinfo(db.Model):
    __tablename__='sub_info'
    sub_no=db.Column(db.Integer, primary_key=True, nullable=False)
    sub_name=db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"subject(no={self.sub_no},name={self.sub_name})"
    
class Roleinfo(db.Model):
    __tablename__='roles_info'
    role_no=db.Column(db.Integer ,primary_key=True, nullable=False)
    role_name=db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"role(no={self.role_no},name={self.role_name})"
    
class Userinfo(db.Model):
    __tablename__='user_info'
    username=db.Column(db.String(100), primary_key=True, nullable=False)
    passwords=db.Column(db.String(100), nullable=False)
    role_no=db.Column(db.Integer, db.ForeignKey('roles_info.role_no', ondelete='CASCADE'), nullable=False)

    def __repr__(self):
        return f"user(name:{self.username},password:{self.passwords},Role_no:{self.role_no})"

class Teacherinfo(db.Model):
    __tablename__="teacher_info"
    t_no=db.Column(db.Integer, primary_key=True, nullable=False)
    t_name=db.Column(db.String(100), nullable=False)
    t_class=db.Column('class',db.String(100),unique=True, nullable=False)
    username=db.Column(db.String(100), db.ForeignKey("user_info.username", ondelete='CASCADE'), nullable=False)

    user= db.relationship('Userinfo', backref=db.backref('teacher', uselist=False, cascade='all, delete'))

    def __repr__(self):
        return f"teacher(no:{self.t_no},name:{self.t_name},class:{self.t_class},username:{self.username})"

class Studentinfo(db.Model):
    __tablename__='student_info'
    roll_no=db.Column(db.Integer,primary_key=True, nullable=False)
    s_name=db.Column(db.String(100), nullable=False)
    s_class=db.Column('class',db.String(100),db.ForeignKey('teacher_info.class',ondelete='CASCADE'), nullable=False)
    username=db.Column(db.String(100),db.ForeignKey('user_info.username',ondelete='CASCADE'), nullable=False)
    s_age=db.Column(db.Integer, nullable=False)
    fee=db.Column(db.String(100), nullable=False)
    gender=db.Column(db.String(100), nullable=False)

    user=db.relationship('Userinfo', backref=db.backref('student',uselist=False, cascade='all, delete'))
    teacher_class=db.relationship('Teacherinfo',backref=db.backref('students', cascade="all,delete"), primaryjoin=foreign(s_class) == Teacherinfo.t_class)

    def __repr__(self):
        return f"student(no:{self.roll_no},name:{self.s_name},class:{self.s_class},username:{self.username},age:{self.s_age},fee details:{self.fee},gender:{self.gender})"

class Marksinfo(db.Model):
    __tablename__='marks_info'
    id=db.Column(db.Integer,primary_key=True)
    roll_no=db.Column(db.Integer,db.ForeignKey('student_info.roll_no',ondelete="CASCADE"), nullable=False)
    sub_no=db.Column(db.Integer,db.ForeignKey('sub_info.sub_no',ondelete="CASCADE"), nullable=False)
    marks=db.Column(db.Integer, nullable=False)
    grade=db.Column(db.String(100))

    __table_args__ = (
        UniqueConstraint('roll_no', 'sub_no', name='uix_rollno_subno'),
    )

    student=db.relationship('Studentinfo',backref=db.backref('marks',cascade='all, delete'))
    subject=db.relationship('Subinfo',backref=db.backref('marks',cascade="all, delete"))

    def __repr__(self):
        return f"marks(roll no:{self.roll_no},Subject no:{self.sub_no},marks:{self.marks},grade:{self.grade})"

# API classes
class login(Resource):
    def post(self):
        data=request.get_json()
        username=data.get('username')
        password=data.get('password')

        if not username or not password:
            return {'message':'username and password are required'},400
        
        auser=db.session.query(Userinfo,Teacherinfo,Studentinfo).outerjoin(Studentinfo,Userinfo.username==Studentinfo.username).outerjoin(Teacherinfo, Userinfo.username==Teacherinfo.username).filter(Userinfo.username==username,Userinfo.passwords==password).first()
        if not auser:
            return {"message": "User not found. Try again."},401
        print(auser)
        # session['log_in']=True
        # session['username']=auser[0].username
        # session['role']=auser[0].role_no
        if auser[0].role_no!=3:
            # session['t_no']=auser[1].t_no
            data={
                "role_no":auser[0].role_no,
                "username": auser[0].username,
                "t_no": auser[1].t_no,
                "name":auser[1].t_name
            }
        else:
            # session['roll_no']=auser[2].roll_no
            data={
                "role_no":auser[0].role_no,
                "username": auser[0].username,
                "roll_no": auser[2].roll_no,
                "name":auser[2].s_name
            }
        return {"info":data, "message":"Log in successful"},200
    
class students(Resource):
    # @checklogin
    def get(self,role_no,auth_no,roll_no=None):
        if roll_no:
            if role_no==3:
                print(auth_no)
                if roll_no!=auth_no:
                    return {"message":"Student not found. Try again"},404
                results=db.session.query(Studentinfo, Marksinfo, Subinfo).outerjoin(Marksinfo, Studentinfo.roll_no == Marksinfo.roll_no).outerjoin(Subinfo, Marksinfo.sub_no == Subinfo.sub_no).filter(Studentinfo.roll_no==roll_no).all()
                # print(results)
                # print(results[0][0].roll_no)
                if not results:
                    return {"message":"Student not found. Try again"}, 404
                data={
                    'student':{
                            'roll_no': results[0][0].roll_no,
                            's_name': results[0][0].s_name,
                            's_class': results[0][0].s_class,
                            'age': results[0][0].s_age,
                            'fee': results[0][0].fee,
                            'gender': results[0][0].gender
                        },
                    'marks':[]
                }
                print(results)
                for student,marks,subject in results:
                    if not marks:
                        break
                    data['marks'].append({
                        'subject':subject.sub_name,
                        'marks':marks.marks,
                        "grade":marks.grade
                    })
                print(data)
                return {"info":data,"message":"ok"}
            elif role_no==2:
                print(auth_no)
                results=db.session.query(Studentinfo, Marksinfo, Subinfo,Teacherinfo).outerjoin(Marksinfo, Studentinfo.roll_no == Marksinfo.roll_no).outerjoin(Subinfo, Marksinfo.sub_no == Subinfo.sub_no).outerjoin(Teacherinfo, Teacherinfo.t_class==Studentinfo.s_class).filter(Teacherinfo.t_no==auth_no,Studentinfo.roll_no==roll_no).all()
                # print(results)
                # print(results[0][0].roll_no)
                if not results:
                    return {"message":"Student not found. Try again"},404
                data={
                    'student':{
                            'roll_no': results[0][0].roll_no,
                            's_name': results[0][0].s_name,
                            's_class': results[0][0].s_class,
                            'age': results[0][0].s_age,
                            'fee': results[0][0].fee,
                            'gender': results[0][0].gender
                        },
                    'marks':[]
                }
                for student,marks,subject,teacher in results:
                    if not marks:
                        break
                    data['marks'].append({
                        'subject':subject.sub_name,
                        'marks':marks.marks,
                        "grade":marks.grade
                    })
                    print(teacher)
                # print(data)
                return {"info":data,"message":"ok"}
            elif role_no==1:
                print("hellooooooooooooooooooooooooooooooooooooooooooooo")
                try:
                    results=db.session.query(Studentinfo, Marksinfo, Subinfo).outerjoin(Marksinfo, Studentinfo.roll_no == Marksinfo.roll_no).outerjoin(Subinfo, Marksinfo.sub_no == Subinfo.sub_no).filter(Studentinfo.roll_no == roll_no).all()
                    print("hellooooooooooooooooooooooooooooooooooooooooooooo",results)
                    print(results[0][0].roll_no)
                    data={
                        'student':{
                                'roll_no': results[0][0].roll_no,
                                's_name': results[0][0].s_name,
                                's_class': results[0][0].s_class,
                                'age': results[0][0].s_age,
                                'fee': results[0][0].fee,
                                'gender': results[0][0].gender
                            },
                        'marks':[]
                    }
                    print(results)
                    for student,marks,subject in results:
                        if not marks:
                            break
                        data['marks'].append({
                            'subject':subject.sub_name,
                            'marks':marks.marks,
                            "grade":marks.grade
                        })
                    print(data)
                    return {"info":data,"message":"ok"}
                except Exception as e:
                    return {"message": f"An error occurred: {e}"}, 500
            else:
                return {"message":"You don't have access to this page"},401
        else:
            if role_no==2:
                t_no=auth_no
                result=Studentinfo.query.outerjoin(Teacherinfo).filter(Teacherinfo.t_no==t_no).all()
                # student={
                #     'roll_no': result.roll_no,
                #     's_name': result.s_name,
                #     's_class': result.s_class,
                #     'age': result.s_age,
                #     'fee': result.fee,
                #     'gender': result.gender
                # }
                data=[]
                for student in result:
                    data.append({
                        'roll_no': student.roll_no,
                        's_name': student.s_name,
                        's_class': student.s_class,
                        'age': student.s_age,
                        'fee': student.fee,
                        'gender': student.gender
                    })
                return {"students":data,"message":"ok"}
            elif role_no==1:
                result=Studentinfo.query.all()
                data=[]
                for student in result:
                    data.append({
                        'roll_no': student.roll_no,
                        's_name': student.s_name,
                        's_class': student.s_class,
                        'age': student.s_age,
                        'fee': student.fee,
                        'gender': student.gender
                    })
                return {"students":data,"message":"ok"}
            else:
                roll_no=auth_no
                results=db.session.query(Studentinfo, Marksinfo, Subinfo).join(Marksinfo, Studentinfo.roll_no == Marksinfo.roll_no).join(Subinfo, Marksinfo.sub_no == Subinfo.sub_no).filter(Studentinfo.roll_no == roll_no).all()
                # print(results)
                # print(results[0][0].roll_no)
                if not results:
                    return {"message":"Student not found. Try again"}
                data={
                    'student':{
                            'roll_no': results[0][0].roll_no,
                            's_name': results[0][0].s_name,
                            's_class': results[0][0].s_class,
                            'age': results[0][0].s_age,
                            'fee': results[0][0].fee,
                            'gender': results[0][0].gender
                        },
                    'marks':[]
                }
                for student,marks,subject in results:
                    if not marks:
                        break
                    data['marks'].append({
                        'subject':subject.sub_name,
                        'marks':marks.marks,
                        "grade":marks.grade
                    })
                print(data)
                return {"info":data,"message":"ok"}

class teachers(Resource):
    # @checklogin
    def get(self,role_no,auth_no,t_no=None):
        if t_no:
            if role_no==1:
                teacher=Teacherinfo.query.filter_by(t_no=t_no).first()
                if not teacher:
                    return {"message": "this teacher doen't exist"},404
                data={
                    'teacher_no':teacher.t_no,
                    'name':teacher.t_name,
                    'class':teacher.t_class,
                    'username':teacher.username
                }
                return {"info":data,"message":"ok"}
            elif role_no==2:
                if auth_no!=t_no:
                    return {"message":"You(teacher) don't have access to this page"},401
                try:
                    teacher=Teacherinfo.query.filter_by(t_no=t_no).first()
                except Exception:
                    return {"message":"You(teacher) don't have access to this page"},401
                if not teacher:
                    return {"message":"You(teacher) don't have access to this page"},401
                data={
                    'teacher_no':teacher.t_no,
                    'name':teacher.t_name,
                    'class':teacher.t_class,
                    'username':teacher.username
                }
                return {"info":data,"message":"ok"}
            else:
                return {"message":"You(student) don't have access to this page"},401
        else:
            if role_no==2:
                teacher=Teacherinfo.query.filter_by(t_no=auth_no).first()
                data={
                    'teacher_no':teacher.t_no,
                    'name':teacher.t_name,
                    'class':teacher.t_class,
                    'username':teacher.username
                }
                print(data)
                return {"info":data,"message":"ok"}
            elif role_no==1:
                results=Teacherinfo.query.all()
                data=[]
                for teacher in results:
                    data.append({
                        'teacher_no':teacher.t_no,
                        'name':teacher.t_name,
                        'class':teacher.t_class,
                        'username':teacher.username
                    })
                print(data)
                return {"info":data,"message":"ok"}
            else:
                return {"message":"You don't have access to this page"}, 401

class logout(Resource):
    # @checklogin
    def post(self):
        session.clear()
        return {"message":"logged out successfully"}
    def get(self):
        return {"message":"Method Not Allowed – HTTP method not allowed"},405

class adduser(Resource):
    # @checklogin
    def post(self,role_no):
        if role_no==1:
            data=request.get_json()
            if data:
                role=data.get('role')
                new_user=Userinfo(
                    role_no=role,
                    username=data.get('username'),
                    passwords=data.get('password')
                )
                print("new_user:                              ",new_user)
                if(role==3):
                    try:
                        new_student=Studentinfo(
                            username=data.get('username'),
                            s_name=data.get('name'),
                            s_class=data.get('class'),
                            s_age=data.get('age'),
                            fee=data.get('fee_details'),
                            gender=data.get('gender')
                        )
                        print("new_student:                      ",new_student)
                        db.session.add(new_user)
                        db.session.commit()
                        db.session.add(new_student)
                        db.session.commit()
                        return {'message':"Student added"}
                    except Exception as e:
                        return {'message':f"Enter the correct values for student. the error: {e}"},502
                elif(role==2):
                    try:
                        new_teacher=Teacherinfo(
                            username=data.get('username'),
                            t_name=data.get('teacher_name'),
                            t_class=data.get('class')
                        )
                        db.session.add(new_user)
                        db.session.commit()
                        db.session.add(new_teacher)
                        db.session.commit()
                        return {'message':"Teacher added"}
                    except Exception as e:
                        return {f'message':"Enter the correct values for Teacher. the error: {e}"},502
                else:
                    return {'message':"error: You can only add Student or Teacher"},502
            else:
                return {'message':"error: There is no data sent"},502
        else:
            return {'message':"error: Only an admin can add Users"},402

class addmarks(Resource):
    # @checklogin
    def post(self,role_no,auth_no):
        if role_no==2:
            try:
                data=request.get_json()
                print("data                     ",data)
                if not Studentinfo.query.join(Teacherinfo).filter(Studentinfo.roll_no==data.get('roll_no'),Teacherinfo.t_no==auth_no).first():
                    return {"message":"There is no student with the given roll_no"},502
                if not Subinfo.query.filter_by(sub_no=data.get('sub_no')).first():
                    return {"message":"There is no subject with the given sub_no"},502
                grade=None
                if data.get('marks') >= 90: grade= 'A'
                elif data.get('marks') >= 75: grade= 'B'
                elif data.get('marks') >= 60: grade= 'C'
                elif data.get('marks') >= 40: grade= 'P'
                else: grade= 'F'
                print("grade:         ",grade)
                new_marks=Marksinfo(
                    roll_no=data.get('roll_no'),
                    sub_no=data.get('sub_no'),
                    marks=data.get('marks'),
                    grade=grade
                )
                print("new_marks!!!!!!!!!!!!!!!!!!!!!!",new_marks)
                db.session.add(new_marks)
                db.session.commit()
                return {"message":"Marks successfully added"}
            except Exception as e:
                return {"message": f"An error occurred: {e}"}, 500
        else:
            return {"message":"You(Admin) are Unauthorized to do to the task"},401

class deletestudent(Resource):
    # @checklogin
    def delete(self,role_no,roll_no):
        if role_no!=1:
            return {"message":"You are Unauthorized, only admin can perform this task."},401
        try:
            user=Userinfo.query.join(Studentinfo).filter(Studentinfo.roll_no==roll_no).first()
            db.session.delete(user)
            db.session.commit()
            return {"message":"Student successfully deleted."}
        except Exception as e:
            return {"message": f"An error occurred: {e}"}, 500

class editstudent(Resource):
    # @checklogin
    def put(self,role_no,roll_no):
        if role_no!=1:
            return {"message":"You are Unauthorized, only admin can perform this task."},401
        data=request.get_json()
        if not data:
            return {"message":"Data is not valid."},502
        try:
            student=Studentinfo.query.filter_by(roll_no=roll_no).first()
            print(data)
            if data.get('name'):
                print("name")
                student.s_name=data.get('name')
            if data.get('class'):
                print("class")
                student.s_class=data.get('class')
            if data.get('age'):
                print("age")
                print(data.get('age'))
                student.s_age=data.get('age')
            if data.get('fee_details'):
                print("fee")
                student.fee=data.get('fee_details')
            if data.get('gender'):
                print("gender")
                student.gender=data.get('gender')
            db.session.commit()
            return {'message':"student updated"}
        except Exception as e:
            return {"message": f"An error occurred: {e}"}, 500

class editmarks(Resource):
    # @checklogin
    def put(self,role_no,auth_no,roll_no):
        if role_no!=2:
            return {"message":"You are Unauthorized, only admin can perform this task."},401
        data=request.get_json()
        if not data:
            return {"message":"Data is not valid."},502
        try:
            mark=Marksinfo.query.join(Studentinfo, Studentinfo.roll_no==Marksinfo.roll_no).join(Subinfo,Subinfo.sub_no==Marksinfo.sub_no).join(Teacherinfo,Teacherinfo.t_class==Studentinfo.s_class).filter(Studentinfo.roll_no==roll_no,Teacherinfo.t_no==auth_no,Subinfo.sub_no==data.get('sub_no')).first()
            print(mark)
            if data.get('sub_no'):
                mark.sub_no=data.get('sub_no')
            if data.get('marks'):
                mark.marks=data.get('marks')
                grade=None
                if data.get('marks') >= 90: grade= 'A'
                elif data.get('marks') >= 75: grade= 'B'
                elif data.get('marks') >= 60: grade= 'C'
                elif data.get('marks') >= 40: grade= 'P'
                else: grade= 'F'
                mark.grade=grade
            db.session.commit()
            print(mark)
            return {'message':"student updated"}
        except Exception as e:
            return {"message": f"An error occurred: {e}"}, 500

class dashboard(Resource):
    # @checklogin
    def get(self,role_no):
        if role_no!=1:
            return {"message":"You are Unauthorized, only admin can perform this task."},401
        try:
            total = db.session.query(func.count(Studentinfo.roll_no)).scalar()
            gender = dict(db.session.query(Studentinfo.gender, func.count()).group_by(Studentinfo.gender).all())
            fee = dict(db.session.query(Studentinfo.fee, func.count()).group_by(Studentinfo.fee).all())
            avgmarks_raw = dict(db.session.query(Subinfo.sub_name, func.avg(Marksinfo.marks)).join(Marksinfo, Marksinfo.sub_no == Subinfo.sub_no).group_by(Subinfo.sub_name).all())
            stuinclass = dict(db.session.query(Studentinfo.s_class, func.count()).group_by(Studentinfo.s_class).all())
            male = dict(db.session.query(Studentinfo.s_class, func.count()).filter(Studentinfo.gender == 'male').group_by(Studentinfo.s_class).all())
            female = dict(db.session.query(Studentinfo.s_class, func.count()).filter(Studentinfo.gender == 'female').group_by(Studentinfo.s_class).all())
            print(total)
            print()
            print(gender)
            print()
            print(fee)
            print()
            print(avgmarks_raw)
            print()
            print(stuinclass)
            print()
            print(male)
            print()
            print(female)
            for x,y in avgmarks_raw.items():
                print(x,"->",y)
            avgmarks = {x: float(y) if y is not None else None for x,y in avgmarks_raw.items()}
            data={
                "total":total,
                "gender":gender,
                "fee":fee,
                "avg":avgmarks,
                "stu":stuinclass,
                "male":male,
                "female":female
            }
            return {"info":data,"message":"ok"}
        except Exception as e:
            return {"message": f"An error occurred: {e}"}, 500
        

#api
api.add_resource(login,'/api/login/')
api.add_resource(logout,'/api/logout/')
api.add_resource(students,'/api/students/<int:role_no>/<int:auth_no>/','/api/students/<int:role_no>/<int:auth_no>/<int:roll_no>/',endpoint='students_resource')
api.add_resource(teachers,'/api/teachers/<int:role_no>/<int:auth_no>/', '/api/teachers/<int:role_no>/<int:auth_no>/<int:t_no>/',endpoint='teachers_resource')
api.add_resource(adduser,'/api/adduser/<int:role_no>/',endpoint='adduser_resource')
api.add_resource(addmarks,'/api/addmarks/<int:role_no>/<int:auth_no>/',endpoint="addmarks_resource")
api.add_resource(deletestudent,"/api/deletestudent/<int:role_no>/<int:roll_no>/",endpoint="deletestudent_resource")
api.add_resource(editstudent,'/api/editstudent/<int:role_no>/<int:roll_no>/',endpoint='editstudent_resource')
api.add_resource(editmarks,'/api/editmarks/<int:role_no>/<int:auth_no>/<int:roll_no>/',endpoint='editmarks_resource')
api.add_resource(dashboard,'/api/dashboard/<int:role_no>/',endpoint="dashboard_resource")


if __name__=="__main__":
    app.run(debug=True)