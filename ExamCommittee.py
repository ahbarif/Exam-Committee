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


@app.route('/index.html')
def index():
    return render_template('index.html')


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

    cursor = mysql.connect().cursor()
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


if __name__ == '__main__':
    app.run()
