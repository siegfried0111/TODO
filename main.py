from fastapi import FastAPI
from routes import todo, auth, admin, users

app = FastAPI()

app.include_router(todo.route)
app.include_router(auth.route)
app.include_router(admin.route)
app.include_router(users.route)


























