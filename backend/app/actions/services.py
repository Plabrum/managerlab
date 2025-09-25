"""Action service and registry."""

from typing import TYPE_CHECKING, Dict, Any, List, Type
import time

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.actions.models import ActionLog, BaseAction
from app.objects.models.base import BaseObject

if TYPE_CHECKING:
    pass


class ActionRegistry:
    """Registry for actions by object type."""

    def __init__(self):
        self._actions: Dict[str, List[Type[BaseAction]]] = {}

    def register(self, object_type: str, action_class: Type[BaseAction]) -> None:
        """Register an action for an object type."""
        if object_type not in self._actions:
            self._actions[object_type] = []
        self._actions[object_type].append(action_class)

    def get_actions(self, object_type: str) -> List[Type[BaseAction]]:
        """Get all actions for an object type."""
        return self._actions.get(object_type, [])

    def get_action(self, object_type: str, action_name: str) -> Type[BaseAction] | None:
        """Get a specific action by name."""
        actions = self.get_actions(object_type)
        for action_class in actions:
            # Check action_name class property
            if action_class.action_name == action_name:
                return action_class
        return None


# Global action registry
action_registry = ActionRegistry()


class ActionService:
    """Service for managing action execution."""

    def __init__(self, registry: ActionRegistry = None):
        self.registry = registry or action_registry

    async def get_available_actions(
        self,
        session: AsyncSession,
        obj: BaseObject,
        user_id: int | None = None,
        context: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        """Get all available actions for an object, sorted by priority."""
        if context is None:
            context = {}

        actions = self.registry.get_actions(obj.object_type)
        available_actions = []

        for action_class in actions:
            action_instance = action_class()
            is_available = await action_instance.is_available(
                session=session, obj=obj, user_id=user_id, context=context
            )

            available_actions.append(
                {
                    "action": action_class.action_name,
                    "label": action_class.label,
                    "available": is_available,
                    "priority": action_class.priority,
                }
            )

        # Sort by priority then name
        available_actions.sort(key=lambda x: (x["priority"], x["action"]))
        return available_actions

    async def perform_action(
        self,
        session: AsyncSession,
        obj: BaseObject,
        action_name: str,
        user_id: int | None = None,
        object_version: int | None = None,
        idempotency_key: str | None = None,
        context: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Perform an action on an object.

        Returns:
        - success: bool
        - result: Dict[str, Any] - action result or error details
        - new_state: Optional[str]
        - updated_fields: Optional[Dict[str, Any]]
        """
        if context is None:
            context = {}

        start_time = time.time()
        action_result = {
            "success": False,
            "result": {},
            "new_state": None,
            "updated_fields": None,
        }

        try:
            # Check for idempotency
            if idempotency_key:
                existing_log = await self._find_existing_action(
                    session=session,
                    obj=obj,
                    action_name=action_name,
                    idempotency_key=idempotency_key,
                )
                if existing_log:
                    # Return cached result
                    return {
                        "success": existing_log.success,
                        "result": existing_log.result or {},
                        "new_state": None,  # State already applied
                        "updated_fields": None,
                    }

            # Verify object version for optimistic locking
            if object_version is not None and obj.object_version != object_version:
                raise ValueError(
                    f"Object version mismatch. Expected {object_version}, "
                    f"got {obj.object_version}"
                )

            # Find the action
            action_class = self.registry.get_action(obj.object_type, action_name)
            if not action_class:
                raise ValueError(f"Unknown action: {action_name}")

            action_instance = action_class()

            # Check if action is available
            is_available = await action_instance.is_available(
                session=session, obj=obj, user_id=user_id, context=context
            )
            if not is_available:
                raise ValueError(f"Action {action_name} is not available")

            # Perform the action
            result = await action_instance.perform(
                session=session, obj=obj, user_id=user_id, context=context
            )

            execution_time = int((time.time() - start_time) * 1000)

            # Log successful action
            await self._log_action(
                session=session,
                obj=obj,
                action_name=action_name,
                user_id=user_id,
                object_version=obj.object_version,
                idempotency_key=idempotency_key,
                context=context,
                result=result,
                success=True,
                execution_time_ms=execution_time,
            )

            action_result.update(
                {
                    "success": True,
                    "result": result.get("result", {}),
                    "new_state": result.get("new_state"),
                    "updated_fields": result.get("updated_fields"),
                }
            )

            return action_result

        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)

            # Log failed action
            await self._log_action(
                session=session,
                obj=obj,
                action_name=action_name,
                user_id=user_id,
                object_version=obj.object_version,
                idempotency_key=idempotency_key,
                context=context,
                result=None,
                success=False,
                error_message=str(e),
                execution_time_ms=execution_time,
            )

            action_result.update({"success": False, "result": {"error": str(e)}})

            return action_result

    async def _find_existing_action(
        self,
        session: AsyncSession,
        obj: BaseObject,
        action_name: str,
        idempotency_key: str,
    ) -> ActionLog | None:
        """Find existing action log by idempotency key."""
        stmt = (
            select(ActionLog)
            .where(
                ActionLog.object_type == obj.object_type,
                ActionLog.object_id == obj.id,
                ActionLog.action_name == action_name,
                ActionLog.idempotency_key == idempotency_key,
            )
            .order_by(ActionLog.created_at.desc())
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def _log_action(
        self,
        session: AsyncSession,
        obj: BaseObject,
        action_name: str,
        user_id: int | None,
        object_version: int,
        idempotency_key: str | None,
        context: Dict[str, Any],
        result: Dict[str, Any] | None,
        success: bool,
        error_message: str | None = None,
        execution_time_ms: int | None = None,
    ) -> None:
        """Log an action execution."""
        log_entry = ActionLog(
            object_type=obj.object_type,
            object_id=obj.id,
            action_name=action_name,
            user_id=user_id,
            object_version=object_version,
            idempotency_key=idempotency_key,
            context=context,
            result=result,
            success=success,
            error_message=error_message,
            execution_time_ms=execution_time_ms,
        )
        session.add(log_entry)
        await session.flush()  # Ensure the log is written
