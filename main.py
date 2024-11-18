from fastapi import FastAPI
from money_manager.init import app as money_manager
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/money-manager", money_manager)

@app.get('/')
async def homeLab():
    return {"message": "Home Lab - Home page"}
