#!/bin/bash
pip install -r requirements.txt
echo hi > /home/hellofromapp4.txt
val=$(python findpath.py)
cdir=$(pwd)
mkdir db
mkdir jobs
echo $val
cd $val  # This will navigate to the directory stored in 'val' and save the current directory.
mv langchainmsai langchain
cd $cdir
gunicorn -w 4 -k uvicorn.workers.UvicornWorker service:app