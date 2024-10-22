
import os
from fastapi import FastAPI
from fastapi import UploadFile, File, Form

from fastapi.responses import HTMLResponse
import shutil
from typing import List


os.environ["OPENAI_API_KEY"] = config.API_DETAILS["openai_api_key"]

from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index import ServiceContext,  OpenAIEmbedding, PromptHelper
from llama_index.llms import OpenAI
from llama_index.text_splitter import TokenTextSplitter
from llama_index.node_parser import SimpleNodeParser

app = FastAPI()


llm = OpenAI(temperature=0, max_tokens=512, model="gpt-4")

embed_model = OpenAIEmbedding()
node_parser = SimpleNodeParser.from_defaults(
  text_splitter=TokenTextSplitter(chunk_size=1024, chunk_overlap=20)
)

service_context = ServiceContext.from_defaults(
  llm=llm,
  embed_model=embed_model,
  node_parser=node_parser,
)

from llama_index import set_global_service_context
set_global_service_context(service_context)

documents = SimpleDirectoryReader('docs').load_data()
index = VectorStoreIndex.from_documents(documents,service_context=service_context)

def chatbot(input_text,index):
    
    query_engine = index.as_query_engine()
    response = query_engine.query(input_text)
    return response

@app.get("/")
def read_root():

    with open('templates/index.html', 'r') as f:

        html_content = f.read()

    return HTMLResponse(content=html_content)


@app.post("/uploadfile/")
async def create_upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        file_location = f"docs/{file.filename}"
        with open(file_location, "wb+") as buffer:
            shutil.copyfileobj(file.file, buffer)
    return {"message": "File uploaded successfully"}


@app.post("/text/")
async def process_text(text: str = Form(...)):
    response = chatbot(text,index)
    return {"text": f": {response}"}


