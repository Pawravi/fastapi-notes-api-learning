from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel



app=FastAPI()

class Note(BaseModel):
    note_id:int
    note_name:str

notes_db={}   

@app.get("/notes/{note_id}")
def get_note(note_id:int):
    return notes_db.get(note_id,{"error":"not found"})

@app.get("/notes-name{note_name}")
def notes_name(note_name:str):
    return notes_name

@app.post("/create-notes")
def create_notes(note:Note):
    if note.note_id in notes_db:
      return {"error":"Note ID already exists"}
    notes_db[note.note_id]=note.model_dump()
    return notes_db[note.note_id]

@app.put("/note_update{note_id}")
def update_note(note_id:int,note:Note):
    if note_id not in notes_db:
        return {"error":"note ID does not exists."}
    notes_db[note_id]=note.model_dump()
    return{"success":"note updated!"}

@app.delete("/delete-note{note_id}")
def delete_note(note_id:int):
    if note_id not in notes_db:
        return{"error":"note ID does not exist."}
    delete_note=notes_db.pop(note_id)
    return{"success":"note deleted!"}




