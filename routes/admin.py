from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends, Path
from sqlalchemy.orm import Session
from database import SessionLocal, Todo
from pydantic import BaseModel, Field
from .auth import get_user_from_token

route = APIRouter(prefix='/admin', tags=['admin'])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_user_from_token)]


@route.get('/todo', status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency, user: user_dependency):
    if user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return db.query(Todo).all()


@route.delete('/todo/delete/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(ge=1)):
    if user['role'] != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'todo_id={todo_id} is not found.')
    db.delete(todo_model)
    db.commit()


