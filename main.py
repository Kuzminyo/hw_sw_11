from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.database.db import engine, get_db
from src.database.models import Base
from src.routes import contacts


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Contacts API",
    description="REST API for storing and managing contacts (FastAPI + SQLAlchemy + PostgreSQL).",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(contacts.router, prefix="/api")


@app.get("/", tags=["root"])
def root():
    return {"message": "Contacts API. Docs: /docs"}


@app.get("/api/healthchecker", tags=["root"])
def healthchecker(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=500, detail="Error connecting to the database")
    return {"message": "Database is up"}
