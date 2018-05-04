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





@app.route('/createComm')
def CreateCommittee():

    #return Admin(mysql,session).createCommittee()
    cursor = mysql.connect().cursor()
    sqlString = "SELECT Title from syllabus"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    syllabuses = []

    for x in data:
        syllabuses.append(trimString(x))

    cursor = mysql.connect().cursor()
    sqlString = "SELECT Name from teacher where DeptID = 1"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    chairmans = []

    for x in data:
        chairmans.append(trimString(x))

    cursor = mysql.connect().cursor()
    sqlString = "SELECT Name from teacher where DeptID != 1"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    externals = []

    for x in data:
        externals.append(trimString(x))

    return render_template("AdminTasks/createComm.html", syallbus=syllabuses, chairman=chairmans,
                           external=externals);


def trimString(s):
    new_str = ''
    for char in s:
        new_str = new_str + char
    return new_str


@app.route('/saveCommittee', methods=['POST','GET'])
def saveCommitteeToDB():

    if request.method== 'POST':
        result = request.form.to_dict();
        print(result)

        for r in result:
            print(r+" : "+result[r])

    sqlString ="INSERT INTO committee VALUES("
    CommitteeID ="'"+ result["AcademicYear"]+"-"+result["CalendarYear"]+"',"
    CalendarYear ="'"+ result["CalendarYear"]+"',"
    AcademicYear = "'"+ result["AcademicYear"]+"',"
    StartDate = "'"+ result["StartDate"]+"',"
    EndDate = "'"+ result["EndDate"]+"',"
    CommitteeName = "'"+ result["CommitteeName"]+"',"

    ch_id = getTeacherID(result['Chairman'])
    ChairmanID = "'"+ ch_id+"',"

    gen1_id = getTeacherID(result['GeneralMember1'])
    GeneralMember1 = "'" + gen1_id + "',"

    gen2_id = getTeacherID(result['GeneralMember2'])
    GeneralMember2 = "'" + gen2_id + "',"

    ext_id = getTeacherID(result['ExtMember'])
    ExternalMember = "'" + ext_id + "',"

    SyllabusID = "'" + getSyllabusID(result['SyllabusID']) + "')"

    sqlString += CommitteeID+CalendarYear+AcademicYear+StartDate+EndDate+CommitteeName
    sqlString += ChairmanID+GeneralMember1+GeneralMember2+ExternalMember+SyllabusID

    print(sqlString)

    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute(sqlString)
    con.commit()

    flash("New Committee is Created.")
            
    return redirect(url_for('adminHomePage'))

def getTeacherID(username):

    print("Username = " + username)
    subsql = "SELECT TeacherID from teacher WHERE Name = '" + username + "'"
    print(subsql)
    con = mysql.connect()
    cursor = con.cursor(pymysql.cursors.DictCursor)
    cursor.execute(subsql)
    teacherID = cursor.fetchone()
    print(teacherID['TeacherID'])
    return teacherID['TeacherID']

def getSyllabusID(syl_name):
    subsql = "SELECT SyllabusID from syllabus WHERE Title = '" + syl_name + "'"
    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute(subsql)
    id = cursor.fetchone()

    return id[0]

@app.route('/allCommittees')
def allCommittees():

    teacherInfo = getAllTeachers()


    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    sqlString = "SELECT * FROM `committee` WHERE 1 ORDER BY StartDate DESC "
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        print(x)

    return render_template('AdminTasks/CommitteeList.html', data= data, teacherInfo=teacherInfo)

def getAllTeachers():
    teacherNames = []
    teacherIDs = []

    cursor = mysql.connect().cursor()
    sqlString = "SELECT Name from teacher"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
         teacherNames.append(trimString(x))

    sqlString = "SELECT TeacherID from teacher"
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        teacherIDs.append(trimString(x))

    teacher_dict = {}
    for i in range(len(teacherIDs)):
        teacher_dict[teacherIDs[i]] = teacherNames[i]

    return teacher_dict

def getMember(type, id):
    committees = []
    qtype = "'" + id + "'"
    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    sqlString = "SELECT CommitteeName from committee where " + type + " = " + qtype
    print(sqlString)
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        committees.append(trimString(x))

    return committees

    return render_template("AdminTasks/CommitteeList.html")


@app.route('/NewTeacher')
def NewTeacher():
    return render_template("AdminTasks/addTeacher.html")


@app.route('/NewTeacher/save/', methods=['POST', 'GET'])
def add_teacher():
    if request.method == 'POST':
        result = request.form.to_dict()
        print(result)

        sqlString = "INSERT INTO teacher VALUES (" \
                    + "'" + result['teacherid'] + "'" + "," \
                    + "'" + result['teachername'] + "'" + "," \
                    + "'" + result[ 'designation'] + "'" + "," \
                    + "'" + result['departmentid'] + "'" + "," \
                    + "'" + result['email'] + "'" + ","\
                    + "'" + result['phone'] + "'" + "," \
                    + "'" + result['address'] + "'" + "," \
                    + "'" + result['bankaccountname'] + "'"+ ","\
                    + "'" + result['bankaccountnumber'] + "'" + "," \
                    + "'" + result['bankname'] + "'" + "," \
                    + "'" + result['username'] + "'" + "," \
                    + "'" + result['password'] + "'" + ");"
        print(sqlString);

    con = mysql.connect()
    cursor = con.cursor()
    cursor.execute(sqlString)
    con.commit()

    return redirect(url_for('adminHomePage'))


@app.route('/allTeachers')
def allTeachers():

    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    sqlString = "SELECT * FROM `teacher` WHERE 1 ORDER BY TeacherID ASC "
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        print(x)

    return render_template('AdminTasks/TeacherList.html', data= data)


if __name__ == '__main__':
    app.run()