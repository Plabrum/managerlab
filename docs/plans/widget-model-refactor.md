# Widget Model Refactor Plan

## Overview

Refactor widgets from JSONB storage in Dashboard.config to their own database model. This enables:
- Widget-level actions (edit, delete) via standard ObjectActions pattern
- Proper permissions and RLS support
- Activity tracking per widget
- Cleaner architecture following existing patterns

---

## Part 1: Backend - Widget Model

### 1.1 Create Widget Model

**File:** `backend/app/dashboard/models.py`

```python
class Widget(BaseDBModel):
    """Widget within a dashboard."""

    __tablename__ = "widgets"

    dashboard_id: Mapped[int] = mapped_column(
        sa.ForeignKey("dashboards.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(sa.String(50), nullable=False)  # bar_chart, line_chart, etc.
    title: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(sa.Text, nullable=True)
    query: Mapped[dict[str, Any]] = mapped_column(
        MutableDict.as_mutable(JSONB),
        nullable=False,
        server_default=sa.text("'{}'::jsonb"),
    )
    position_x: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    position_y: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=0)
    size_w: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)
    size_h: Mapped[int] = mapped_column(sa.Integer, nullable=False, default=1)

    # Relationships
    dashboard: Mapped["Dashboard"] = relationship(back_populates="widgets")

    # Team scoping (inherited from dashboard, but needed for RLS)
    team_id: Mapped[int] = mapped_column(sa.ForeignKey("teams.id"), nullable=False)
```

**Update Dashboard model:**
```python
# Add to Dashboard class
widgets: Mapped[list["Widget"]] = relationship(
    back_populates="dashboard",
    cascade="all, delete-orphan",
    order_by="Widget.position_y, Widget.position_x",
)
```

### 1.2 Create Migration

**File:** `backend/alembic/versions/xxx_add_widgets_table.py`

```python
def upgrade():
    # Create widgets table
    op.create_table(
        "widgets",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("dashboard_id", sa.BigInteger(), nullable=False),
        sa.Column("team_id", sa.BigInteger(), nullable=False),
        sa.Column("type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("query", JSONB(), nullable=False, server_default="{}"),
        sa.Column("position_x", sa.Integer(), nullable=False, default=0),
        sa.Column("position_y", sa.Integer(), nullable=False, default=0),
        sa.Column("size_w", sa.Integer(), nullable=False, default=1),
        sa.Column("size_h", sa.Integer(), nullable=False, default=1),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["dashboard_id"], ["dashboards.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Migrate existing JSONB widgets to new table
    # (Run data migration script separately or include here)

def downgrade():
    op.drop_table("widgets")
```

### 1.3 Data Migration Script

**File:** `backend/scripts/migrate_widgets.py`

```python
"""Migrate widgets from Dashboard.config JSONB to Widget table."""

async def migrate_widgets():
    async with get_session() as session:
        dashboards = await session.execute(select(Dashboard))
        for dashboard in dashboards.scalars():
            widgets_config = dashboard.config.get("widgets", [])
            for w in widgets_config:
                widget = Widget(
                    dashboard_id=dashboard.id,
                    team_id=dashboard.team_id,
                    type=w.get("type"),
                    title=w.get("display", {}).get("title", "Untitled"),
                    description=w.get("display", {}).get("description"),
                    query=w.get("query", {}),
                    position_x=w.get("position", {}).get("x", 0),
                    position_y=w.get("position", {}).get("y", 0),
                    size_w=w.get("size", {}).get("w", 1),
                    size_h=w.get("size", {}).get("h", 1),
                )
                session.add(widget)
            # Clear old config
            dashboard.config["widgets"] = []
        await session.commit()
```

---

## Part 2: Backend - Widget Schemas

### 2.1 Create Widget Schemas

**File:** `backend/app/dashboard/schemas.py`

```python
class WidgetSchema(BaseSchema):
    """Response schema for Widget."""
    id: Sqid
    dashboard_id: Sqid
    type: str
    title: str
    description: str | None
    query: dict[str, Any]
    position_x: int
    position_y: int
    size_w: int
    size_h: int
    created_at: datetime
    updated_at: datetime
    actions: list[ActionDTO]


class CreateWidgetSchema(BaseSchema):
    """Schema for creating a widget."""
    dashboard_id: Sqid
    type: str  # bar_chart, line_chart, pie_chart, stat_number
    title: str
    description: str | None = None
    query: dict[str, Any]
    position_x: int = 0
    position_y: int = 0
    size_w: int = 1
    size_h: int = 1


class UpdateWidgetSchema(BaseSchema):
    """Schema for updating a widget."""
    type: str | None = None
    title: str | None = None
    description: str | None = None
    query: dict[str, Any] | None = None
    position_x: int | None = None
    position_y: int | None = None
    size_w: int | None = None
    size_h: int | None = None


class ReorderWidgetsSchema(BaseSchema):
    """Schema for reordering widgets (batch position update)."""
    widgets: list[dict[str, Any]]  # [{ id: Sqid, position_x: int, position_y: int }]
```

---

## Part 3: Backend - Widget Actions

### 3.1 Create Action Group Type

**File:** `backend/app/actions/enums.py`

```python
class ActionGroupType(StrEnum):
    # ... existing ...
    WidgetActions = "widget_actions"
```

### 3.2 Create Widget Enums

**File:** `backend/app/dashboard/enums.py`

```python
class WidgetActions(StrEnum):
    """Widget action keys."""
    create = "create"
    update = "update"
    delete = "delete"
```

### 3.3 Create Widget Actions

**File:** `backend/app/dashboard/widget_actions.py`

```python
from app.actions import ActionGroupType, BaseObjectAction, BaseTopLevelAction, action_group_factory
from app.actions.base import EmptyActionData
from app.actions.deps import ActionDeps
from app.actions.enums import ActionIcon
from app.actions.schemas import ActionExecutionResponse
from app.dashboard.enums import WidgetActions
from app.dashboard.models import Widget
from app.dashboard.schemas import CreateWidgetSchema, UpdateWidgetSchema
from app.utils.db import update_model

widget_actions = action_group_factory(
    ActionGroupType.WidgetActions,
    model_type=Widget,
)


@widget_actions
class CreateWidget(BaseTopLevelAction[CreateWidgetSchema]):
    """Create a new widget."""

    action_key = WidgetActions.create
    label = "Add Widget"
    priority = 10
    icon = ActionIcon.plus

    @classmethod
    async def execute(
        cls,
        data: CreateWidgetSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        widget = Widget(
            dashboard_id=data.dashboard_id,
            team_id=deps.team_id,
            type=data.type,
            title=data.title,
            description=data.description,
            query=data.query,
            position_x=data.position_x,
            position_y=data.position_y,
            size_w=data.size_w,
            size_h=data.size_h,
        )
        transaction.add(widget)
        await transaction.flush()

        return ActionExecutionResponse(
            message="Widget created successfully",
            invalidate_queries=["dashboards", "widgets"],
        )


@widget_actions
class UpdateWidget(BaseObjectAction[Widget, UpdateWidgetSchema]):
    """Update a widget."""

    action_key = WidgetActions.update
    label = "Edit"
    priority = 10
    icon = ActionIcon.edit

    @classmethod
    async def execute(
        cls,
        obj: Widget,
        data: UpdateWidgetSchema,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await update_model(
            session=transaction,
            model_instance=obj,
            update_vals=data,
            user_id=deps.user,
            team_id=obj.team_id,
        )

        return ActionExecutionResponse(
            message="Widget updated successfully",
            invalidate_queries=["dashboards", "widgets"],
        )


@widget_actions
class DeleteWidget(BaseObjectAction[Widget, EmptyActionData]):
    """Delete a widget."""

    action_key = WidgetActions.delete
    label = "Delete"
    priority = 100
    icon = ActionIcon.trash
    confirmation_message = "Are you sure you want to delete this widget?"

    @classmethod
    async def execute(
        cls,
        obj: Widget,
        data: EmptyActionData,
        transaction: AsyncSession,
        deps: ActionDeps,
    ) -> ActionExecutionResponse:
        await transaction.delete(obj)

        return ActionExecutionResponse(
            message="Widget deleted successfully",
            invalidate_queries=["dashboards", "widgets"],
        )
```

---

## Part 4: Backend - Widget Routes

### 4.1 Create Widget Controller

**File:** `backend/app/dashboard/widget_routes.py`

```python
from litestar import Controller, get, post, patch, delete
from litestar.di import Provide

from app.dashboard.models import Widget
from app.dashboard.schemas import WidgetSchema, CreateWidgetSchema, UpdateWidgetSchema, ReorderWidgetsSchema


class WidgetController(Controller):
    path = "/widgets"
    tags = ["Widgets"]

    @get("/{widget_id:int}")
    async def get_widget(self, widget_id: int) -> WidgetSchema:
        """Get a single widget by ID."""
        ...

    @post("/reorder")
    async def reorder_widgets(self, data: ReorderWidgetsSchema) -> dict:
        """Batch update widget positions (for drag-and-drop reordering)."""
        ...
```

### 4.2 Update Dashboard Schema to Include Widgets

**File:** `backend/app/dashboard/schemas.py`

```python
class DashboardSchema(BaseSchema):
    # ... existing fields ...
    widgets: list[WidgetSchema]  # Add this
```

### 4.3 Update Dashboard Query to Load Widgets

**File:** `backend/app/dashboard/routes.py`

```python
# Add eager loading for widgets
dashboard_actions = action_group_factory(
    ActionGroupType.DashboardActions,
    model_type=Dashboard,
    load_options=[selectinload(Dashboard.widgets)],  # Add this
)
```

---

## Part 5: Frontend Changes

### 5.1 Run Codegen

```bash
make codegen
```

This generates:
- `WidgetSchema`, `CreateWidgetSchema`, `UpdateWidgetSchema`
- `widget_actions__create`, `widget_actions__update`, `widget_actions__delete` action types

### 5.2 Update Actions Registry

**File:** `frontend/src/lib/actions/registry.tsx`

```typescript
// Add to ActionToObjectMap
widget_actions__create: never;  // Top-level action
widget_actions__update: WidgetSchema;
widget_actions__delete: WidgetSchema;

// Add to actionRegistry
widget_actions__create: {
  render: ({ onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => (
    <CreateWidgetForm ... />
  ),
},
widget_actions__update: {
  render: ({ objectData, onSubmit, onClose, isSubmitting, isOpen, actionLabel }) => (
    <UpdateWidgetForm defaultValues={objectData} ... />
  ),
},
widget_actions__delete: {
  render: () => null,  // Uses confirmation dialog
},
```

### 5.3 Create Widget Forms

**File:** `frontend/src/components/actions/create-widget-form.tsx`

```typescript
'use client';

import { createTypedForm } from '@/components/forms/base';
import type { CreateWidgetSchema } from '@/openapi/ariveAPI.schemas';

const { FormModal, FormString, FormSelect, FormCustom } = createTypedForm<CreateWidgetSchema>();

export function CreateWidgetForm({ ... }) {
  return (
    <FormModal ...>
      <FormSelect name="type" label="Widget Type" options={WIDGET_TYPES} required />
      <FormString name="title" label="Title" required />
      <FormString name="description" label="Description (optional)" />
      <FormCustom name="query">
        {({ value, onChange }) => <QueryBuilderForm query={value} onChange={onChange} />}
      </FormCustom>
    </FormModal>
  );
}
```

**File:** `frontend/src/components/actions/update-widget-form.tsx`

Similar to CreateWidgetForm but for updates.

### 5.4 Update WidgetContainer to Show Actions

**File:** `frontend/src/components/dashboard/widget-container.tsx`

```typescript
import { ObjectActions } from '@/components/object-detail';
import { ActionGroupType } from '@/openapi/ariveAPI.schemas';

interface WidgetContainerProps {
  widget: WidgetSchema;  // Now uses the full schema with actions
  children: React.ReactNode;
  onRefetch: () => void;
}

export function WidgetContainer({ widget, children, onRefetch }: WidgetContainerProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{widget.title}</CardTitle>
        {/* Widget actions (Edit, Delete) appear here */}
        <ObjectActions
          data={widget}
          actionGroup={ActionGroupType.widget_actions}
          onRefetch={onRefetch}
        />
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
```

### 5.5 Update DashboardContent

**File:** `frontend/src/components/dashboard-content.tsx`

```typescript
// Widgets now come from dashboard.widgets (not dashboard.config.widgets)
const widgets = dashboard.widgets;

// Render each widget with its own actions
{widgets.map((widget) => (
  <WidgetContainer
    key={widget.id}
    widget={widget}
    onRefetch={onUpdate}
  >
    {renderWidget(widget)}
  </WidgetContainer>
))}
```

### 5.6 Handle Widget Reordering

For drag-and-drop reordering, call the `/widgets/reorder` endpoint:

```typescript
const handleWidgetReorder = async (reorderedWidgets: WidgetSchema[]) => {
  await widgetsReorder({
    widgets: reorderedWidgets.map((w, index) => ({
      id: w.id,
      position_x: index % 3,
      position_y: Math.floor(index / 3),
    })),
  });
  onUpdate();
};
```

### 5.7 Remove Old Widget Editor Drawer

Delete `frontend/src/components/dashboard/widget-editor-drawer.tsx` - no longer needed since widgets use standard action forms.

---

## Part 6: Cleanup

### 6.1 Remove Old Dashboard Widget Actions

**File:** `backend/app/dashboard/enums.py`

Remove:
```python
edit_widget = "edit_widget"
delete_widget = "delete_widget"
```

**File:** `backend/app/dashboard/actions.py`

Remove `EditWidget` and `DeleteWidget` classes (move to widget_actions.py).

### 6.2 Remove Dashboard.config Widget Storage

After migration is complete and verified, remove widget storage from Dashboard.config:
- Remove `config["widgets"]` handling from dashboard update logic
- Optionally remove `config` column if no longer needed

---

## Files Summary

| File | Action |
|------|--------|
| `backend/app/dashboard/models.py` | Add Widget model, update Dashboard |
| `backend/app/dashboard/schemas.py` | Add widget schemas |
| `backend/app/dashboard/enums.py` | Add WidgetActions enum |
| `backend/app/dashboard/widget_actions.py` | Create (new file) |
| `backend/app/dashboard/widget_routes.py` | Create (new file) |
| `backend/app/actions/enums.py` | Add WidgetActions group type |
| `backend/alembic/versions/xxx_add_widgets.py` | Create migration |
| `frontend/src/lib/actions/registry.tsx` | Register widget actions |
| `frontend/src/components/actions/create-widget-form.tsx` | Create |
| `frontend/src/components/actions/update-widget-form.tsx` | Create |
| `frontend/src/components/dashboard/widget-container.tsx` | Add ObjectActions |
| `frontend/src/components/dashboard-content.tsx` | Use dashboard.widgets |
| `frontend/src/components/dashboard/widget-editor-drawer.tsx` | Delete |

---

## Implementation Order

1. Create Widget model and migration
2. Create widget schemas
3. Add WidgetActions to action group types
4. Create widget actions (create, update, delete)
5. Create widget routes (get, reorder)
6. Update Dashboard schema to include widgets
7. Run `make codegen`
8. Create frontend widget forms
9. Update actions registry
10. Update WidgetContainer with ObjectActions
11. Update DashboardContent to use dashboard.widgets
12. Remove old widget-editor-drawer
13. Run data migration script
14. Clean up old dashboard widget code
