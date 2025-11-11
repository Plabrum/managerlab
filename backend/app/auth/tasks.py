"""Authentication-related background tasks."""

from datetime import UTC, datetime, timedelta

from saq.types import Context
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.auth.models import MagicLinkToken, TeamInvitationToken
from app.queue.registry import scheduled_task

__all__ = ["cleanup_expired_tokens"]


@scheduled_task(cron="0 2 * * *", timeout=600)
async def cleanup_expired_tokens(ctx: Context) -> dict:
    """Clean up expired and used authentication tokens.

    This task runs daily at 2 AM UTC and deletes:
    - Magic link tokens that are expired or used and older than 7 days
    - Team invitation tokens that are expired or accepted and older than 7 days

    Args:
        ctx: SAQ task context

    Returns:
        Dictionary with cleanup statistics
    """
    # Get database session from context
    session_maker: async_sessionmaker = ctx["db_sessionmaker"]

    async with session_maker() as session:
        cutoff_date = datetime.now(tz=UTC) - timedelta(days=7)

        # Delete old magic link tokens (expired or used)
        magic_link_delete_stmt = delete(MagicLinkToken).where(
            (MagicLinkToken.expires_at < cutoff_date) | (MagicLinkToken.used_at < cutoff_date)
        )
        magic_link_result = await session.execute(magic_link_delete_stmt)
        magic_links_deleted = magic_link_result.rowcount

        # Delete old invitation tokens (expired or accepted)
        invitation_delete_stmt = delete(TeamInvitationToken).where(
            (TeamInvitationToken.expires_at < cutoff_date) | (TeamInvitationToken.accepted_at < cutoff_date)
        )
        invitation_result = await session.execute(invitation_delete_stmt)
        invitations_deleted = invitation_result.rowcount

        await session.commit()

        result = {
            "magic_links_deleted": magic_links_deleted,
            "invitations_deleted": invitations_deleted,
            "cutoff_date": cutoff_date.isoformat(),
        }

        ctx["logger"].info(f"Token cleanup completed: {result}")
        return result
