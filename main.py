from contextlib import asynccontextmanager


from fastapi import FastAPI
from routers import comment, post, user
from db.database import engine, Base
from fastapi.staticfiles import StaticFiles
from auth import authentication

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(authentication.router)
app.include_router(comment.router)

app.mount("/images", StaticFiles(directory="images"), name="images")