from fastapi import APIRouter, Form
import os

from privateGPT.ingest import text_main

router = APIRouter()

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

