import pymysql

def get_db_connection():
    connection = pymysql.connect(
        host='172.24.100.103',
        user='client',
        password='',
        database='data',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection