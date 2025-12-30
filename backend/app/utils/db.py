"""Database utility functions for common operations."""

from enum import Enum
from typing import Any

from litestar import Request
from litestar.exceptions import NotFoundException
from msgspec import structs
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.compiler import compiles

from app.auth.enums import ScopeType
from app.base.models import BaseDBModel
from app.base.schemas import BaseSchema
from app.events.enums import EventType
from app.events.schemas import CreatedEventData, UpdatedEventData, make_field_changes
from app.events.service import emit_event
from app.utils.configure import config

logger = logging.getLogger(__name__)


class TextEnum[E: Enum](types.TypeDecorator[E]):
    """Store enum as TEXT, converting between enum and string.

    This avoids PostgreSQL ENUM type complexity when adding/removing values.
    Values are stored as the enum's .name attribute.

    Example:
        class Status(str, Enum):
            DRAFT = "draft"
            PUBLISHED = "published"

        class Post(Base):
            status: Mapped[Status] = mapped_column(
                TextEnum(Status),
                nullable=False,
                default=Status.DRAFT,
            )
    """

    impl = types.Text
    cache_ok = True

    def __init__(self, enum_class: type[E], *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value: E | None, dialect: Any) -> str | None:
        """Convert enum to string for database."""
        if value is None:
            return None
        return value.name

    def process_result_value(self, value: str | None, dialect: Any) -> E | None:
        """Convert string from database to enum."""
        if value is None:
            return None
        return self.enum_class[value]


@compiles(TextEnum, "postgresql")
def compile_text_enum(element: TextEnum, compiler: Any, **kw: Any) -> str:
    """Compile TextEnum to TEXT for PostgreSQL."""
    return "TEXT"


async def _emit_created_event(
    session: AsyncSession,
    obj: BaseDBModel,
    user_id: int,
    team_id: int,
    create_vals: BaseSchema,
    track_fields: list[str] | None,
) -> None:
    """Helper to emit a CREATED event for a newly created object."""
    # Determine which fields to track
    if track_fields is None:
        # Track all non-None fields from create_vals
        initial_values = {field: value for field, value in structs.asdict(create_vals).items() if value is not None}
    else:
        # Track only specified fields
        initial_values = {field: getattr(obj, field, None) for field in track_fields}

    await emit_event(
        session=session,
        event_type=EventType.CREATED,
        obj=obj,
        user_id=user_id,
        team_id=team_id,
        event_data=CreatedEventData(initial_values=initial_values),
    )


async def _emit_updated_event(
    session: AsyncSession,
    obj: BaseDBModel,
    user_id: int,
    team_id: int,
    old_values: dict[str, Any],
) -> None:
    """Helper to emit an UPDATED event for a modified object."""
    # Capture new values after update
    new_values = {field: getattr(obj, field, None) for field in old_values.keys() if hasattr(obj, field)}

    # Compute changes and emit event if anything changed
    changes = make_field_changes(old_values, new_values)
    if changes:
        await emit_event(
            session=session,
            event_type=EventType.UPDATED,
            obj=obj,
            user_id=user_id,
            team_id=team_id,
            event_data=UpdatedEventData(changes=changes),
        )


async def get_or_404[T: BaseDBModel](
    session: AsyncSession,
    model_class: type[T],
    id: int,
    load_options: list | None = None,
) -> T:
    query = select(model_class).where(model_class.id == id)
    if load_options:
        query = query.options(*load_options)

    result = await session.execute(query)
    entity = result.unique().scalar_one_or_none()
    if not entity:
        raise NotFoundException(detail="Not found")
    return entity


async def update_model[T: BaseDBModel](
    session: AsyncSession,
    model_instance: T,
    update_vals: BaseSchema,
    user_id: int,
    team_id: int | None,
    should_track: bool = True,
    track_fields: list[str] | None = None,
) -> T:
    """Update a model instance from a DTO/struct, with optional event tracking.

    Updates are declarative: all fields in update_vals are applied to the model.
    Nested objects (e.g., address) are handled recursively - existing nested
    objects are updated, None clears the relationship.

    Args:
        session: Database session
        model_instance: The model instance to update
        update_vals: DTO/struct with complete update data (all fields required)
        user_id: User who is updating the object
        team_id: Team ID for RLS and event tracking (None for user-owned resources)
        should_track: Whether to emit an UPDATED event (default: True)
        track_fields: Optional list of field names to track for changes.
                     If None, tracks all non-nested fields from update_vals.

    Returns:
        The updated model instance
    """
    # Convert update_vals to dict
    # Note: Recursively convert nested Structs to dicts for proper handling
    update_dict = structs.asdict(update_vals)
    fields_to_update = {}
    for k, v in update_dict.items():
        # Recursively convert nested Structs to dicts
        if hasattr(v, "__struct_fields__"):  # It's a msgspec Struct
            fields_to_update[k] = structs.asdict(v)
        else:
            fields_to_update[k] = v

    # Capture old values before update (if tracking is enabled)
    old_values = None
    if should_track and team_id is not None:
        if track_fields:
            # Use explicitly provided track_fields
            fields_to_track = track_fields
        else:
            # Auto-determine fields to track: exclude nested objects (fields with {field}_id)
            fields_to_track = [
                field
                for field in fields_to_update.keys()
                if not hasattr(model_instance, f"{field}_id")  # Skip nested objects
            ]
        old_values = {
            field: getattr(model_instance, field, None) for field in fields_to_track if hasattr(model_instance, field)
        }

    # Update the model (handle nested objects recursively)
    for field, value in fields_to_update.items():
        if not hasattr(model_instance, field):
            continue

        # Check if this is a nested object relationship (has {field}_id foreign key)
        nested_id_field = f"{field}_id"
        if hasattr(model_instance, nested_id_field):
            # This is a nested object field (e.g., address)
            # Don't include it in tracked fields or try to set it directly
            if value is None:
                # Clear the relationship
                setattr(model_instance, nested_id_field, None)
            elif isinstance(value, dict):
                # Update existing nested object
                existing_nested = getattr(model_instance, field, None)
                if existing_nested:
                    for nested_field, nested_value in value.items():
                        if hasattr(existing_nested, nested_field):
                            setattr(existing_nested, nested_field, nested_value)
                else:
                    # Cannot auto-create nested object - let action handle it
                    logger.warning(f"Cannot auto-create nested object for field '{field}' - handle in action")
            else:
                # Value is not a dict or None - this shouldn't happen with proper schemas
                logger.warning(f"Unexpected value type for nested field '{field}': {type(value)}")
        else:
            # Regular field - set directly
            setattr(model_instance, field, value)

    await session.flush()

    # Emit event if tracking is enabled
    if old_values is not None:
        try:
            await _emit_updated_event(
                session=session,
                obj=model_instance,
                user_id=user_id,
                team_id=team_id,  # type: ignore - we know it's not None here
                old_values=old_values,
            )
        except Exception as e:
            logger.warning(f"Failed to emit UPDATED event: {e}")

    return model_instance


async def create_model[T: BaseDBModel](
    session: AsyncSession,
    team_id: int | None,
    campaign_id: int | None,
    model_class: type[T],
    create_vals: BaseSchema,
    user_id: int,
    ignore_fields: list[str] | None = None,
    should_track: bool = True,
    track_fields: list[str] | None = None,
) -> T:
    """Create a new model instance from a DTO/struct, with optional event tracking.

    Args:
        session: Database session
        team_id: Team ID for RLS
        campaign_id: Campaign ID for RLS (optional)
        model_class: The model class to instantiate
        create_vals: DTO/struct with creation data
        user_id: User who is creating the object
        should_track: Whether to emit a CREATED event (default: True)
        track_fields: Optional list of field names to include in event data.
                     If None, includes all non-None fields from create_vals.

    Returns:
        The created model instance (after flush, with ID)
    """
    ignore_fields = ignore_fields or []
    # Create the model instance
    data = {
        field: value
        for field, value in structs.asdict(create_vals).items()
        if value is not None and field not in ignore_fields
    }

    # Add row-level security context
    rls_fields = {}
    if team_id is not None:
        rls_fields["team_id"] = team_id
    if campaign_id is not None:
        rls_fields["campaign_id"] = campaign_id

    merged = {**data, **rls_fields}
    obj = model_class(**merged)

    session.add(obj)
    await session.flush()

    # Emit CREATED event if tracking is enabled
    event_team_id = team_id if team_id is not None else campaign_id
    if should_track and event_team_id is not None:
        try:
            await _emit_created_event(
                session=session,
                obj=obj,
                user_id=user_id,
                team_id=event_team_id,
                create_vals=create_vals,
                track_fields=track_fields,
            )
        except Exception as e:
            logger.warning(f"Failed to emit CREATED event: {e}")

    return obj


async def set_rls_variables(session: AsyncSession, request: Request) -> None:
    """Set PostgreSQL RLS session variables for database-level security.

    Session variables for RLS:
    - app.team_id: Set when user has team scope
    - app.campaign_id: Set when user has campaign scope
    - app.is_system_mode: Set to true for admin/system operations that bypass RLS

    Note: Must be called within an active transaction (after begin()).
    SET LOCAL is transaction-scoped and doesn't support parameter binding.
    We use f-strings with validated integer IDs, which is safe since PostgreSQL
    expects numeric literals for SET LOCAL with integer values.

    Application-level filters are set via session.info in provide_transaction().
    """
    # Set system mode flag
    if config.IS_SYSTEM_MODE:
        await session.execute(text("SET LOCAL app.is_system_mode = true"))
        return  # System mode bypasses all scope checks

    # Check for scope_type in session
    scope_type = request.session.get("scope_type")

    if not scope_type:
        # No scope set - this is an unauthenticated request (e.g., login, signup)
        # Don't set any RLS variables. Tables with RLS will return empty results,
        # tables without RLS (sessions, users for lookup) will work normally.
        logger.warning(
            "No scope_type in session - RLS variables NOT set",
            extra={
                "path": request.url.path,
                "session_keys": list(request.session.keys()),
                "has_user_id": bool(request.session.get("user_id")),
            },
        )
        return

    if scope_type == ScopeType.TEAM.value:
        team_id = request.session.get("team_id")
        if team_id:
            await session.execute(text(f"SET LOCAL app.team_id = {team_id}"))
        else:
            raise ValueError("scope_type is TEAM but no team_id in session")

    elif scope_type == ScopeType.CAMPAIGN.value:
        campaign_id = request.session.get("campaign_id")
        if campaign_id:
            await session.execute(text(f"SET LOCAL app.campaign_id = {campaign_id}"))
        else:
            raise ValueError("scope_type is CAMPAIGN but no campaign_id in session")
    else:
        raise ValueError(f"Invalid scope_type in session: {scope_type}")
