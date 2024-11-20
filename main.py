from fastapi import FastAPI
from money_manager.init import app as money_manager
from fastapi.staticfiles import StaticFiles

prefix = '/api'
app = FastAPI()

app.mount(f"{prefix}/manager", money_manager)
