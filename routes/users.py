from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field
from database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated
from .auth import get_user_from_token, ctx

from database import User

route = APIRouter(prefix='/users', tags=['users'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_user_from_token)]


class PWRequest(BaseModel):
    old_password: str = Field(min_length=1)
    new_password: str = Field(min_length=1)


class UserRequest(BaseModel):
    email: str = Field(min_length=1)
    username: str = Field(min_length=1)
    firstname: str = Field(min_length=1)
    lastname: str = Field(min_length=1)
    non_hash_password: str = Field(min_length=1)
    is_active: bool = Field(default=True)
    role: str = Field(min_length=1)


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


@route.get('')
async def get_user(user: user_dependency, db: db_dependency):

    return db.query(User).filter(User.id == user.get('id')).first()


@route.post('/ChgPW', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, pw: PWRequest):
    user_model = db.query(User).filter(User.id == user.get('id')).first()
    if user_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'user id={user.get("id")} not founded')
    if not ctx.verify(pw.old_password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f'Error Old Password')
    user_model.hashed_password = ctx.hash(pw.new_password)
    db.commit()
