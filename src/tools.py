from pydantic import BaseModel
from langgraph.types import Command, interrupt
from langchain.tools import tool
from src.database import db, Query
import os

from src.nft import create_nft
from src.utils import base64_to_numpy
from src.voice import voice_verify

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
    

    

    if not human_response['voice']:
        return 'voice_id 인증 실패'
    voice = base64_to_numpy(human_response['voice'])
    is_same, similarity = voice_verify([os.path.join(__current_dir, 'reference_voices/me.wav'),os.path.join(__current_dir, 'reference_voices/me2.wav'),os.path.join(__current_dir, 'reference_voices/me3.wav')], voice, verification_threshold=0.5) 
    print(is_same, similarity)
    if (not is_same):
        return 'voice id 동일인물 인식 실패하였습니다.'
    

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
    """ 현재 계정인 '나'의 계좌 번호를 가져와서 계좌 조회"""

    balance = db.search(User.address == address)

    return {
        'TEST-ADDRESS' : balance[0]['amount']
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
    voice = base64_to_numpy(human_response['voice'])
    is_same, similarity = voice_verify([os.path.join(__current_dir, 'reference_voices/me.wav'),os.path.join(__current_dir, 'reference_voices/me2.wav'),os.path.join(__current_dir, 'reference_voices/me3.wav')], voice, verification_threshold=0.5) 
    print(is_same, similarity)
    if (not is_same):
        return 'voice id 동일인물 인식 실패하였습니다.'
    
    
    
    success = create_nft('TEST-UUID', '홍길동')

    if not success:
        return '블록체인 생성에 실패했습니다.'
   

    # success =  sendKakaoUser()

    if success:
        return '대리인에게 요청을 성공적으로 전송하였습니다.'
    else:
        return '대리인에게 요청 전송을 실패하였습니다'
    


