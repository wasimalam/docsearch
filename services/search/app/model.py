from pydantic import BaseModel
class SeacrhRequest(BaseModel):
    query: str
    author: str
    tags: str
    from_date: str
    to_date:str
    size: int
    offset: int

# Define Pydantic models
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class DBSettings(BaseModel):
    user:str
    password:str
    port:int
    dbname:str
    host:str
class ElasticSearchSettings(BaseModel):
    server:str
    port:int
    document_index:str
class GeneralSettings(BaseModel):
    loglevel :str

class StorageSettings(BaseModel):
    folder:str

class Config(BaseModel):
    general:GeneralSettings
    db:DBSettings
    es:ElasticSearchSettings
    storage:StorageSettings

