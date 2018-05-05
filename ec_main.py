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
    return Teacher(mysql, session).showDashBoard()

@app.route('/committeehome', methods=['POST', 'GET'])
def show_committee_details():
    if (request.method == 'POST'):

        result = request.form.to_dict()

        if result is None:
            return redirect('/teacher', 302)

        else: return Teacher(mysql, session).show_committee_details(result)


@app.route('/profile')
def show_profile():

     return Teacher(mysql, session).show_profile()


@app.route('/profile/update', methods=['POST', 'GET'])
def update_profile():

    if request.method == 'POST':
        result = request.form.to_dict()
        return Teacher(mysql, session).update_profile(result)


@app.route('/questionsetting', methods=['POST', 'GET'])
def set_question():
    if (request.method == 'POST'):

        result = request.form.to_dict()

        return  Teacher(mysql, session).question_setting(result)



@app.route('/questionstatus', methods=['POST', 'GET'])
def set_question_status():
    if (request.method == 'POST'):

        result = request.form.to_dict()

        return Teacher(mysql, session).set_question_status(result)

###

if __name__ == '__main__':
    app.run()
