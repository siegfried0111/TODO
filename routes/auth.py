from datetime import datetime, timedelta
from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from database import User, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError

route = APIRouter(prefix='/auth', tags=['authenticate'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/auth/token')

Secret_Key = 'Qekkvw51cqwfJy8jQx/rNbmewkhXRAK7oV43wbnbJvk='
Algo = 'HS256'

ctx = CryptContext(
    schemes=["pbkdf2_sha256", "des_crypt"],
    default="pbkdf2_sha256"
)


@route.post('/token')
async def authenticate(form_body: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user_data = db.query(User).filter(User.username == form_body.username).first()
    if user_data is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    if not ctx.verify(form_body.password, user_data.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    payload = {
        'user': user_data.username,
        'id': user_data.id,
        'role': user_data.role,
        'exp': datetime.now() + timedelta(minutes=10)
    }
    token = jwt.encode(claims=payload, key=Secret_Key, algorithm=Algo)
    return {'access_token': token, 'token_type': 'bearer'}


async def get_user_from_token(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, Secret_Key, algorithms=Algo)
        if payload.get('user') is None or payload.get('id') is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not verify the user.')
        else:
            return {'user': payload['user'], 'id': payload['id'], 'role': payload['role']}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='JWTError, Could not verify the user.')
