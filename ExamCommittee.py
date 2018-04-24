from flask import Flask, render_template, request, flash, redirect, session, abort
# import pymysql
from flaskext.mysql import MySQL

mysql = MySQL()
app = Flask(__name__)

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '1152104'
app.config['MYSQL_DATABASE_DB'] = 'examCommittee'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
teacherID=0

@app.route('/')
def hello_world():
    return render_template('login.html')


@app.route('/forgot-password.html')
def forgotPass():
    return render_template('forgot-password.html')


@app.route('/signin.html')
def login():
    return render_template('login.html')


@app.route('/index.html',methods = ['POST', 'GET'])
def index():
    if request.method == 'POST':
    examInfo = request.form.to_dict()
    print(examInfo)
    examid = examInfo["exid"]
    courseid = examInfo["course"]
    committeeid = examInfo["committee"]
    examname = examInfo["exam"]
    year = examInfo["year"]
    semester = examInfo["semester"]
    genre = examInfo["typed"]
    examdate = examInfo["examdate"]
    starter = examInfo["timer1"]
    ender = examInfo["timer2"]
    invigilator1=examInfo["invig1"]
    invigilator2 = examInfo["invig2"]
    invigilator3 = examInfo["invig3"]
    #print(examid,courseid,examname,year,semester,genre,examdate,starter,ender,invigilator1,invigilator2,invigilator3)
    cursor.callproc('create_exam',(examid,courseid,committeeid,examname,year,semester,genre,examdate,starter,ender,invigilator1,invigilator2,invigilator3))
    data = cursor.fetchall()
    #session['user']=data[0][0]
    conn.commit()
    tablestr2="SELECT * FROM ExamTable"
    cursor.execute(tablestr2)
    data2=cursor.fetchall()
    flash('Exam is created successfully')
    return render_template('index.html',data2=data2)


@app.route('/Authenticate', methods=['POST', 'GET'])
def Authenticate():
    # username = request.args.get('UserName')
    # username = request.form['username']
    # password = request.form['password']

    result = {'a': '20'}
    if request.method == 'POST':
        result = request.form.to_dict()

    print(result)
    for x in result:
        if x == "username":
            print("username: " + result[x])
        else:
            print("password: " + result[x])

    # print(result)

    #cursor = mysql.connect().cursor()
    sqlString = "SELECT * from teacher where Username='" + result["username"] + "' and Password='" + result[
        "password"] + "'"
    cursor.execute(sqlString)
    data = cursor.fetchone()
    # data2 = cursor.fetchall()
    if data is None:
        return "Username or Password is wrong"
    else:
        #exam-list
        global teacherId
        teacherId = data[0]
        tablestr = "SELECT * FROM ExamTable"
        cursor.execute(tablestr)
        data2 = cursor.fetchall()
        return render_template('index.html', data2=data2)
    
@app.route('/create_exam.html',methods=['GET','POST'])
def createExam():
    course_id = "SELECT ID FROM Courses"
    cursor.execute(course_id)
    courseData=cursor.fetchall()
    global teacherId
    committee_id = "SELECT ID FROM Committee WHERE ChairmanID=(%s) OR GeneralMember1=(%s) OR GeneralMember2=(%s) OR ExternalMember1=(%s)"
    cursor.execute(committee_id,(str(teacherId),str(teacherId),str(teacherId),str(teacherId)))
    committeeData=cursor.fetchall()
    teacheridList="SELECT ID FROM Teacher"
    cursor.execute(teacheridList)
    teacherData=cursor.fetchall()
    conn.commit()
    return render_template('create_exam.html',courseData=courseData,committeeData=committeeData,teacherData=teacherData)



if __name__ == '__main__':
    app.run()
