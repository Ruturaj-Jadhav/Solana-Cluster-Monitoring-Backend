from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown
    pass


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan,
    )

    # Include API router
    application.include_router(api_router, prefix=settings.API_V1_STR)

    return application


app = create_application()


@app.get("/")
async def root():
    return {"message": "Solana Parent-Child Wallet Detection API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"} 