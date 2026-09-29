from fastapi import FastAPI

from src.api import contacts, utils

app = FastAPI()

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")