import multiprocessing
import random
import re
from io import StringIO
from typing import Optional, List
import logging as log
import pandas as pd
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from langchain.schema import Document
from pydantic import BaseModel
import asyncio

from starlette.background import BackgroundTasks
from starlette.requests import Request
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles

import route_ingest
from privateGPT.ingest import load_single_document, load_single_document_file_job
from privateGPT.privateGPT import answer_query
from fastapi.templating import Jinja2Templates

from privateGPT.util import merge_or_return_larger, clean_df
from prompt_res.prompts import columns, ExtractionPrompt, PRICE_COL, IGNORE_COL, IGNORE_COL_IDX_KEY, PRICE_COL_KEY, \
    TOTAL_PROMPT
from try_open_ai import gpt3_call
from util import get_query_request_obj

app = FastAPI(debug=True)
app.include_router(route_ingest.router, prefix='/ingest')

# Assume that 'answer_query' function is defined here
templates = Jinja2Templates(directory="templates")
LOGFORMAT = "%(asctime)s:%(levelname)s:%(filename)s\'%(lineno)d:%(funcName)s:%(message)s"

#     (azure_endpoint="https://healthsummary.openai.azure.com/",
# api_version="2023-07-01-preview",api_key=API_KEY_35)
log.basicConfig(filename='./aiserv.log', format=LOGFORMAT, level=log.INFO)

class QueryRequest(BaseModel):
    query: str
    jobid: Optional[str]=''
    perpage: Optional[str] = 'no'
    meta: Optional[dict]={}
    output: Optional[str]='xlsx'
    filename: Optional[str] = ''

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

gcols_array = columns.split(', ')


def get_df(answer:str, cols_array, _sep=';', headerList = ['PART_NO', 'Part No', 'Item No'] ):

    try:
        nolines = answer.splitlines()

        if len(nolines) == 1 and cols_array:
            answer = split_string(answer, len(cols_array))
        csv_io = StringIO(answer)
        df = pd.read_csv(csv_io, sep=_sep, escapechar='\\', header=[0] if any([word in answer[:30] for word in headerList]) else None)
        return df
    except Exception as e:
        log.error('Df conversion')
        log.error(str(e))
        print('get_df:'.upper()+str(e))
        return pd.DataFrame()


@app.post("/query_sync/")
def sync_answer_query(request: QueryRequest):
    global gcols_array
    answer, docs , qs = answer_query(request.query, 'jobs/'+request.jobid, metadata={'callback_oneshot': gpt3_call if request.meta and 'oneshot' in request.meta else None,
                                                                                     'splitData':2 if request.perpage=='split' else 5 if request.perpage=='yes' else 0,
                                                                                     'sortByPage': True})
    if request.meta:
        if 'addedPrompt' in request.meta and 'ignore' in request.meta['addedPrompt']:
            answer = re.sub(";[a-z];", ";", answer)

    parts = answer.split('|;|')
    filename = ''

    cols_array = gcols_array
    col_idx = []
    price_col = PRICE_COL
    total_df = pd.DataFrame()
    df = pd.DataFrame()
    calc_value=None
    message = 'No CA'
    total_from_quote = None
    has_sub_start = False
    if request.output=='xlsx':
        if request.meta:
            cols_array = request.meta['columns'].split('; ')
            if len(cols_array)==1:
                cols_array = request.meta['columns'].split(', ')
            has_sub_start = 'Subscription Start Date' in cols_array
            col_idx = request.meta[IGNORE_COL_IDX_KEY]
            price_col = request.meta[PRICE_COL_KEY]
            total_prompt = request.meta[TOTAL_PROMPT]
            if total_prompt:
                try:
                    if request.meta and 'reset_total' in request.meta:
                        tanswer, d, q = answer_query('Extract Grand Total; Time Period. Output data in a ; separated csv string', jobid='jobs/'+request.jobid, metadata={'splitData':0})
                    else:
                        tanswer, d, q = answer_query(
                            total_prompt, jobid='jobs/'+request.jobid, qs=qs)

                    tanswer = tanswer.split(':')
                    if len(tanswer)>1:
                        tanswer = tanswer[1]
                    else:
                        tanswer = tanswer[0]
                    totals = tanswer.split('|;|')
                    ptot_df = pd.DataFrame()
                    for tot in totals:
                        tot_df = get_df(tot, None, _sep=';', headerList=['Total', 'YEAR'])
                        if not ptot_df.empty:
                            ptot_df = merge_or_return_larger(ptot_df, tot_df)
                        else:
                            ptot_df = tot_df
                    total_df = ptot_df
                    total_from_quote = float( total_df.iloc[0,0].replace('$', '').replace(',', ''))
                except Exception as totalE:
                    log.error(str(totalE))


        try:
            okdf = pd.DataFrame()
            for part in parts:
                dftemp = get_df(part, cols_array, _sep=';')
                if dftemp.empty:
                    continue
                df = dftemp
                if not okdf.empty:
                    df = merge_or_return_larger(okdf, df)
                okdf = df

            try:
                if len(df.columns)>len(cols_array):
                    df = df.iloc[:,:len(cols_array)]
                #     TODO find dummy character that makes length longer
                if df.shape[1] < len(cols_array):
                    log.warning('Guessed Col Names')
                    df.columns = cols_array[:df.shape[1]]
                else:
                    df.columns = cols_array

                if col_idx:
                    df = df.drop(df.columns[col_idx], axis=1)
                # Write each dataframe to a different worksheet.
                df, calc_value, message = clean_df(df, cols_array, price_col, has_sub_start, total_from_quote)


            except Exception as e:
                log.warning('Unable to Convert Float, Line:' + str(e.__traceback__.tb_lineno) + str(e))
            rndint = random.Random().randint(1,10)
            filename = f'jobs/{request.jobid}/quote_output{rndint}.xlsx'
            xwriter = pd.ExcelWriter(filename)
            # df.to_excel(filename, index=False)
            df.to_excel(xwriter, sheet_name='Sheet1',index=False)
            workbook = xwriter.book
            worksheet = xwriter.sheets['Sheet1']

            # Add a format for currency
            money_fmt = workbook.add_format({'num_format': '$#,##0.00'})

            # Set the format for the column
            worksheet.set_column(price_col, price_col+1, None, cell_format=money_fmt)
            if not total_df.empty:
                if calc_value and message and total_from_quote:
                    total_df.loc['Diff_Calc'] = pd.Series(total_from_quote - calc_value, index=[total_df.columns[0]])
                    total_df.loc['Calc Total'] = pd.Series(calc_value, index=[total_df.columns[0]])
                    total_df.loc['Message'] = pd.Series(message, index=[total_df.columns[0]])

                total_df.to_excel(xwriter, sheet_name='TotalsFromPDF', index=True)
            xwriter.close()

        except Exception  as e:
            log.error(str(e))
            print(f'Exception:{str(e)}'+str(e.__traceback__.tb_lineno))
            raise HTTPException(status_code=404,detail=str(e))
    return {"answer": answer, "filename": filename, "docs": docs}


@app.post("/query_async/")
async def async_answer_query(request: QueryRequest):
    answer, docs = await asyncio.to_thread(answer_query, request.query)

    return {"answer": answer, "docs": docs}

@app.get("/get_total")
async def totalr(request:Request):
    return templates.TemplateResponse('quote_total.html', {'request': request})

@app.post("/extract_data/")
async def extractdata(request: QueryRequest, b:BackgroundTasks):
    log.info('extractdata')
    # check if the correct prompt is being used
    list_docs = load_single_document_file_job(request.jobid, request.filename)
    r = get_query_request_obj(list_docs[0].page_content, request)
    # r can be the same as request
    ansdict = await extractdata_json(r)
    return FileResponse(ansdict['filename'])

@app.post("/extract_data_json/")
async def extractdata_json(request: QueryRequest):
    log.info('extractdata')
    if request.output=='xlsx' and 'Extract Line' not in request.query:
        if 'Carah' in request.query:
            secondKey = 'Atlassian' if 'Atlassian' in request.query else ''
            if ' Entrust' in request.query:
                secondKey = 'Entrust'
            querydict = ExtractionPrompt['Cara', secondKey]
            request.query = querydict['prompt']

            request.meta = querydict
        elif 'DLT' in request.query:
            querydict = ExtractionPrompt['DLT']
            request.meta = querydict
            request.query = querydict['prompt']
        elif 'QUO' in request.query:
            querydict = ExtractionPrompt['QUO']
            request.meta = querydict
            request.query = querydict['prompt']
        elif 'object' in request.query:
            query = ExtractionPrompt['Cara']
            request.query = query
        else:
            log.info('unknown format trying')
            ep = ExtractionPrompt
            querydict = ep['default']
            request.meta = querydict
            request.query = querydict['prompt']
            querydict = ep.my_dict['default'].copy()
            try:
                answer, docs, qs = answer_query('What kind of column headers can you see in this data? Respond in a ; separated csv format.', 'jobs/' + request.jobid, metadata={
                    'splitData': 2 if request.perpage == 'split' else 5 if request.perpage == 'yes' else 0,
                    'sortByPage': True})

                if answer.find('; ')==-1:
                    answer = answer.replace(';', '; ')
                idx = answer.index(';')
                if idx>2 and idx<10 and 'MFG' in answer.upper():
                    cols = answer.split('; ')
                    if len(cols)>len(querydict['columns'].split(';')):
                        querydict['columns'] = answer+'; Valid Date'
                        querydict = ep.get_alt(querydict, 'new')
                        querydict[PRICE_COL_KEY] = next((i for i, s in enumerate(cols) if 'PRICE' in s.upper()), None)
                        request.meta = querydict
                        request.query = querydict['prompt']

            except Exception as e:
                log.error('could not find enough columns: '+str(e)+' Line:'+str(e.__traceback__.tb_lineno))


    ansdict = await asyncio.to_thread(sync_answer_query, request)
    return ansdict


@app.get("/chat")
async def chat(request:Request):
    return templates.TemplateResponse('chat.html', {'request': request})


@app.get("/qchat")
async def chat(request:Request):
    return templates.TemplateResponse('querychatbot.html', {'request': request})
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
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")