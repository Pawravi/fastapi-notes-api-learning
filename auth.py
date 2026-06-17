import bcrypt
from datetime import datetime,timedelta,timezone
from jose import jwt, JWTError
from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import session
from database import get_db
from models import UserDB



#jwt configuration
SECRET_KEY="codewithpawravi"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")



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

