from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import init_db
from app.routers import clients, entries

app = FastAPI(title="Timeline Generator")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(clients.router)
app.include_router(entries.router)


@app.on_event("startup")
async def startup():
    init_db()
