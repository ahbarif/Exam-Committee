from flask import Flask, flash, json, jsonify, make_response, render_template, request, redirect, url_for, session, \
    abort
from flaskext.mysql import MySQL

import pymysql
import smtplib
from email.mime import multipart, text as mailText


class Teacher:
    mysql = MySQL()

    def __init__(self, mysql, session):
        self.mysql = mysql
        self.session = session

    def showDashBoard(self):
        username = session['username']
        teacherId = self.getTeacherID(username)

        chairman = self.getMember("ChairmanID", teacherId)
        generalMember1 = self.getMember("GeneralMember1", teacherId)
        generalMember2 = self.getMember("GeneralMember2", teacherId)
        external = self.getMember("ExternalMember", teacherId)

        return render_template('TeacherTasks/dashboard.html', chairman=chairman, g1=generalMember1, g2=generalMember2,
                               external=external)

    def getTeacherID(self, username):
        sqlString = "Select TeacherID from teacher where Username = " + "'" + username + "'"
        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sqlString)
        data = cursor.fetchone()
        return data['TeacherID']

    def getMember(self, type, id):
        qtype = "'" + id + "'"
        cursor = self.mysql.connect().cursor()
        sqlString = "SELECT CommitteeName from committee where " + type + " = " + qtype
        cursor.execute(sqlString)
        data = cursor.fetchall()
        info = ""

        for x in data:
            info = self.trimString(x)

        return info

    def trimString(self, s):
        new_str = ''
        for char in s:
            new_str = new_str + char
        return new_str


    def show_committee_details(self, result):
        name = "'" + result['committeeName'] + "'"

        sqlString = "Select * from committee where CommitteeName = " + name
        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sqlString)
        data = cursor.fetchone()

        print(data)

        committeeInfo = []

        committeeInfo.append(data['CommitteeName'])
        committeeInfo.append(self.get_teacher_by_id(data['ChairmanID']))
        committeeInfo.append(self.get_teacher_by_id(data['GeneralMember1']))
        committeeInfo.append(self.get_teacher_by_id(data['GeneralMember2']))
        committeeInfo.append(self.get_teacher_by_id(data['ExternalMember']))
        print(committeeInfo)

        return render_template('TeacherTasks/committeehome.html', info=committeeInfo)


    def get_teacher_by_id(self, id):
        sqlString = "Select Name from teacher where TeacherID = " + "'" + id + "'"
        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sqlString)
        data = cursor.fetchone()
        return data['Name']

    def show_profile(self):
        username = session['username']
        teacherId = self.getTeacherID(username)

        con = self.mysql.connect()
        cursor = con.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "Select * From teacher t INNER JOIN dept d on t.DeptID = d.ID where TeacherID = " + "'" + teacherId + "'")
        data = cursor.fetchone()

        return render_template('TeacherTasks/profile.html', data=data)

    def update_profile(self, result):

        username = session['username']
        teacherId = self.getTeacherID(username)

        sqlQuery = "Update teacher Set " + self.update_query_values("Name", result['name'].strip())
        sqlQuery += ", " + self.update_query_values("EmailAddr", result['email'].strip())
        sqlQuery += ", " + self.update_query_values("Phone", result['phone'].strip())
        sqlQuery += ", " + self.update_query_values("Address", result['address'].strip())
        sqlQuery += ", " + self.update_query_values("BankAccName", result['accname'].strip())
        sqlQuery += ", " + self.update_query_values("BankAccNumber", result['accno'].strip())
        sqlQuery += ", " + self.update_query_values("BankName", result['bank'].strip())
        sqlQuery += " where Username = " + "'" + result['username'] + "'"

        print(sqlQuery)

        con = self.mysql.connect()
        cursor = con.cursor()
        cursor.execute(sqlQuery)
        con.commit()

        con = self.mysql.connect()
        cursor = con.cursor(pymysql.cursors.DictCursor)
        cursor.execute(
            "Select * From teacher t INNER JOIN dept d on t.DeptID = d.ID where TeacherID = " + "'" + teacherId + "'")
        data = cursor.fetchone()

        return render_template('TeacherTasks/profile.html', data=data)

    def update_query_values(self, type, value):
        return type + " = '" + value + "'"


    def question_setting(self, result):

        if 'committeeName' in result:



            committeeId = self.get_CommitteeId(result['committeeName'])
            year = self.get_CommitteeYear(result['committeeName'])

            print('name = ' + result['committeeName'])
            print(year)

            subjects = self.getCourseList(year)
            exams = self.getExamList(committeeId)
            teachers = self.getTeacherList()

            return render_template('TeacherTasks/questionsetting.html', subjetcs=subjects, exams=exams,
                                   teachers=teachers)

        else:
            courseId = result['courses'].split(' : ')[0]

            con = self.mysql.connect()
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

            con = self.mysql.connect()
            cursor = con.cursor()
            cursor.execute(sqlInsert)
            con.commit()

            return redirect('/teacher', 302)

    def get_CommitteeId(self, Name):
        sqlString = "Select CommitteeId from committee where CommitteeName = " + "'" + Name + "'"
        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sqlString)
        data = cursor.fetchone()
        return data['CommitteeId']

    def get_CommitteeYear(self, Name):
        sqlString = "Select AcademicYear from committee where CommitteeName = " + "'" + Name + "'"
        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        print("Year query = " + sqlString)
        cursor.execute(sqlString)
        data = cursor.fetchone()
        return data['AcademicYear']

    def getCourseList(self, year):
        courseNames = []
        courseIds = []
        subjects = []

        cursor = self.mysql.connect().cursor()
        sqlString = "SELECT Title from courses where Year = " + "'" + str(year) + "'"
        print("Course query = " + sqlString)
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            courseNames.append(self.trimString(x))

        sqlString = "SELECT CourseID from courses where Year = " + "'" + str(year) + "'"
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            courseIds.append(self.trimString(x))

        for i in range(0, len(courseIds)):
            subjects.append(courseIds[i] + " : " + courseNames[i])

        return subjects

    def getExamList(self, committeeId):
        exams = []

        cursor = self.mysql.connect().cursor()
        sqlString = "SELECT DISTINCT ExamName from exam where CommitteeID = " + "'" + committeeId + "'"
        print(sqlString)
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            exams.append(self.trimString(x))

        return exams

    def getTeacherList(self):
        teachers = []

        cursor = self.mysql.connect().cursor()
        sqlString = "SELECT Name from teacher"
        cursor.execute(sqlString)
        data = cursor.fetchall()

        for x in data:
            teachers.append(self.trimString(x))

        return teachers

    def set_question_status(self, result):

            if 'committeeName' in result:
                committeeName = result['committeeName']
                committeeId = self.get_CommitteeId(committeeName)
                sqlString = "SELECT Type, CourseID, Qsetter1, Qsetter2, Status, q.CommitteeID FROM exam e INNER JOIN Qsetting q on q.ExamID = e.ID WHERE q.CommitteeID = " + "'" + committeeId + "'"
                cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
                cursor.execute(sqlString)
                data = cursor.fetchall()

                for row in data:
                    print(row)

                return render_template('TeacherTasks/questionstatus.html', data=data)

            elif 'committeeInfo' in result:
                self.create_mail(result['recipient'], result['rem_course'], result['msg'])

                sqlString = "SELECT Type, CourseID, Qsetter1, Qsetter2, Status, q.CommitteeID FROM exam e INNER JOIN Qsetting q on q.ExamID = e.ID WHERE q.CommitteeID = " + "'" + \
                            result['committeeInfo'] + "'"
                cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
                cursor.execute(sqlString)
                data = cursor.fetchall()

                return render_template('TeacherTasks/questionstatus.html', data=data)


            else:
                print(result)
                print("Update query was run")
                status = 0
                committeeId = result['committeeId']
                courseId = result['courseId']

                if 'status1' in result and 'status2' in result:
                    status = 3
                elif 'status1' in result:
                    status = 1
                elif 'status2' in result:
                    status = 2
                else:
                    status = 0

                self.update_question_status(courseId.strip(), str(status))

                sqlString = "SELECT Type, CourseID, Qsetter1, Qsetter2, Status, q.CommitteeID FROM exam e INNER JOIN Qsetting q on q.ExamID = e.ID WHERE q.CommitteeID = " + "'" + committeeId + "'"
                cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
                cursor.execute(sqlString)
                data = cursor.fetchall()

                return render_template('TeacherTasks/questionstatus.html', data=data)

    def update_question_status(self, courseId, status):
        sqlString = "Select ID from exam where CourseID = " + "'" + courseId + "'"
        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sqlString)
        data = cursor.fetchone()

        examId = data['ID']

        print(sqlString)
        print("ID = " + str(examId))

        sqlString = "Update Qsetting set STATUS = " + status + " where ExamID = " + "'" + str(examId) + "'"
        print("UPDATE = " + sqlString)

        con = self.mysql.connect()
        cursor = con.cursor()
        cursor.execute(sqlString)
        con.commit()

    def create_mail(self, name, course, msg):

        sqlString = "Select EmailAddr from teacher where Name = " + "'" + name.strip() + "'"
        cursor = self.mysql.connect().cursor(pymysql.cursors.DictCursor)
        cursor.execute(sqlString)
        data = cursor.fetchone()
        toAddr = data['EmailAddr']

        msg_body = "You have a question setting task pending \n\n" \
                   + "Course: " + course.strip() + "\n\n"

        msg_body += msg

        self.send_mail(msg_body, toAddr)

    def send_mail(self, msg_body, toaddr):

        fromaddr = "2015-216-797@student.cse.du.ac.bd"
        msg = multipart.MIMEMultipart()
        msg['From'] = "Exam Committee"
        # msg['To'] = toaddr
        toaddr = 'hasibulhq.moon@gmail.com'
        msg['Subject'] = "Question Setting Task Pending"

        msg.attach(mailText.MIMEText(msg_body, 'plain'))
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("2015-216-797@student.cse.du.ac.bd", "01521331720")
        text = msg.as_string()

        print(text)
        server.sendmail(fromaddr, toaddr, text)
        server.quit()
