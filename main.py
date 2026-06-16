#imports
from fastapi import FastAPI,HTTPException
from typing import Optional,List
from pydantic import BaseModel,Field,field_validator
from datetime import datetime,timedelta,timezone
from sqlalchemy import Column, Integer, String,Boolean,DateTime
from database import Base, engine
from database import sessionlocal
from fastapi import Depends
from sqlalchemy.orm import session
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
import bcrypt

#app
app=FastAPI()
#jwt configuration
SECRET_KEY="codewithpawravi"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")


#database model
class NoteDB(Base):
    __tablename__="notes"
    id= Column(Integer,primary_key=True, index=True )
    title=Column(String)
    content=Column(String,nullable=False)
    category=Column(String,nullable=True)
    is_important=Column(Boolean,default=False)
    created_at=Column(DateTime,default=datetime.utcnow)
    user_id=Column(Integer)


#user database   
class UserDB(Base):
    __tablename__="users"
    id=Column(Integer, primary_key=True,index=True)
    username=Column(String,unique=True,index=True)
    email=Column(String,unique=True,index=True)
    password=Column(String)


#create tables
print(Base)
print(type(Base))
Base.metadata.create_all(bind=engine)

#dependency
def get_db():
    db=sessionlocal()
    try:
        yield db
    finally:
        db.close()


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
    
 #input model for users   
class UserCreate(BaseModel):
    username:str
    email:str
    password:str
    
 #user login model
class UserLogin(BaseModel):
    username:str
    password:str


 #output model

class NoteResponse(BaseModel):
    id:int
    tile:str
    content:str
    category:Optional[str]
    is_important:bool
    created_at: datetime   

 #output model for users
class UserResponse(BaseModel):
    id:int
    email:str
    username:str

#to convert sqlalchemy object into reponsemodel
class config:
    from_attributes=True


#handler function or hashed password
def hash_pwd(password:str,rounds=12)->str:
    pwd=bcrypt.hashpw(password.encode(),bcrypt.gensalt(rounds=rounds))
    return pwd.decode()


def verify_password(plain_password:str,hashed_password:str) ->bool:
    return bcrypt.checkpw(plain_password.encode(),hashed_password.encode())


def create_access_token(data:dict):
    to_encode=data.copy()
    expire = datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token:str=Depends(oauth2_scheme),db:session=Depends(get_db)):
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get("sub")
        if username is None:
           raise HTTPException(status_code=401,detail="invalid token!")
        db_user=(db.query(UserDB).filter(UserDB.username ==username)).first()
        if db_user is None:
            raise HTTPException(status_code=401,detail="user not found!")
        
        return db_user 

    except JWTError:
            raise HTTPException(status_code=401,detail="invalid token!")





#get by ID
@app.get("/notes/{note_id}")
def get_note(note_id:int,db:session=Depends(get_db)):
   note=db.query(NoteDB).filter(NoteDB.id==note_id).first()
   if not note:
    raise HTTPException(status_code=404,detail="Note not found!")
   return note



#get ALL
@app.get("/notes")
def get_notes(db:session=Depends(get_db)):
    notes= db.query(NoteDB).all()
    return notes


#CREATE
@app.post("/notes")
def create_note(note:NoteCreate,current_user=Depends(get_current_user),db:session=Depends(get_db)):


    new_note=NoteDB(
        title=note.title,
        content=note.content,
        category=note.category,
        is_important=note.is_important,
        user_id= current_user.id
        )
       
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note

#post endpoint for users
@app.post("/users",response_model=UserResponse)
def create_users(user:UserCreate,db:session=Depends(get_db)):

    new_user=UserDB(
        username=user.username,
        email=user.email,
        password=hash_pwd(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#user login
@app.post("/login")
def login(user:UserLogin,db:session=Depends(get_db)):
    db_user=db.query(UserDB).filter(UserDB.username==user.username).first()
    if not db_user:
        raise HTTPException(status_code=401,detail="invalid username or password")
    if not verify_password(user.password,db_user.password):
        raise HTTPException(status_code=401,detail="invalid username or password")
    access_token=create_access_token({"sub":db_user.username})
    return {"access_token": access_token, "message": "login successful!"}



#UPDATE
@app.put("/note/{note_id}")
def update_note(note_id:int,updated_note:NoteCreate,db:session=Depends(get_db)):
   note=db.query(NoteDB).filter(NoteDB.id==note_id).first()
   if not note:
       raise HTTPException(status_code=404,detail="Note not Found!")
   
   note.title = updated_note.title
   note.content = updated_note.content
   note.category = updated_note.category
   note.is_important = updated_note.is_important
   
   db.commit()
   db.refresh(note)
   return note

    

#DELETE

@app.delete("/note/{note_id}")
def delete_note (note_id:int,db:session=Depends(get_db)):
   note=db.query(NoteDB).filter(NoteDB.id==note_id).first()

   if not note:
       raise HTTPException(status_code=404,detail="Note not found!")
   
   db.delete(note)
   db.commit()
   return{"message":"note deleted succesfully"}


# protected route
@app.get("/profile")
def profile(current_user:UserDB=Depends(get_current_user)):
    return {"user":current_user.id,"username":current_user.username,"email":current_user.email}
      
@app.get("/test_token")
def test_token(current_user:UserDB=Depends(get_current_user)):
    return{"username":current_user.username}



