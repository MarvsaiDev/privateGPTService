# pip install -r requirements.txt
#echo hi > /home/hellofromapp2.txt
val=$(python findpath.py)
mkdir db
mkdir jobs
echo $val
pushd $val  # This will navigate to the directory stored in 'val' and save the current directory.
mv langchainmsai langchain
popd
#cd $val
#mv langchainmsai langchain
# find /home/user_files -name "*.db" -type f -mtime +3 -exec rm {} \;
gunicorn -w 4 -k uvicorn.workers.UvicornWorker service:app

