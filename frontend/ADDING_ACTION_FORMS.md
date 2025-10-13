# Adding Forms for Actions

This guide explains how to add custom forms for actions that require data input.

## When Do You Need a Custom Form?

If an action requires data (like UpdatePost, UpdateInvoice, etc.), you'll need to create a custom form for it. Actions that don't require data (like Delete, Publish) work automatically.

## Step 1: Create the Form Component

Create a form component in `frontend/src/components/actions/action-forms/`:

```tsx
// frontend/src/components/actions/action-forms/update-post-form.tsx
'use client';

import { createTypedForm } from '@/components/forms/base';
import type { AppPostsSchemasPostUpdateDTOSchema } from '@/openapi/managerLab.schemas';
import { Button } from '@/components/ui/button';

// Create a typed form for the UpdatePost action
const { Form, FormString, FormText } =
  createTypedForm<AppPostsSchemasPostUpdateDTOSchema>();

interface UpdatePostFormProps {
  onSubmit: (data: AppPostsSchemasPostUpdateDTOSchema) => void;
  onCancel: () => void;
  isSubmitting: boolean;
  defaultValues?: Partial<AppPostsSchemasPostUpdateDTOSchema>;
}

export function UpdatePostForm({
  onSubmit,
  onCancel,
  isSubmitting,
  defaultValues,
}: UpdatePostFormProps) {
  return (
    <Form onSubmit={onSubmit} defaultValues={defaultValues}>
      <FormString name="content" label="Content" placeholder="Post content" />

      <FormText
        name="notes"
        label="Notes"
        placeholder="Add notes..."
        rows={4}
      />

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
    </Form>
  );
}
```

## Step 2: Create a Form Registry

Create `frontend/src/components/actions/action-forms/registry.tsx`:

```tsx
import type { ActionDTO } from '@/openapi/managerLab.schemas';
import { UpdatePostForm } from './update-post-form';

type ActionFormComponent = React.ComponentType<{
  action: ActionDTO;
  onSubmit: (data: Record<string, unknown>) => void;
  onCancel: () => void;
  isSubmitting: boolean;
  defaultValues?: Record<string, unknown>;
}>;

/**
 * Registry mapping action keys to their form components
 */
const ACTION_FORMS: Record<string, ActionFormComponent> = {
  post_actions__post_update: (props) => <UpdatePostForm {...props} />,
  // Add more action forms here as needed
};

/**
 * Get the form component for an action, or null if no form is registered
 */
export function getActionForm(actionKey: string): ActionFormComponent | null {
  return ACTION_FORMS[actionKey] || null;
}
```

## Step 3: Update Component to Use Forms

Modify your action menu/button components to check for registered forms:

```tsx
import { getActionForm } from '@/components/actions/action-forms/registry';
import { ActionFormDialog } from '@/components/actions/action-form-dialog';

// In your component:
const FormComponent = executor.pendingAction
  ? getActionForm(executor.pendingAction.action)
  : null;

return (
  <>
    {/* Your existing action button/menu */}

    {/* Add form dialog */}
    {FormComponent && (
      <ActionFormDialog
        open={executor.showForm}
        action={executor.pendingAction}
        isExecuting={executor.isExecuting}
        onCancel={executor.cancelAction}
      >
        <FormComponent
          action={executor.pendingAction}
          onSubmit={executor.executeWithData}
          onCancel={executor.cancelAction}
          isSubmitting={executor.isExecuting}
        />
      </ActionFormDialog>
    )}
  </>
);
```

## Step 4: Trigger Form Instead of Direct Execution

Update the action executor hook to show forms for actions that have registered forms:

```tsx
// In useActionExecutor hook:
const initiateAction = useCallback((action: ActionDTO) => {
  // Check if action has a form
  const formComponent = getActionForm(action.action);

  if (formComponent) {
    showFormForAction(action);
    return;
  }

  // Existing logic for confirmation/direct execution
  if (action.confirmation_message) {
    // ... show confirmation
  } else {
    // ... execute directly
  }
}, []);
```

## Example: Complete Flow

1. User clicks "Update Post" action
2. System checks if form is registered for `post_actions__post_update`
3. If form exists, shows `ActionFormDialog` with `UpdatePostForm`
4. User fills form and clicks "Update Post"
5. Form calls `executor.executeWithData(formData)`
6. Action executes with data, shows success toast
7. Dialog closes, table/detail view refreshes

## Action Key Format

Action keys follow this pattern:

- Object actions: `{action_group}__{action_name}` (e.g., `post_actions__post_update`)
- Top-level actions: `{action_group}__{action_name}` (e.g., `top_level_post_actions__top_level_post_create`)

You can find these in the backend action definitions or by inspecting the `action` field in the ActionDTO.
