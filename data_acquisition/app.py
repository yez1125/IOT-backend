from pymodbus.client.serial import ModbusSerialClient
from pymodbus.transaction import ModbusAsciiFramer
from pymodbus.exceptions import ModbusException
import pymysql
import time

client = ModbusSerialClient(framer=ModbusAsciiFramer, port = "COM7", stopbits = 1, bytesize = 7, parity = "E", baudrate = 9600)
connection = client.connect()

# MySQL建立聯接
try:
    database = pymysql.connect(host='localhost', port = 3306, user='root', passwd='root', charset='utf8', db='plc', autocommit=True)
    print('資料庫連接成功')
except Exception as e:
    print('Error: ' + str(e))


if connection:
    print('PLC連接成功')

    query_template = "INSERT INTO data (temperature, humidity) VALUES ({}, {})"
    i = 0
    # 抓取PLC資料
    try:
        while True:
            temperature = client.read_holding_registers(address=4120, count=4, slave=1).registers[0] * 0.1
            humidity = client.read_holding_registers(address=4118, count=1, slave=1).registers[0] * 0.1
            
            #寫入資料
            with database.cursor() as cursor:
                query = query_template.format(str(temperature), str(humidity))
                cursor.execute(query)
            
            print("溫度：" + str(round(temperature, 2)))
            print("濕度：" + str(round(humidity, 2)))

            i+=1
            time.sleep(1)

    except ModbusException as e:
        print('Error: ' + e)

    finally:
        client.close()
        print("PLC關閉連接")

# 關閉資料庫連接
try:
    database.close()
    print("資料庫已關閉連接")
except Exception as e:
    print("Error: " + str(e))
    