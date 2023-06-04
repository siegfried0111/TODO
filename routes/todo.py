from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends, Path
from sqlalchemy.orm import Session
from database import SessionLocal, Todo
from pydantic import BaseModel, Field
from .auth import get_user_from_token

route = APIRouter(prefix="/todo", tags=["todo"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_user_from_token)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
    complete: bool = Field(False)


@route.get('', status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, user: user_dependency):
    return db.query(Todo).filter(Todo.owner_id == user.get('id')).all()


@route.get('/{todo_id}')
async def read_todo_by_id(db: db_dependency, user: user_dependency, todo_id: int = Path(ge=1)):
    todo_data = (
        db.query(Todo).filter(Todo.id == todo_id)
        .filter(Todo.owner_id == user.get('id'))
        .first()
    )
    if todo_data is not None:
        return todo_data
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Todo todo_id={todo_id} not found')


@route.post('', status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoRequest, user: user_dependency, db: db_dependency):
    todo_model = Todo(**todo.dict(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()


@route.put('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo_by_id(db: db_dependency, todo: TodoRequest, user: user_dependency, todo_id: int = Path(ge=1)):
    todo_data = (
        db.query(Todo).filter(Todo.id == todo_id)
        .filter(Todo.owner_id == user.get('id'))
        .first()
    )
    if todo_data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Todo todo_id={todo_id} not found')
    todo_data.title = todo.title
    todo_data.description = todo.description
    todo_data.priority = todo.priority
    todo_data.complete = todo.complete
    db.add(todo_data)
    db.commit()
    # return



@route.delete('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo_by_id(db: db_dependency, user: user_dependency, todo_id: int = Path(ge=1)):
    todo_data = (
        db.query(Todo).filter(Todo.id == todo_id)
        .filter(Todo.owner_id == user.get('id'))
        .first()
    )

    if todo_data is not None:
        db.delete(todo_data)
        db.commit()
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Todo todo_id={todo_id} not found')
