import pymysql
from flask import Flask, render_template, request, flash, redirect, session, abort
from flaskext.mysql import MySQL

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
    external = getMember("ExternalMember", teacherId)

    return render_template('TeacherTasks/dashboard.html', chairman=chairman, g1=generalMember1, g2=generalMember2, external=external)


def getMember(type, id):
    qtype = "'" + id + "'"
    cursor = mysql.connect().cursor()
    sqlString = "SELECT CommitteeName from committee where " + type + " = " + qtype
    cursor.execute(sqlString)
    data = cursor.fetchall()
    info = ""

    for x in data:
        info = trimString(x)

    return info


def trimString(s):
    new_str = ''
    for char in s:
        new_str = new_str + char
    return new_str


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
    teacherId = "101"

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

            return redirect('/', 302)


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



if __name__ == '__main__':
    app.run()
