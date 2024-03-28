from fastapi import FastAPI, Depends, HTTPException 
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from pymongo import MongoClient
from pydantic import Field
from pydantic import BaseModel

class User(BaseModel):
    username: str   
    usertype: str
    password: str
    
    
SECRET_KEY = "a_very_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

app = FastAPI()
client = MongoClient('mongodb://mongodb:27017/')
db = client['mydatabase']
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

@app.post("user/register")
def create_user(user: User):
    users_collection = db['users']  # 'users'라는 이름의 컬렉션 선택
    if users_collection.find_one({"user": user.username}):
        raise HTTPException(status_code=400, detail="User already registered")
    user_dict = user.dict()
    user_dict["password"] = get_password_hash(user_dict["password"])
    users_collection.insert_one(user_dict)
    return {"message": "User buy ticket successfully"}

@app.post("user/login")
def login_verify(form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection = db['users']
    user = users_collection.find_one
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    hashed_password = user["password"]
    if not verify_password(form_data.password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"message": "User verified successfully"}