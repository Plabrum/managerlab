"""Authentication guards for route protection."""

from litestar.connection import ASGIConnection
from litestar.exceptions import PermissionDeniedException, NotAuthorizedException
from litestar.handlers.base import BaseRouteHandler

from app.users.models import User


def requires_authenticated_user(
    connection: ASGIConnection, _: BaseRouteHandler
) -> None:
    """Guard that requires an authenticated user.

    Raises:
        NotAuthorizedException: If no user is authenticated.
    """
    if not connection.user:
        raise NotAuthorizedException("Authentication required")


def requires_active_user(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires an active user account.

    Raises:
        NotAuthorizedException: If no user is authenticated.
        PermissionDeniedException: If user account is not active.
    """
    user: User | None = connection.user

    if not user:
        raise NotAuthorizedException("Authentication required")

    # For now, all users are considered active since we don't have an active field
    # This can be extended when we add user account status fields
    # if not user.is_active:
    #     raise PermissionDeniedException("Account is not active")


def requires_verified_user(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires a verified user account.

    Raises:
        NotAuthorizedException: If no user is authenticated.
        PermissionDeniedException: If user account is not verified.
    """
    user: User | None = connection.user

    if not user:
        raise NotAuthorizedException("Authentication required")

    if not user.email_verified:
        raise PermissionDeniedException("Email verification required")


def requires_superuser(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Guard that requires superuser privileges.

    Raises:
        NotAuthorizedException: If no user is authenticated.
        PermissionDeniedException: If user is not a superuser.
    """
    user: User | None = connection.user

    if not user:
        raise NotAuthorizedException("Authentication required")

    # For now, check if user has superuser email patterns
    # This can be extended when we add proper role/permission system
    superuser_emails = ["admin@manageros.com", "support@manageros.com"]

    if user.email not in superuser_emails:
        raise PermissionDeniedException("Superuser privileges required")
