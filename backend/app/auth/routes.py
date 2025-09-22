"""Authentication-related routes and user management."""

from litestar import Request, Router, post

from app.auth.google.routes import google_auth_router


@post("/logout")
async def logout_user(request: Request) -> None:
    request.clear_session()


# Authentication router
auth_router = Router(
    path="/auth",
    route_handlers=[
        logout_user,
        google_auth_router,
    ],
    tags=["auth"],
)
