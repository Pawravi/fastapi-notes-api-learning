from fastapi import FastAPI,HTTPException
from typing import Optional,List
from pydantic import BaseModel,Field,field_validator
from datetime import datetime



app=FastAPI()

notes_db={}
next_id=1 
#input model 

class NoteCreate(BaseModel):
    title:str=Field(...,min_length=3,max_length=100)
    content:str=Field(...,min_length=10,max_length=100000)
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
    note_id:int
    tile:str
    content:str
    category:Optional[str]
    is_important:bool
    created_at: datetime   

    
#get by ID
@app.get("/notes/{note_id}",response_model=NoteResponse)
def get_note(note_id:int):
    if note_id not in notes_db:
     raise HTTPException(status_code=404,detail="Note not found!")
    return notes_db[note_id]



#get ALL
@app.get("/notes",response_model=NoteResponse)
def get_all_notes():
    return list(notes_db.values())


#CREATE
@app.post("/notes",response_model=NoteResponse)
def create_notes(note:NoteCreate):
    global next_id

    new_note={
        "note_id":next_id,
        "title":note.title,
        "content":note.content,
        "category":note.category,
        "is_important":note.is_important,
        "Created_at":datetime.utcnow()
    }
    notes_db[next_id]=new_note
    next_id +=1
    return new_note


   
#UPDATE
@app.put("/note/{note_id}")
def update_note(note_id:int,note:NoteCreate):
    if note_id not in notes_db:
        raise HTTPException(status_code=404,detail="Note not Found!")
    updated_note={
        "note_id":note_id,
        "title":note.title,
        "content":note.content,
        "category":note.category,
        "is_important":note.is_important,
        "created_at":notes_db[note_id]
        ["created_at"] #keep original time
    }
    notes_db[note_id]=updated_note
    return updated_note

#DELETE

@app.delete("/note/{note_id}")
def delete_note(note_id:int):
    if note_id not in notes_db:
       raise HTTPException(status_code=404,detail="Note not found!")
    deleted_note=notes_db.pop(note_id)
    return{"success":"note deleted!","note":deleted_note}




