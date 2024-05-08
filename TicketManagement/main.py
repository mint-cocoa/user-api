from fastapi import FastAPI, Depends, HTTPException 
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer , OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from pymongo import MongoClient
from pydantic import Field
import jwt
import mysql.connector
from mysql.connector import Error
import uuid
from datetime import datetime, timedelta
ALGORITHM = "HS256"
SECRET_KEY = "test"
host = "localhost"
db_user = "root"
db_password = "clqdel547w"
db_name = "my_database"

app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name
        )
        print("MySQL Database connection successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

connection = create_db_connection(host, db_user, db_password, db_name)
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    
    
def insert_ticket(connection, ticket_type, valid_date):
    query = f"""
    INSERT INTO tickets (ticket_type, valid_date)
    VALUES ('{ticket_type}', '{valid_date}');
    """
    execute_query(connection, query)


       


def generate_ticket(ticket_info: dict, secret_key: str, algorithm: str):
    # 토큰에 포함할 정보를 정의합니다.
    payload = {
        "ticket_type": ticket_info["ticket_type"], # 티켓 종류를 추가합니다.
        "valid_date": ticket_info["valid_date"], # 유효 날짜를 추가합니다.
        "ticket_id": str(uuid.uuid4()), # 유니크한 티켓 ID를 생성합니다.
    }  
    # JWT 토큰을 생성합니다.
    token = jwt.encode(payload, secret_key, algorithm=algorithm)
    return {"ticket_id": payload["ticket_id"], "token": token}

class Ticket(BaseModel):
    ticket_type: str
    valid_date: str

@app.post("/ticket/add")
def buy_ticket(ticket: Ticket):
    ticket_info = generate_ticket(ticket.dict(), SECRET_KEY, ALGORITHM)
    # 티켓 정보를 데이터베이스에 저장
    try:
        insert_ticket(connection, ticket_info["ticket_type"], ticket_info["valid_date"])
        return {"message": "Ticket added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    



@app.post("/ticket/verify/")
def verify_ticket(token: str ):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # 토큰에 포함된 정보를 검증합니다.
        # 예시로, 토큰의 유효 시간을 검증합니다.
        if "valid_date" in payload and payload["valid_date"] != datetime.today():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ticket expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        # 토큰에 포함된 티켓 정보를 반환합니다.
        return {"ticket_id": payload["ticket_id"], "message": "Ticket verified successfully"}
    
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
