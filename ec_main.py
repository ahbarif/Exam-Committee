from flask import Flask,flash,json, jsonify, make_response, render_template,request,redirect, url_for, session, abort
from flaskext.mysql import MySQL
from json import dump
import gc
import pymysql
from loginHelper import LoginHelper
from teacher import Teacher
from admin import Admin

mysql = MySQL()
app = Flask(__name__)

app.secret_key = "NowYouDontKnowMe"

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1152104'
app.config['MYSQL_DATABASE_DB'] = 'examCommittee'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def login():
    return render_template('Common/loginPage.html')

@app.route('/logout')
def logout():
    session.clear()
    gc.collect()
    return render_template('Common/loginPage.html')

@app.route('/Authenticate',methods = ["GET","POST"])
def Authenticate():
    try:
        query = request.args['query']
        query = json.loads(query)
        #print(query)
        loginObj=LoginHelper(mysql)
        res=loginObj.loginFunction(query, session, gc)
        print("Returning: "+res)
        return res

    except Exception as e:
        print(str(e))
        error = "Invalid Email/Pass. Authentication Failed. Error: " + str(e)
        return error

@app.route('/admin')
def adminHomePage():
    return render_template('AdminTasks/indexAdmin.html')

#########Admin Tasks

@app.route('/createComm')
def CreateCommittee():

    return Admin(mysql,session).createCommittee()


@app.route('/saveCommittee', methods=['POST','GET'])
def saveCommitteeToDB():

    if request.method== 'POST':
        result = request.form.to_dict();
        print(result)

        for r in result:
            print(r+" : "+result[r])

        return Admin(mysql, session).saveCommitteeToDB(result)
    else:
        return redirect(url_for('CreateCommittee'))


@app.route('/allCommittees')
def allCommittees():
    return Admin(mysql, session).showAllCommittees()

@app.route('/NewTeacher')
def NewTeacher():
    return render_template("AdminTasks/addTeacher.html")


@app.route('/NewTeacher/save/', methods=['POST', 'GET'])
def add_teacher():
    if request.method == 'POST':
        result = request.form.to_dict()
        print(result)

        if result is None:
            return redirect(url_for('NewTeacher'))
        return Admin(mysql, session).saveTeacherToDB(result)

    else:
        return redirect(url_for('NewTeacher'))


@app.route('/allTeachers')
def allTeachers():
    return Admin(mysql, session).allTeachers()

###### Teacher Home Page

@app.route('/teacher')
def teacherHomePage():
    return Teacher(mysql,session).showDashBoard()

@app.route('/committeehome', methods=['POST', 'GET'])
def show_committee_details():
    if (request.method == 'POST'):
        result = request.form.to_dict()
        name = "'" + result['committeeName'] + "'"

        sqlString = "Select * from committee where CommitteeName = " + name
        cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sqlString)
        data = cursor.fetchone()

        print(data)

        committeeInfo = []

        committeeInfo.append(data['CommitteeName'])
        committeeInfo.append(get_teacher_by_id(data['ChairmanID']))
        committeeInfo.append(get_teacher_by_id(data['GeneralMember1']))
        committeeInfo.append(get_teacher_by_id(data['GeneralMember2']))
        committeeInfo.append(get_teacher_by_id(data['ExternalMember']))
        print(committeeInfo)

    return render_template('TeacherTasks/committeehome.html', info=committeeInfo)


def get_teacher_by_id(id):
    sqlString = "Select Name from teacher where TeacherID = " + "'" + id + "'"
    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    cursor.execute(sqlString)
    data = cursor.fetchone()
    return data['Name']


@app.route('/profile', methods=['POST', 'GET'])
def show_profile():
    teacherId = "102"

    if request.method == 'POST':
        result = request.form.to_dict()

        username = result['username']

        sqlQuery = []

        sqlQuery.append(
            "Update teacher Set Name = " + "'" + result['name'] + "'" + " where Username = " + "'" + username + "'")
        sqlQuery.append("Update teacher Set EmailAddr = " + "'" + result[
            'email'] + "'" + " where Username = " + "'" + username + "'")

        for query in sqlQuery:
            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute(query)
            con.commit()

    con = mysql.connect()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute(
        "Select * From teacher t INNER JOIN dept d on t.DeptID = d.ID where TeacherID = " + "'" + teacherId + "'")
    data = cursor.fetchone()

    return render_template('TeacherTasks/profile.html', data=data)


@app.route('/questionsetting', methods=['POST', 'GET'])
def set_question():
    if (request.method == 'POST'):

        result = request.form.to_dict()

        if 'committeeName' in result:

            committeeId = get_CommitteeId(result['committeeName'])
            year = get_CommitteeYear(result['committeeName'])

            subjects = getCourseList(year)
            exams = getExamList(committeeId)
            teachers = getTeacherList()

            return render_template('TeacherTasks/questionsetting.html', subjetcs=subjects, exams=exams, teachers=teachers)

        else:
            courseId = result['courses'].split(' : ')[0]

            con = mysql.connect()
            cursor = con.cursor(pymysql.cursors.DictCursor)
            cursor.execute("Select * From exam WHERE CourseID = " + "'" + courseId + "'")
            data = cursor.fetchone()
            examID = str(data['ID'])

            sqlInsert = "INSERT INTO Qsetting (ExamID, CommitteeID, Qsetter1, Qsetter2, status) values ("
            sqlInsert += "'" + examID + "', "
            sqlInsert += "'" + data['CommitteeID'] + "', "
            sqlInsert += "'" + result['setter1'] + "', "
            sqlInsert += "'" + result['setter2'] + "', "
            sqlInsert += "0)"

            con = mysql.connect()
            cursor = con.cursor()
            cursor.execute(sqlInsert)
            con.commit()

            return redirect('/teacher', 302)


def get_CommitteeId(Name):
    sqlString = "Select CommitteeId from committee where CommitteeName = " + "'" + Name + "'"
    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    cursor.execute(sqlString)
    data = cursor.fetchone()
    return data['CommitteeId']


def get_CommitteeYear(Name):
    sqlString = "Select AcademicYear from committee where CommitteeName = " + "'" + Name + "'"
    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    print("Year query = " + sqlString)
    cursor.execute(sqlString)
    data = cursor.fetchone()
    return data['AcademicYear']


def getCourseList(year):
    courseNames = []
    courseIds = []
    subjects = []

    cursor = mysql.connect().cursor()
    sqlString = "SELECT Title from courses where Year = " + "'" + str(year) + "'"
    print("Course query = " + sqlString)
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        courseNames.append(trimString(x))

    sqlString = "SELECT CourseID from courses where Year = " + "'" + str(year) + "'"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        courseIds.append(trimString(x))

    for i in range(0, len(courseIds)):
        subjects.append(courseIds[i] + " : " + courseNames[i])

    return subjects


def getExamList(committeeId):
    exams = []

    cursor = mysql.connect().cursor()
    sqlString = "SELECT DISTINCT ExamName from exam where CommitteeID = " + "'" + committeeId + "'"
    print(sqlString)
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        exams.append(trimString(x))

    return exams


def getTeacherList():
    teachers = []

    cursor = mysql.connect().cursor()
    sqlString = "SELECT Name from teacher"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        teachers.append(trimString(x))

    return teachers


@app.route('/questionstatus', methods=['POST', 'GET'])
def set_question_status():



    if (request.method == 'POST'):

        result = request.form.to_dict()

        if 'committeeName' in result:
            committeeName = result['committeeName']
            committeeId = get_CommitteeId(committeeName)
            sqlString = "SELECT Type, CourseID, Qsetter1, Qsetter2, Status, q.CommitteeID FROM exam e INNER JOIN Qsetting q on q.ExamID = e.ID WHERE q.CommitteeID = " + "'" + committeeId + "'"
            cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
            cursor.execute(sqlString)
            data = cursor.fetchall()

            for row in data:
                print(row)

            return render_template('TeacherTasks/questionstatus.html', data=data)

        else:
            print("$$$")
            print(result)

            return render_template('TeacherTasks/questionstatus.html')






def trimString(s):
    new_str = ''
    for char in s:
        new_str = new_str + char
    return new_str

if __name__ == '__main__':
    app.run()