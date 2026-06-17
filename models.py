from sqlalchemy import Column, Integer, String,Boolean,DateTime
from database import Base, engine
from datetime import datetime



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
