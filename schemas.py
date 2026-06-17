from pydantic import BaseModel, Field,field_validator
from typing import Optional
from datetime import datetime



#to convert sqlalchemy object into reponsemodel
class config:
    from_attributes=True

#input model for users   
class UserCreate(BaseModel):
    username:str
    email:str
    password:str
    
 #user login model
class UserLogin(BaseModel):
    username:str
    password:str

 #output model for users
class UserResponse(BaseModel):
    id:int
    email:str
    username:str

#input model 

class NoteCreate(BaseModel):
    title:str=Field(...,min_length=3,max_length=100)
    content:str=Field(...,min_length=5,max_length=100000)
    category:Optional[str]=Field(None,max_length=50)
    is_important:bool=False

    @field_validator("title")
    @classmethod
    def clean_title(cls,value):
        value=value.strip()
        if not value:
            raise ValueError("Title cannot be blank")
        return value
    


 #output model

class NoteResponse(BaseModel):
    id:int
    tile:str
    content:str
    category:Optional[str]
    is_important:bool
    created_at: datetime  