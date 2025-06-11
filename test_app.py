import pytest
from unittest.mock import patch, MagicMock
from app import app


#fixtures
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
@pytest.fixture
def test_admin(client):
    """A Flask client logged in as admin."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 1
        sess['user'] = 'test_admin'
        sess['roll_no'] = 300
    return client

@pytest.fixture
def test_teacher(client):
    """A Flask client logged in as a teacher."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 2
        sess['user'] = 'test_teacher'
        sess['roll_no'] = 101
    return client

@pytest.fixture
def test_student(client):
    """A Flask client logged in as a student."""
    with client.session_transaction() as sess:
        sess['logged_in'] = True
        sess['role'] = 3
        sess['user'] = 'test_student'
        sess['roll_no'] = 101
    return client

#testing

@patch('app.requests.post')
def test_login_success(mock_post,client):
    mock_post.return_value.status_code= 200
    mock_post.return_value.json.return_value={
        "info": {
            "role_no": 2,
            "username": "Test@teacher.com",
            "t_no": 142,
            "name": "test_user"
        }
        ,"message": "Log in successful"}

    response=client.post('/login',data={
        "username": "test@teacher.com",
        "password": "test_password",
    }, follow_redirects=False)
    
    # Check that the server responded with a redirect
    assert response.status_code == 302

    # Confirm it's redirecting to anypages
    assert response.headers['Location'] in [
    '/studentslist',
    '/teacherslist',
    '/studentdashboard']

@patch('app.requests.post')
def test_login_failed(mock_post,client):
    mock_post.return_value.status_code=404
    mock_post.return_value.json.return_value={"message": "User not found. Try again."}

    response=client.post('/login',data={
        "username": "test@teacher.com",
        "password": "test_password",
    }, follow_redirects=False)
    
    # Check that the server responded with a redirect
    assert response.status_code == 302

    # Confirm it's redirecting to /login
    assert response.headers['Location'] == '/login'

@patch('app.requests.get')
def test_dashboard(mock_get,test_admin):
    mock_get.return_value.status_code=200
    mock_get.return_value.json.return_value={
        "info": {
            "total": 13,
            "gender": {
                "Female": 4,
                "Male": 9
            },
            "fee": {
                "Paid": 9,
                "Unpaid": 4
            },
            "avg": {
                "Science": 75.25,
                "Maths": 72.8889,
                "Telugu": 77.75,
                "Hindi": 77.625
            },
            "stu": {
                "10A": 3,
                "11A": 3,
                "11B": 2,
                "12A": 2,
                "12B": 3
            },
            "male": {
                "10A": 3,
                "11A": 2,
                "11B": 1,
                "12A": 1,
                "12B": 2
            },
            "female": {
                "11A": 1,
                "11B": 1,
                "12A": 1,
                "12B": 1
            }
        },
        "message": "ok"
    }
    response=test_admin.get('/dashboard')

    assert response.status_code==200
    assert b'Dashboard' in response.data

@patch('app.requests.get')
def test_studentslist(mock_get,test_admin):
    mock_get.return_value.status_code=200
    mock_get.return_value.json.return_value={
        "students": [
            {
                "roll_no": 1,
                "s_name": "Anu",
                "s_class": "11A",
                "age": 15,
                "fee": "Paid",
                "gender": "Female"
            },
            {
                "roll_no": 2,
                "s_name": "Arun",
                "s_class": "11A",
                "age": 17,
                "fee": "Paid",
                "gender": "Male"
            },
            {
                "roll_no": 3,
                "s_name": "Bala",
                "s_class": "11B",
                "age": 16,
                "fee": "Paid",
                "gender": "Male"
            }
        ],
        "message": "ok"
    }
    response=test_admin.get('/studentslist')

    assert response.status_code==200
    assert b'Students List' in response.data

@patch('app.requests.get')
def test_teacherslist(mock_get,test_admin):
    mock_get.return_value.status_code=200
    mock_get.return_value.json.return_value={
        "info": [
            {
                "teacher_no": 101,
                "name": "Ram",
                "class": "11A",
                "username": "ram@teacher.com"
            },
            {
                "teacher_no": 102,
                "name": "Ravi",
                "class": "11B",
                "username": "ravi@teacher.com"
            },
            {
                "teacher_no": 103,
                "name": "Latha",
                "class": "12A",
                "username": "latha@teacher.com"
            }
        ],
        "message": "ok"
    }
    response=test_admin.get('/teacherslist')

    assert response.status_code==200
    assert b'Teachers Profile' in response.data

@patch('app.requests.get')
def test_students(mock_get,test_admin):
    mock_get.return_value.status_code=200
    mock_get.return_value.json.return_value={
        "info": {
            "student": {
            "roll_no": 1,
            "s_name": "Anu",
            "s_class": "11A",
            "age": 15,
            "fee": "Paid",
            "gender": "Female"
            },
            "marks": [
                {
                    "subject": "Science",
                    "marks": 85,
                    "grade": "A"
                },
                {
                    "subject": "Maths",
                    "marks": 78,
                    "grade": "B"
                },
                {
                    "subject": "Telugu",
                    "marks": 90,
                    "grade": "A"
                },
                {
                    "subject": "Hindi",
                    "marks": 88,
                    "grade": "A"
                }
            ]
        },
        "message": "ok"
    }
    response=test_admin.get('/students/1')

    assert response.status_code==200
    assert b'Students' in response.data

@patch('app.requests.post')
def test_add_student_success(mock_post, test_admin):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'message': 'Student added successfully'}

    response = test_admin.post('/addstudent', data={
        "username": "test@student.com",
        "password": "test_password",
        "name": "test_user",
        "class": "11A",
        "age": 18,
        "fee": "paid",
        "gender": "male"
    }, follow_redirects=False)

    # Check that the server responded with a redirect
    assert response.status_code == 302

    # Confirm it's redirecting to /studentslist
    assert '/studentslist' in response.headers['Location']

@patch('app.requests.post')
def test_add_teacher_success(mock_post, test_admin):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {'message': 'Teacher added'}

    response = test_admin.post('/addteacher', data={
        "username": "new@teacher.com",
        "password": "pass123",
        "name": "New Teacher",
        "class": "10B"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/teacherslist' in response.headers['Location']

@patch('app.requests.post')
def test_add_marks_success(mock_post, test_teacher):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"message": "Marks added"}

    response = test_teacher.post('/addmarks/101', data={
        "subject": "1",
        "marks": "85"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/students' in response.headers['Location']

@patch('app.requests.put')
def test_edit_student_success(mock_put, test_admin):
    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {'message': 'Student updated'}

    response = test_admin.post('/editstudent/101', data={
        "name": "Updated Name",
        "age": 17,
        "class": "12A",
        "fee": "paid",
        "gender": "female"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/studentslist' in response.headers['Location']

@patch('app.requests.put')
def test_edit_marks_success(mock_put, test_teacher):
    mock_put.return_value.status_code = 200
    mock_put.return_value.json.return_value = {"message": "Marks updated"}

    response = test_teacher.post('/editmarks/101/', data={
        "subject": "1",
        "marks": "90"
    }, follow_redirects=False)

    assert response.status_code == 302
    assert '/students' in response.headers['Location']

@patch('app.requests.delete')
def test_delete_student_success(mock_delete, test_admin):
    mock_delete.return_value.status_code = 200
    mock_delete.return_value.json.return_value = {'message': 'Student deleted'}

    response = test_admin.get('/deletestudent/101', follow_redirects=False)

    assert response.status_code == 302
    assert '/studentslist' in response.headers['Location']

def test_logout(test_admin):
    response = test_admin.get('/logout', follow_redirects=False)
    assert response.status_code == 302
    assert '/login' in response.headers['Location']
