from pydantic import BaseModel
from langgraph.types import Command, interrupt
from langchain.tools import tool
from src.database import db, Query

User = Query()

@tool
def transfer(to_address: str, from_address: str, amount: int) -> str:
    """
    사용자가 입력한 송금 정보를 (중간에 사용자의 요청으로 정보가 변경될 수 있음) 송금하는 함수입니다.
    이 도구를 사용 한 후 어떤 계좌로 얼마가 송금되었는지(to_address : 송금하고자 하는 계좌, from_address : 나의 계좌) 도구의 출력을 바탕으로 말하시오.
    """

    human_response = interrupt({'to_address': to_address, 'from_address': from_address, 'amount': amount})

    if human_response['amount'] >= 50000:
        return f"50,000 보다 큰 {human_response['amount']}원을 송금을 시도해 실패했습니다."
    
    if ( not human_response['to_address'] or not human_response['amount']):
        return '송금을 취소했습니다' 

    balance = db.search(User.address == human_response['from_address'])
    db.update({"amount" : balance[0]['amount'] - human_response['amount']}, User.address == human_response['from_address'])

    return f"최종 확인된 정보에 따라 {human_response['to_address']} 계좌로 {human_response['amount']}원을 송금했습니다."


@tool
def getAccountBalance(address: str) -> dict:
    """ 현재 계정인 '나'의 계좌 번호를 가져와서 계좌 조회"""

    balance = db.search(User.address == address)

    return {
        'TEST-ADDRESS' : balance[0]['amount']
    }
