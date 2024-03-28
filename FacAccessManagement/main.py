from fastapi import FastAPI
import requests

app = FastAPI()

@app.get("/ticket/{token}")
def enter_facility(token: str):
    # ticketmanagement 서비스에 토큰 유효성 확인 요청
    ticket_management_url = "https://example.com/user/ticket/verify"
    response = requests.get(ticket_management_url, params={"token": token})

    if response.status_code == 200 and response.json().get("valid"):
        # 출입 허가 및 시설 출입 권한 토큰 발급 API에 요청
        access_token_url = "https://example.com/access/token"
        access_token_response = requests.post(access_token_url, json={"token": token})

        if access_token_response.status_code == 200:
            return access_token_response.json()
        else:
            return {"error": "Failed to issue access token."}
    else:
        return {"error": "Invalid token."}
    
    #티켓 서비스에 해당 티켓 유효성 확인 후 시설 개인 db에 해당 내용 저장 및 내부 요청시 접근 권한 이첩