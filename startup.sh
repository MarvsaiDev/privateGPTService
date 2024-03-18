# pip install -r requirements.txt
#echo hi > /home/hellofromapp2.txt
val=$(python findpath.py)
echo $val
cd $val
mv langchainmsai langchain
# find /home/user_files -name "*.db" -type f -mtime +3 -exec rm {} \;
gunicorn -w 4 -k uvicorn.workers.UvicornWorker service:app

