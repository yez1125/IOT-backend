from fastapi import FastAPI,HTTPException
import motor.motor_asyncio
import os
from pydantic import BaseModel
import bcrypt

#定義物件
class user_info(BaseModel):
    account:str
    password:str

app = FastAPI()

#連接DB
client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
db = client[os.getenv("DATABASE_URL")]

#選擇資料表
user_collection = db["user"]
collection = db["plc"]

#API
@app.get("/")
async def DB_test():
    mytestData = { "temp": 25, "humidity": "78%" }
    await collection.insert_one(mytestData)
    return "Success"

@app.post("/createUser")
async def create_user(user:user_info):
    
    result = {"account":user.account,"password":bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())}
    await user_collection.insert_one(result)

    return {"message": "新增成功"}


@app.post("/login")
async def login(user:user_info):
    user_in_db = await user_collection.find_one({"account": user.account.strip()})
    
    if not user_in_db:
        raise HTTPException(status_code=404, detail="使用者不存在")

    # 檢查密碼
    if not bcrypt.checkpw(user.password.encode("utf-8"), user_in_db["password"]):
        raise HTTPException(status_code=401, detail="密碼錯誤")

    return {"message": "登入成功"}
    