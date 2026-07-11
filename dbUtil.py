import os,sqlite3
from openpyxl import load_workbook
from datetime import datetime

codeList = []
InBoundList = []
OutBoundList = []
dbpath = './VolumeCorrectionValue.db'
datalist=[(1.38, 1.7, 1.9, 2.3, 2.4, 3.6, 3.3, None),
          (1.38, 1.7, 1.9, 2.2, 2.3, 3.4, 3.2, None),
          (1.36, 1.6, 1.8, 2.2, 2.2, 3.2, 3.0, None),
          (1.33, 1.6, 1.8, 2.1, 2.2, 3.0, 2.8, None),
          (1.29, 1.5, 1.7, 2.0, 2.1, 2.7, 2.6, None),\
          \
          (1.23, 1.5, 1.6, 1.9, 2.0, 2.5, 2.4, 10.8),
          (1.17, 1.4, 1.5, 1.8, 1.8, 2.3, 2.2, 9.6),
          (1.10, 1.3, 1.4, 1.6, 1.7, 2.0, 2.0, 8.5),
          (0.99, 1.1, 1.2, 1.4, 1.5, 1.8, 1.8, 7.4),
          (0.88, 1.0, 1.1, 1.2, 1.3, 1.6, 1.5, 6.5),\
          \
          (0.77, 0.9, 0.9, 1.0, 1.1, 1.3, 1.3, 5.2),
          (0.64, 0.7, 0.8, 0.8, 0.9, 1.1, 1.1, 4.2),
          (0.50, 0.6, 0.6, 0.6, 0.7, 0.8, 0.8, 3.1),
          (0.34, 0.4, 0.4, 0.4, 0.5, 0.6, 0.6, 2.1),
          (0.18, 0.2, 0.2, 0.2, 0.2, 0.3, 0.3, 1.0),\
          \
          (0.00, 0.00, 0.00, 0.0, 0.00, 0.00, 0.0, 0.0),
          (-0.18, -0.2, -0.2, -0.2, -0.2, -0.3, -0.3, -1.1),
          (-0.38, -0.4, -0.4, -0.5, -0.5, -0.6, -0.6, -2.2),
          (-0.58, -0.6, -0.7, -0.7, -0.8, -0.9, -0.9, -3.3),
          (-0.80, -0.9, -0.9, -1.0, -1.0, -1.2, -1.0, -4.2),\
          \
          (-1.03, -1.1, -1.1, -1.2, -1.3, -1.5, -1.5, -5.3),
          (-1.26, -1.4, -1.4, -1.4, -1.5, -1.8, -1.8, -6.4),
          (-1.51, -1.7, -1.7, -1.7, -1.8, -2.1, -2.1, -7.5),
          (-1.76, -2.0, -2.0, -2.0, -2.1, -2.4, -2.4, -8.5),
          (-2.01, -2.3, -2.3, -2.3, -2.4, -2.8, -2.8, -9.6),\
          \
          (-2.30, -2.5, -2.5, -2.6, -2.8, -3.2, -3.1, -10.6),
          (-2.58, -2.7, -2.7, -2.9, -3.1, -3.5, None, -11.6),
          (-2.86, -3.0, -3.0, -3.2, -3.4, -3.9, None, -12.6),
          (-3.04, -3.2, -3.3, -3.5, -3.7, -4.2, None, -13.7),
          (-3.47, -3.7, -3.6, -3.8, -4.1, -4.6, None, -14.8),\
          \
          (-3.78, -4.0, -4.0, -4.1, -4.4, -5.0, None, -16.0),
          (-4.10, -4.3, -4.3, -4.4, -4.7, -5.3, None, -17.0)]

class dbtool():
    def __init__(self,path):
        self.conn = sqlite3.connect(path)
        #Software information
        self.cur = self.conn.cursor()
        print("连接成功")

    # 保存
    def __del__(self): 
            #5. Submit transaction
            self.conn.commit() 
            self.cur.close()
            #6. Close the database connection
            self.conn.close() 
    
    # 执行
    def dbexectue(self, txt): 
        self.cur.execute(txt)
    #Insert multiple rows of data
    def InsertList(self, txt, datalist): 
        self.cur.executemany(txt, datalist)
        # "INSERT INTO t_user(id, userName, password) VALUES(?,?,?)"
    #Set log configuration
    def fetchall(self): 
        #-- The select statement returns content, which needs to be obtained through fetchall(). The returned content is a list, and the list element is a single record (a single record is a tuple, and the elements are each value)
        return self.cur.fetchall()
    #Set log configuration
    def read_Alldb(self, txt): 
        self.cur.execute(txt)
        #-- The select statement returns content, which needs to be obtained through fetchall(). The returned content is a list, and the list element is a single record (a single record is a tuple, and the elements are each value)
        return self.cur.fetchall()
    
if __name__ == "__main__":
    
    #Create db database
    try:
        os.remove(dbpath)
    except FileNotFoundError:
        pass
    dbt = dbtool(dbpath)
    # 班级表
    dbt.dbexectue("""CREATE TABLE VolumeCorrectionValue
                  (temperature INTEGER PRIMARY KEY AUTOINCREMENT,
                  water__0_05 FLOAT,
                  water__0_1__0_2 FLOAT,
                  HCl__0_5 FLOAT,
                  HCl__1 FLOAT,
                  SulfuricAcid__0_5__SodiumHydroxide__0_5 FLOAT,
                  SulfuricAcid__1__SodiumHydroxide__1 FLOAT,
                  SodiumCarbonate FLOAT,
                  PotassiumHydroxide_ethanol__0_1 FLOAT)""")
    

    dbt.dbexectue("INSERT INTO VolumeCorrectionValue(temperature,water__0_05) VALUES(4,NULL)")
    dbt.dbexectue("DELETE FROM VolumeCorrectionValue WHERE temperature = 4;")
    
    dbt.InsertList("INSERT INTO VolumeCorrectionValue(water__0_05, water__0_1__0_2, HCl__0_5, HCl__1, SulfuricAcid__0_5__SodiumHydroxide__0_5,\
                   SulfuricAcid__1__SodiumHydroxide__1, SodiumCarbonate, PotassiumHydroxide_ethanol__0_1) VALUES(?,?,?,?,?,?,?,?)", 
                   datalist)


    # 学生表
    # dbt.dbexectue("""CREATE TABLE student
    #               (student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #               student_name VARCHAR(255) NOT NULL,
    #               student_number VARCHAR(255) NOT NULL,
    #               gender INTEGER NOT NULL,
    #               class_id INTEGER NOT NULL,
    #               chinese_score FLOAT,
    #               math_score FLOAT,
    #               englist_score FLOAT,
    #               FOREIGN KEY (class_id) REFERENCES classes(class_id)
    #               )""")
    # 老师表
    # dbt.dbexectue("""CREATE TABLE user
    #               (user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #               username VARCHAR(255) NOT NULL,
    #               password VARCHAR(255) NOT NULL,
    #               nickname VARCHAR(255),
    #               user_role INTEGER,
    #               class_id VARCHAR(255)
    #               )""")