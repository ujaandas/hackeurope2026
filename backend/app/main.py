from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import init_db
from app.analyzer.engine import AnalysisEngine
from app.analyzer.patterns.sorting import SortingPatternDetector
from app.analyzer.patterns.memory import MemoryPatternDetector
from app.analyzer.patterns.network import NetworkPatternDetector
from app.routers import analyze, optimize, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    engine = AnalysisEngine()
    engine.register(SortingPatternDetector())
    engine.register(MemoryPatternDetector())
    engine.register(NetworkPatternDetector())
    app.state.engine = engine
    yield
    # Shutdown - nothing to clean up


app = FastAPI(
    title="GreenLinter API",
    description="AI-powered code energy efficiency analyzer",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api")
app.include_router(optimize.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health")
async def health():
    return {"status": "ok"}
