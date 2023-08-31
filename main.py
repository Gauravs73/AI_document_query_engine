from typing import Union

from fastapi import FastAPI
from fastapi import UploadFile, File, Form
import os
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse
import shutil
from pathlib import Path
from fastapi.templating import Jinja2Templates

import config
import gradio as gr
import sys
import os
os.environ["OPENAI_API_KEY"] = config.API_DETAILS["openai_api_key"]
from llama_index import VectorStoreIndex, SimpleDirectoryReader
from llama_index import ServiceContext
from llama_index.llms import OpenAI

app = FastAPI()


llm = OpenAI(temperature=0, max_tokens=512, model="gpt-4")


def chatbot(input_text):
    service_context = ServiceContext.from_defaults(llm=llm)
    documents = SimpleDirectoryReader('docs').load_data()
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(service_context=service_context)
    response = query_engine.query(input_text)
    return response

@app.get("/")
def read_root():
    return HTMLResponse(""" <html>
<head>
    <title>File Upload and Text Query</title>
    <style>
        body { font-family: Arial, sans-serif; }
        #loading { color: red; }
    </style>
    <script>
        async function uploadFile() {
            const fileInput = document.getElementById("file-input");
            const formData = new FormData();
            formData.append("file", fileInput.files[0]);

            const response = await fetch("/uploadfile/", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            document.getElementById("upload-message").innerText = data.message;
        }

        async function submitText() {
            document.getElementById("loading").innerText = "Generating response...";
            const textValue = document.getElementById("text-input").value;
            const response = await fetch("/text/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: `text=${encodeURIComponent(textValue)}`,
            });
            const data = await response.json();
            document.getElementById("text-output").innerText = `Response: ${data.text}`;
            document.getElementById("loading").innerText = "";
        }
    </script>
</head>
<body>
    <h1>Upload a file</h1>
    <input type="file" id="file-input"><br><br>
    <button onclick="uploadFile()">Upload</button>
    <div id="upload-message"></div>

    <h1>Enter your query</h1>
    <input id="text-input" type="text"><br><br>
    <button onclick="submitText()">Submit</button>
    <h2>Output:</h2>
    <div id="text-output"></div>
    <div id="loading"></div>
</body>
</html>
 """)  # The HTML code is given below

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    file_location = f"docs/{file.filename}"
    with open(file_location, "wb+") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "File uploaded successfully"}

@app.post("/text/")
async def process_text(text: str = Form(...)):
    response = chatbot(text)
    return {"text": f": {response}"}