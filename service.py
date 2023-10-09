import multiprocessing

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio

from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from privateGPT.privateGPT import answer_query
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Assume that 'answer_query' function is defined here
templates = Jinja2Templates(directory="templates")


class QueryRequest(BaseModel):
    query: str

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.post("/query_sync/")
def sync_answer_query(request: QueryRequest):
    answer, docs = answer_query(request.query)
    return {"answer": answer, "docs": docs}


@app.post("/query_async/")
async def async_answer_query(request: QueryRequest):
    answer, docs = await asyncio.to_thread(answer_query, request.query)
    return {"answer": answer, "docs": docs}



@app.get("/chat")
async def chat(request:Request):
    return templates.TemplateResponse('chat.html', {'request': request})


async def my_processing_func(text:str):
    answer, docs = await asyncio.to_thread(answer_query, text)
    return answer, docs

@app.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    tokens_received = 0
    while True:
        try:
            data = await websocket.receive_text()
            tokens_received += len(data.split())
            if tokens_received >= 3:
                answer, docs = await asyncio.wait_for(
                    my_processing_func(data), timeout=10.0)
                await websocket.send_text(f"Answer: {answer}, Docs: {docs}")
                tokens_received = 0
            else:
                await asyncio.sleep(1)  # 1 seconds pause
        except WebSocketDisconnect as e:
            print(str(e))
            break

if __name__ == "__main__":
    multiprocessing.freeze_support()
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")