

class LoginHelper:
    def __init__(self,mysql):
        self.mysql=mysql

    def loginFunction(self, query, session, gc ):

        error =""
        try:

            tableName = ""

            if query[2] == "Admin":
                tableName = "admin"
            if query[2] == "Teacher":
                tableName = "teacher"
            if query[2] == "Staff":
                tableName = "staff"

            # print(tableName);

            cursor = self.mysql.connect().cursor()
            data = cursor.execute("SELECT * from " + tableName + " where Username= %s and Password= %s",
                                  (query[0], query[1],))

            #print(data)
            userInfo = cursor.fetchone()

            if userInfo is None:
                print("No result found!")

            if data == 1:
                session['logged_in'] = True
                session['username'] = query[0]
                session['userFullName'] = userInfo[0]
                session['userType'] = query[2]
                gc.collect()
                print(query[2] + ": " + userInfo[0])
                return "OK_" + query[2]
            else:
                print(query[2] + "_NotFound")
                return query[2] + "_NotFound"


        except Exception as e:
            print(str(e))
            error = "Invalid Email/Pass. Authentication Failed."
            return error
