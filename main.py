from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers import post, post_comment, user
from db.database import engine
from fastapi.staticfiles import StaticFiles
from auth import authentication

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(post_comment.router)

app.mount("/media", StaticFiles(directory="media"), name="media")