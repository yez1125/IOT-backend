from components.db_connection import MySQL
from components.plc_connection import PLCConnection
from pymodbus.transaction import ModbusAsciiFramer
import time

# 測試用
import random

db_info = {
    'host': 'localhost', 
    'port': 3306,
    'user':'root', 
    'passwd':'root', 
    'db':'plc'
}

plc_info = {
    'framer': ModbusAsciiFramer,
    'port' : "COM5", 
    "stopbits": 1,
    'bytesize': 7,
    'parity': "E",
    'baudrate': 9600
}

def main():
    db = MySQL(host=db_info['host'],port=db_info['port'], user=db_info['user'], passwd=db_info['passwd'], db=db_info['db'])
    plc = PLCConnection(framer= plc_info['framer'], port = plc_info['port'], stopbits = plc_info['stopbits'], bytesize = plc_info['bytesize'], parity = plc_info['parity'], baudrate = plc_info['baudrate'])

    # 資料庫連線
    db.connect()
    # PLC連線
    plc.connect()

    while True:
        # 獲取PLC資料
        temperature, humidity = plc.get_data()

        # 測試用
        tvoc = random.randint(0, 56) * 0.01
        co2 = random.randint(300, 1000)
        pm25 = random.randint(0, 35)
        
        # 讀取db的status
        status = db.get_status()

        # 若db的status改變，則plc的output也改變的跟status一樣
        if db.is_status_changed():
            plc.change_output(status)

        # 將資料傳入資料庫
        db.add(temperature, humidity, tvoc, co2, pm25, status)

        time.sleep(1)

    # 關閉PLC、資料庫連線
    db.close()
    plc.close()

if __name__ == '__main__':
    main()

        