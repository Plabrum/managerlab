# Universal Action Execution System

## Overview

The action system provides a universal way to handle all user actions across the application, with automatic support for:

- **Simple actions** - Execute immediately (no code needed)
- **Confirmation dialogs** - For destructive actions (backend controlled)
- **Custom forms** - For actions requiring data (page-specific callbacks)
- **Type-safe** - Leverages discriminated unions from OpenAPI schema
- Success/error toasts
- Loading states

**See [ACTION_SYSTEM_GUIDE.md](./ACTION_SYSTEM_GUIDE.md) for detailed usage examples.**

## Architecture

### Core Components

```
frontend/src/
├── hooks/
│   └── use-action-executor.ts              # Main orchestration hook
├── components/
│   ├── actions/
│   │   ├── action-confirmation-dialog.tsx  # Confirmation UI
│   │   ├── action-form-dialog.tsx          # Form wrapper UI
│   │   └── update-post-form.tsx            # Example custom form
│   ├── actions-menu.tsx                    # Top-level actions menu
│   └── object-detail/
│       └── object-actions.tsx              # Object-level actions menu
```

**No global registry!** Forms are defined per-page via callbacks.

## How Actions Work

### Backend Action Definition

Actions are defined in the backend and control their own behavior:

```python
# Simple action - executes immediately
@post_actions
class PublishPost(BaseAction):
    action_key = PostActions.publish
    label = "Publish"

    @classmethod
    async def execute(cls, obj: Post) -> ActionExecutionResponse:
        obj.state = PostStates.POSTED
        return ActionExecutionResponse(success=True, message="Published post")

# Confirmation action - shows dialog
@post_actions
class DeletePost(BaseAction):
    action_key = PostActions.delete
    label = "Delete"
    confirmation_message = "Are you sure you want to delete this post?"

    @classmethod
    async def execute(cls, obj: Post, transaction: AsyncSession) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(success=True, message="Deleted post")

# Data-requiring action - needs custom form
@post_actions
class UpdatePost(BaseAction):
    action_key = PostActions.update
    label = "Update"

    @classmethod
    async def execute(cls, obj: Post, data: PostUpdateDTO, transaction: AsyncSession) -> ActionExecutionResponse:
        update_model(obj, data)
        return ActionExecutionResponse(success=True, message="Updated post")
```

### Frontend Action Flow

1. **Action List Fetched**: Frontend receives `ActionDTO[]` from API
2. **User Clicks Action**: Triggers `executor.initiateAction(action)`
3. **Action Type Detection**:
   - Has custom form renderer? → Show form dialog
   - Has `confirmation_message`? → Show confirmation dialog
   - Neither? → Execute directly with `{ action: "key" }`
4. **Execution**: Call action API with discriminated union body
5. **Result Handling**: Show toast, trigger callbacks, close dialogs

### Type-Safe Execution

The backend generates a discriminated union for all actions:

```typescript
// Auto-generated from OpenAPI schema
export type ActionsActionGroupExecuteActionBody =
  | DeletePostAction // { action: "post_actions__post_delete" }
  | UpdatePostAction // { action: "post_actions__post_update", data: PostUpdateDTO }
  | PublishPostAction // { action: "post_actions__post_publish" }
  | CreatePostAction; // { action: "top_level_post_actions__top_level_post_create", data: PostCreateDTO }
// ... all other actions
```

This ensures type safety at compile time!

## Action Types

### 1. Simple Actions (No Confirmation, No Data)

**Example**: Publish Post

```typescript
// Backend
@post_actions
class PublishPost(BaseAction):
    action_key = PostActions.publish
    label = "Publish"

    @classmethod
    async def execute(cls, obj: Post) -> ActionExecutionResponse:
        obj.state = PostStates.POSTED
        return ActionExecutionResponse(success=True, message="Published post")
```

**Behavior**: Executes immediately when clicked, shows success toast.

### 2. Confirmation Actions (No Data)

**Example**: Delete Post

```typescript
// Backend
@post_actions
class DeletePost(BaseAction):
    action_key = PostActions.delete
    label = "Delete"
    confirmation_message = "Are you sure you want to delete this post?"

    @classmethod
    async def execute(cls, obj: Post, transaction: AsyncSession) -> ActionExecutionResponse:
        await transaction.delete(obj)
        return ActionExecutionResponse(success=True, message="Deleted post")
```

**Behavior**: Shows confirmation dialog → User confirms → Executes → Shows success toast.

### 3. Form Actions (Requires Data)

**Example**: Update Post

```typescript
// Backend - defines the action
@post_actions
class UpdatePost(BaseAction):
    action_key = PostActions.update
    label = "Update"

    @classmethod
    async def execute(cls, obj: Post, data: PostUpdateDTO, transaction: AsyncSession) -> ActionExecutionResponse:
        update_model(obj, data)
        return ActionExecutionResponse(success=True, message="Updated post")

// Frontend - provides custom form via callback
const renderPostActionForm = useCallback((props) => {
  if (props.action.action === 'post_actions__post_update') {
    return (
      <UpdatePostForm
        defaultValues={data}
        onSubmit={props.onSubmit}
        onCancel={props.onCancel}
        isSubmitting={props.isSubmitting}
      />
    );
  }
  return null;
}, [data]);

<ObjectActions
  actions={data.actions}
  actionGroup="post_actions"
  objectId={id}
  renderActionForm={renderPostActionForm}
/>
```

**Behavior**: Shows form dialog → User fills form → Submits → Executes with data → Shows success toast.

## Using Actions in Your Components

### Top-Level Actions (List Pages)

```tsx
import { ActionsMenu } from '@/components/actions-menu';

function PostsPage() {
  const { data } = useListObjectsSuspense('posts', request);

  return (
    <ActionsMenu
      actions={data.actions}
      actionGroup="top_level_post_actions"
      onActionComplete={() => {
        // Optional: Refetch data, invalidate queries, etc.
      }}
    />
  );
}
```

### Object-Level Actions (Detail Pages)

Simple usage (actions work automatically):

```tsx
import { ObjectActions } from '@/components/object-detail/object-actions';

function PostDetailPage({ id }: { id: string }) {
  const { data } = useOObjectTypeIdGetObjectDetailSuspense('posts', id);

  return (
    <ObjectActions
      actions={data.actions}
      actionGroup="post_actions"
      objectId={id}
    />
  );
}
```

With custom forms (for data-requiring actions):

```tsx
import { ObjectActions } from '@/components/object-detail/object-actions';
import { UpdatePostForm } from '@/components/actions/update-post-form';
import { useCallback } from 'react';

function PostDetailPage({ id }: { id: string }) {
  const { data } = useOObjectTypeIdGetObjectDetailSuspense('posts', id);

  const renderPostActionForm = useCallback(
    (props) => {
      if (props.action.action === 'post_actions__post_update') {
        return (
          <UpdatePostForm
            defaultValues={data}
            onSubmit={props.onSubmit}
            onCancel={props.onCancel}
            isSubmitting={props.isSubmitting}
          />
        );
      }
      return null;
    },
    [data]
  );

  return (
    <ObjectActions
      actions={data.actions}
      actionGroup="post_actions"
      objectId={id}
      renderActionForm={renderPostActionForm}
    />
  );
}
```

## API Reference

### `useActionExecutor` Hook

```typescript
type ActionFormRenderer = (props: {
  action: ActionDTO;
  onSubmit: (data: Record<string, unknown>) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}) => React.ReactNode | null;

const executor = useActionExecutor({
  actionGroup: ActionGroupType;           // e.g., 'post_actions'
  objectId?: string;                      // Optional for object-level actions
  renderActionForm?: ActionFormRenderer;  // Optional custom form renderer
  onSuccess?: (action, response) => void;
  onError?: (action, error) => void;
});

// Returns:
{
  isExecuting: boolean;              // Is action currently running?
  pendingAction: ActionDTO | null;   // Currently selected action
  showConfirmation: boolean;         // Should show confirmation dialog?
  showForm: boolean;                 // Should show form dialog?
  error: string | null;              // Current error message
  renderActionForm?: ActionFormRenderer; // The form renderer

  initiateAction: (action: ActionDTO) => void;     // Start action flow
  confirmAction: () => void;                       // Confirm pending action
  cancelAction: () => void;                        // Cancel pending action
  executeWithData: (data: object) => void;         // Execute with form data
  showFormForAction: (action: ActionDTO) => void;  // Manually show form
}
```

### Action Execution Request Format

```typescript
// For actions without data
{
  action: "post_actions__post_publish",
  data: {}
}

// For actions with data
{
  action: "post_actions__post_update",
  data: {
    content: "Updated content",
    notes: { key: "value" }
  }
}
```

### Action Execution Response Format

```typescript
{
  success: boolean;
  message: string;           // Shown in toast
  results?: object;          // Optional additional data
}
```

## Action Groups

Available action groups (from `backend/app/actions/enums.py`):

- `media_actions` - Actions on media objects
- `top_level_media_actions` - Actions at media list level
- `post_actions` - Actions on post objects
- `top_level_post_actions` - Actions at posts list level
- `brand_actions` - Actions on brand objects
- `campaign_actions` - Actions on campaign objects
- `top_level_campaign_actions` - Actions at campaigns list level
- `invoice_actions` - Actions on invoice objects
- `top_level_invoice_actions` - Actions at invoices list level

## Extending the System

### Adding a New Simple Action (Backend)

```python
# backend/app/posts/actions.py
@post_actions
class ArchivePost(BaseAction):
    action_key = PostActions.archive
    label = "Archive"
    priority = 50
    icon = ActionIcon.archive
    confirmation_message = "Archive this post?"

    @classmethod
    async def execute(cls, obj: Post) -> ActionExecutionResponse:
        obj.archived = True
        return ActionExecutionResponse(success=True, message="Post archived")
```

**Done!** The frontend will automatically handle this action with confirmation.

### Adding a New Data-Requiring Action

See [ACTION_SYSTEM_GUIDE.md](./ACTION_SYSTEM_GUIDE.md) for complete guide with examples.

## Error Handling

The system automatically handles errors:

1. **Network Errors**: Shows error toast with message
2. **Validation Errors**: Shows error toast (form validation should prevent most)
3. **Backend Errors**: Shows error message from `ActionExecutionResponse`
4. **Missing Data**: Currently shows error toast (will be improved with form registry)

## Best Practices

### Backend

1. **Always provide confirmation for destructive actions** (delete, archive, etc.)
2. **Keep action labels short and clear** ("Delete", not "Delete This Post")
3. **Use appropriate icons** (trash for delete, send for publish, etc.)
4. **Set priority for action ordering** (0 = highest priority, shown first)
5. **Return helpful success messages** ("Post published successfully" not just "Success")

### Frontend

1. **Keep forms co-located with pages** - Don't create global registries
2. **Use TypeScript for type safety** - Import schema types for forms
3. **Return null for unhandled actions** - Let system execute automatically
4. **Access page data in forms** - Pass defaultValues from page state
5. **Use `onActionComplete` callback** - Refresh data after successful actions

## Troubleshooting

### Action button does nothing

- Check that `actionGroup` prop matches backend action group
- Check browser console for errors
- Verify action has `available: true` in ActionDTO

### Confirmation dialog doesn't appear

- Verify action has `confirmation_message` defined in backend
- Check that action is in the `availableActions` list

### Form needed but not showing

- Action requires data but no form renderer provided
- Add `renderActionForm` callback to your component
- See [ACTION_SYSTEM_GUIDE.md](./ACTION_SYSTEM_GUIDE.md) for examples
- Temporarily, action will try to execute and may fail with error toast

### Wrong action executes

- Verify `actionGroup` matches the object type
- Check that `objectId` is provided for object-level actions
