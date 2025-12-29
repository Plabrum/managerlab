# Universal Action Execution System - Developer Guide

## Overview

The action system provides a universal way to handle all user actions across the application with automatic support for:

- **Simple actions** - Execute immediately (e.g., Publish)
- **Confirmation dialogs** - For destructive actions (e.g., Delete)
- **Custom forms** - For actions requiring data input (e.g., Update)
- **Type-safe** - Leverages TypeScript discriminated unions from OpenAPI schema

## Quick Start

### Simple Actions (No Code Needed!)

Actions without confirmation or data requirements work automatically:

```tsx
<ObjectActions
  actions={data.actions}
  actionGroup="post_actions"
  objectId={id}
/>
```

That's it! Actions like "Publish" will execute immediately when clicked.

### Actions with Confirmation

Actions with a `confirmation_message` automatically show a confirmation dialog:

```python
# Backend
@post_actions
class DeletePost(BaseAction):
    confirmation_message = "Are you sure you want to delete this post?"
```

No frontend code needed - the dialog appears automatically!

### Actions Requiring Data (Custom Forms)

For actions that need user input, provide a `renderActionForm` callback:

```tsx
import { UpdatePostForm } from '@/components/actions/update-post-form';
import { useCallback } from 'react';

const renderPostActionForm = useCallback(
  (props) => {
    const { action, onSubmit, onCancel, isSubmitting } = props;

    // Check action key and return custom form
    if (action.action === 'post_actions__post_update') {
      return (
        <UpdatePostForm
          defaultValues={data} // Pass page data
          onSubmit={onSubmit}
          onCancel={onCancel}
          isSubmitting={isSubmitting}
        />
      );
    }

    // Return null for actions without custom forms
    return null;
  },
  [data]
);

<ObjectActions
  actions={data.actions}
  actionGroup="post_actions"
  objectId={id}
  renderActionForm={renderPostActionForm}
/>;
```

## Creating a Custom Action Form

### Step 1: Create the Form Component

```tsx
// frontend/src/components/actions/update-post-form.tsx
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import type { AppPostsSchemasPostUpdateDTOSchema } from '@/openapi/managerLab.schemas';
import { useState } from 'react';

interface UpdatePostFormProps {
  defaultValues?: Partial<AppPostsSchemasPostUpdateDTOSchema>;
  onSubmit: (data: Record<string, unknown>) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}

export function UpdatePostForm({
  defaultValues,
  onSubmit,
  onCancel,
  isSubmitting,
}: UpdatePostFormProps) {
  const [title, setTitle] = useState(defaultValues?.title || '');
  const [content, setContent] = useState(defaultValues?.content || '');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Build the complete data object matching the schema
    onSubmit({
      title,
      content: content || null,
      platforms: defaultValues?.platforms || 'instagram',
      posting_date: defaultValues?.posting_date || new Date().toISOString(),
      notes: defaultValues?.notes || {},
      state: defaultValues?.state || 'draft',
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="title">Title</Label>
        <Input
          id="title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          disabled={isSubmitting}
          required
        />
      </div>

      <div>
        <Label htmlFor="content">Content</Label>
        <Textarea
          id="content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          disabled={isSubmitting}
          rows={4}
        />
      </div>

      <div className="flex gap-3 pt-4">
        <Button type="submit" disabled={isSubmitting} className="flex-1">
          {isSubmitting ? 'Updating...' : 'Update Post'}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isSubmitting}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
```

### Step 2: Use the Form in Your Page

```tsx
// frontend/src/pages/posts/post-detail-page.tsx
import { useCallback } from 'react';
import { ObjectActions } from '@/components/object-detail';
import { UpdatePostForm } from '@/components/actions/update-post-form';
import { useParams } from '@tanstack/react-router';

export default function PostDetailPage() {
  const { id } = useParams({ from: '/posts/$id' });
  const { data } = useOObjectTypeIdGetObjectDetailSuspense('posts', id);

  const renderPostActionForm = useCallback(
    (props) => {
      if (props.action.action === 'post_actions__post_update') {
        return (
          <UpdatePostForm
            defaultValues={{
              title: data.title,
              state: data.state,
              // ... other fields
            }}
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

### `ActionFormRenderer` Type

```typescript
type ActionFormRenderer = (props: {
  action: ActionDTO;
  onSubmit: (data: Record<string, unknown>) => void;
  onCancel: () => void;
  isSubmitting: boolean;
}) => React.ReactNode | null;
```

### `ActionsMenu` Props

```typescript
interface ActionsMenuProps {
  actions: ActionDTO[]; // Actions to display
  actionGroup: ActionGroupType; // e.g., 'top_level_post_actions'
  onActionComplete?: () => void; // Called after successful execution
  renderActionForm?: ActionFormRenderer; // Optional custom form renderer
}
```

### `ObjectActions` Props

```typescript
interface ObjectActionsProps {
  actions: ActionDTO[]; // Actions to display
  actionGroup: ActionGroupType; // e.g., 'post_actions'
  objectId: string; // Object ID for context
  onActionComplete?: () => void; // Called after successful execution
  renderActionForm?: ActionFormRenderer; // Optional custom form renderer
}
```

## How It Works

### Action Execution Flow

1. **User clicks action** → Opens dropdown menu
2. **User selects action** → `initiateAction(action)` called
3. **System checks**:
   - Has custom form renderer? → Show custom form dialog
   - Has confirmation message? → Show confirmation dialog
   - Neither? → Execute immediately
4. **Execution** → Call API with `{ action: "key", data: {...} }`
5. **Result** → Show toast, call callbacks, close dialogs

### Type Safety with Discriminated Unions

The backend generates discriminated union types for all actions:

```typescript
// Generated from OpenAPI schema
export type ActionsActionGroupExecuteActionBody =
  | DeletePostAction // { action: "post_actions__post_delete" }
  | UpdatePostAction // { action: "post_actions__post_update", data: {...} }
  | PublishPostAction // { action: "post_actions__post_publish" }
  | CreatePostAction; // { action: "top_level_post_actions__top_level_post_create", data: {...} }
// ... more actions
```

The request body is type-checked at compile time!

## Action Keys Reference

Action keys follow the pattern: `{action_group}__{action_name}`

### Common Object Actions

- `post_actions__post_update` - Update post (requires data)
- `post_actions__post_delete` - Delete post (confirmation)
- `post_actions__post_publish` - Publish post (simple)
- `campaign_actions__campaign_update` - Update campaign (requires data)
- `campaign_actions__campaign_delete` - Delete campaign (confirmation)
- `invoice_actions__invoice_update` - Update invoice (requires data)
- `invoice_actions__invoice_delete` - Delete invoice (confirmation)

### Common Top-Level Actions

- `top_level_post_actions__top_level_post_create` - Create post (requires data)
- `top_level_campaign_actions__campaign_create` - Create campaign (requires data)
- `top_level_invoice_actions__invoice_create` - Create invoice (requires data)

## Best Practices

### 1. Keep Forms Co-Located with Pages

Don't create a global form registry. Keep forms near the pages that use them:

```
src/
├── pages/posts/
│   ├── post-detail-page.tsx        # Uses UpdatePostForm
│   └── components/
│       └── update-post-form.tsx    # Form specific to this page
```

Or create shared forms in `src/components/actions/` for reuse.

### 2. Use TypeScript for Type Safety

Import the schema types for your forms:

```tsx
import type { AppPostsSchemasPostUpdateDTOSchema } from '@/openapi/managerLab.schemas';
```

### 3. Handle All Required Fields

Make sure your form submission includes all required fields from the schema:

```tsx
onSubmit({
  // Required fields
  title,
  platforms,
  posting_date,
  notes,
  state,
  // Optional fields
  content: content || null,
  campaign_id: campaignId || undefined,
});
```

### 4. Use Page Data for Default Values

Access page data in your `renderActionForm` callback:

```tsx
const renderForm = useCallback(
  (props) => {
    return (
      <UpdateForm
        defaultValues={{
          title: data.title, // Access page data
          state: data.state,
        }}
        {...props}
      />
    );
  },
  [data]
); // Include data in dependencies
```

### 5. Return null for Unhandled Actions

If your callback doesn't handle an action, return `null`:

```tsx
const renderForm = useCallback((props) => {
  if (props.action.action === 'post_actions__post_update') {
    return <UpdatePostForm {...props} />;
  }

  // Let system handle other actions automatically
  return null;
}, []);
```

## Troubleshooting

### Form doesn't appear when clicking action

**Check:**

- Is `renderActionForm` prop passed to `ObjectActions`/`ActionsMenu`?
- Does your callback return a form component for that action key?
- Check browser console for errors

**Debug:**

```tsx
const renderForm = useCallback((props) => {
  console.log('Action clicked:', props.action.action);
  // ... rest of callback
}, []);
```

### Action executes without showing form

This is expected if your `renderActionForm` returns `null` for that action. The system will try to execute it automatically.

### Type errors with form data

Make sure your form submission matches the schema exactly:

```tsx
// Check the generated type
import type { AppPostsSchemasPostUpdateDTOSchema } from '@/openapi/managerLab.schemas';

// Use it in your form props
interface UpdatePostFormProps {
  defaultValues?: Partial<AppPostsSchemasPostUpdateDTOSchema>;
  onSubmit: (data: Record<string, unknown>) => void;
}
```

### Confirmation dialog doesn't appear

Confirmations are controlled by the backend. Check that the action has `confirmation_message` set:

```python
@post_actions
class DeletePost(BaseAction):
    confirmation_message = "Are you sure?"  # Add this
```

## Examples

See the complete working example in:

- **Form**: `frontend/src/components/actions/update-post-form.tsx`
- **Usage**: `frontend/src/pages/posts/post-detail-page.tsx`

## Summary

✅ Simple actions work automatically (no code needed)
✅ Confirmations handled by backend
✅ Custom forms via page-specific callbacks
✅ Type-safe with discriminated unions
✅ Form logic co-located with pages
✅ No global registry needed
✅ Access to page data in forms
✅ Progressive enhancement

The system is designed to be simple for simple cases and flexible for complex ones!
