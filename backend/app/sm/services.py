"""State machine service methods."""

from typing import TYPE_CHECKING, Dict, Any, Optional
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession

from app.sm.models import StateTransitionLog, MachineSpec
from app.objects.models.base import BaseObject

if TYPE_CHECKING:
    pass


class StateMachineService:
    """Service for managing state machine transitions."""

    def __init__(self, machine_spec: MachineSpec):
        self.machine_spec = machine_spec

    async def transition_to(
        self,
        session: AsyncSession,
        obj: BaseObject,
        target_state: Enum,
        user_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Transition an object to a new state.

        Returns True if successful, False if transition was not allowed.
        Raises exception for system errors.
        """
        if context is None:
            context = {}

        current_state_enum = self.machine_spec.enum_type(obj.state)
        current_state_class = self.machine_spec.get_state_class(current_state_enum)
        target_state_class = self.machine_spec.get_state_class(target_state)

        current_state_instance = current_state_class(self.machine_spec)
        target_state_instance = target_state_class(self.machine_spec)

        # Check if transition is allowed by state machine definition
        if target_state not in current_state_instance.transitions:
            await self._log_transition(
                session=session,
                obj=obj,
                from_state=current_state_enum.value,
                to_state=target_state.value,
                user_id=user_id,
                context=context,
                success=False,
                error_message=(
                    f"Transition not allowed: {current_state_enum.value} -> "
                    f"{target_state.value}"
                ),
            )
            return False

        # Check if current state allows leaving
        can_leave = await current_state_instance.can_leave(
            session=session, obj=obj, to=target_state, ctx=context
        )
        if not can_leave:
            await self._log_transition(
                session=session,
                obj=obj,
                from_state=current_state_enum.value,
                to_state=target_state.value,
                user_id=user_id,
                context=context,
                success=False,
                error_message=(
                    f"Current state {current_state_enum.value} does not allow leaving"
                ),
            )
            return False

        # Check if target state allows entry
        can_enter = await target_state_instance.can_enter(
            session=session, obj=obj, from_state_class=current_state_class, ctx=context
        )
        if not can_enter:
            await self._log_transition(
                session=session,
                obj=obj,
                from_state=current_state_enum.value,
                to_state=target_state.value,
                user_id=user_id,
                context=context,
                success=False,
                error_message=f"Target state {target_state.value} does not allow entry",
            )
            return False

        # Perform the transition
        try:
            # Exit current state
            await current_state_instance.on_exit(
                session=session, obj=obj, to_state_class=target_state_class, ctx=context
            )

            # Update the object state
            old_state = obj.state
            obj.state = target_state.value
            obj.increment_version()

            # Enter new state
            await target_state_instance.on_enter(
                session=session,
                obj=obj,
                from_state_class=current_state_class,
                ctx=context,
            )

            # Log successful transition
            await self._log_transition(
                session=session,
                obj=obj,
                from_state=old_state,
                to_state=target_state.value,
                user_id=user_id,
                context=context,
                success=True,
            )

            return True

        except Exception as e:
            # Log failed transition
            await self._log_transition(
                session=session,
                obj=obj,
                from_state=current_state_enum.value,
                to_state=target_state.value,
                user_id=user_id,
                context=context,
                success=False,
                error_message=str(e),
            )
            raise

    async def get_available_transitions(
        self, session: AsyncSession, obj: BaseObject
    ) -> list[Enum]:
        """Get list of states this object can transition to."""
        current_state_enum = self.machine_spec.enum_type(obj.state)
        current_state_class = self.machine_spec.get_state_class(current_state_enum)
        current_state_instance = current_state_class(self.machine_spec)

        available = []
        for target_state in current_state_instance.transitions:
            target_state_class = self.machine_spec.get_state_class(target_state)
            target_state_instance = target_state_class(self.machine_spec)

            # Check both can_leave and can_enter
            can_leave = await current_state_instance.can_leave(
                session=session, obj=obj, to=target_state
            )
            can_enter = await target_state_instance.can_enter(
                session=session, obj=obj, from_state_class=current_state_class
            )

            if can_leave and can_enter:
                available.append(target_state)

        return available

    async def _log_transition(
        self,
        session: AsyncSession,
        obj: BaseObject,
        from_state: str,
        to_state: str,
        user_id: Optional[int],
        context: Dict[str, Any],
        success: bool,
        error_message: Optional[str] = None,
    ) -> None:
        """Log a state transition attempt."""
        log_entry = StateTransitionLog(
            object_type=obj.object_type,
            object_id=obj.id,
            from_state=from_state,
            to_state=to_state,
            user_id=user_id,
            context=context,
            success=success,
            error_message=error_message,
        )
        session.add(log_entry)
        await (
            session.flush()
        )  # Ensure the log is written even if parent transaction fails
