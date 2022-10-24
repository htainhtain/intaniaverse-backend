from fastapi import Depends, HTTPException, status
from jwttoken import verify_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jwttoken import SECRET_KEY, ALGORITHM
from jwttoken import TokenData
from pymongo import MongoClient
# from main import db

##
# Database
##
mongodb_uri = 'mongodb+srv://loyar:l85WoPCln2z0Aefh@cluster0.dh0g9cd.mongodb.net/?retryWrites=true&w=majority'
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["VerseUser"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db['users'].find_one({"username": token_data.username})
    if user is None:
        raise credentials_exception
    return user['username']
