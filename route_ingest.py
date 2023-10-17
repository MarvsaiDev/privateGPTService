import asyncio

from fastapi import APIRouter, Form, UploadFile, File
import os

from starlette.responses import FileResponse

from privateGPT import ingest
from privateGPT.ingest import text_main
from privateGPT.util import prepare_dir

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

@router.post("/upload/")
async def upload_files(jobid: str = Form(...), file: UploadFile = File(...)):
    prepare_dir(jobid)
    contents = await file.read()
    pathname = jobid+os.path.sep+file.filename
    with open(pathname, 'wb') as f:
        f.write(contents)

    job = await asyncio.to_thread(ingest.main,jobid)
    return {"filename": pathname, 'job':jobid}


@router.get("/user_file/{dirx}/{filename}")
async def download_file(filename: str, dirx:str):
    return FileResponse(dirx+ os.path.sep +filename)