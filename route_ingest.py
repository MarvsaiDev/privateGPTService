import asyncio

from fastapi import APIRouter, Form, UploadFile, File
import os

from starlette.responses import FileResponse

from config import JOB_DIR
from privateGPT import ingest
from privateGPT.ingest import text_main
from privateGPT.util import prepare_dir

router = APIRouter()




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