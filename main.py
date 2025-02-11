from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from money_manager.init import app as money_manager

prefix = '/api'
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount(f"{prefix}/manager", money_manager)
