from flask import Flask,flash,json, jsonify, make_response, render_template,request,redirect, url_for, session, abort
from flaskext.mysql import MySQL
from json import dump
import gc
import pymysql

mysql = MySQL()
app = Flask(__name__)

app.secret_key = "adminSecretKey"

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

@app.route('/admin')
def adminHomePage():
    return render_template('AdminTasks/indexAdmin.html')

@app.route('/teacher')
def teacherHomePage():

    username = session['username'] # -- eikhane teacher er email ase.. email diye query kore id ana lagbe
    teacherId = getTeacherID(username)

    chairman = getMember("ChairmanID", teacherId)
    generalMember1 = getMember("GeneralMember1", teacherId)
    generalMember2 = getMember("GeneralMember2", teacherId)
    external = getMember("ExternalMember", teacherId)

    return render_template('TeacherTasks/dashboard.html', chairman=chairman, g1=generalMember1, g2=generalMember2, external=external)

def getTeacherID(username):
    sqlString = "Select TeacherID from teacher where Username = " + "'" + username + "'"
    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    cursor.execute(sqlString)
    data = cursor.fetchone()
    return data['TeacherID']

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

    return render_template('TeacherTasks/dashboard.html')

@app.route('/Authenticate',methods = ["GET","POST"])
def Authenticate():

    error = ""
    print("inside Auth")
    try:
        query = request.args['query']
        query = json.loads(query)

        print(query)

        tableName = ""

        if query[2] == "Admin":
            tableName = "admin"
        if query[2] == "Teacher":
            tableName = "teacher"
        if query[2] == "Staff":
            tableName = "staff"

        #print(tableName);

        cursor = mysql.connect().cursor()
        data = cursor.execute("SELECT * from " + tableName + " where Username= %s and Password= %s",
                       (query[0], query[1],))

        print(data)
        userInfo = cursor.fetchone()

        if userInfo is None:
            print("No result found!")
        else:
            for x in userInfo:
                print(x)

        if data==1:
            session['logged_in'] = True
            session['username'] = query[0]
            session['userFullName'] = userInfo[0]
            session['userType'] = query[2]
            gc.collect()
            print(query[2]+": "+userInfo[0])
            return "OK_"+query[2]
        else:
            print(query[2]+"_NotFound")
            return query[2]+"_NotFound"


    except Exception as e:
        print(str(e))
        error = "Invalid Email/Pass. Authentication Failed."
        return error

@app.route('/createComm')
def CreateCommittee():

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

    return render_template("AdminTasks/createComm.html", syallbus=syllabuses, chairman = chairmans, external = externals);

def trimString(s):
    new_str = ''
    for char in s:
        new_str = new_str + char
    return new_str

@app.route('/NewCommittee/save/', methods=['POST','GET'])
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

    ch_id = getTeacherID(result["Chairman"])
    ChairmanID = "'"+ ch_id+"',"

    gen1_id = getTeacherID(result["GeneralMember1"])
    GeneralMember1 = "'" + gen1_id + "',"

    gen2_id = getTeacherID(result["GeneralMember2"])
    GeneralMember2 = "'" + gen2_id + "',"

    ext_id = getTeacherID(result["ExtMember"])
    ExternalMember = "'" + ext_id + "',"

    SyllabusID = "'" + getSyllabusID(result["SyllabusID"]) + "')"

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
    subsql = "SELECT TeacherID from teacher WHERE Username = '" + username + "'"
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

    cursor = mysql.connect().cursor(pymysql.cursors.DictCursor)
    sqlString = "SELECT * FROM `committee` WHERE 1 ORDER BY StartDate DESC "
    cursor.execute(sqlString)
    data = cursor.fetchall()

    for x in data:
        print(x)

    return render_template('AdminTasks/CommitteeList.html', data= data)


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