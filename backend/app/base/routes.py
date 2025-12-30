from litestar import Response, Router, get
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@get("/health")
async def health_check() -> Response:
    return Response(content={"detail": "ok"}, status_code=200)


@get("/db_health")
async def db_health_check(transaction: AsyncSession) -> Response:
    # Simple query to wake Aurora and verify connectivity
    # Litestar will handle any exceptions (connection errors, timeouts, etc.)
    await transaction.execute(text("SELECT 1"))
    return Response(content={"detail": "ok", "database": "connected"}, status_code=200)


# System router for health checks and monitoring endpoints
# No authentication required - used by ALB, monitoring, and public warmup
system_router = Router(
    path="/",
    route_handlers=[health_check, db_health_check],
    tags=["system"],
    guards=[],
)
