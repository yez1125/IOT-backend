from pymodbus.client.serial import ModbusSerialClient
from pymodbus.transaction import ModbusAsciiFramer
from pymodbus.exceptions import ModbusException

class PLCConnection:
    def __init__(self, framer=ModbusAsciiFramer, port = "COM7", stopbits = 1, bytesize = 7, parity = "E", baudrate = 9600):
        self.framer = framer
        self.port = port
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.parity = parity
        self.baudrate = baudrate
        self.client = None
        self.connection = None
    
    def connect(self):
        self.client = ModbusSerialClient(framer= self.framer, port = self.port, stopbits = self.stopbits, bytesize = self.bytesize, parity = self.parity, baudrate = self.baudrate)
        self.connection = self.client.connect()
        print('PLC已連接')

    def get_data(self):
        if self.connection:
        # 每秒抓取PLC資料，並傳送到database
            try:
                temperature = self.client.read_holding_registers(address=4120, count=4, slave=1).registers[0] * 0.1
                humidity = self.client.read_holding_registers(address=4118, count=1, slave=1).registers[0] * 0.1    
                
            except ModbusException as e:
                print('Error: ' + e)

            print("溫度：" + str(round(temperature, 2)))
            print("濕度：" + str(round(humidity, 2)))

            return temperature, humidity

    def change_output(self, status):
        # 如果status改變，則將Y0的狀態改變
        self.client.write_coil(address=1280, value=status, slave=1)

    def close(self):
        self.client.close()
        print("PLC關閉連接")