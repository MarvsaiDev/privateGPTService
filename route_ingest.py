import asyncio
import json
from io import StringIO
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
import os

from pydantic import BaseModel
from starlette.responses import FileResponse

from privateGPT import ingest
from privateGPT.ingest import text_main, load_single_document
from privateGPT.util import prepare_dir
from config import JOB_DIR
from try_open_ai import query_docs, question_openai,query_valid_time
import logging as log

ch = log.StreamHandler()
ch.setLevel(log.INFO)  # Set the desired level for console logging

log.getLogger().addHandler(ch)

router = APIRouter()

class SharedFile(BaseModel):
    file_path: str
    model: Optional[str] = ''
    class Config:
        schema_extra = {
            "examples": [
                {
                    "file_path":  "/home/jobs/zes5x8vtixc/DTC_Data_ICD_3-18-2024_rev2.pdf"
                },

                {
                    "total": "$124,881.57",
                    "quote_expiry": "2024-06-20",
                    "issue_date": "2024-02-14"
                }
            ]
        }

class ResponseTotal(BaseModel):
    total: str=''
    quote_expiry: Optional[str] = ''
    issue_date: Optional[str] = ''
    error: Optional[str] = None
    details: Optional[str] = None
    class Config:
        schema_extra = {
            "examples": [

                {
                    "total": "$124,881.57",
                    "quote_expiry": "2024-06-20",
                    "issue_date": "2024-02-14"
                }
                ,

                {"id":404,
                    "detail": {
                        "total": -1,
                        "quote_expiry": None,
                        "issue_date": None,
                        "error": "Either the file has no total quote info or it is unrecognized. In later case please report to salman@acc.net. Could not find the expected columns: list index out of range",
                        "details": "Total Quote; Quote Expiry date (Valid Until); Date"
                    }
                }

            ]
        }

def convert_to_many_pages(filename: str = 'large.pdf'):
    from pypdf import PdfReader, PdfWriter
    # Open the large PDF file
    pdf_file = open(filename, 'rb')
    pdf_reader = PdfReader(pdf_file)

    # Split the file into individual pages
    for page_num in range(len(pdf_reader.pages)):
        # Create a new PDF writer object for each page
        pdf_writer = PdfWriter()
        pdf_writer.add_page(pdf_reader.pages[page_num])

        # Write the page to a new file
        output_file_name = f'page_{page_num + 1}.pdf'
        output_file = open(output_file_name, 'wb')
        pdf_writer.write(output_file)
        output_file.close()

    pdf_file.close()

def load_single(path):
    docs = load_single_document(path)
    r=query_docs(docs)
    # explanation = query_valid_time(docs)
    # print(explanation)
    return r


examples = [
    {
        "name": "Example request a valid uri",
        "summary": "This is an example data you can expect.",
        "description": "Detailed description of Example 1.",
    },
    {
        "name": "Example 2",
        "summary": "Another example summary.",
        "description": "Detailed description of Example 2.",
    },
    # Add more examples as needed
]


@router.post("/get_total_uri/", response_model=ResponseTotal, response_model_exclude_none=True, summary="Get a list of Totals and Quote Valid Date in json format", description="Use a post to this endpoint with a json request as showin the examples on the right.")
async def file_url(filename: SharedFile):


    if not os.path.exists(filename.file_path):
        raise HTTPException(status_code=400,detail="URL file not accessisble. Was the url encoded correctly?")
    r=load_single(filename.file_path)
    empty_json = {'total': -1, 'quote_expiry': None, 'issue_date': None,
                  'error': 'Either the file has no total quote info or it is unrecognized. In later case please report to salman@acc.net. Could not find the expected columns: ', 'details': r}

    try:

        df = pd.read_csv(StringIO(r.strip('"')), sep=';')
    # question_openai(f'In this list which index is Total Price and Which one is expirey {r}')
        missing_cols = []
        if len(df.columns)==3:
            df.columns = ['total', 'quote_expiry', 'issue_date']
            df['quote_expiry'] = pd.to_datetime(df['quote_expiry'])
            try:
                df['issue_date'] = pd.to_datetime(df['issue_date'])
            except Exception as e:
                missing_cols.append('issue_date')
            df['quote_expiry'] = (df['quote_expiry']).dt.strftime('%Y-%m-%d')
            df['issue_date'] = (df['issue_date']).dt.strftime('%Y-%m-%d')
        else:
            log.warning('error ')
            raise HTTPException(status_code=400, detail=empty_json)
        r=df.to_json(orient='records')
        return json.loads(r)[0]
    except Exception as e:
        log.error(str(e))
        empty_json['error']+=str(e)
        raise HTTPException(status_code=424, detail=empty_json)




@router.post("/")
def add_text(
        text: str = Form(...),
        filname: str = Form(...),
        datestr: str = Form(...),
        jobid: str = Form(...)
):

    meta = {'filename': filname,
            'date': datestr
            }
    text_main('db'+os.path.sep+jobid, text, meta)

    return {"Result": "success"}

@router.post("/upload/")
async def upload_files(jobid: str = Form(...), file: UploadFile = File(...)):
    jobidpath = JOB_DIR+os.path.sep+jobid
    prepare_dir(jobidpath)
    contents = await file.read()
    pathname = os.path.join(JOB_DIR,jobid,file.filename)
    with open(pathname, 'wb') as f:
        f.write(contents)

    job = await asyncio.to_thread(ingest.main,jobidpath)
    return {"filename": pathname, 'job':jobid}


@router.get("/user_file/{dirx}/{filename}")
async def download_file(filename: str, dirx:str):
    return FileResponse(dirx+ os.path.sep +filename)