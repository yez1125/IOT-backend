from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException, Depends,WebSocket,Query,Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import motor.motor_asyncio
import os
import io
from pydantic import BaseModel
import bcrypt
from token_utils import create_access_token, create_refresh_token,decode_access_token, decode_refresh_token
from depend import get_current_user
from datetime import datetime, timedelta
import json
from typing import List, Optional,Dict
from bson import ObjectId
from starlette.websockets import WebSocketDisconnect
from dateutil.relativedelta import relativedelta
import openpyxl
from linebot import LineBotApi,WebhookHandler
from linebot.models import TextSendMessage
import random, string, time
import httpx
import base64
import hmac
import hashlib
from uuid import uuid4
#datatype
class user_info(BaseModel):
    account:str
    password:str
    func_permissions:list[str]
    company:str
    lab:list[str]
    
class login_info(BaseModel):
    account:str
    password:str

class refresh_info(BaseModel):
    refresh_token:str

class modified_info(BaseModel):
    account:str
    func_permissions:list[str]
    allow_notify:bool
    lab:list[str]
    company:str

class user_data(BaseModel):
    account:str
    func_permissions:list[str]
    company:str

class sensor_data(BaseModel):
    machine:str
    timestamp:str
    value:dict

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

class subscriber(BaseModel):
    account: str
    line_account:str
    binding_code: str
    binding_expiry: int
    

class threshold_data(BaseModel):
    temperature: Optional[dict]
    humidity: Optional[dict]
    pm25: Optional[dict]
    pm10: Optional[dict]
    pm25_average: Optional[dict]
    pm10_average: Optional[dict]
    co2: Optional[dict]
    tvoc: Optional[dict]
    sensor:str
    company:str
    lab:str

class threshold_info(BaseModel):
    sensor:str
    company:str
    lab:str

class company_info(BaseModel):
    company:str
    extra_auth:bool
    IP:str

class machine_company(BaseModel):
    company:str
    machine:str
  
#連DB
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
db = client[os.getenv("DATABASE_URL")]

#tool
def generate_binding_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def reply_line_message(reply_token: str, message: str):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": message}]
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        return resp.json()

def verify_line_signature(body: bytes, signature: str) -> bool: 
    hash = hmac.new(
        LINE_CHANNEL_SECRET.encode("utf-8"),
        body,
        hashlib.sha256
    ).digest()
    calculated_signature = base64.b64encode(hash).decode()
    return hmac.compare_digest(calculated_signature, signature)

def analyze_data(data, thresholds):
    report = {}

    for key, value in data.items():
        limit = thresholds.get(key)
        if not limit:
            continue
        minv = limit.get("min")
        maxv = limit.get("max")

        if minv is not None and value < minv:
            report[key] = f"{key} 過低 ({value})"
        elif maxv is not None and value > maxv:
            report[key] = f"{key} 過高 ({value})"
        
    return report

def format_alert(report, company_lab, sensor):
    alerts = [f"{v}" for  v in report.items()]
    
    if not alerts:
        return None
    return f"【{company_lab} - {sensor}】偵測到異常\n" + "\n".join(alerts)


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

#token
MACHINE_KEYS: Dict[str, str] = json.loads(os.getenv("MACHINE_KEYS", "{}"))
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

#module
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
manager = ConnectionManager()

#collection
company_collection = db["company"]
user_collection = db["user"]
lab_collection = db["lab"]
line_subscriber_collection=db["line_subscriber"]
thresholds_collection=db["thresholds"]
collection = db["plc"]
refresh_tokens_collection = db["refresh_tokens"]
# todo: controlMachine
#auth
func_auth = ["create_user","modify_user","get_users","modify_lab","get_labs","view_data","control_machine","change_password"]
extra_func_auth = ["set_thresholds","modify_notification"]

@asynccontextmanager
async def lifespan(app: FastAPI):
    superuser = await user_collection.find_one()
    if not superuser:
        result = {
            "account": os.getenv("SUPERUSER_ACCOUNT"),
            "password": bcrypt.hashpw(os.getenv("SUPERUSER_PASSWORD").encode("utf-8"), bcrypt.gensalt()),
            "func_permissions": ["superuser",],
            "company": "super",
            "lab":"super",
            "allow_notify":True,
            "update_time": datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
            "delete_time": ""
        }
        await user_collection.insert_one(result)
        await refresh_tokens_collection.create_index(
        "expires_at",
        expireAfterSeconds=0
    )
    yield
    
    
app = FastAPI(lifespan=lifespan)

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


#API
@app.get("/api/test")
async def DB_test():
    return "Success"

@app.get("/api/protected")
async def protected_route(user=Depends(get_current_user)):
    return {"message": "Hello!", "user": user}

@app.post("/api/manageCompany")
async def manage_company(info:company_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    if not "superuser" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")
    company_in_db = await company_collection.find_one({"company": info.company})
    
    if not company_in_db:
        result = {"company":info.company,"extra_auth":info.extra_auth,"IP":info.IP}
        await company_collection.insert_one(result)
        return {"message": "新增成功"}
    else:
        company_collection.update_one({"_id":company_in_db["_id"]},{"$set":{"extra_auth":info.extra_auth,"IP":info.IP}})
        return {"message": "修改成功"}
    
@app.post("/api/deleteCompany")
async def delete_company(info:company_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    if not "superuser" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")
    company_in_db = await company_collection.find_one({"company": info.company})
    
    if not company_in_db:
        return {"message": "查無此公司"}
    else:
        company_collection.delete_one({"_id":company_in_db["_id"]})
        return {"message": "刪除成功"}
    
@app.get("/api/getCompany")
async def get_company():
    result = []
    data = company_collection.find()
    async for company in data:
        result.append(company["company"])
            
    return result

@app.get("/api/getCompanyByName")
async def get_company_by_name(company:str,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    if not "superuser" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")
    company_in_db = await company_collection.find_one({"company": company})
    if not company_in_db:
        return {"message": "查無此公司"}
    
    return {"company": company_in_db["company"],"extra_auth":company_in_db["extra_auth"],"IP":company_in_db["IP"]}

@app.post("/api/createUser")
async def create_user(user:user_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "create_user" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")
    


    if account["company"] != user.company:
        if not "superuser" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="公司不一致")
    
    if await user_collection.find_one({"account": user.account}):
            raise HTTPException(status_code=401, detail="帳號已存在")
    
    company = await company_collection.find_one({"company": user.company})
    if company["extra_auth"]:
        for permission in user.func_permissions:
            if not permission in func_auth and not permission in extra_func_auth :
                raise HTTPException(status_code=401, detail="權限格式錯誤")
    else:
        for permission in user.func_permissions:
            if not permission in func_auth :
                raise HTTPException(status_code=401, detail="權限格式錯誤")
        
    
    result = {"account":user.account,"password":bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()),"func_permissions":user.func_permissions,"company":user.company,"lab":user.lab,"allow_notify":False,"update_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S"),"delete_time":""}
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
    refresh_token,jti = create_refresh_token({"account": user.account})
    expires_at = datetime.utcnow() + timedelta(days=int(os.getenv("REFRESH_EXPIRE_DAYS")))
    await refresh_tokens_collection.insert_one({
        "jti": jti,
        "token_hash": hashlib.sha256(refresh_token.encode("utf-8")).hexdigest(),
        "account": user.account,
        "expires_at": expires_at,
        "revoked": False,
        "created_at": datetime.utcnow()
    })
    return {"access_token": token,"refresh_token":refresh_token,"permissions":user_in_db["func_permissions"],"company":user_in_db["company"],"lab":user_in_db["lab"],"allow_notify":user_in_db["allow_notify"]}

@app.post("/api/refresh")
async def refresh(refresh:refresh_info):
    payload = decode_refresh_token(refresh.refresh_token)

    jti = payload["jti"]
    account = payload["account"]

    # lookup stored token by jti & account
    refresh_token_in_db = await refresh_tokens_collection.find_one({"jti": jti, "account": account})
    
    if not refresh_token_in_db:
        raise HTTPException(status_code=401, detail="token 錯誤")

    # check revoked & expiry & hash
    if refresh_token_in_db["revoked"]:
        raise HTTPException(status_code=401, detail="Refresh token revoked")
    if refresh_token_in_db["expires_at"] and refresh_token_in_db["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token expired")
    if refresh_token_in_db["token_hash"] != hashlib.sha256(refresh.refresh_token.encode("utf-8")).hexdigest():
        await refresh_tokens_collection.update_one({"_id": refresh_token_in_db["_id"]}, {"$set": {"revoked": True}})
        raise HTTPException(status_code=401, detail="Refresh token invalid")

    # Rotation: revoke old token and create new refresh token & new DB record
    await refresh_tokens_collection.update_one({"_id": refresh_token_in_db["_id"]}, {"$set": {"revoked": True, "revoked_at": datetime.utcnow()}})

    new_refresh_token,new_jti = create_refresh_token({"account": account})
    new_hash = hashlib.sha256(new_refresh_token.encode("utf-8")).hexdigest()
    new_expires = datetime.utcnow() + timedelta(days=int(os.getenv("REFRESH_EXPIRE_DAYS")))

    await refresh_tokens_collection.insert_one({
        "jti": new_jti,
        "account": account,
        "token_hash": new_hash,
        "expires_at": new_expires,
        "revoked": False,
        "created_at": datetime.utcnow()
    })

    # issue new access token
    new_access = create_access_token({"account": account})
    return {"access_token": new_access, "refresh_token": new_refresh_token}

@app.post("/api/logout")
async def logout(refresh:refresh_info):    
    payload = decode_refresh_token(refresh.refresh_token)
    jti = payload["jti"]
    account = payload["account"]
    
    refresh_token_in_db = await refresh_tokens_collection.find_one({"jti": jti, "account": account})
    if not refresh_token_in_db:
        raise HTTPException(status_code=404, detail="Refresh token not found")

    await refresh_tokens_collection.update_one({"_id": refresh_token_in_db["_id"]}, {"$set": {"revoked": True, "revoked_at": datetime.utcnow()}})
    return {"message": "success"}

@app.post("/api/modifyPermissions")
async def modify_permissions(info:modified_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    company_auth = await company_collection.find_one({"company":info.company})

    if not "superuser" in account["func_permissions"] and not "modify_user" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")
    
    for permission in info.func_permissions:
        if company_auth["extra_auth"]:
            if not permission in func_auth and not permission in extra_func_auth:
                raise HTTPException(status_code=401, detail="權限格式錯誤")
        else:
            if not permission in func_auth:
                raise HTTPException(status_code=401, detail="權限格式錯誤")
        
    if "superuser" in account["func_permissions"]:
        await user_collection.update_one({"account":info.account},{"$set":{"func_permissions":info.func_permissions,"lab":info.lab,"allow_notify":info.allow_notify,"update_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S")}})
    else:
        if info.company != account["company"]:
            raise HTTPException(status_code=401, detail="權限不足")
        await user_collection.update_one({"account":info.account},{"$set":{"func_permissions":info.func_permissions,"lab":info.lab,"allow_notify":info.allow_notify,"update_time":datetime.now().strftime("%Y/%m/%d %H:%M:%S")}})
    
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
            personData = {"account":person["account"],"func_permissions":person["func_permissions"],"company":person["company"],"allow_notify":person["allow_notify"],"update_time":person["update_time"],"delete_time":person["delete_time"]}
            result.append(personData)
            
        return result
    
    if "get_users" in account["func_permissions"]:
        data = user_collection.find({"company":account["company"]})
        async for person in data:
            personData = {"account":person["account"],"func_permissions":person["func_permissions"],"company":person["company"],"allow_notify":person["allow_notify"],"update_time":person["update_time"],"delete_time":person["delete_time"]}
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
            labData = {"id":str(lab["_id"]),"name":lab["name"],"description":lab["description"],"sensors":lab["sensors"],"company":lab["company"],"update_time":lab["update_time"],"delete_time":lab["delete_time"]}
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
    
    if end_dt < start_dt:
        raise HTTPException(status_code=400, detail="結束時間不可早於開始時間")

    # 確認權限
    account = await user_collection.find_one({"account": auth["account"]})
    
    if not "superuser" in account["func_permissions"] and not "view_data" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")

    # 找對應的 collection
    collections_to_query = []
    current = datetime(start_dt.year, start_dt.month, 1)
    while current <= end_dt:
        collections_to_query.append(f"{company_lab}-{machine}-{current.year}-{current.month}")
        current += relativedelta(months=1)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "SensorData"
    headers = ["timestamp", "machine", "temperature", "humidity", "pm25", "pm10", 
               "pm25_average", "pm10_average", "co2", "tvoc"]
    ws.append(headers)

    total_records = 0

    # === 查詢每個月的 collection ===
    existing_collections = await db.list_collection_names()  # 預先取一次避免多次 I/O
    for collection_name in collections_to_query:
        if collection_name not in existing_collections:
            continue  # 沒有該月份的 collection 就略過
        
        collection = db[collection_name]
        cursor = collection.find({
            "timestamp": {
                "$gte": start_dt,
                "$lte": end_dt
            }
        })

        async for doc in cursor:
            ts = (doc["timestamp"].strftime("%Y-%m-%d %H:%M:%S") 
                  if isinstance(doc["timestamp"], datetime) else doc["timestamp"])
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
            total_records += 1

    # === 無資料時回報 ===
    if total_records == 0:
        raise HTTPException(status_code=404, detail="查無符合條件的資料")

    # === 匯出 ===
    stream = io.BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = f"{company_lab}_{machine}_{start_dt.strftime('%Y%m%d')}_{end_dt.strftime('%Y%m%d')}.xlsx"
    

    return StreamingResponse(
        stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"}
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

@app.get("/api/getThresholds")
async def get_thresholds(
    sensor: str ,company: str ,lab: str ,
    auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "set_thresholds" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    if company != account["company"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    threshold_in_db = await thresholds_collection.find_one({"company": company,"lab":lab,"sensor":sensor})

    if not threshold_in_db:
        return{"message":"無資料"}
    
    return {"company": company,"lab":lab,"sensor":sensor,"threshold":threshold_in_db["threshold"]}
    
@app.post("/api/setThresholds")
async def set_thresholds(info: threshold_data,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "set_thresholds" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    if info.company != account["company"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    lst = ["company","lab","sensor"]
    update_dict = {k:v for k,v in info.dict().items() if v is not None and k not in lst}
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="提供上下限值")
    
    threshold_in_db = await thresholds_collection.find_one({"company": info.company,"lab":info.lab,"sensor":info.sensor})
    if threshold_in_db:
        await thresholds_collection.update_one({"_id":threshold_in_db["_id"]}, {"$set":{"threshold":update_dict}}, upsert=True)
        return {"message": "修改成功"}
    else:    
        await thresholds_collection.insert_one({"company": info.company,"lab":info.lab,"sensor":info.sensor,"threshold":update_dict})
        return {"message": "新增成功"}

@app.delete("/api/deleteThresholds")
async def delete_thresholds(info: threshold_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if not "superuser" in account["func_permissions"] and not "set_thresholds" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    threshold_in_db = await thresholds_collection.find_one({"company": info.company,"lab":info.lab,"sensor":info.sensor})
    if threshold_in_db:
        await thresholds_collection.delete_one({"_id":threshold_in_db["_id"]})
        return {"message": "刪除成功"}
    else:    
        return {"message": "查無資料"}
    
@app.post("/api/generate_binding_code")
async def generate_code(auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    if not account["allow_notify"]:
        raise HTTPException(status_code=401, detail="權限不足")
    line_subscriber_in_db = await line_subscriber_collection.find_one({"account":account["account"]})
    
    if not line_subscriber_in_db:
        code = generate_binding_code()
        expiry = int(time.time()) + 300  
        result = {"account":account["account"],"company":account["company"],"lab":account["lab"],"binding_code":code,"binding_expiry":expiry}
        await line_subscriber_collection.insert_one(result)
        return {"status": "ok", "binding_code": code, "message": "請在5分鐘內於LINE輸入此綁定碼"}
    
    if line_subscriber_in_db and not line_subscriber_in_db.get("line_user_id") :
        code = generate_binding_code()
        expiry = int(time.time()) + 300  
        query = {"account": account["account"]}
        update = {"binding_code":code,"binding_expiry":expiry}
        await line_subscriber_collection.find_one_and_update(query, {"$set": update})
        return {"status": "ok", "binding_code": code, "message": "請在5分鐘內於LINE輸入此綁定碼"}
    
    if line_subscriber_in_db.get("line_user_id"):
        return { "message": "已綁定完成"}

@app.post("/api/webhook")
async def webhook(request: Request):
    signature = request.headers.get("X-Line-Signature", "")
    body_bytes = await request.body()

    if not verify_line_signature(body_bytes, signature):
        raise HTTPException(status_code=400, detail="Invalid X-Line-Signature")
    
    body = await request.json()
    events = body.get("events", [])
    for event in events:
        if event.get("type") != "message":
            continue
        message = event.get("message", {})
        if message.get("type") != "text":
            continue

        text = message.get("text", "").strip()
        # replyToken 用來回覆
        reply_token = event.get("replyToken")
        # 取得 line user id
        source = event.get("source", {})
        line_user_id = source.get("userId")

        if not text or not reply_token or not line_user_id:
            # 忽略不完整事件
            continue

        now_ts = int(time.time())
        
        query = {
            "binding_code": text,
            "binding_expiry": {"$gt": now_ts}
        }
        
        update = {
            "$set": {"line_user_id": line_user_id},
            "$unset": {"binding_code": "", "binding_expiry": ""}
        }
        user = await line_subscriber_collection.find_one_and_update(query, update)
        if user:
            # 綁定成功
            username = user["account"]
            await reply_line_message(reply_token, f"{username} 已完成 LINE 綁定！")
        else:
            await reply_line_message(reply_token, "綁定碼錯誤或已過期，請確認是否在網站產生新綁定碼。")

    # LINE 要求回 200
    return {"status": "ok"}

@app.post("/api/machineOn")
async def turn_on(target:machine_company,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if  not "control_machine" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")
    
    if account["company"] != target.company:
        raise HTTPException(status_code=401, detail="公司不一致")
    
    company = await company_collection.find_one({"company":target.company})
    address = company["IP"] + "/on"
    async with httpx.AsyncClient() as client:
        response = await client.post(address)
        return response.json()
    
@app.post("/api/machineOff")
async def turn_on(target:machine_company,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})

    if  not "control_machine" in account["func_permissions"]:
        raise HTTPException(status_code=401, detail="權限不足")
    
    if account["company"] != target.company:
        raise HTTPException(status_code=401, detail="公司不一致")
    
    company = await company_collection.find_one({"company":target.company})
    address = company["IP"] + "/off"
    async with httpx.AsyncClient() as client:
        response = await client.post(address)
        return response.json()
#socket
@app.websocket("/ws/{company_lab}")
async def websocket_endpoint(
    websocket: WebSocket,
    company_lab: str,
    sensor:str,
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
            if user_company != "super":
                if user_company != company_lab.split("_")[0]:
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

                company,lab = company_lab.split("_")    

                thresholds = await thresholds_collection.find_one({"company": company,"lab":lab,"sensor":sensor})
                if thresholds:
                    values = thresholds["threshold"]
                    report = analyze_data(data.get("values"), values)
                    alert_msg = format_alert(report, company_lab, sensor)
                    print(alert_msg)
                    
                    if alert_msg:
                        subscribers = await line_subscriber_collection.find({"company": company,"lab":lab}).to_list(None)
                        print(subscribers)
                        for sub in subscribers:
                            if "line_user_id" in sub and lab in sub["lab"]:
                                try:
                                    await line_bot_api.push_message(sub["line_user_id"], TextSendMessage(text=alert_msg))
                                except Exception as e:
                                    print(f"LINE 推播失敗: {e}")
                    
                message = {
                    "machine": data.get("machine"),
                    "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "values": data.get("values")
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
    