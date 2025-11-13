import structlog
from litestar import Response, get


@get("/health", tags=["system"], guards=[])
async def health_check() -> Response:
    """Health check endpoint."""
    return Response(content={"detail": "ok"}, status_code=200)
