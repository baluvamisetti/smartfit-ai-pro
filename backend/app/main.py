import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.routers import analysis, skin, recommend, stats
from app.db.database import init_db, SessionLocal
from app.db.models import RequestLog
from app.core.logging_config import logger

app = FastAPI(
    title="SmartFit AI Pro X",
    description="AI Fashion Intelligence Platform - Body & Skin Tone Analysis + Recommendations",
    version="1.0.0-mvp",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    init_db()
    logger.info("SmartFit AI Pro X backend started", extra={"event": "startup"})


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logs every request to stdout (structured JSON) and to the request_logs
    table, so you have both live tail logs and queryable history."""
    start = time.time()
    error_detail = None
    try:
        response = await call_next(request)
        status_code = response.status_code
    except Exception as exc:
        status_code = 500
        error_detail = str(exc)
        logger.error(
            "Unhandled exception",
            extra={"path": request.url.path, "method": request.method, "error": error_detail},
        )
        raise
    finally:
        duration_ms = round((time.time() - start) * 1000, 2)
        logger.info(
            "request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": locals().get("status_code", 500),
                "duration_ms": duration_ms,
            },
        )
        try:
            db = SessionLocal()
            db.add(RequestLog(
                method=request.method,
                path=request.url.path,
                status_code=locals().get("status_code", 500),
                duration_ms=duration_ms,
                client_ip=request.client.host if request.client else None,
                error_detail=error_detail,
            ))
            db.commit()
            db.close()
        except Exception:
            logger.warning("Failed to write request log to DB")

    return response


app.include_router(analysis.router)
app.include_router(skin.router)
app.include_router(recommend.router)
app.include_router(stats.router)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "SmartFit AI Pro X Backend",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
