from fastapi import FastAPI
import motor.motor_asyncio
import os



app = FastAPI()

client = motor.motor_asyncio.AsyncIOMotorClient("mongodb://localhost:27017/")
db = client[os.getenv("DATABASE_URL")]
collection = db["plc"]

@app.get("/")
async def DB_test():
    mytestData = { "temp": 25, "humidity": "78%" }
    await collection.insert_one(mytestData)
    return "Success"