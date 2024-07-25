import pymysql

class MySQL:
    def __init__(self, host='localhost', port=3306, user='root', passwd='root', db='plc'):
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.db = db
        self.database = None
        self.last_status = None
        self.now_status = None

    def connect(self):
        try:
            self.database = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                passwd=self.passwd,
                charset='utf8',
                db=self.db,
                autocommit=True
            )
            print('資料庫連接成功')
        except Exception as e:
            print('Error: ' + str(e))

    def close(self):
        try:
            self.database.close()
            print("資料庫已關閉連接")
        except Exception as e:
            print("Error: " + str(e))

    def add(self, temperature, humidity, status):
        query_template = "INSERT INTO data (temperature, humidity, status) VALUES ({}, {}, {})"
        
        with self.database.cursor() as cursor:
            query = query_template.format(str(temperature), str(humidity), str(status))
            cursor.execute(query)

    def is_status_changed(self):
        new_record = None
        last_record = None
        with self.database.cursor() as cursor:
            query = "SELECT * FROM data ORDER BY time DESC LIMIT 2"
            cursor.execute(query)
            result = cursor.fetchall()
            new_record = result[0]
            last_record = result [1]

        new_status = new_record[4]
        last_status = last_record[4]
        
        return (new_status != last_status)
    
    def get_data(self):
        with self.database.cursor() as cursor:
            query = "SELECT * FROM data ORDER BY time DESC LIMIT 1"
            cursor.execute(query)
            result = cursor.fetchall()
            record = result[0]
            return record
