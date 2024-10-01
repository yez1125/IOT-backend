from components.db_connection import MySQL
import random
import time

db_info = {
    'host': '172.24.100.103', 
    'port': 3306,
    'user':'dcde22345', 
    'passwd':'Zxcn-1357', 
    'db':'data'
}


def main():
    db = MySQL(host=db_info['host'],port=db_info['port'], user=db_info['user'], passwd=db_info['passwd'], db=db_info['db'])
    # 資料庫連線
    db.connect()
    
    # # PLC連線
    # while True:
    #     # 獲取PLC資料
    #     temperature = random.uniform(25, 30)
    #     humidity = random.uniform(40, 60)
    #     tvoc = random.randint(0, 56) * 0.01
    #     co2 = random.randint(300, 1000)
    #     pm25 = random.randint(0, 35)
        
    #     # 讀取db的status
    #     status = db.get_status()

    #     # 若db的status改變，則plc的output也改變的跟status一樣
    #     # if db.is_status_changed():
    #     #     print("changed!")

    #     # 將資料傳入資料庫
    #     db.add(temperature, humidity, tvoc, co2, pm25, status)

    #     time.sleep(1)

    # 關閉PLC、資料庫連線
    db.close()
    # plc.close()

if __name__ == '__main__':
    main()

        