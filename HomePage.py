from flask import Flask, render_template, request, redirect, url_for
from flaskext.mysql import MySQL
import pymysql.cursors
from collections import OrderedDict
import string

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1234567'
app.config['MYSQL_DATABASE_DB'] = 'examCommittee'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


@app.route('/')
def show_Dash():

    teacherId = "101"

    chairman = getMember("ChairmanID", teacherId)
    generalMember1 = getMember("GeneralMember1", teacherId)
    generalMember2 = getMember("GeneralMember2", teacherId)
    generalMember1.append(generalMember2)
    external = getMember("ExternalMember", teacherId)

    return render_template('homepage.html', chairman=chairman, generalMember=generalMember1, external=external)
    #   return  render_template('dropdown.html')


def getMember(type, id):
    committees = []
    qtype = "'" + id + "'"
    cursor = mysql.connect().cursor()
    sqlString = "SELECT CommitteeName from committee where " + type + " = " + qtype
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        committees.append(trimString(x))

    return committees


def trimString(s):
    new_str = ''
    for char in s:
        new_str = new_str + char
    return new_str


@app.route('/committeehome', methods=['POST', 'GET'])
def show_committee_details():
    if (request.method == 'POST'):
        result = request.form.getlist('committeeName')
        name = ""

        for x in result:
            name = "'" + x + "'"

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


        # print(committeeInfo)

    return render_template('committehome.html', info=committeeInfo)


def get_teacher_by_id(id):
    sqlString = "Select Name from teacher where TeacherID = " + "'" + id + "'"
    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    cursor.execute(sqlString)
    data = cursor.fetchone()
    return data['Name']


@app.route('/profile', methods=['POST', 'GET'])
def show_profile():

        teacherId = "101"

        con = mysql.connect()
        cursor = con.cursor(pymysql.cursors.DictCursor)
        cursor.execute("Select * From teacher t INNER JOIN dept d on t.DeptID = d.ID where TeacherID = " + "'" + teacherId +"'")
        data = cursor.fetchone()
        print(data)


        return render_template('profile.html', data = data)



@app.route('/questionsetting', methods=['POST', 'GET'])
def set_question():
    if (request.method == 'POST'):

        result = request.form.to_dict()
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

        print(sqlInsert)

        con = mysql.connect()
        cursor = con.cursor()
        cursor.execute(sqlInsert)
        con.commit()

        return redirect('/', 302)


    else:
        subjects = getCourseList()
        exams = getExamList()
        teachers = getTeacherList()

        return render_template('questionSetting.html', subjetcs=subjects, exams=exams, teachers=teachers)


@app.route('/questionstatus', methods=['POST', 'GET'])
def set_question_status():

    sqlString = "SELECT Type, CourseID, Qsetter1, Qsetter2, Status FROM exam e INNER JOIN Qsetting q on q.ExamID = e.ID"
    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for row in data:
        print(row)

    return render_template('questionstatus.html', data = data)


def getCourseList():
    courseNames = []
    courseIds = []
    subjects = []

    cursor = mysql.connect().cursor()
    sqlString = "SELECT Title from courses"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        courseNames.append(trimString(x))

    sqlString = "SELECT CourseID from courses"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        courseIds.append(trimString(x))

    for i in range(0, len(courseIds)):
        subjects.append(courseIds[i] + " : " + courseNames[i])

    return subjects


def getExamList():
    exams = []

    cursor = mysql.connect().cursor()
    sqlString = "SELECT DISTINCT ExamName from exam"
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

if __name__ == '__main__':
    app.run()
