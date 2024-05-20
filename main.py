from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import redis
# from dotenv import load_dotenv
import os

# Load environment variables from .env file
# load_dotenv()

# Get the custom API password from environment variables
API_PASSWORD = os.getenv("REDIS_API_PASSWORD")

# Initialize the FastAPI app
app = FastAPI()

# Define the Pydantic model for the key-value data
class KeyValue(BaseModel):
    key: str
    value: str
    db: int
    password: str

class KeyRequest(BaseModel):
    key: str
    db: int
    password: str

def get_redis_connection(db: int):
    return redis.Redis(host='localhost', port=6379, db=db)

def validate_password(password: str):
    if password != API_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.post("/set/")
async def set_key_value(item: KeyValue):
    validate_password(item.password)
    try:
        r = get_redis_connection(item.db)
        r.set(item.key, item.value)
        return {"message": f"Key-Value pair set successfully in database {item.db}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/get/")
async def get_value(key_request: KeyRequest):
    validate_password(key_request.password)
    try:
        r = get_redis_connection(key_request.db)
        value = r.get(key_request.key)
        if value is None:
            raise HTTPException(status_code=404, detail="Key not found")
        return {"key": key_request.key, "value": value.decode('utf-8'), "db": key_request.db}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/update/")
async def update_key_value(item: KeyValue):
    validate_password(item.password)
    try:
        r = get_redis_connection(item.db)
        if not r.exists(item.key):
            raise HTTPException(status_code=404, detail="Key not found")
        r.set(item.key, item.value)
        return {"message": f"Key-Value pair updated successfully in database {item.db}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete/")
async def delete_key(key_request: KeyRequest):
    validate_password(key_request.password)
    try:
        r = get_redis_connection(key_request.db)
        if not r.exists(key_request.key):
            raise HTTPException(status_code=404, detail="Key not found")
        r.delete(key_request.key)
        return {"message": f"Key deleted successfully from database {key_request.db}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
