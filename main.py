from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from routers import feed, post, post_comment, post_like, upload, user, user_follow
from db.database import engine
from auth import authentication
import logfire

@asynccontextmanager
async def lifespan(_app: FastAPI):
    yield
    # Shutdown
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title="Instagram API",
    description="A FastAPI backend for a social photo-sharing app.",
)
templates = Jinja2Templates(directory="templates")
API_PREFIX = "/api/v1"


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def homepage(request: Request):
    return templates.TemplateResponse(request, "index.html")

logfire.configure()
logfire.instrument_fastapi(app)
logfire.instrument_pydantic()
logfire.instrument_sqlalchemy(engine=engine)

app.include_router(user.router, prefix=API_PREFIX)
app.include_router(authentication.router, prefix=API_PREFIX)
app.include_router(post.router, prefix=API_PREFIX)
app.include_router(post_comment.router, prefix=API_PREFIX)
app.include_router(post_like.router, prefix=API_PREFIX)
app.include_router(user_follow.router, prefix=API_PREFIX)
app.include_router(feed.router, prefix=API_PREFIX)
app.include_router(upload.router, prefix=API_PREFIX)
