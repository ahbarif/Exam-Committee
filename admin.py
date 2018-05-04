from flask import Flask,flash,json, jsonify, make_response, render_template,request,redirect, url_for, session, abort
from flaskext.mysql import MySQL
from json import dump
import gc
import pymysql
from teacher import Teacher

class Admin:

    mysql = MySQL()

    def __init__(self,mysql,session):
        self.mysql = mysql
        self.session = session

    def createCommittee(self):
        cursor = self.mysql.connect().cursor()
        sqlString = "SELECT Title from syllabus"
        cursor.execute(sqlString)
        data = cursor.fetchall()

        syllabuses = []

        for x in data:
            syllabuses.append(self.trimString(x))

        cursor = self.mysql.connect().cursor()
        sqlString = "SELECT Name from teacher where DeptID = 1"
        cursor.execute(sqlString)
        data = cursor.fetchall()

        chairmans = []

        for x in data:
            chairmans.append(self.trimString(x))

        cursor = self.mysql.connect().cursor()
        sqlString = "SELECT Name from teacher where DeptID != 1"
        cursor.execute(sqlString)
        data = cursor.fetchall()

        externals = []

        for x in data:
            externals.append(self.trimString(x))

        return render_template("AdminTasks/createComm.html", syallbus=syllabuses, chairman=chairmans,
                               external=externals);

    def saveCommitteeToDB(self,result):
        sqlString = "INSERT INTO committee VALUES("
        CommitteeID = "'" + result["AcademicYear"] + "-" + result["CalendarYear"] + "',"
        CalendarYear = "'" + result["CalendarYear"] + "',"
        AcademicYear = "'" + result["AcademicYear"] + "',"
        StartDate = "'" + result["StartDate"] + "',"
        EndDate = "'" + result["EndDate"] + "',"
        CommitteeName = "'" + result["CommitteeName"] + "',"

        ch_id = self.getTeacherID(result['Chairman'])
        ChairmanID = "'" + ch_id + "',"

        gen1_id = self.getTeacherID(result['GeneralMember1'])
        GeneralMember1 = "'" + gen1_id + "',"

        gen2_id = self.getTeacherID(result['GeneralMember2'])
        GeneralMember2 = "'" + gen2_id + "',"

        ext_id = self.getTeacherID(result['ExtMember'])
        ExternalMember = "'" + ext_id + "',"

        SyllabusID = "'" + self.getSyllabusID(result['SyllabusID']) + "')"

        sqlString += CommitteeID + CalendarYear + AcademicYear + StartDate + EndDate + CommitteeName
        sqlString += ChairmanID + GeneralMember1 + GeneralMember2 + ExternalMember + SyllabusID

        print(sqlString)

        con = self.mysql.connect()
        cursor = con.cursor()
        cursor.execute(sqlString)
        con.commit()

        return redirect(url_for('adminHomePage'))

    def getTeacherID(self, username):
        print("Username = " + username)
        subsql = "SELECT TeacherID from teacher WHERE Name = '" + username + "'"
        print(subsql)
        con = self.mysql.connect()
        cursor = con.cursor(pymysql.cursors.DictCursor)
        cursor.execute(subsql)
        teacherID = cursor.fetchone()
        print(teacherID['TeacherID'])
        return teacherID['TeacherID']

    def getSyllabusID(self,syl_name):
        subsql = "SELECT SyllabusID from syllabus WHERE Title = '" + syl_name + "'"
        con = self.mysql.connect()
        cursor = con.cursor()
        cursor.execute(subsql)
        id = cursor.fetchone()

        return id[0]


    def showAllCommittees(self):
        teacherInfo = self.getAllTeachers()

        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        sqlString = "SELECT * FROM `committee` WHERE 1 ORDER BY StartDate DESC "
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            print(x)

        return render_template('AdminTasks/CommitteeList.html', data=data, teacherInfo=teacherInfo)

    def getAllTeachers(self):
        teacherNames = []
        teacherIDs = []

        cursor = self.mysql.connect().cursor()
        sqlString = "SELECT Name from teacher"
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            teacherNames.append(self.trimString(x))

        sqlString = "SELECT TeacherID from teacher"
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            teacherIDs.append(self.trimString(x))

        teacher_dict = {}
        for i in range(len(teacherIDs)):
            teacher_dict[teacherIDs[i]] = teacherNames[i]

        return teacher_dict

    def getMember(self,type, id):
        committees = []
        qtype = "'" + id + "'"
        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        sqlString = "SELECT CommitteeName from committee where " + type + " = " + qtype
        print(sqlString)
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            committees.append(self.trimString(x))

        return committees

        return render_template("AdminTasks/CommitteeList.html")

    ########
    def saveTeacherToDB(self,result):

        sqlString = "INSERT INTO teacher VALUES (" \
                    + "'" + result['teacherid'] + "'" + "," \
                    + "'" + result['teachername'] + "'" + "," \
                    + "'" + result['designation'] + "'" + "," \
                    + "'" + result['departmentid'] + "'" + "," \
                    + "'" + result['email'] + "'" + "," \
                    + "'" + result['phone'] + "'" + "," \
                    + "'" + result['address'] + "'" + "," \
                    + "'" + result['bankaccountname'] + "'" + "," \
                    + "'" + result['bankaccountnumber'] + "'" + "," \
                    + "'" + result['bankname'] + "'" + "," \
                    + "'" + result['username'] + "'" + "," \
                    + "'" + result['password'] + "'" + ");"
        print(sqlString);

        con = self.mysql.connect()
        cursor = con.cursor()
        cursor.execute(sqlString)
        con.commit()

        return redirect(url_for('adminHomePage'))

    def allTeachers(self):

        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        sqlString = "SELECT * FROM `teacher` WHERE 1 ORDER BY TeacherID ASC "
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            print(x)

        return render_template('AdminTasks/TeacherList.html', data=data)

    def trimString(self, s):
        new_str = ''
        for char in s:
            new_str = new_str + char
        return new_str
