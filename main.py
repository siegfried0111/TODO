from fastapi import FastAPI
from routes import todo

app = FastAPI()

app.include_router(todo.route)


























