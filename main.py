#imports
from fastapi import FastAPI,HTTPException
from database import Base,engine
from database import sessionlocal
from fastapi import Depends
from sqlalchemy.orm import session
from models import NoteDB,UserDB
from schemas import (UserCreate,UserLogin,UserResponse,NoteCreate,NoteResponse)
from auth import(hash_pwd,verify_password,create_access_token,get_current_user,oauth2_scheme)
from database import get_db
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
#app
app=FastAPI()


#create tables
print(Base)
print(type(Base))
Base.metadata.create_all(bind=engine)



#get by ID
@app.get("/notes/{note_id}")
def get_note(note_id:int,db:session=Depends(get_db)):
   note=db.query(NoteDB).filter(NoteDB.id==note_id).first()
   if not note:
    raise HTTPException(status_code=404,detail="Note not found!")
   return note



#get ALL
@app.get("/notes")
def get_notes(db:session=Depends(get_db),current_user:UserDB=Depends(get_current_user)):
    return (db.query(NoteDB).filter(NoteDB.user_id==current_user.id).all())


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
def login(from_data:OAuth2PasswordRequestForm=Depends(),db:session=Depends(get_db)):
    db_user=db.query(UserDB).filter(UserDB.username==from_data.username).first()
    if not db_user:
        raise HTTPException(status_code=401,detail="invalid username or password")
    if not verify_password(from_data.password,db_user.password):
        raise HTTPException(status_code=401,detail="invalid username or password")
    access_token=create_access_token({"sub":db_user.username})
    return {"access_token": access_token, "message": "login successful!"}



#UPDATE
@app.put("/note/{note_id}")
def update_note(note_id:int,updated_note:NoteCreate,db:session=Depends(get_db),current_user:UserDB=Depends(get_current_user)):
   note=(db.query(NoteDB).filter(NoteDB.id==note_id,NoteDB.user_id==current_user.id).first())
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
def delete_note (note_id:int,db:session=Depends(get_db),current_user:UserDB=Depends(get_current_user)):
   note=(db.query(NoteDB).filter(NoteDB.id==note_id,NoteDB.user_id==current_user.id).first())

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



