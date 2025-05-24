import asyncio
import time
import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import FileResponse, PlainTextResponse, HTMLResponse
from starlette.websockets import WebSocketDisconnect

from app.lib.extract import extract_curve_metrics, extract_multi_curves, run_loop
from cache.local_cache import ResultsCache

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
    asyncio.create_task(run_loop())
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

    uvicorn.run(app, host=host, port=int(port),ws_ping_timeout=None,log_config=None)

@app.get("/", response_class=HTMLResponse)
def home():
    return "<h1> STATUS </h1>"

@app.get("/log", response_class=HTMLResponse)
def log():
    for h in logging.getLogger().handlers:
        if h.name == "file":
            return FileResponse(h.baseFilename)

    return PlainTextResponse("no file logger configured")

@app.get("/analytic_build_curve", response_class=HTMLResponse)
def extract_analytic_build_curve(curve_name: str = "SONIA"):
    df = extract_curve_metrics()
    return JSONResponse(
        content = jsonable_encoder(
            df.fillna("").to_dict(orient="records")
        )
    )

@app.get("/multi_analytic_build_curve", response_class=HTMLResponse)
async def extract_multi_analytic_build_curve():
    df  = await extract_multi_curves()
    return JSONResponse(
        content = jsonable_encoder(
            df.fillna("").to_dict(orient="records")
        )
    )

import pandas as pd
from fastapi import WebSocket
from typing import List
from datetime import datetime

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] =[]

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        await asyncio.gather(
            *[connection.send_text(message) for connection in self.active_connections]
        )

manager = ConnectionManager()
# conda activate adel_tst
# python -m websocket ws://localhost:8000/ws

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_id = 10
    await manager.connect(websocket)
    try:
        while True:
            df = pd.DataFrame(ResultsCache().get_all_results())
            df["TimeStame"] = datetime.now().isoformat()
            json_str = df.to_json(orient="records")
            await manager.send_message(json_str, websocket)
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} disconnected ")
    except Exception as ex:
        print(f"Error: {ex}")
        manager.disconnect(websocket)