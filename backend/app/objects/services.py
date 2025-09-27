from datetime import date, datetime
from decimal import Decimal
from typing import Any


from app.objects.schemas import FieldType


#
#
# class ObjectService:
#     """Base service for object operations."""
#
#     def __init__(self, action_service: "ActionService"):
#         self.action_service = action_service
#
#     async def get_object_detail(
#         self,
#         session: AsyncSession,
#         obj: BaseObject,
#         user_id: int | None = None,
#         include_actions: bool = True,
#     ) -> ObjectDetailDTO:
#         """Convert object to detailed DTO."""
#         # Get state info
#         state = await self._get_state_dto(obj)
#
#         # Get fields
#         fields = await self._get_object_fields(obj)
#
#         # Get actions if requested
#         actions = []
#         if include_actions:
#             action_data = await self.action_service.get_available_actions(
#                 session=session, obj=obj, user_id=user_id
#             )
#             actions = [ActionDTO(**action) for action in action_data]
#
#         # Get relationships (placeholder for now)
#         children, parents = await self._get_object_relationships(session, obj)
#
#         return ObjectDetailDTO(
#             id=SqidDTO(obj.id),
#             object_type=obj.object_type,
#             state=state,
#             object_version=obj.object_version,
#             fields=fields,
#             actions=actions,
#             children=children,
#             parents=parents,
#             created_at=obj.created_at.isoformat(),
#             updated_at=obj.updated_at.isoformat(),
#         )
#
#     async def get_object_list_item(
#         self, session: AsyncSession, obj: BaseObject, user_id: int | None = None
#     ) -> ObjectListDTO:
#         """Convert object to list item DTO."""
#         # Get state info
#         state = await self._get_state_dto(obj)
#
#         # Get title and subtitle
#         title, subtitle = await self._get_object_title_subtitle(obj)
#
#         # Get key actions only (limit to 3 most important)
#         action_data = await self.action_service.get_available_actions(
#             session=session, obj=obj, user_id=user_id
#         )
#         # Filter only available actions and limit to 3
#         available_actions = [
#             ActionDTO(action=a["action"], label=a["label"], priority=a["priority"])
#             for a in action_data
#             if a["available"]
#         ][:3]
#
#         return ObjectListDTO(
#             sqid=obj.sqid,
#             object_type=obj.object_type,
#             title=title,
#             subtitle=subtitle,
#             state=state,
#             actions=available_actions,
#             created_at=obj.created_at.isoformat(),
#             updated_at=obj.updated_at.isoformat(),
#         )
#
#     async def _get_state_dto(self, obj: BaseObject) -> StateDTO:
#         """Get state DTO for object."""
#         # This should be overridden by specific object services
#         # For now, return basic state info
#         return StateDTO(key=obj.state, label=obj.state.replace("_", " ").title())
#
#     async def _get_object_fields(self, obj: BaseObject) -> List[ObjectFieldDTO]:
#         """Get field DTOs for object."""
#         # This should be overridden by specific object services
#         # For now, return basic fields
#         fields = []
#
#         # Add basic fields
#         fields.append(
#             ObjectFieldDTO(
#                 key="id",
#                 value=obj.sqid,
#                 type=FieldType.STRING,
#                 label="ID",
#                 editable=False,
#             )
#         )
#
#         fields.append(
#             ObjectFieldDTO(
#                 key="created_at",
#                 value=obj.created_at.isoformat(),
#                 type=FieldType.DATETIME,
#                 label="Created At",
#                 editable=False,
#             )
#         )
#
#         fields.append(
#             ObjectFieldDTO(
#                 key="updated_at",
#                 value=obj.updated_at.isoformat(),
#                 type=FieldType.DATETIME,
#                 label="Updated At",
#                 editable=False,
#             )
#         )
#
#         return fields
#
#     async def _get_object_title_subtitle(
#         self, obj: BaseObject
#     ) -> tuple[str, str | None]:
#         """Get title and subtitle for object."""
#         # This should be overridden by specific object services
#         return f"{obj.object_type.title()} {obj.sqid}", None
#
#     async def _get_object_relationships(
#         self, session: AsyncSession, obj: BaseObject
#     ) -> tuple[List[Dict[str, ObjectRelationDTO]], List[Dict[str, ObjectRelationDTO]]]:
#         """Get object relationships."""
#         # This should be overridden by specific object services
#         # For now, return empty relationships
#         return [], []


def convert_value_to_field_type(value: Any) -> tuple[Any, FieldType]:
    """Convert a value to appropriate field type."""
    if value is None:
        return value, FieldType.String

    if isinstance(value, bool):
        return value, FieldType.Bool
    elif isinstance(value, int):
        return value, FieldType.Int
    elif isinstance(value, float):
        return value, FieldType.Float
    elif isinstance(value, Decimal):
        return float(value), FieldType.USD  # Assume decimals are currency
    elif isinstance(value, date):
        return value.isoformat(), FieldType.Date
    elif isinstance(value, datetime):
        return value.isoformat(), FieldType.Datetime
    elif isinstance(value, str):
        # Check for email pattern
        if "@" in value and "." in value.split("@")[-1]:
            return value, FieldType.Email
        # Check for URL pattern
        elif value.startswith(("http://", "https://")):
            return value, FieldType.URL
        # Check if it's long text
        elif len(value) > 100:
            return value, FieldType.Text
        else:
            return value, FieldType.String
    else:
        return str(value), FieldType.String
