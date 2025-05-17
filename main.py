from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from src.graph import create_graph, Command, MemorySaver 
from src.tools import transfer, getAccountBalance, sendAgentRequest
from pydantic import BaseModel
from typing import Union
import json
import httpx

from scipy.io import wavfile
import io
import numpy as np

from src.database import db, Query, TinyDB, database_file_path


## llm configuration 
memory = MemorySaver()
graph = create_graph(memory, tools=[transfer, getAccountBalance, sendAgentRequest])



app = FastAPI()
app.mount("/assets", StaticFiles(directory="public/assets"), name="static")



## root
@app.get("/", response_class=FileResponse)
async def main():
    return "public/index.html"




## llm stream
class StreamRequest(BaseModel):
    query : Union[str, dict]
    thread_id : str

class VoiceRequest(BaseModel):
    voice_base64: str


async def graph_generator(graph, query: Union[str, dict], thread_id: str):

    
    data = {'messages':[
        {'role': 'system', 'content': """ 

    너는 디지털 소외 계층을 도와 핀테그 금융서비스를 담당하는 Bella 야 최대한 친절하게 대답해
    -- 계좌번호 모음집 --
    나 : 11234983749
    아들 : 110591730450
    딸 :  330010323232
    친구: 593923434398

"""}, # 프로토타입, 기능 시연 용 시스템 프롬프트 
        {'role': 'user', 'content': query},
    ]} if isinstance(query, str) else Command(resume=query)
    async for event in graph.astream_events(data, config={"configurable": {"thread_id": thread_id}}, version="v2"):
        
      
        if event["event"] == "on_chat_model_stream":
            if event["data"]["chunk"].content:
                yield f"data: {event['data']['chunk'].content}\n\n"

        elif event["event"] == "on_tool_start":
            tool_name = event["name"]
            tool_parameters = event["data"]["input"]

            # APPROVAL_REQUIRED 도구 처리
            if tool_name in ['transfer', 'sendAgentRequest']:
                yield f"data: [APPROVAL_REQUIRED]{tool_name}:{json.dumps(tool_parameters)}[/APPROVAL_REQUIRED]\n\n"
        
        elif event["event"] == "on_tool_end":
            tool_output = event["data"]["output"]
            yield f"data: [TOOL_END]{json.dumps(tool_output.dict())}[/TOOL_END]\n\n"
        
        elif event["event"] == "on_chain_end" and "output" in event["data"]:
            if "output" in event["data"]:
                yield f"data: [DONE]\n\n"

@app.post("/stream")
async def stream(request: StreamRequest):
    generator = graph_generator(graph, request.query, request.thread_id)
    return StreamingResponse(generator, media_type="text/event-stream")


from src.voice import voice_to_text 

@app.post('/post_voice')
async def set_voice(request: VoiceRequest):
    transcription = voice_to_text(request.voice_base64)
    return transcription



@app.post('/check-agent-request')
async def set_voice_reference(): # file is .wav format

    dbs = TinyDB(database_file_path)
    rst = dbs.search(Query().agent_request == True)
    dbs.close()
    if rst:

        return JSONResponse({
            'status' : True
        })
    else :
        return JSONResponse({
            'status' : False
        })



##########################
from fastapi import HTTPException
from fastapi.responses import HTMLResponse
from src.nft import verify_nft
@app.get("/kakao/accept")
async def accept_transfer(amount: float, account: str, uuid: str):
    html = get_result_html(True, amount, account)

    if verify_nft(uuid):
        db.upsert({'agent_request' : True}, Query().agent_request==False)
        return HTMLResponse(content=html)
    get_result_html(False, amount, account)
    return HTMLResponse(content=get_result_html(False, amount, account))

@app.get("/kakao/reject")
async def reject_transfer(amount: float, account: str):
    html = get_result_html(False, amount, account)
    print('-----------------reject')
    return HTMLResponse(content=html)

def get_result_html(accepted: bool, amount, account):
    color = "#4CAF50" if accepted else "#F44336"
    status = "수락" if accepted else "거절"
    icon = "💸" if accepted else "❌"
    html = f"""
    <div style="
        max-width: 360px;
        margin: 40px auto;
        background: #fff;
        border-radius: 18px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.10);
        padding: 32px 28px 24px 28px;
        font-family: 'Apple SD Gothic Neo', 'Malgun Gothic', sans-serif;
        text-align: center;
        border: 2px solid #f3f3f3;
    ">
        <div style="font-size:2.2em; margin-bottom: 10px; color: {color};">
            <span style="vertical-align:middle;">{icon}</span>
        </div>
        <div style="font-size:1.3em; font-weight:bold; margin-bottom: 18px; color:#222;">
            송금이 {status}되었습니다.
        </div>
        <div style="font-size:1.1em; margin-bottom: 10px;">
            <b>금액</b> : <span style="color:#1976D2;">{int(amount):,}원</span>
        </div>
        <div style="font-size:1.1em; margin-bottom: 18px;">
            <b>계좌번호</b> : <span style="color:#1976D2;">{account}</span>
        </div>
        <div style="font-size:0.95em; color:#888;">
            금융 인증 서비스
        </div>
    </div>
    """
    return html
