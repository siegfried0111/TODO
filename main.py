from fastapi import FastAPI
from routes import todo, auth

app = FastAPI()

app.include_router(todo.route)
app.include_router(auth.route)


























