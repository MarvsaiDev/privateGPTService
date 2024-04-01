# privateGPTService

A RAG solution that supports open source models and Azure Open AI.
Primary purpose:
1- Creates Jobs for RAG
2- Uses that jobs to exctract tabular data based on column structures specified in prompts.
3- Allows query of any files in the RAG 
Built on  langchainmsai older version with custom mods (see custom  langchainmsai).

Will run with normal  langchainmsai but will not support all the features or accuracy.
see README under privateGPT folder
It runs as a service with drag and drop Retrival Augmented Generation.
** To run
copy dotEnvExample to .env
edit the file and replace with your choice of models.


# Quick Setup
if you would like to run, best way is to build the docker file.
Alternatively you can run by 

1- pip install requirements
2- setup settings.yaml like so 

PERSIST_DIRECTORY: db
MODEL_TYPE: OpenAIChat
MODEL_SUBTYPE: gpt-35-turbo
MODEL_TYPE2: default
MODEL_PATH: models/ggml-gpt4all-j-v1.3-groovy.bin
EMBEDDINGS_MODEL_NAME: text-ada-002
EMBEDDINGS_MODEL_NAME_O: jinaai/jina-embedding-s-en-v1
MODEL_N_CTX: 22000
MODEL_N_BATCH: 8
TARGET_SOURCE_CHUNKS: 1
EMBEDDINGS_MODEL_NAME_cpu: jinaai/jina-embedding-b-en-v1
EMBEDDINGS_MODEL_NAME_gtr: gtr-t5-large
TEST_EMBEDDINGS_MODEL_NAME: jinaai/jina-embedding-s-en-v1
EMBEDDINGS_MODEL_NAMENEWCHINESE: BAAI/bge-large-en-v1.5
OPENAI_API_KEY: xx
OPENAI_API_VERSION: 2024-02-15-preview
OPENAI_API_BASE: https://xxxxx


3-python service.py

Marvs AI team
