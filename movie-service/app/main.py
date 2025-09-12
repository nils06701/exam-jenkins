from fastapi import FastAPI
import asyncio
from app.api.movies import movies
from app.api.db import metadata, database, engine

metadata.create_all(engine)

app = FastAPI(openapi_url="/api/v1/movies/openapi.json", docs_url="/api/v1/movies/docs")

@app.on_event("startup")
async def startup():
    await asyncio.sleep(5)
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


app.include_router(movies, prefix='/api/v1/movies', tags=['movies'])