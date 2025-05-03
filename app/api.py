import time

import uvicorn
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, status, Depends
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from starlette.responses import FileResponse, PlainTextResponse, HTMLResponse

logger = logging.getLogger(__name__)

def make_process_time_middleware():
    async def add_process_time_header(request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    return add_process_time_header


@asynccontextmanager
async def start_api(api_app: FastAPI):
    logger.info(f"Starting API with {api_app.title}")
    logger.info(f"API version starting : {api_app.version}")
    yield
    logger.info(f"API version shutting down")

app = FastAPI(lifespan=start_api)
static_path = Path(__file__).parent.parent / "app/html"
app.mount("/static", app=StaticFiles(directory=static_path), name="static")
favicon_path = static_path / "favicon.ico"

def start_rest_api(log_level):
    host = "127.0.0.1"
    port = "8000"
    protocols = ["http","https","ws","wss"]
    origins = [f"{protocol}://{host}:{port}" for protocol in protocols]
    logger.info(f"Premitted origins {origins}")
    app.middleware("http")(make_process_time_middleware())

    app.add_middleware(CORSMiddleware,
                       allow_origins=["*"],
                       allow_methods=["*"],
                       allow_headers=["*"],
                       allow_credentials=True,)
    app.add_middleware(GZipMiddleware, minimum_size=10000)

    uvicorn.run(app, host=host, port=port, log_level=log_level.lower(),ws_ping_timeout=None,log_config=None)

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1> STATUS </h1>"

@app.get("/log", response_class=HTMLResponse)
def home():
    for h in logging.getLogger().handlers:
        if h.name == "file":
            return FileResponse(h.baseFilename)

    return PlainTextResponse("no file logger configured")
