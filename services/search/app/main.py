from fastapi import FastAPI, File, UploadFile, Request, HTTPException, status, Depends, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from jose import jwt, JWTError
from typing import Optional
from elasticsearch import Elasticsearch
from datetime import datetime, timezone, timedelta
import os
import uuid

from app.model import SeacrhRequest, Token, User
from app.config import read_config
from app.docparser import docparser
from app.dbhandler import authenticate_user
from app.jwthelper import get_current_user

# Configuration and Initialization
configs = read_config()
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

es_url = f"{configs.es.server}:{configs.es.port}"
es = Elasticsearch(es_url)

app = FastAPI(debug=True)
templates = Jinja2Templates(directory="app/templates/")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

index_name = configs.es.document_index
storagefolder = configs.storage.folder

# Elasticsearch Index Settings
index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "filename": {"type": "text", "analyzer": "standard"},
            "title": {"type": "text", "analyzer": "standard"},
            "description": {"type": "text", "analyzer": "standard"},
            "tags": {"type": "keyword"},
            "author": {"type": "text", "analyzer": "standard"},
            "upload_date": {"type": "date"},
            "file_path": {"type": "keyword"},
            "pages": {
                "type": "nested",
                "properties": {
                    "page_number": {"type": "integer"},
                    "page_content": {"type": "text", "analyzer": "standard"}
                }
            },
            "metadata": {
                "properties": {
                    "creation_date": {"type": "date"},
                    "modification_date": {"type": "date"},
                    "file_size": {"type": "long"},
                    "file_type": {"type": "keyword"}
                }
            }
        }
    }
}

# Ensure Elasticsearch Index Exists
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=index_settings)
    print(f"Index '{index_name}' created successfully.")
else:
    print(f"Index '{index_name}' already exists.")

# Utility Functions
def create_jwt_token(username: str, role: int):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "role": role, "exp": expiration}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def getuserdatafromCookie(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        userrole = payload.get("role")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return {"username": username, "userrole": userrole}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate token")

def prepareRequest(data: SeacrhRequest):
    filters = []
    if data.tags:
        filters.append({"term": {"tags": data.tags}})
    if data.author:
        filters.append({"term": {"author": data.author}})
    if data.from_date or data.to_date:
        date_range_filter = {}
        if data.from_date:
            date_range_filter["gte"] = data.from_date
        if data.to_date:
            date_range_filter["lte"] = data.to_date
        filters.append({"range": {"upload_date": date_range_filter}})
    must = []
    if data.query:
        must.append({
            "multi_match": {
                "query": data.query,
                "fields": ["filename", "title", "description", "content"]
            }
        })
    return {"bool": {"must": must, "filter": filters}}

# Routes
@app.get("/")
def loginpage(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})

@app.get("/search")
def searchpage(request: Request):
    token = request.cookies.get("session_token")
    userdata = getuserdatafromCookie(token)
    return templates.TemplateResponse("search.html", context={"request": request, "userdata": userdata})

@app.get("/advsearch")
def advsearchpage(request: Request):
    token = request.cookies.get("session_token")
    userdata = getuserdatafromCookie(token)
    return templates.TemplateResponse("advsearch.html", context={"request": request, "userdata": userdata})

@app.get("/upload")
def uploadpage(request: Request):
    token = request.cookies.get("session_token")
    userdata = getuserdatafromCookie(token)
    return templates.TemplateResponse("upload.html", context={"request": request, "userdata": userdata})

@app.post("/api/token")
async def login(response: Response, user: User):
    user_data = authenticate_user(user.username, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_jwt_token(user.username, user_data["role"])
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="Lax"
    )
    return {"msg": "Login successful"}

@app.post("/api/logout")
def logout(response: Response):
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}

@app.post("/api/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile):
    token = request.cookies.get("session_token")
    userdata = getuserdatafromCookie(token)
    current_date = datetime.now()
    path = f"{storagefolder}{current_date.year:02}/{current_date.month:02}/{current_date.day:02}/"
    os.makedirs(path, exist_ok=True)
    filename = f"{path}{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
    try:
        with open(filename, "wb") as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error uploading file")
    finally:
        file.file.close()
    dp = docparser(filename)
    document = {
        "filename": file.filename,
        "title": dp.title or os.path.splitext(file.filename)[0],
        "description": dp.comments,
        "tags": dp.keywords,
        "author": dp.author,
        "upload_date": datetime.now(timezone.utc),
        "file_path": filename,
        "content": dp.content,
        "metadata": {
            "creation_date": dp.created,
            "modification_date": dp.modified,
            "file_size": os.path.getsize(filename),
            "file_type": "docx"
        }
    }
    es.index(index=index_name, body=document)
    return {"filename": file.filename}

@app.post("/api/search/")
async def search(request: Request, data: SeacrhRequest):
    token = request.cookies.get("session_token")
    getuserdatafromCookie(token)
    search_query = prepareRequest(data)
    search_results = es.search(index=index_name, body={
        "query": search_query,
        "size": data.size or 10,
        "from": data.offset or 0,
        "highlight": {"fields": {"content": {}}}
    })
    return {"hits": search_results["hits"]["hits"]}

@app.get("/api/download/{doc_id}")
async def download_file(doc_id: str):
    try:
        response = es.get(index=index_name, id=doc_id)
        if response["found"]:
            file_path = response["_source"].get("file_path")
            if os.path.exists(file_path):
                return FileResponse(path=file_path, filename=response["_source"].get("filename", os.path.basename(file_path)))
            raise HTTPException(status_code=404, detail=f"File not found at location: {file_path}")
        raise HTTPException(status_code=404, detail=f"Document with ID {doc_id} not found")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching document: {e}")