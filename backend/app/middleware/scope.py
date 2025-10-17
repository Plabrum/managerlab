"""Scope middleware for multi-tenancy.

Extracts scope from session and sets it in global context for the request lifecycle.
"""

from litestar.types import ASGIApp, Scope, Receive, Send

from app.auth.scope_context import CurrentScope, set_request_scope


class ScopeMiddleware:
    """Middleware that extracts and sets request scope in global context.

    ContextVars are safe for concurrent async requests - each asyncio task
    automatically gets its own isolated context.
    """

    def __init__(self, app: ASGIApp) -> None:
        """Initialize middleware with ASGI app."""
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Extract scope from session and set in context for this request.

        Note: This runs AFTER session middleware, so session data is available.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Get session data from scope (populated by session middleware)
        session = scope.get("session", {})

        user_id = session.get("user_id")
        scope_type = session.get("scope_type")

        # Build CurrentScope if we have auth data
        current_scope = None
        if user_id and scope_type:
            if scope_type == "team":
                team_id = session.get("team_id")
                if team_id:
                    current_scope = CurrentScope(
                        user_id=user_id,
                        scope_type="team",
                        team_id=team_id,
                        campaign_id=None,
                    )
            elif scope_type == "campaign":
                campaign_id = session.get("campaign_id")
                if campaign_id:
                    current_scope = CurrentScope(
                        user_id=user_id,
                        scope_type="campaign",
                        team_id=None,
                        campaign_id=campaign_id,
                    )

        # Set in context for this request
        # ContextVars are async-safe: each asyncio task gets isolated context
        set_request_scope(current_scope)

        try:
            await self.app(scope, receive, send)
        finally:
            # Clear context after request completes
            # This ensures no context leakage between requests
            set_request_scope(None)
