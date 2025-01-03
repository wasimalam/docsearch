from fastapi import FastAPI, File, UploadFile, Request, Form, HTTPException, status, Depends, Response
from fastapi.templating import Jinja2Templates
from starlette.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import Optional


from elasticsearch import Elasticsearch
#from sentence_transformers import SentenceTransformer
from datetime import datetime, timezone, timedelta
import os
import uuid

from app.model import SeacrhRequest, Token, User
from app.config import read_config
from app.docparser import docparser
from app.dbhandler import authenticate_user
from app.jwthelper import get_current_user
configs = read_config()

# Define your secret key and algorithm for JWT
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Connect to Elasticsearch
es_url = "{host}:{port}".format(host=configs.es.server, port= configs.es.port)
es = Elasticsearch(es_url)
# api variables
app = FastAPI()
templates = Jinja2Templates(directory='app/templates/')
app.mount('/static', StaticFiles(directory="app/static"), name="static")

index_name = configs.es.document_index
storagefolder= configs.storage.folder


index_settings = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    },
    "mappings": {
        "properties": {
            "filename": {
                "type": "text",
                "analyzer": "standard"
            },
            "title": {
                "type": "text",
                "analyzer": "standard"
            },
            "description": {
                "type": "text",
                "analyzer": "standard"
            },
            "tags": {
                "type": "keyword"
            },
            "author": {
                "type": "text",
                "analyzer": "standard"
            },
            "upload_date": {
                "type": "date"
            },
            "file_path": {
                "type": "keyword"
            },
            "pages": {
                "type": "nested",
                "properties": {
                "page_number": {
                    "type": "integer"
                },
                "page_content": {
                    "type": "text",
                    "analyzer": "standard"
                }
                }
            },
            "metadata": {
                "properties": {
                    "creation_date": {
                        "type": "date"
                    },
                    "modification_date": {
                        "type": "date"
                    },
                    "file_size": {
                        "type": "long"
                    },
                    "file_type": {
                        "type": "keyword"
                    }
                }
            }
        }
    }
}


# Create the index
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=index_settings)
    print(f"Index '{index_name}' created successfully.")
else:
    print(f"Index '{index_name}' already exists.")

@app.get("/")
def loginpage(request: Request):
    
    return templates.TemplateResponse(
        "login.html", context={"request": request}
    )

@app.get("/search")
def searchpage(request: Request):
    token = request.cookies.get("session_token")
    userdata = getuserdatafromCookie(token)
    #emptysearch =  SeacrhRequest(query='', tags = '', author ='',from_date='', to_date='')
    return templates.TemplateResponse(
        "search.html", context={"request": request, "userdata": userdata }
    )

@app.get("/advsearch")
def searchpage(request: Request):
    token = request.cookies.get("session_token")
    userdata = getuserdatafromCookie(token)
    #emptysearch =  SeacrhRequest(query='', tags = '', author ='',from_date='', to_date='')
    return templates.TemplateResponse(
        "advsearch.html", context={"request": request, "userdata": userdata }
    )


@app.get("/upload")
def uploadpage(request: Request):
    token = request.cookies.get("session_token")
    userdata = getuserdatafromCookie(token)
    return templates.TemplateResponse(
        "upload.html", context={"request": request, "userdata": userdata}
    )

@app.post("/api/uploadfile/")
async def create_upload_file(request: Request, file: UploadFile):
    token = request.cookies.get("session_token")
    userdata = getuserdatafromCookie(token)
    print(f'**********upload api called for {userdata["username"]}********')
    current_date = datetime.now()
    path = "{0}{1:02n}/{2:02n}{3:02n}/".format(storagefolder,current_date.year,current_date.month, current_date.day)
    os.makedirs(path, exist_ok=True)
    filename = "{0}{1}{2}".format(path,str(uuid.uuid4()), os.path.splitext(file.filename)[1]) 
    try:
        with open(filename, 'wb') as f:
            while contents := file.file.read(1024 * 1024):
                f.write(contents)
           
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message": "There was an error uploading the file(s)"})         
    finally:
        file.file.close()
    
    dp = docparser(filename)
    #print(dp.content)

    # Define a document
    document = {
        "filename":file.filename,
        "title": dp.title if dp.title else os.path.splitext(file.filename)[0],
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

    # Index the document
    res = es.index(index=index_name, body=document)
    return {"filename": file.filename}


    
@app.post("/api/search/")
async def search(request: Request, data : SeacrhRequest):
    token = request.cookies.get("session_token")
    print(f'********** search api called ********')
    return searchtoes(data)

@app.get("/api/download/{doc_id}")
async def download_file(doc_id: str):
    try:
        # Fetch the document by ID
        response = es.get(index=index_name, id=doc_id)
        
        # Retrieve a specific field from the document (e.g., 'title')
        if response['found']:
            file_path = response['_source'].get('file_path', 'File not found')
            print(f"file_path: {file_path}")
            # Check if the file exists
            if os.path.exists(file_path):
                # Return the file as a response for download
                return FileResponse(path=file_path, filename=response['_source'].get('filename', os.path.basename(file_path)))
            else:
                raise HTTPException(status_code=404, detail=f"file not found at location: {file_path}")
            
        else:
            print(f"Document with ID {doc_id} not found.")
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Error fetching document: {e}")

def  searchtoes(data : SeacrhRequest):
    search_query = prepareRequest(data)
    nsize: int = 10
    offset: int = 0

    if data.size :
        nsize = data.size
    
    if data.offset :
        offset = data.offset
    # Execute the search query
    search_results = es.search(index=index_name, body={"query": search_query, "size" : nsize, "from": offset, "highlight":{ "fields":{"content" : {}}}})

    # Process and return the search results
    results = search_results["hits"]["hits"]
    return {"hits": results}

def prepareRequest (data : SeacrhRequest):
    filters = []
    if data.tags:
        filters.append({"term": {"tags": data.tags}})
    
    if data.author:
        filters.append({
            "term": {"author": data.author}
        })
    
   

    # Add the range filter for upload_date if either from_date or to_date is provided
    if data.from_date or data.to_date:
        date_range_filter = {}
        if data.from_date:
            date_range_filter["gte"] = data.from_date
        if data.to_date:
            date_range_filter["lte"] = data.to_date
        
        filters.append({
            "range": {
                "upload_date": date_range_filter
            }
        })
    must = []
    if data.query:
        must.append( {
                    "multi_match": {
                        "query": data.query,
                        "fields": ["filename", "title", "description", "content"]
                    }
                }); 


    # Define a search query
    return {
        "bool": {
            "must": must,
            "filter": filters
        }
    }

def create_jwt_token(username: str, role: int):
    expiration = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({"sub": username, "role": role, "exp": expiration}, SECRET_KEY, algorithm=ALGORITHM)
    return token

def getuserdatafromCookie(token:str):
    try:
        username: str = ""
        userrole: int = 0
        if token :
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            userrole = payload.get("role")
            if username is None:
                raise credentials_exception
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user for uploada file",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"username" : username, "userrole" : userrole}


@app.post("/api/token")
async def login(response: Response, user: User):
    user_data = authenticate_user(user.username, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_jwt_token(user.username, user_data["role"])
    # Set the JWT token in an HTTP-only session cookie
    response.set_cookie(
        key="session_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,  # Cookie expires in the same time as the token
        expires=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        #secure=True,  # Set to True if using HTTPS
        samesite="Lax"  # or 'Strict' depending on your needs
    )
    return {"msg": "Login successful"}

@app.post("/api/logout")
def logout(response: Response):
    # Clear the cookie by setting it to an empty value and expiring it immediately
    response.delete_cookie(key="session_token")
    return {"message": "Logged out successfully"}

"""
@app.get("/searchbyembedding/")
async def search(query: str):
    # Perform text embedding using SentenceTransformer
    model = SentenceTransformer('quora-distilbert-multilingual')
    embedding = model.encode(query, show_progress_bar=False)

    # Build the Elasticsearch script query
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                "params": {"query_vector": embedding.tolist()}
            }
        }
    }

    # Execute the search query
    search_results = es.search(index=index_name, body={"query": script_query})

    # Process and return the search results
    results = search_results["hits"]["hits"]
    return {"results": results}

"""