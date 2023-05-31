from typing import Annotated
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, status, HTTPException
from database import User, SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext

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



# @route.get('', status_code=)
