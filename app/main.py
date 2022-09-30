"""FastAPI configuration file.

Middlewares, routers must be connected here.
"""

from os import environ

from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .app import app
from .routers import example

# Setup logger
if environ.get("LOG_FILE") is not None:
    logger.add(
        environ.get("LOG_FILE", "logs.txt"),
        rotation="100 MB",
        retention="2 days",
        backtrace=True,
        diagnose=True,
    )

# Check for required environment variables
required_env = ["DB_URL", "IPFS_URL", "SECRET"]
for env in required_env:
    if environ.get(env) is None:
        logger.error(f"{env} is not present in environment variables. Exiting...")
        exit(1)


origins = [environ.get("ORIGIN", "*")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=str)
async def hello_world() -> str:
    """Hello world endpoint."""
    return "Hello world!"


app.include_router(example.router)


@app.on_event("startup")
def on_start() -> None:
    """Started FastAPI event."""
    logger.info("Started")
