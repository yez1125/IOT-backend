from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from components.plc_connection import PLCConnection
from components.http_client import HTTPClient
from pymodbus.transaction import ModbusAsciiFramer
import threading
import time
import json
from datetime import datetime
from typing import Optional

# 建立 FastAPI 應用
app = FastAPI(
    title="AIoT 監控系統 PLC 本地端 Server",
    description="基於 FastAPI 的本地端 HTTP API Server，用於提供 PLC 感測器資料的即時存取",
    version="2.0.0"
)

# CORS 中間件設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允許所有來源，生產環境請限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 模型定義
class PLCControlRequest(BaseModel):
    action: str  # 'open' 或 'close'

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

# 全域變數儲存最新的感測器資料
latest_sensor_data = {
    'temperature': 0,
    'humidity': 0,
    'pm25': 0,
    'pm10': 0,
    'pm25_average': 0,
    'pm10_average': 0,
    'co2': 0,
    'tvoc': 0,
    'timestamp': None,
    'status': 'disconnected'
}

# PLC 連線設定
plc_info = {
    'framer': ModbusAsciiFramer,
    'port': "COM10", 
    "stopbits": 1,
    'bytesize': 7,
    'parity': "E",
    'baudrate': 9600
}

# 初始化 PLC 連線和 HTTP 客戶端
plc = None
db = None
http_client = None

def init_connections():
    """初始化 PLC、資料庫連線和 HTTP 客戶端"""
    global plc, db, http_client
    
    # 初始化 PLC 連線
    try:
        plc = PLCConnection(
            framer=plc_info['framer'], 
            port=plc_info['port'], 
            stopbits=plc_info['stopbits'], 
            bytesize=plc_info['bytesize'], 
            parity=plc_info['parity'], 
            baudrate=plc_info['baudrate']
        )
        plc.connect()
        print("✅ PLC 連線已建立")
    except Exception as e:
        print(f"⚠️  PLC 連線失敗: {e}")
        print("💡 請檢查 PLC 設備和串列埠設定")
        plc = None
    
    # 資料庫連線 (準備 MongoDB 整合)
    db = None
    print("💡 資料庫功能已移除，準備整合 MongoDB")
    
    # 初始化 HTTP 客戶端
    try:
        print("🔄 初始化 HTTP 客戶端...")
        http_client = HTTPClient(base_url="http://127.0.0.1:8787")
        
        # 測試連線
        if http_client.test_connection():
            print("✅ HTTP 客戶端已初始化並連線成功")
        else:
            print("⚠️  HTTP 客戶端已初始化但連線失敗")
    except Exception as e:
        print(f"❌ HTTP 客戶端初始化失敗: {e}")
        http_client = None
    
    # 設定系統狀態
    if plc and plc.connection:
        latest_sensor_data['status'] = 'connected'
        print("🎉 系統初始化完成")
    else:
        latest_sensor_data['status'] = 'plc_disconnected'
        print("⚠️  PLC 未連線，只有連線後才會收集資料")
        
    if not db:
        print("⚠️  資料庫未連線，資料將不會被儲存")
        print("💡 執行 'python setup_database.py' 來設置資料庫")

def data_collection_loop():
    """背景執行緒持續收集感測器資料"""
    global latest_sensor_data
    
    print("🔄 資料收集執行緒已啟動")
    
    while True:
        try:
            if plc and plc.connection:
                # 取得真實的感測器資料
                sensor_data = plc.get_data()
                if sensor_data:
                    temperature, humidity, pm25, pm10, pm25_avg, pm10_avg, co2, tvoc = sensor_data
                    
                    # 更新全域資料
                    latest_sensor_data.update({
                        'temperature': temperature,
                        'humidity': humidity,
                        'pm25': pm25,
                        'pm10': pm10,
                        'pm25_average': pm25_avg,
                        'pm10_average': pm10_avg,
                        'co2': co2,
                        'tvoc': tvoc,
                        'timestamp': datetime.now().isoformat(),
                        'status': 'connected'
                    })
                    
                    # 傳送資料到後端 API
                    if http_client:
                        try:
                            http_success = http_client.send_sensor_data(
                                temperature, humidity, pm25, pm10, pm25_avg, pm10_avg, co2, tvoc, 'connected'
                            )
                            if not http_success:
                                print("⚠️  HTTP 資料傳送失敗")
                        except Exception as e:
                            print(f"❌ HTTP 傳送錯誤: {e}")
                    
                    # 資料庫插入功能已移除，準備 MongoDB 整合
                            
            else:
                # PLC 未連線時不收集資料
                latest_sensor_data.update({
                    'status': 'plc_disconnected',
                    'timestamp': datetime.now().isoformat()
                })
                print("⚠️  PLC 未連線，等待連線...")
                time.sleep(5)  # PLC 未連線時每5秒檢查一次
                continue
                
        except Exception as e:
            print(f"❌ 資料收集錯誤: {e}")
            latest_sensor_data['status'] = 'error'
            
        time.sleep(1)  # PLC 連線時每秒更新一次

# API 路由定義

@app.get("/", response_model=dict)
async def index():
    """根路徑 - API 資訊"""
    return {
        'message': 'AIoT 監控系統 PLC 本地端 Server',
        'version': '2.0.0 (FastAPI)',
        'status': latest_sensor_data['status'],
        'docs_url': '/docs',  # Swagger UI
        'redoc_url': '/redoc',  # ReDoc
        'endpoints': {
            '/api/sensors/current': 'GET - 取得目前感測器資料',
            '/api/sensors/temperature': 'GET - 取得溫度資料',
            '/api/sensors/humidity': 'GET - 取得濕度資料',
            '/api/sensors/air_quality': 'GET - 取得空氣品質資料',
            '/api/plc/control': 'POST - 控制 PLC 輸出',
            '/api/status': 'GET - 取得系統狀態'
        }
    }

@app.get("/api/sensors/current", response_model=dict)
async def get_current_sensors():
    """取得目前所有感測器資料"""
    if latest_sensor_data['status'] == 'plc_disconnected':
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                'success': False,
                'data': {
                    'status': 'plc_disconnected',
                    'timestamp': latest_sensor_data['timestamp']
                },
                'message': 'PLC 未連線，無法取得感測器資料'
            }
        )
    
    return {
        'success': True,
        'data': latest_sensor_data,
        'message': '成功取得感測器資料'
    }

@app.get("/api/sensors/temperature", response_model=dict)
async def get_temperature():
    """取得溫度資料"""
    if latest_sensor_data['status'] == 'plc_disconnected':
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                'success': False,
                'message': 'PLC 未連線，無法取得溫度資料'
            }
        )
        
    return {
        'success': True,
        'data': {
            'temperature': latest_sensor_data['temperature'],
            'timestamp': latest_sensor_data['timestamp'],
            'unit': '°C'
        },
        'message': '成功取得溫度資料'
    }

@app.get("/api/sensors/humidity", response_model=dict)
async def get_humidity():
    """取得濕度資料"""
    if latest_sensor_data['status'] == 'plc_disconnected':
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                'success': False,
                'message': 'PLC 未連線，無法取得濕度資料'
            }
        )
        
    return {
        'success': True,
        'data': {
            'humidity': latest_sensor_data['humidity'],
            'timestamp': latest_sensor_data['timestamp'],
            'unit': '%'
        },
        'message': '成功取得濕度資料'
    }

@app.get("/api/sensors/air_quality", response_model=dict)
async def get_air_quality():
    """取得空氣品質資料"""
    if latest_sensor_data['status'] == 'plc_disconnected':
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                'success': False,
                'message': 'PLC 未連線，無法取得空氣品質資料'
            }
        )
        
    return {
        'success': True,
        'data': {
            'pm25': latest_sensor_data['pm25'],
            'pm10': latest_sensor_data['pm10'],
            'pm25_average': latest_sensor_data['pm25_average'],
            'pm10_average': latest_sensor_data['pm10_average'],
            'co2': latest_sensor_data['co2'],
            'tvoc': latest_sensor_data['tvoc'],
            'timestamp': latest_sensor_data['timestamp'],
            'units': {
                'pm25': 'μg/m³',
                'pm10': 'μg/m³',
                'co2': 'ppm',
                'tvoc': 'mg/m³'
            }
        },
        'message': '成功取得空氣品質資料'
    }

@app.post("/api/plc/control", response_model=dict)
async def control_plc(request: PLCControlRequest):
    """控制 PLC 輸出"""
    try:
        action = request.action
        
        if not plc or not plc.connection:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail={
                    'success': False,
                    'message': 'PLC 未連線'
                }
            )
            
        if action == 'open':
            plc.open()
            message = 'PLC 輸出已開啟'
        elif action == 'close':
            plc.close()
            message = 'PLC 輸出已關閉'
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    'success': False,
                    'message': '無效的操作，請使用 "open" 或 "close"'
                }
            )
            
        return {
            'success': True,
            'message': message,
            'action': action
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                'success': False,
                'message': f'控制 PLC 時發生錯誤: {str(e)}'
            }
        )

@app.get("/api/status", response_model=dict)
async def get_status():
    """取得系統狀態"""
    
    # 資料庫狀態 (準備 MongoDB 整合)
    db_status = 'not_configured'
    db_type = 'mongodb_pending'
    db_info = {'message': '等待 MongoDB 整合'}
    
    # HTTP 客戶端狀態
    http_status = 'not_initialized'
    http_info = {'message': 'HTTP 客戶端未初始化'}
    if http_client:
        http_info = http_client.get_status()
        http_status = 'connected' if http_info['connected'] else 'disconnected'
    
    return {
        'success': True,
        'data': {
            'plc_status': latest_sensor_data['status'],
            'plc_connected': plc is not None and hasattr(plc, 'connection') and plc.connection,
            'database_status': db_status,
            'database_type': db_type,
            'database_info': db_info,
            'http_status': http_status,
            'http_info': http_info,
            'last_update': latest_sensor_data['timestamp'],
            'server_time': datetime.now().isoformat()
        },
        'message': '成功取得系統狀態'
    }

# 全域例外處理器
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """404 錯誤處理"""
    return {
        'success': False,
        'message': '找不到請求的資源',
        'error': '404 Not Found'
    }

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """500 錯誤處理"""
    return {
        'success': False,
        'message': '伺服器內部錯誤',
        'error': '500 Internal Server Error'
    }

# 啟動事件
@app.on_event("startup")
async def startup_event():
    """應用啟動時執行"""
    print("正在啟動 AIoT 監控系統 PLC 本地端 Server (FastAPI)...")
    
    # 初始化連線
    init_connections()
    
    # 啟動背景資料收集執行緒
    data_thread = threading.Thread(target=data_collection_loop, daemon=True)
    data_thread.start()
    
    print("伺服器正在啟動...")
    print("API 文件可在以下位址查看:")
    print("  Swagger UI: http://localhost:8000/docs")
    print("  ReDoc: http://localhost:8000/redoc")

# 關閉事件
@app.on_event("shutdown")
async def shutdown_event():
    """應用關閉時執行"""
    print("正在關閉 AIoT 監控系統...")
    
    # 關閉 PLC 連線
    if plc and plc.connection:
        try:
            plc.close()
            print("✅ PLC 連線已關閉")
        except:
            pass
    
    # 關閉 HTTP 客戶端
    if http_client:
        try:
            http_client.close()
            print("✅ HTTP 客戶端已關閉")
        except:
            pass
    
    # 資料庫關閉 (MongoDB 整合後會啟用)
    print("💡 資料庫功能已移除")
    
    print("👋 伺服器已停止")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000) 