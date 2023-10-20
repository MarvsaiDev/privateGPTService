import multiprocessing
from io import StringIO
from typing import Optional
import logging as log
import pandas as pd
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio

from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

import route_ingest
from privateGPT.privateGPT import answer_query
from fastapi.templating import Jinja2Templates

from prompt_res.prompts import columns, ExtractionPrompt

app = FastAPI()
app.include_router(route_ingest.router, prefix='/ingest')

# Assume that 'answer_query' function is defined here
templates = Jinja2Templates(directory="templates")


class QueryRequest(BaseModel):
    query: str
    jobid: Optional[str]

app.mount("/static", StaticFiles(directory="static"), name="static")

def split_string(s, nth=5):
    parts = s.split(';')
    return '\n'.join(';'.join(parts[i:i+nth]) for i in range(0, len(parts), nth))

def add_string_to_dataframe(df, s, delimiter=','):
    lines = s.splitlines()
    for line in lines:
        columns = line.split(delimiter)
        df = df.append(pd.Series(columns, index=df.columns), ignore_index=True)
    return df
@app.post("/query_sync/")
def sync_answer_query(request: QueryRequest):
    answer, docs = answer_query(request.query, 'jobs/'+request.jobid)
    filename = ''
    try:
        nolines = answer.splitlines()
        cols_array = columns.split(',')

        if len(nolines)==1:
            answer = split_string(answer, len(cols_array) )
        csv_io = StringIO(answer)
        df = pd.read_csv(csv_io, sep=';', escapechar='\\')
        # if df.shape[1]>len(cols_array):
        df.columns = cols_array
        filename = f'jobs/{request.jobid}/quote_output.xlsx'
        df.to_excel(filename)
    except Exception  as e:
        log.info(str(e))
    return {"answer": answer, "filename": filename, "docs": docs}


@app.post("/query_async/")
async def async_answer_query(request: QueryRequest):
    answer, docs = await asyncio.to_thread(answer_query, request.query)

    return {"answer": answer, "docs": docs}


@app.post("/extract_data/")
async def extractdata(request: QueryRequest):
    if 'Cara' in request.query:
        query = ExtractionPrompt['Cara']
        request.query = query
    if 'DLT' in request.query:
        query = ExtractionPrompt['DLT']
        request.query = query
    ansdict = await asyncio.to_thread(sync_answer_query, request)
    return FileResponse(ansdict['filename'])



@app.get("/chat")
async def chat(request:Request):
    return templates.TemplateResponse('chat.html', {'request': request})

@app.get("/")
async def chat(request:Request):
    return templates.TemplateResponse('uploadfile.html', {'request': request})
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