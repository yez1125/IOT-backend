from fastapi import FastAPI,HTTPException, Depends,WebSocket,Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
import os
import io
from pydantic import BaseModel
import bcrypt
from token_utils import create_access_token,decode_access_token
from depend import get_current_user
from datetime import datetime
import json
from bson import ObjectId
from starlette.websockets import WebSocketDisconnect
from dateutil.relativedelta import relativedelta
import openpyxl
from typing import Dict




#定義物件
class user_info(BaseModel):
    account:str
    password:str
    func_permissions:list[str]
    company:str

class login_info(BaseModel):
    account:str
    password:str

class modified_info(BaseModel):
    account:str
    func_permissions:list[str]

class user_data(BaseModel):
    account:str
    func_permissions:list[str]
    company:str

class sensor_data(BaseModel):
    machine:str
    timestamp:str
    value:dict

class abox_info(BaseModel):
    CO:float
    CO2:float
    toxic_gas:float
    temperature:float
    humidity:float

class fan_info(BaseModel):
    rpm:int

class fridge_info(BaseModel):
    temperature:float  

class sensor_info(BaseModel):
    name:str
    description:str
    company:str
    lab:str

class lab_data(BaseModel):
    name:str
    description:str
    sensors:list[sensor_info]
    company:str

class lab_info(BaseModel):
    id:str
    name:str
    description:str
    sensors:list[sensor_info]
    company:str    

class delete_lab_info(BaseModel):
    id:str

class delete_user_info(BaseModel):
    account:str
  
app = FastAPI()

#CORS
origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#連接DB
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
db = client[os.getenv("DATABASE_URL")]
MACHINE_KEYS: Dict[str, str] = json.loads(os.getenv("MACHINE_KEYS", "{}"))

#選擇資料表
user_collection = db["user"]
lab_collection = db["lab"]
collection = db["plc"]

func_auth = ["create_user","modify_user","get_users","modify_lab","get_labs","view_data","control_machine","change_password"]


@app.on_event("startup")
async def ensure_superuser():
    superuser = await user_collection.find_one()
    if not superuser:
        result = {
            "account": os.getenv("SUPERUSER_ACCOUNT"),
            "password": bcrypt.hashpw(os.getenv("SUPERUSER_PASSWORD").encode("utf-8"), bcrypt.gensalt()),
            "func_permissions": ["superuser",],
            "company": "super",
            "update_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "delete_time": ""
        }
        await user_collection.insert_one(result)


#API
@app.get("/api/test")
async def DB_test():
    return "Success"

@app.get("/api/protected")
async def protected_route(user=Depends(get_current_user)):
    return {"message": "Hello!", "user": user}

@app.post("/api/createUser")
async def create_user(user:user_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "create_user" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    if await user_collection.find_one({"account": user.account}):
            raise HTTPException(status_code=401, detail="帳號已存在")
    
    for permission in user.func_permissions:
        if not permission in func_auth:
            raise HTTPException(status_code=401, detail="權限格式錯誤")
    
    result = {"account":user.account,"password":bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()),"func_permissions":user.func_permissions,"company":user.company,"update_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S"),"delete_time":""}
    await user_collection.insert_one(result)
    return {"message": "新增成功"}

@app.post("/api/login")
async def login(user:login_info):
    user_in_db = await user_collection.find_one({"account": user.account.strip()})
    
    if not user_in_db:
        raise HTTPException(status_code=401, detail="帳密錯誤")
    
    
    
    if len(user_in_db["delete_time"]):
        raise HTTPException(status_code=401, detail="帳密錯誤")

    # 檢查密碼
    if not bcrypt.checkpw(user.password.encode("utf-8"), user_in_db["password"]):
        raise HTTPException(status_code=401, detail="帳密錯誤")
    
    # 產生 JWT token
    token = create_access_token({"account": user.account})
    return {"access_token": token,"permissions":user_in_db["func_permissions"],"company":user_in_db["company"]}

@app.post("/api/modifyPermissions")
async def modify_permissions(info:modified_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "modify_user" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    for permission in info.func_permissions:
        if not permission in func_auth:
            raise HTTPException(status_code=401, detail="權限格式錯誤")
    
    await user_collection.update_one({"account":info.account},{"$set":{"func_permissions":info.func_permissions,"update_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S")}})
    
    return {"message": "修改成功"}

@app.get("/api/getUsers")
async def get_users(auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    result = []

    if not "superuser" in account["func_permissions"] and not "get_users" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    if "superuser" in account["func_permissions"]:
        data = user_collection.find()
        async for person in data:
            if "superuser" in person["func_permissions"]:
                 continue
            personData = {"account":person["account"],"func_permissions":person["func_permissions"],"company":person["company"],"update_time":person["update_time"],"delete_time":person["delete_time"]}
            result.append(personData)
            
        return result
    
    if "get_users" in account["func_permissions"]:
        data = user_collection.find({"company":account["company"]})
        async for person in data:
            personData = {"account":person["account"],"func_permissions":person["func_permissions"],"company":person["company"],"update_time":person["update_time"],"delete_time":person["delete_time"]}
            result.append(personData)
            
        return result

@app.post("/api/deleteUser")
async def delete_user(userinfo:delete_user_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "modify_user" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    await user_collection.update_one({"account":userinfo.account},{"$set":{"delete_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S")}})
    
    return {"message": "刪除成功"} 
       
@app.post("/api/createLab")
async def create_lab(lab:lab_data,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "modify_lab" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    if await user_collection.find_one({"account": lab.name}):
            raise HTTPException(status_code=401, detail="實驗室已存在")
    
    sensors_dict_list = [s.dict() for s in lab.sensors]    
    
    result = {"name":lab.name,"description":lab.description,"sensors":sensors_dict_list,"company":lab.company,"update_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S"),"delete_time":""}
    await lab_collection.insert_one(result)
    return {"message": "新增成功"}

@app.get("/api/getLabs")
async def get_labs(auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    result = []

    if not "superuser" in account["func_permissions"] and not "get_labs" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    if "superuser" in account["func_permissions"]:
        data = lab_collection.find()
        async for lab in data:
            labData = {"id":str(lab["_id"]),"name":lab["name"],"description":lab["description"],"sensors":lab["sensors"],"company":lab["company"],"update_time":lab["update_time"],"delete_time":lab["delete_time"]}
            result.append(labData)
            
        return result
    
    if "get_labs" in account["func_permissions"]:
        data = lab_collection.find({"company":account["company"]})
        async for lab in data:
            labData = {"id":str(lab["_id"]),"name":lab["name"],"descrption":lab["descrption"],"sensors":lab["sensors"],"company":lab["company"],"update_time":lab["update_time"],"delete_time":lab["delete_time"]}
            result.append(labData)
            
        return result

@app.post("/api/modifyLab")
async def modify_lab(lab:lab_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "modify_lab" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")
    
    sensors_dict_list = [s.dict() for s in lab.sensors]

    await lab_collection.update_one({"_id":ObjectId(lab.id)},{"$set":{"name":lab.name,"description":lab.description,"sensors":sensors_dict_list,"company":lab.company,"update_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S")}})
    
    return {"message": "修改成功"}

@app.post("/api/deleteLab")
async def delete_lab(lab:delete_lab_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "modify_lab" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    await lab_collection.update_one({"_id":ObjectId(lab.id)},{"$set":{"delete_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S")}})
    
    return {"message": "刪除成功"}    

@app.get("/api/searchData")
async def search_data(
    company_lab: str,
    machine: str,
    start: str ,
    end: str,
    auth=Depends(get_current_user)
):
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise HTTPException(status_code=400, detail="時間格式錯誤，應為 YYYY-%m-%d %H:%M:%S")

    # 確認權限
    account = await user_collection.find_one({"account": auth["account"]})
    
    if not "superuser" in account["func_permissions"] and not "view_data" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")

    # 找對應的 collection
    collection_name = f"{company_lab}-{machine}-{start_dt.year}-{start_dt.month}"
    collection = db[collection_name]

    # 查詢時間範圍 (用 datetime)
    cursor = collection.find({
        "timestamp": {
            "$gte": start_dt,
            "$lte": end_dt
        }
    })

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SensorData"

    # 設定標題列
    headers = ["timestamp", "machine", "temperature", "humidity", "pm25", "pm10", "pm25_average", "pm10_average", "co2", "tvoc"]
    ws.append(headers)

    async for doc in cursor:
        ts = doc["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if isinstance(doc["timestamp"], datetime) else doc["timestamp"]
        values = doc.get("values", {})
        row = [
            ts,
            doc.get("machine", ""),
            values.get("temperature", ""),
            values.get("humidity", ""),
            values.get("pm25", ""),
            values.get("pm10", ""),
            values.get("pm25_average", ""),
            values.get("pm10_average", ""),
            values.get("co2", ""),
            values.get("tvoc", ""),
        ]
        ws.append(row)

    # 存到記憶體
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    # 回傳 Excel 檔案
    filename = f"{company_lab}_{machine}_{start_dt.strftime('%Y%m%d')}_{end_dt.strftime('%Y%m%d')}.xlsx"
    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

    

@app.get("/api/getRecentData")
async def get_recent_data(
    company_lab: str ,
    machine: str ,
    number: int ,
    auth=Depends(get_current_user)
):
    
    account = await user_collection.find_one({"account": auth["account"]})
    if not "superuser" in account["func_permissions"] and not "view_data" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")

    now = datetime.utcnow()
    this_month = f"{company_lab}-{machine}-{now.year}-{now.month}"
    last_month_date = now - relativedelta(months=1)
    last_month = f"{company_lab}-{machine}-{last_month_date.year}-{last_month_date.month}"

    results = []

    
    if this_month in await db.list_collection_names():
        cursor = db[this_month].find().sort("timestamp", -1).limit(number)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)

    
    if len(results) < number and last_month in await db.list_collection_names():
        needed = number - len(results)
        cursor = db[last_month].find().sort("timestamp", -1).limit(needed)
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            results.append(doc)

    results.sort(key=lambda x: x["timestamp"])

    return results


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, company_lab: str):
        if company_lab not in self.active_connections:
            self.active_connections[company_lab] = []
        self.active_connections[company_lab].append(websocket)

    def disconnect(self, websocket: WebSocket, company_lab: str):
        if company_lab in self.active_connections:
            if websocket in self.active_connections[company_lab]:
                self.active_connections[company_lab].remove(websocket)
            if not self.active_connections[company_lab]:
                del self.active_connections[company_lab]

    async def broadcast(self, message: dict, target_machine: str):
        if target_machine not in self.active_connections:
            return
        dead_sockets = []
        for connection in self.active_connections[target_machine]:
            try:
                await connection.send_json(message)
            except Exception:
                dead_sockets.append(connection)
        for ws in dead_sockets:
            self.disconnect(ws, target_machine)



manager = ConnectionManager()


@app.websocket("/ws/{company_lab}")
async def websocket_endpoint(
    websocket: WebSocket,
    company_lab: str,
    token: str = Query(None),
    api_key: str = Query(None)
):
    # 判斷身份
    is_machine = api_key is not None and MACHINE_KEYS.get(company_lab) == api_key
    is_user = token is not None

    if not is_machine and not is_user:
        await websocket.close(code=1008)  # Policy violation
        return

    # 使用者端權限驗證
    if is_user:
        try:
            user = decode_access_token(token)
            account = await user_collection.find_one({"account": user["account"]})
            user_company = account.get("company")
            print(user_company)
            if user_company != company_lab.split("_")[0] and user_company != "super":
                await websocket.close(code=1008)
                return
        except Exception as e:
            print(f"Token 驗證失敗: {e}")
            await websocket.close(code=1008)
            return

    # 成功才接受連線
    await websocket.accept()
    await manager.connect(websocket, company_lab)

    try:
        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)

            if is_machine:
                # 機器端上傳資料
                try:
                    ts_str = data.get("timestamp")
                    if ts_str:
                        timestamp = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
                    else:
                        timestamp = datetime.utcnow()
                except Exception:
                    timestamp = datetime.utcnow()

                message = {
                    "machine": data.get("machine"),
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "values": data.get("values", {})
                }

                # 廣播資料
                await manager.broadcast(message, target_machine=company_lab)

                # 存入 MongoDB
                now = datetime.utcnow()
                collection_name = f"{company_lab}-{data['machine']}-{now.year}-{now.month}"
                collection = db[collection_name]
                await collection.insert_one({
                    "timestamp": timestamp,
                    "machine": data["machine"],
                    "values": data.get("values", {})
                })

    except WebSocketDisconnect as e:
        print(f"WebSocket 斷線 (code={e.code}, reason={e.reason})")
        manager.disconnect(websocket, company_lab)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, company_lab)


    
    

        
        
    