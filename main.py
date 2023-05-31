from fastapi import FastAPI
from routes import todo, user

app = FastAPI()

app.include_router(todo.route)
app.include_router(user.route)


























