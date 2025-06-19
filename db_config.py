import pymysql

def conectar():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='escola',
        port=3306,
    )