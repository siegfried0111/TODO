from typing import Annotated
from fastapi import APIRouter, HTTPException, status, Depends, Path
from sqlalchemy.orm import Session
from database import SessionLocal, Todo
from pydantic import BaseModel, Field

route = APIRouter(prefix="/todo", tags=["todo"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=1)
    description: str = Field(min_length=1)
    priority: int = Field(ge=1, le=5)
    complete: bool = Field(False)


@route.get('', status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency):
    return db.query(Todo).all()


@route.get('/{todo_id}')
async def read_todo_by_id(db: db_dependency, todo_id: int = Path(ge=1)):
    todo_data = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_data is not None:
        return todo_data
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Todo todo_id={todo_id} not found')


@route.post('', status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoRequest, db: db_dependency):
    todo_model = Todo(**todo.dict())
    db.add(todo_model)
    db.commit()


@route.put('/{todo_id}', status_code=status.HTTP_202_ACCEPTED)
async def update_todo_by_id(db: db_dependency, todo: TodoRequest, todo_id: int = Path(ge=1)):
    todo_data = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_data is not None:
        todo_data.title = todo.title
        todo_data.description = todo.description
        todo_data.priority = todo.priority
        todo_data.complete = todo.complete
        db.commit()
        return todo_data
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Todo todo_id={todo_id} not found')


@route.delete('/{todo_id}', status_code=status.HTTP_202_ACCEPTED)
async def delete_todo_by_id(db: db_dependency, todo_id: int = Path(ge=1)):
    todo_data = db.query(Todo).filter(Todo.id == todo_id).first()
    print(todo_data)
    if todo_data is not None:
        db.delete(todo_data)
        db.commit()
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Todo todo_id={todo_id} not found')
