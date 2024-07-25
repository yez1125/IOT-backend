from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, desc
from flask_cors import CORS

import os
from dotenv import load_dotenv

# Load the config
# load_dotenv()
# endpoint = os.getenv('ENDPOINT')
# user = os.getenv('USER')
# password = os.getenv('PASSWORD')
# database = os.getenv('DATABASE')


user = 'root'
password = 'root'
endpoint = 'localhost'
database = 'plc'

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://{}:{}@{}:3306/{}'.format(user, password, endpoint, database)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 
db = SQLAlchemy(app)

# 建立初始化database model
class data(db.Model):
    __tablename__ = 'data'
    _id = db.Column('id', db.INTEGER, primary_key=True)
    temperature = db.Column('temperature', db.FLOAT)
    humidity = db.Column('humidity', db.FLOAT)
    # tvoc = db.Column('TVOC', db.FLOAT)
    # co2 = db.Column('CO2', db.FLOAT)
    # pm2_5 = db.Column('pm25', db.Float)
    time = db.Column('time', db.TIMESTAMP, server_default = text('CURRENT_TIMESTAMP'))
    status = db.Column('status', db.BOOLEAN, default = False) # 開關機狀態

    def __init__(self, temperature, humidity, status):
        self.temperature = temperature
        self.humidity = humidity
        # self.tvoc = tvoc
        # self.co2 = co2
        # self.pm2_5 = pm2_5
        self.status = status


# Restful API
@app.route('/api/1min_data', methods = ['GET'])
def get_1min_data():
    results = db.session.query(data.temperature, data.humidity, data.time)\
                        .order_by(desc(data.time))\
                        .limit(60)\
                        .all()
    
    result_list = [{'temperature': temp, 'humidity': humid, 'time': time} for temp, humid, time in results]


    return jsonify(result_list)

# 開關ABox
@app.route('/api/toggle_status', methods=['GET'])
def toggle_status ():
    latest_record = db.session.query(data).order_by(desc(data._id)).first()

    new_record= data(temperature=latest_record.temperature, humidity=latest_record.humidity, status= not latest_record.status)
    db.session.add(new_record)
    db.session.commit()
    return jsonify({'status':new_record.status})

# 獲取ABox目前狀態
@app.route('/api/get_status', methods=['GET'])
def get_status():
    record = db.session.query(data).order_by(desc(data._id)).first()
    return jsonify({'status': record.status})

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=3002)
