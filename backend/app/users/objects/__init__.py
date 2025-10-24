"""User objects module.

Contains object definitions for users domain.
"""

from app.users.objects.team import TeamObject
from app.users.objects.user import UserObject

__all__ = ["UserObject", "TeamObject"]
