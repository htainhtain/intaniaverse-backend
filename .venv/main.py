from os import access
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from hashing import Hash
from datetime import timedelta
from jwttoken import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from oauth import get_current_user


##
# Database
##
mongodb_uri = 'mongodb+srv://loyar:l85WoPCln2z0Aefh@cluster0.dh0g9cd.mongodb.net/?retryWrites=true&w=majority'
port = 8000
client = MongoClient(mongodb_uri, port)
db = client["VerseUser"]
 

class User(BaseModel):
    firstname: str
    lastname: str
    username: str
    email: str
    password: str
    disabled: bool | None = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


app = FastAPI()

origins = {
    "http://localhost:3000",
    "http://www.intaniaverse.com",
    "http://intaniaverse.com"
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Authentication
@app.get("/", tags=["Authentication"])
async def root(current_user: User = Depends(get_current_user)):
    return {'current user': current_user}


@app.post('/register', tags=["Authentication"])
def create_user(request: User):
    user_object = dict(request)
    user_id = db['users'].insert_one(user_object)
    return {"res": "created"}


@app.post('/login', response_model=Token, tags=["Authentication"])
def login(request: OAuth2PasswordRequestForm = Depends()):
    print('request: ', request)
    user = db['users'].find_one({"username": request.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not Hash.verify_password(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
