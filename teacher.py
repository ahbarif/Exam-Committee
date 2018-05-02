from flask import Flask,flash,json, jsonify, make_response, render_template,request,redirect, url_for, session, abort
from flaskext.mysql import MySQL
from json import dump
import gc
import pymysql


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

