import typer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api import routes_scan, routes_reports, routes_tools
from core.queue_manager import initialize_queue
from database.db_connect import create_db_and_tables, close_db_connection
from utils.logger import logger
from config import settings
from worker import run_worker

cli = typer.Typer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    logger.info("Starting up CyberSentinel backend...")
    await create_db_and_tables()
    await initialize_queue()
    yield
    logger.info("Shutting down CyberSentinel backend...")
    await close_db_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Enterprise-grade cybersecurity command platform.",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(routes_scan.router, prefix="/api/scan", tags=["Scan"])
app.include_router(routes_reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(routes_tools.router, prefix="/api/tools", tags=["Tools"])


@app.get("/", tags=["Health Check"])
async def read_root():
    """
    Root endpoint for health check.
    """
    return {"status": "CyberSentinel backend is running"}


@cli.command()
def run_api():
    """
    Run the FastAPI application.
    """
    import uvicorn
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)

@cli.command()
def worker():
    """
    Run the background worker process.
    """
    logger.info("Starting background worker...")
    run_worker()


if __name__ == "__main__":
    cli()
