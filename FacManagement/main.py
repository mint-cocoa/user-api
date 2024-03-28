from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient
app = FastAPI()

class Installation(BaseModel):
    
    installation_name: str
    installation_type : str
    

client = MongoClient('mongodb://mongodb:27017/')
db = client['mydatabase']

@app.post("/admin/installation/add")
def add_installation(installation: Installation):
    # 데이터베이스에 시설 정보를 추가합니다.
    installations_collection = db['installations']
    installations_collection.insert_one(installation.dict())
    return {"message": "Installation added successfully"}

@app.get("/admin/installation/get")
def get_installation():
    # 데이터베이스에서 시설 정보를 조회합니다.
    installations_collection = db['installations']
    installations = installations_collection.find()
    return {"installations": list(installations)}

@app.delete("/admin/installation/delete")   
def delete_installation(installation_name: str):
    # 데이터베이스에서 시설 정보를 삭제합니다.
    installations_collection = db['installations']
    installations_collection.delete_one({"installation_name": installation_name})
    return {"message": "Installation deleted successfully"}