import sqlite3
from datetime import datetime
from sqlite3 import Error

import os.path


class DataBase:

    def __init__(self, db_file="FarmDatabase.sqlite"):

        self.db_file = db_file
        self.creating_new_db = False

        # check if database exists, if not create new, empty with table
        if not os.path.isfile('FarmDatabase.sqlite'):
            self.creating_new_db = True
            self.createConnection()

    def update(self, sqlUpdate, args):

        conn = self.createConnection()
        if conn is not None:

            self.execSql(conn, sqlUpdate, args)
        else:
            print("Error! cannot create the database connection.")

    def sqlSelectJson(self, farmId):
        sql_select = """SELECT farmId, gold, productionLimit, timeOfharvest, timeOfsowing, 
                       costOfsowing, updateCost,growTime, isHarvested FROM Farms  where farmId= ?;"""
        conn = self.createConnection()
        if conn is not None:

            Sql_result = self.execSql(conn, sql_select, farmId)

            FarmDataJson = {
                "farmId": Sql_result[0][0],
                "gold": Sql_result[0][1],
                "productionLimit": Sql_result[0][2],
                "timeOfHarvest": Sql_result[0][3],
                "timeOfSowing": Sql_result[0][4],
                "costOfSowing": Sql_result[0][5],
                "updateCost": Sql_result[0][6],
                "growTime": Sql_result[0][7],
                "isHarvested": Sql_result[0][8],
            }
            return FarmDataJson
        else:
            print("Error! cannot create the database connection.")

    # method that create Database with table Cards or just create connection
    def createConnection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)

            print(sqlite3.version)

            if self.creating_new_db:
                sql_create_table = """
                CREATE TABLE IF NOT EXISTS Farms (
                farmId integer PRIMARY KEY,
                gold integer,
                productionLimit integer,
                timeOfharvest time,
                timeOfsowing time,
                costOfsowing integer,
                updateCost integer,
                growTime integer,
                isHarvested integer
                );
                """
                now = datetime.now()
                now.strftime("%d/%m/%Y %H:%M:%S")
                sql_insert_init = """INSERT INTO Farms (farmId,gold ,productionLimit,costOfsowing,updateCost,growTime,isHarvested,timeOfharvest,timeOfsowing)
                                             VALUES(?,?,?,?,?,?,?,?,?);"""
                insert_values_tuble= (1,30,20,10,10,10,1,now.strftime("%d/%m/%Y %H:%M:%S"),now.strftime("%d/%m/%Y %H:%M:%S"))


                self.creating_new_db = False

                if conn is not None:

                    self.execSql(conn, sql_create_table)
                    self.execSql(conn, sql_insert_init,insert_values_tuble)
                else:
                    print("Error! cannot create the database connection.")
        except Error as e:
            print(e)

        return conn

    # that method "takes" sql code and execute it
    @staticmethod
    def execSql(conn, sqlcode, *args):
        try:
            c = conn.cursor()
            c.execute(sqlcode, *args)
            conn.commit()
            rows = c.fetchall()
            return rows

        except Error as e:
            print(e)



DataBase()