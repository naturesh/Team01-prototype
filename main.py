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

from src.database import db, Query


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
    
    return JSONResponse({
        'status' : True
    })
