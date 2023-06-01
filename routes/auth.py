from datetime import datetime, timedelta
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import User, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

route = APIRouter(prefix='/auth', tags=['authenticate'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class UserRequest(BaseModel):
    email: str = Field(min_length=1)
    username: str = Field(min_length=1)
    firstname: str = Field(min_length=1)
    lastname: str = Field(min_length=1)
    non_hash_password: str = Field(min_length=1)
    is_active: bool = Field(default=True)
    role: str = Field(min_length=1)


ctx = CryptContext(
    schemes=["pbkdf2_sha256", "des_crypt"],
    default="pbkdf2_sha256"
)

Secret_Key = 'Qekkvw51cqwfJy8jQx/rNbmewkhXRAK7oV43wbnbJvk='
Algo = 'HS256'


def jwt_token(payload):
    return jwt.encode(claims=payload, key=Secret_Key, algorithm=Algo)


@route.post('', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, body: UserRequest):
    user_data = User(
        email=body.email,
        username=body.username,
        firstname=body.firstname,
        lastname=body.lastname,
        hashed_password=ctx.hash(body.non_hash_password),
        is_active=body.is_active,
        role=body.role
    )
    try:
        db.add(user_data)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f'{e}')


@route.post('/token')
async def get_token(form_body: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user_data = db.query(User).filter(User.username == form_body.username).first()
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    if not ctx.verify(form_body.password, user_data.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    payload = {
       'sub': user_data.username,
       'id': user_data.id,
       'exp': datetime.now() + timedelta(minutes=10)
    }
    token = jwt.encode(claims=payload, key=Secret_Key, algorithm=Algo)
    return {'token': token, 'type': 'bearer'}

# payload = {
#        'sub': "A",
#        'id': 1,
#        'exp': datetime.now() + timedelta(minutes=10)
#     }
# print(jwt.encode(claims=payload, key=Secret_Key, algorithm=Algo))