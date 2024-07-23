import pymysql
import random

try:
    database = pymysql.connect(
        host='iot-database.cbqiacqs0rw1.ap-northeast-1.rds.amazonaws.com',
        port = 3306,
        user='admin',
        passwd='Zxcn-1357',
        charset='utf8',
        database='iot-database',
        autocommit=True)
    print('資料庫連接成功')

    query_template = "INSERT INTO data (temperature, humidity, TVOC, CO2, PM25, status) VALUES ({}, {}, {}, {}, {}, {})"

    for i in range(200):
        t = round(random.uniform(25., 30.))
        h = round(random.uniform(40., 60.))
        tvoc = round(random.uniform(0., 1.))
        co2 = random.randint(300, 1000)
        pm2_5 = round(random.uniform(0., 50.))
        status = bool(random.randint(0,2))
        
        with database.cursor() as cursor:
            query = query_template.format(str(t), str(h), str(tvoc), str(co2), str(pm2_5), str(status))
            cursor.execute(query)
    print('OK!')

    database.close()
    print('關閉')

except Exception as e:
    print('Error: ' + str(e))