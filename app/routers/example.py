"""Example router."""

from fastapi import APIRouter

router: APIRouter = APIRouter(prefix="/example")


@router.get("/", response_model=str)
async def get_example() -> str:
    """Example router endpoint."""
    return "example response"
