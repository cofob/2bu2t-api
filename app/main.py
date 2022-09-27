"""FastAPI configuration file.

Middlewares, routers must be connected here.
"""

from os import environ

from fastapi.middleware.cors import CORSMiddleware

from .app import app
from .routers import example

# Check for required environment variables
required_env = ["DB_URL", "IPFS_URL"]
for env in required_env:
    if environ.get(env) is None:
        print(f"{env} is not present in environment variables. Exiting...")
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
