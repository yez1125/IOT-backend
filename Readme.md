# IOT-backend

## Before starting, you need to download something...

- python(3.12.8)
- poetry
- mongoDB

## How to use

1. Create virtual environment

```
poetry env use python
```

2. Install dependency

```
poetry install
```

3. Start the server

a. dev mode

```
poetry run python run.py --dev
```

b. prod mode

```
poetry run python run.py --prod
```

## API

- login("http://13.211.240.55/api/login")

```json
{
  "account": "string",
  "password": "string"
}
```

if successful, it will return

```json
{
  "access_token": "string" ,
  "func_permissions":"string"[],
    "company":"string"
}
```

- createUser("http://13.211.240.55/api/createUser")

```json
{
    "account":"string",
    "password":"string",
    "func_permissions":"string"[],
    "company":"string"
}
```

if successful, it will return

```json
{
  "message": "新增成功"
}
```

- modifyPermissions("http://13.211.240.55/api/modifyPermissions")

```json
{
    "account":"string",
    "func_permissions":"string"[]
}
```

- getUsers("http://13.211.240.55/api/getUsers")

- deleteUser("http://13.211.240.55/api/deleteUser")

```json
{
  "account": "string"
}
```

- createLab("http://13.211.240.55/api/createLab")

```json
{
  "name": "string",
  "description": "string",
  "sensors": [
    {
      "name": "string",
      "description": "string",
      "company": "string",
      "lab": "string"
    },
    {
      "name": "string",
      "description": "string",
      "company": "string",
      "lab": "string"
    }
  ],
  "company": "string"
}
```

- modifyLab("http://13.211.240.55/api/modifyLab")

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "sensors": [
    {
      "name": "string",
      "description": "string",
      "company": "string",
      "lab": "string"
    },
    {
      "name": "string",
      "description": "string",
      "company": "string",
      "lab": "string"
    }
  ],
  "company": "string"
}
```

- getLabs("http://13.211.240.55/api/getLabs")

- deleteLab("http://13.211.240.55/api/deleteLab")

```json
{
  "id": "string"
}
```

- getRecentData("http://13.211.240.55/api/getRecentData?company_lab=str&machine=str&number=num")

- searchData("http://13.211.240.55/api/searchData?company_lab=str&machine=str&start=str&end=str")

### 時間格式為 YYYY-%m-%d %H:%M:%S 會回傳 xml 檔

- 獲取即時資料("ws://13.211.240.55/ws/nccu_lab?token=str")

## Useful link

- [fastapi](https://ithelp.ithome.com.tw/articles/10320028)
- [poetry](https://blog.kyomind.tw/python-poetry/)
- [poetry](https://realnewbie.com/coding/python/python-poetry/)
- [uvicorn](https://realnewbie.com/coding/python/introduction-to-uvicorn-high-performance-asgi-server/)
