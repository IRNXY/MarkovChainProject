from fastapi import FastAPI
# from core.config import settings
from .api.routes import api_router
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI(title="Markov Chain IIR Project")

app.include_router(api_router, prefix="/api/v1")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


app.mount("/styles", StaticFiles(directory=os.path.join(FRONTEND_DIR, "styles")), name="styles")
app.mount("/js", StaticFiles(directory=os.path.join(FRONTEND_DIR, "js")), name="js")
app.mount("/pages", StaticFiles(directory=os.path.join(FRONTEND_DIR, "pages")), name="pages")


@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "pages/index.html"))


@app.get("/health")
async def root():
    return "All good"
