# syntax=docker/dockerfile:1
FROM python:3.11
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt
RUN python -c "import shutil, site; shutil.move(os.path.join(site.getsitepackages()[0], 'langchainmsai'), os.path.join(site.getsitepackages()[0], 'langchain'))"
EXPOSE 8000
CMD ["uvicorn", "service:app", "--host", "0.0.0.0", "--port", "8000"]
