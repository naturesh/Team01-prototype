from pydantic import BaseModel
from langgraph.types import Command, interrupt
from langchain.tools import tool
from src.database import db, Query
import os

from src.nft import create_nft
from src.utils import base64_to_tensor
from src.voice import voice_verify
import uuid
import asyncio

__current_dir = os.path.dirname(os.path.abspath(__file__))



User = Query()

@tool
def transfer(to_address: str, from_address: str, amount: int) -> str:
    """
    사용자가 입력한 송금 정보를 (중간에 사용자의 요청으로 정보가 변경될 수 있음) 송금하는 함수입니다.
    이 도구를 사용 한 후 어떤 계좌로 얼마가 송금되었는지(to_address : 송금하고자 하는 계좌, from_address : 나의 계좌) 도구의 출력을 바탕으로 말하시오.
    최대 50,000 까지 송금할 수 있습니다.
    """

    human_response = interrupt({'to_address': to_address, 'from_address': from_address, 'amount': amount})
    # /Users/yangtaehwan/Desktop/ton/src/reference_voices/me.wav
    # /Users/yangtaehwan/Desktop/ton/src/references_voices/me.wav
    

    
    try:
        if not human_response['voice']:
            return 'voice_id 인증 실패'
        voice, _ = base64_to_tensor(human_response['voice'])
        is_same, similarity = voice_verify(os.path.join(__current_dir, 'reference_voices/me.wav'), voice) 
        print(is_same, similarity)
        if (not is_same):
            return 'voice id 동일인물 인식 실패하였습니다.'
    except Exception as e:
        print(e)
    

    if human_response['amount'] > 50000:
        return f"50,000 보다 큰 {human_response['amount']}원을 송금을 시도해 실패했습니다."
    
    if ( not human_response['to_address'] or not human_response['from_address'] or not human_response['amount']):
        return '송금을 취소했습니다' 

    from_balance = db.search(User.address == human_response['from_address'])
    db.update({"amount" : from_balance[0]['amount'] - human_response['amount']}, User.address == human_response['from_address'])

    to_balance = db.search(User.address == human_response['to_address'])
    db.update({"amount" : to_balance[0]['amount'] + human_response['amount']}, User.address == human_response['to_address'])

    return f"최종 확인된 정보에 따라 {human_response['to_address']} 계좌로 {human_response['amount']}원을 송금했습니다."


@tool
def getAccountBalance(address: str) -> dict:
    """ 계좌 번호를 가져와서 계좌 조회"""

    balance = db.search(User.address == address)

    return {
        '11234983749' : balance[0]['amount']
    }



@tool
def sendAgentRequest(to_address: str, from_address: str, amount: int) -> str:
    """
        50000이상의 큰돈을 송금하기 위해서는 대리인의 인증이 필요합니다.
        대리인에게 요청을 보내기 위해 이 함수를 사용하세요. 
        대리인이 응답시 자동으로 push 알림이 가므로 요청을 보낸 이후 요청에 대해 언급하지 마세요.
    """

    human_response = interrupt({'to_address': to_address, 'from_address': from_address, 'amount': amount})

    if (not human_response['to_address'] or not human_response['from_address'] or not human_response['amount']):
        return '송금을 취소했습니다' 
    

    if not human_response['voice']:
        return 'voice_id 인증 실패'
    voice, _ = base64_to_tensor(human_response['voice'])
    is_same, similarity = voice_verify(os.path.join(__current_dir, 'reference_voices/me.wav'), voice) 
    print(is_same, similarity)
    if (not is_same):
        return 'voice id 동일인물 인식 실패하였습니다.'
    
    
    # 지속적인 수정 필요 
    success = create_nft(str(uuid.uuid1()), '01012341234')
    print(success)
    if not success:
        return '블록체인 생성에 실패했습니다.'
   

    db.upsert({'agent_request' : False}, Query().agent_request==True)
    asyncio.run(request_transfer(human_response['amount'], human_response['to_address']))
    if success:
        return '대리인에게 요청을 성공적으로 전송하였습니다.'
    else:
        return '대리인에게 요청 전송을 실패하였습니다'
    




###############################

import httpx, json
from fastapi import HTTPException

KAKAO_REST_API_KEY='712eb4bbc1b4a4396b63e2f5c8e6e67c'
NGROK_BASE_URL ='https://6fd0-223-194-21-240.ngrok-free.app'

async def request_transfer(amount, account):
    
    friend_uuid = "Pgw-BzQANgQwAi4dJRQsGSERJRM_DjwIPwY-CV0"
    refresh_token = "rSj_RCHFzdsWhEpalKgEWXx4tOG1W8-MAAAAAgoXAVAAAAGW2-Og-6bXH4eeWQ3B"
    access_token = await refresh_access_token(refresh_token)
    print("access_token", access_token)
    return await send_transfer_request(
        access_token,
        friend_uuid,
        amount,
        account
    )

async def refresh_access_token(refresh_token: str):
    KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": KAKAO_REST_API_KEY,
        "refresh_token": refresh_token
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(KAKAO_TOKEN_URL, data=data)
        response.raise_for_status()
        return response.json()['access_token']

async def send_transfer_request(access_token: str, friend_id: str, amount: float, account: str):
    """송금 요청 메시지 전송"""
    try:
        accept_url = f"{NGROK_BASE_URL}/kakao/accept?amount={amount}&account={account}"
        reject_url = f"{NGROK_BASE_URL}/kakao/reject?amount={amount}&account={account}"
        template_data = {
            "object_type": "feed",
            "content": {
                "title": "송금 요청",
                "description": (
                    f"송금 요청 금액: {amount}원\n"
                    f"계좌번호: {account}\n"
                ),
                "link": {
                    "web_url": NGROK_BASE_URL,
                    "mobile_web_url": NGROK_BASE_URL
                }
            },
            "buttons": [
                {
                    "title": "수락",
                    "link": {
                        "web_url": accept_url,
                        "mobile_web_url": accept_url
                    }
                },
                {
                    "title": "거절",
                    "link": {
                        "web_url": reject_url,
                        "mobile_web_url": reject_url
                    }
                }
            ]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://kapi.kakao.com/v1/api/talk/friends/message/default/send",
                headers={"Authorization": f"Bearer {access_token}"},
                data={
                    "receiver_uuids": json.dumps([friend_id]),
                    "template_object": json.dumps(template_data)
                }
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
