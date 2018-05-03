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

    def trimString(self, s):
        new_str = ''
        for char in s:
            new_str = new_str + char
        return new_str
