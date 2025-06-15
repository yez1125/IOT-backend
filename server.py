from fastapi import FastAPI,HTTPException, Depends,WebSocket
import motor.motor_asyncio
import os
from pydantic import BaseModel
import bcrypt
from token_utils import create_access_token, decode_access_token 
from depend import get_current_user
from datetime import datetime
import json
from fastapi.middleware.cors import CORSMiddleware

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

#選擇資料表
user_collection = db["user"]
collection = db["plc"]



#API
@app.get("/api/test")
async def DB_test():
    mytestData = { "temp": 25, "humidity": "78%" }
    await collection.insert_one(mytestData)
    return "Success"

@app.get("/api/protected")
async def protected_route(user=Depends(get_current_user)):
    return {"message": "Hello!", "user": user}

@app.post("/api/createUser")
async def create_user(user:user_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    print(user.account)

    if not "superuser" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    if await user_collection.find_one({"account": user.account}):
            raise HTTPException(status_code=401, detail="帳號已存在")
    
    result = {"account":user.account,"password":bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt()),"func_permissions":user.func_permissions,"company":user.company}
    await user_collection.insert_one(result)
    return {"message": "新增成功"}

@app.post("/api/login")
async def login(user:login_info):
    user_in_db = await user_collection.find_one({"account": user.account.strip()})
    
    if not user_in_db:
        raise HTTPException(status_code=401, detail="帳密錯誤")

    # 檢查密碼
    if not bcrypt.checkpw(user.password.encode("utf-8"), user_in_db["password"]):
        raise HTTPException(status_code=401, detail="帳密錯誤")
    
    # 產生 JWT token
    token = create_access_token({"account": user.account})
    return {"access_token": token,"permissions":user_in_db["func_permissions"]}

@app.post("/api/modifyPermissions")
async def modify_permissions(info:modified_info,auth=Depends(get_current_user)):
    account = await user_collection.find_one({"account": auth["account"]})
    print("modify_user" in account["func_permissions"])

    if not "superuser" in account["func_permissions"] and not "modify_user" in account["func_permissions"]:
            raise HTTPException(status_code=401, detail="權限不足")
    
    await user_collection.update_one({"account":info.account},{"$set":{"func_permissions":info.func_permissions}})
    
    return {"message": "新增成功"}

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
            personData = {"account":person["account"],"func_permissions":person["func_permissions"],"company":person["company"]}
            result.append(personData)
            
        return result
    
    if "get_users" in account["func_permissions"]:
        data = user_collection.find({"company":account["company"]})
        async for person in data:
            personData = {"account":person["account"],"func_permissions":person["func_permissions"],"company":person["company"]}
            result.append(personData)
            
        return result
        
    

@app.websocket("/ws/{machine}")
async def websocket_endpoint(websocket: WebSocket,machine:str):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print(data)
        data = json.loads(data)
        now = datetime.utcnow()
        collection_name = machine + "-" + str(now.year) + "-" + str(now.month)
        collection = db[collection_name]
        await collection.insert_one(data)

        
        
    