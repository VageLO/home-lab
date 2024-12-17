from fastapi import FastAPI
from money_manager.init import app as money_manager

prefix = '/api'
app = FastAPI()

app.mount(f"{prefix}/manager", money_manager)
