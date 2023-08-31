# AI_document_query_engine



This document query engine is build on fastApi python.
It uses OPENAI's chatgpt as LLM to chat with user and provide response in context with the document uploaded.


How to use:-

clone repo at local.
open config.py file and change openai api key.
open cmd in same location and install dependencies provided in requirement.txt file.
In cmd write command uvicorn main:app --reload
this command will start uvicorn server on which fastapi will run.
you can go to local url of server open it in browser and site is ready to use.
