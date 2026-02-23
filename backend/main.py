from fastapi import FastAPI  # type: ignore
import os

from backend.routers import auth, posts, users

app = FastAPI()

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(users.router)


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok"}
