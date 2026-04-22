from fastapi import FastAPI

from app.database import init_db
from app.routers import users

app = FastAPI(title="Hamster Finance")

app.include_router(users.router)


@app.on_event("startup")
async def on_startup():
    await init_db()


@app.get("/")
async def root():
    return {"message": "Hello World"}
